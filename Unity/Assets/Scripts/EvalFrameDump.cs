using System.IO;
using UnityEngine;

// Offline evaluation aid: dumps a camera to PNG frames, independent of
// editor window repaints (the editor skips swapbuffers when unfocused, so
// screen capture of an unattended replay records a frozen image).
// Activates only when a flag file exists, so normal sessions are unaffected.
//
// Camera choice: the virtual replica of the recording sensor
// ("SensorPOVCamera", built by ArucoSceneReceiver at the calibrated camera
// pose with the calibrated vertical FOV) when it exists, else Camera.main.
// The POV camera normally renders as a picture-in-picture inset, so its
// viewport rect is temporarily widened to the full target during capture.
//
// Frame naming: the STREAM frame number (ArucoSceneReceiver.lastFrame, the
// frame the receivers applied this Update) — one PNG per distinct stream
// frame, written from LateUpdate so the rendered pose is exactly the one
// that frame carried. This makes the offline pairing against the recorded
// video an exact join on the frame number, with no timing assumptions.
// Without a receiver in the scene it falls back to sequential numbering at
// a fixed sim-time cadence.
public class EvalFrameDump : MonoBehaviour
{
    // R5 flag/output; the older R4 pair is still accepted so pinned R4
    // procedures keep working.
    const string FlagFileR5 = "/tmp/r5_capture_on";
    const string OutDirR5 = "/tmp/r5_frames";
    const string FlagFileR4 = "/tmp/r4_capture_on";
    const string OutDirR4 = "/tmp/r4_frames";
    const float Fps = 30f;   // fallback cadence only (no receiver)

    static string outDir = OutDirR5;

    RenderTexture rt;
    Texture2D tex;
    int n;                   // fallback counter
    float nextT;
    int lastCaptured = int.MinValue;
    ArucoSceneReceiver recv;
    TextMesh[] labels;
    int written;

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    static void Bootstrap()
    {
        if (File.Exists(FlagFileR5)) outDir = OutDirR5;
        else if (File.Exists(FlagFileR4)) outDir = OutDirR4;
        else return;
        if (FindFirstObjectByType<EvalFrameDump>() != null) return;
        new GameObject("EvalFrameDump").AddComponent<EvalFrameDump>();
        Debug.Log("[EvalFrameDump] active -> " + outDir);
    }

    void Start()
    {
        Directory.CreateDirectory(outDir);
        nextT = Time.time;
    }

    /// The sensor-POV replica if the scene built one, else the main camera.
    Camera PickCamera()
    {
        var go = GameObject.Find("SensorPOVCamera");
        if (go != null)
        {
            var c = go.GetComponent<Camera>();
            if (c != null && c.isActiveAndEnabled) return c;
        }
        return Camera.main;
    }

    void EnsureTargets(bool sensorPov)
    {
        if (rt != null) return;
        // Sensor POV: the real color stream is 4:3, and the POV camera
        // carries the calibrated VERTICAL FOV, so a 4:3 target reproduces
        // the recording's horizontal field as well. Main camera: 16:9.
        int w = sensorPov ? 640 : 1280;
        int h = sensorPov ? 480 : 720;
        rt = new RenderTexture(w, h, 24);
        tex = new Texture2D(w, h, TextureFormat.RGB24, false);
        Debug.Log($"[EvalFrameDump] capture target {w}x{h} "
                  + (sensorPov ? "(SensorPOVCamera)" : "(Camera.main)"));
    }

    /// The scene's TextMesh labels ("desk id2", "object id1", ...) sit ON the
    /// marker nodes, and the desk node is right in front of the sensor, so
    /// from the sensor POV a label fills the frame and hides the pose. They
    /// are hidden for the duration of the capture render only; the editor's
    /// own view keeps them.
    void SetLabels(bool visible)
    {
        if (labels == null)
            labels = FindObjectsByType<TextMesh>(FindObjectsSortMode.None);
        foreach (var t in labels)
        {
            if (t == null) continue;
            var r = t.GetComponent<Renderer>();
            if (r != null) r.enabled = visible;
        }
    }

    void Capture(Camera cam, int index)
    {
        var oldTarget = cam.targetTexture;
        var oldRect = cam.rect;
        SetLabels(false);
        // The held-group spheres are pushed toward the camera that renders
        // them; place them for this camera, then give them back to the
        // main camera so the editor view keeps its own placement.
        HeldMarkers.PlaceAll(cam.transform);
        cam.rect = new Rect(0f, 0f, 1f, 1f);   // undo any PiP inset
        cam.targetTexture = rt;
        cam.Render();
        cam.targetTexture = oldTarget;
        cam.rect = oldRect;
        HeldMarkers.PlaceAll(Camera.main != null ? Camera.main.transform : null);
        SetLabels(true);
        RenderTexture.active = rt;
        tex.ReadPixels(new Rect(0, 0, rt.width, rt.height), 0, 0);
        RenderTexture.active = null;
        File.WriteAllBytes($"{outDir}/f{index:D5}.png", tex.EncodeToPNG());
        written++;
    }

    void LateUpdate()
    {
        var cam = PickCamera();
        if (cam == null) return;
        bool sensorPov = cam.gameObject.name == "SensorPOVCamera";
        if (recv == null) recv = FindFirstObjectByType<ArucoSceneReceiver>();

        if (recv != null)
        {
            // Exact join: one PNG per distinct applied stream frame.
            int f = recv.lastFrame;
            if (f < 0 || f == lastCaptured) return;
            EnsureTargets(sensorPov);
            lastCaptured = f;
            Capture(cam, f);
            return;
        }

        if (Time.time < nextT) return;
        nextT += 1f / Fps;
        EnsureTargets(sensorPov);
        Capture(cam, n);
        n++;
    }

    void OnDestroy()
    {
        Debug.Log($"[EvalFrameDump] wrote {written} PNGs to {outDir}");
        if (rt != null) rt.Release();
    }
}
