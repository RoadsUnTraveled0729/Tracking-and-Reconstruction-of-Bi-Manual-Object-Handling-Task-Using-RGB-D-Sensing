using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEngine.Rendering;

// Opt-in still-image renderer for the Chapter 7 presentation revision.
// Reads saved coordinates; never changes the receiver, stream or recording.
[DefaultExecutionOrder(10000)]
public class Chapter7TrailView : MonoBehaviour
{
    const string ConfigPath = "/tmp/ch7_trails_view.json";
    [Serializable] public class Point
    {
        public float x, y, z;
        public int frame, state;
        public Vector3 Position => new Vector3(x, y, z);
    }
    [Serializable] public class Phase { public string name; public int first, last; }
    [Serializable] public class Config
    {
        public string outputDirectory;
        public Point[] reference, marker, wrist;
        // E-034 (the two-hand rail take): the model left wrist, drawn in its
        // own colour pair. Absent (null or empty) in the Chapter 2 view config.
        public Point[] wristLeft;
        public Phase[] phases;
        public Vector3 cameraDirection;
        public float margin, referenceWidth, trackWidth, waypointSize;
        public float dashLength, dashGap, avatarAlpha;
        public int width, height;
    }
    [Serializable] public class CaptureRecord
    {
        public string phase;
        public int first, last, appliedFrame;
        public Vector3 cameraPosition, cameraTarget;
        public float orthographicSize;
        public Vector3[] waypointViewport;
    }

    Config config;
    Transform world;
    ArucoSceneReceiver receiver;
    Camera view;
    Vector3 target;
    Material lineMaterial, ghostMaterial;
    readonly HashSet<string> captured = new HashSet<string>();
    readonly Color referenceColor = new Color(0.22f, 0.22f, 0.22f);
    readonly Color markerColor = new Color(0.17f, 0.63f, 0.17f);
    readonly Color wristColor = new Color(0.12f, 0.47f, 0.71f);
    readonly Color recoveryColor = new Color(1f, 0.5f, 0.05f);
    // left wrist: matplotlib tab:purple measured, tab:pink rebuilt; a held
    // group (state 1, no measurement and no rebuild) is grey on either wrist,
    // the colour of Figure 7.7 (no such frame exists in the Chapter 2 view)
    readonly Color leftWristColor = new Color(0.58f, 0.40f, 0.74f);
    readonly Color leftRecoveryColor = new Color(0.89f, 0.47f, 0.76f);
    readonly Color heldColor = new Color(0.45f, 0.45f, 0.45f);

    bool HasLeftWrist => config.wristLeft != null && config.wristLeft.Length > 0;

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    static void Bootstrap()
    {
        if (File.Exists(ConfigPath))
            new GameObject("Chapter7TrailView").AddComponent<Chapter7TrailView>();
    }

    void Start()
    {
        config = JsonUtility.FromJson<Config>(File.ReadAllText(ConfigPath));
        Directory.CreateDirectory(config.outputDirectory);
        lineMaterial = new Material(Shader.Find("Sprites/Default"));
        ghostMaterial = new Material(Shader.Find("Chapter7/Ghost"));
        ghostMaterial.color = new Color(0.45f, 0.48f, 0.50f, config.avatarAlpha);
        ghostMaterial.renderQueue = (int)RenderQueue.Transparent;
    }

