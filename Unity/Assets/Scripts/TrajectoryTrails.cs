using System.Collections.Generic;
using System.Globalization;
using System.IO;
using UnityEngine;

// Trails inside the reconstruction for the thesis captures (supervisor
// comment C36 "compare these three plots in the same Unity", decision D9,
// 2026-09-07): the reference path of the cube, the tracked marker origin
// and the right wrist placed by the kinematic model, drawn as lines in the
// scene so that the three trajectories of Figure 7.8 appear in the same
// picture as the rendered person and cube.
//
// Activates only when /tmp/r5_trails.txt exists (written by
// writing/v8/condensed/scripts/make_ch7_trails.py), so ordinary sessions
// are unaffected. The file gives every polyline in DISPLAY AXES, the local
// frame of the "ArucoWorld" node; the lines are parented to that node, so
// the receiver's levelling and floor drop apply to them exactly as to the
// streamed poses. A path marked "frames" grows with the stream: on each
// Update only the points whose frame is at or before the applied stream
// frame (ArucoSceneReceiver.lastFrame) are drawn, so a capture at frame f
// shows the trail up to f. A "static" path is drawn whole.
//
// File format, one item per line:
//   path <name> <r> <g> <b> <width_m> <static|frames>
//   p <x> <y> <z> <frame>        (frame -1 for a static path)
public class TrajectoryTrails : MonoBehaviour
{
    const string TrailFile = "/tmp/r5_trails.txt";

    class Trail
    {
        public string name;
        public Color color;
        public float width;
        public bool byFrame;
        public readonly List<Vector3> pts = new List<Vector3>();
        public readonly List<int> frames = new List<int>();
        public LineRenderer lr;
        public int drawn = -1;
    }

    readonly List<Trail> trails = new List<Trail>();
    Transform world;
    ArucoSceneReceiver recv;

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    static void Bootstrap()
    {
        if (!File.Exists(TrailFile)) return;
        if (FindFirstObjectByType<TrajectoryTrails>() != null) return;
        new GameObject("TrajectoryTrails").AddComponent<TrajectoryTrails>();
        Debug.Log("[TrajectoryTrails] active <- " + TrailFile);
    }

    void Start()
    {
        var ci = CultureInfo.InvariantCulture;
        Trail cur = null;
        foreach (var raw in File.ReadAllLines(TrailFile))
        {
            var line = raw.Trim();
            if (line.Length == 0 || line[0] == '#') continue;
            var t = line.Split(' ');
            if (t[0] == "path" && t.Length >= 7)
            {
                cur = new Trail
                {
                    name = t[1],
                    color = new Color(float.Parse(t[2], ci), float.Parse(t[3], ci), float.Parse(t[4], ci)),
                    width = float.Parse(t[5], ci),
                    byFrame = t[6] == "frames",
                };
                trails.Add(cur);
            }
            else if (t[0] == "p" && cur != null && t.Length >= 5)
            {
                cur.pts.Add(new Vector3(float.Parse(t[1], ci), float.Parse(t[2], ci), float.Parse(t[3], ci)));
                cur.frames.Add(int.Parse(t[4], ci));
            }
        }
        Debug.Log($"[TrajectoryTrails] {trails.Count} paths read");
    }

    void Build()
    {
        foreach (var tr in trails)
        {
            var go = new GameObject("trail_" + tr.name);
            go.transform.SetParent(world, false);
            var lr = go.AddComponent<LineRenderer>();
            lr.useWorldSpace = false;
            lr.material = new Material(Shader.Find("Sprites/Default"));
            lr.startColor = lr.endColor = tr.color;
            lr.startWidth = lr.endWidth = tr.width;
            lr.numCornerVertices = 4;
            lr.numCapVertices = 4;
            lr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            lr.receiveShadows = false;
            lr.positionCount = 0;
            tr.lr = lr;
            if (!tr.byFrame)
            {
                // waypoint balls on the static reference path
                for (int i = 0; i < tr.pts.Count; i++)
                {
                    var s = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                    s.name = $"{tr.name}_wp{i}";
                    Destroy(s.GetComponent<Collider>());
                    s.transform.SetParent(world, false);
                    s.transform.localPosition = tr.pts[i];
                    s.transform.localScale = Vector3.one * (tr.width * 2.2f);
                    s.GetComponent<Renderer>().material.color = tr.color;
                }
            }
        }
    }

    void Apply(Trail tr, int frame)
    {
        int k = tr.pts.Count;
        if (tr.byFrame)
        {
            k = 0;
            while (k < tr.pts.Count && tr.frames[k] <= frame) k++;
        }
        if (k == tr.drawn) return;
        tr.drawn = k;
        tr.lr.positionCount = k;
        for (int i = 0; i < k; i++) tr.lr.SetPosition(i, tr.pts[i]);
    }

    void Update()
    {
        if (world == null)
        {
            var go = GameObject.Find("ArucoWorld");
            if (go == null) return;
            world = go.transform;
            Build();
        }
        if (recv == null) recv = FindFirstObjectByType<ArucoSceneReceiver>();
        int frame = recv != null ? recv.lastFrame : int.MaxValue;
        if (frame < 0) return;
        foreach (var tr in trails) Apply(tr, frame);
    }
}