    void PrepareCamera()
    {
        view = new GameObject("Chapter7PresentationCamera").AddComponent<Camera>();
        view.enabled = false;
        view.orthographic = true;
        view.aspect = (float)config.width / config.height;
        view.clearFlags = CameraClearFlags.SolidColor;
        view.backgroundColor = Color.white;
        view.nearClipPlane = 0.01f;
        view.farClipPlane = 100f;
        var bounds = new Bounds(world.TransformPoint(config.reference[0].Position), Vector3.zero);
        foreach (var p in config.reference) bounds.Encapsulate(world.TransformPoint(p.Position));
        foreach (var p in config.marker) bounds.Encapsulate(world.TransformPoint(p.Position));
        // Frame the union of all three displayed phases. The separate full-history
        // plot retains the earlier parked/startup samples.
        foreach (var p in config.wrist)
            if (p.frame >= config.phases[0].first) bounds.Encapsulate(world.TransformPoint(p.Position));
        if (HasLeftWrist)
            foreach (var p in config.wristLeft)
                if (p.frame >= config.phases[0].first) bounds.Encapsulate(world.TransformPoint(p.Position));
        target = bounds.center;
        float distance = bounds.size.magnitude + 1f;
        view.transform.position = target + config.cameraDirection.normalized * distance;
        view.transform.LookAt(target, Vector3.up);
        float halfWidth = 0, halfHeight = 0;
        var sets = new List<Point[]> { config.reference, config.marker, config.wrist };
        if (HasLeftWrist) sets.Add(config.wristLeft);
        foreach (var samples in sets)
            foreach (var p in samples)
            {
                if (p.frame >= 0 && p.frame < config.phases[0].first
                    && (samples == config.wrist || samples == config.wristLeft)) continue;
                var q = view.transform.InverseTransformPoint(world.TransformPoint(p.Position));
                halfWidth = Mathf.Max(halfWidth, Mathf.Abs(q.x));
                halfHeight = Mathf.Max(halfHeight, Mathf.Abs(q.y));
            }
        view.orthographicSize = config.margin * Mathf.Max(halfHeight, halfWidth / view.aspect);
    }

    void Segment(Transform parent, Vector3 a, Vector3 b, Color color, float width)
    {
        var obj = new GameObject("saved_segment");
        obj.transform.SetParent(parent, false);
        var line = obj.AddComponent<LineRenderer>();
        line.useWorldSpace = false;
        line.sharedMaterial = lineMaterial;
        line.startColor = line.endColor = color;
        line.startWidth = line.endWidth = width;
        line.shadowCastingMode = ShadowCastingMode.Off;
        line.receiveShadows = false;
        line.positionCount = 2;
        line.SetPosition(0, a);
        line.SetPosition(1, b);
    }

    void DrawPath(Transform parent, Point[] points, Phase phase, bool wrist, bool left = false)
    {
        for (int i = 1; i < points.Length; i++)
        {
            var a = points[i - 1]; var b = points[i];
            if (a.frame < phase.first || b.frame > phase.last) continue;
            // A missing detection is a visible gap, not an invented segment.
            if (b.frame != a.frame + 1) continue;
            var color = !wrist ? markerColor
                : a.state == 1 ? heldColor
                : left ? (a.state == 2 ? leftRecoveryColor : leftWristColor)
                : (a.state == 2 ? recoveryColor : wristColor);
            Segment(parent, a.Position, b.Position, color, config.trackWidth);
        }
    }

    void DrawReference(Transform parent)
    {
        for (int i = 1; i < config.reference.Length; i++)
        {
            var a = config.reference[i - 1].Position;
            var b = config.reference[i].Position;
            float length = Vector3.Distance(a, b);
            for (float s = 0; s < length; s += config.dashLength + config.dashGap)
                Segment(parent, Vector3.Lerp(a, b, s / length),
                    Vector3.Lerp(a, b, Mathf.Min(s + config.dashLength, length) / length),
                    referenceColor, config.referenceWidth);
        }
        for (int i = 0; i < config.reference.Length; i++)
        {
            var p = config.reference[i].Position;
            var marker = GameObject.CreatePrimitive(PrimitiveType.Cube);
            Destroy(marker.GetComponent<Collider>());
            marker.transform.SetParent(parent, false);
            marker.transform.localPosition = p;
            marker.transform.localScale = Vector3.one * config.waypointSize;
            marker.GetComponent<Renderer>().material.color = referenceColor;
        }
    }

    void Capture(Phase phase, int frame)
    {
        var group = new GameObject("Chapter7PhaseGeometry");
        group.transform.SetParent(world, false);
        DrawReference(group.transform);
        DrawPath(group.transform, config.marker, phase, false);
        DrawPath(group.transform, config.wrist, phase, true);
        if (HasLeftWrist) DrawPath(group.transform, config.wristLeft, phase, true, true);
        var oldMaterials = new Dictionary<SkinnedMeshRenderer, Material[]>();
        var oldDeskMaterials = new Dictionary<Renderer, Material>();
        var hidden = new List<Renderer>();
        foreach (var renderer in FindObjectsByType<SkinnedMeshRenderer>(FindObjectsSortMode.None))
        {
            oldMaterials[renderer] = renderer.sharedMaterials;
            var ghost = new Material[renderer.sharedMaterials.Length];
            for (int i = 0; i < ghost.Length; i++) ghost[i] = ghostMaterial;
            renderer.sharedMaterials = ghost;
        }
        // Receiver annotations belong to the sensor evidence figure, not this task view.
        foreach (var renderer in FindObjectsByType<Renderer>(FindObjectsSortMode.None))
        {
            string lower = renderer.gameObject.name.ToLowerInvariant();
            if (lower == "desk_top")
            {
                oldDeskMaterials[renderer] = renderer.sharedMaterial;
                var neutral = new Material(renderer.sharedMaterial);
                neutral.color = new Color(0.92f, 0.92f, 0.90f);
                renderer.sharedMaterial = neutral;
            }
            if (renderer.enabled && (renderer.GetComponent<TextMesh>() != null
                || lower.Contains("held") || lower.Contains("occl") || lower == "wall_slab"))
            { hidden.Add(renderer); renderer.enabled = false; }
        }
        var rt = new RenderTexture(config.width, config.height, 24);
        var tex = new Texture2D(config.width, config.height, TextureFormat.RGB24, false);
        var previousActive = RenderTexture.active;
        try
        {
            view.targetTexture = rt;
            view.Render();
            RenderTexture.active = rt;
            tex.ReadPixels(new Rect(0, 0, config.width, config.height), 0, 0);
            tex.Apply();
            File.WriteAllBytes(Path.Combine(config.outputDirectory, phase.name + ".png"), tex.EncodeToPNG());
            var record = new CaptureRecord { phase = phase.name, first = phase.first,
                last = phase.last, appliedFrame = frame, cameraPosition = view.transform.position,
                cameraTarget = target, orthographicSize = view.orthographicSize,
                waypointViewport = new Vector3[config.reference.Length] };
            for (int i = 0; i < config.reference.Length; i++)
                record.waypointViewport[i] = view.WorldToViewportPoint(world.TransformPoint(config.reference[i].Position));
            File.WriteAllText(Path.Combine(config.outputDirectory, phase.name + ".json"), JsonUtility.ToJson(record, true));
            captured.Add(phase.name);
            Debug.Log($"[Chapter7TrailView] captured {phase.name} at {frame}");
        }
        finally
        {
            view.targetTexture = null;
            RenderTexture.active = previousActive;
            foreach (var pair in oldMaterials) pair.Key.sharedMaterials = pair.Value;
            foreach (var pair in oldDeskMaterials)
            {
                var temporary = pair.Key.sharedMaterial;
                pair.Key.sharedMaterial = pair.Value;
                Destroy(temporary);
            }
            foreach (var renderer in hidden) renderer.enabled = true;
            group.SetActive(false);
            Destroy(group);
            rt.Release(); Destroy(rt); Destroy(tex);
        }
    }

    void LateUpdate()
    {
        if (config == null || captured.Count == config.phases.Length) return;
        if (receiver == null) receiver = FindFirstObjectByType<ArucoSceneReceiver>();
        if (receiver == null || receiver.lastFrame < 0) return;
        if (world == null)
        {
            var obj = GameObject.Find("ArucoWorld");
            if (obj == null) return;
            world = obj.transform;
            PrepareCamera();
        }
        foreach (var phase in config.phases)
            if (!captured.Contains(phase.name) && receiver.lastFrame == phase.last)
                Capture(phase, receiver.lastFrame);
    }
}
