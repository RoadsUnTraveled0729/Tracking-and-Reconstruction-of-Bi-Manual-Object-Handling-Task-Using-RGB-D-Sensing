using System.IO;
using UnityEditor;
using UnityEditorInternal;
using UnityEngine;

// Unattended Scene-view screenshot of the rig's root node with the
// editor's own transform gizmo (thesis Figure 3.2(b), user direction
// 2026-08-31). Runs in EDIT MODE: no play mode, no streaming, no
// waiting for a frame - the node's coordinate frame does not depend on
// any streamed pose, and the scene rig stands in the T-pose, which is
// the reference configuration of the kinematic model.
//
// Steps once the editor has settled: hide every scene object except
// the rig, select the rig's top-most parent with the Move tool in
// Local pivot rotation (so Unity itself draws that node's axes), frame
// it in the Scene view, and read the Scene-view pixels to a PNG.
//
// Flag files:
//   /tmp/r5_rootshot_on    present -> active
//   /tmp/r5_rootshot.png   the captured Scene view, written when done
//   /tmp/r5_rootshot_state a short status line, ~1/s
[InitializeOnLoad]
internal static class RootFrameShot
{
    const string OnFlag = "/tmp/r5_rootshot_on";
    const string OutPng = "/tmp/r5_rootshot.png";
    const string StateFile = "/tmp/r5_rootshot_state";
    const double SettleSeconds = 25.0;

    static int phase;            // 0 wait, 1 posed, 2 captured
    static int settleTicks;
    static double lastState;
    static Transform rigRootT;

    // The editor does not reliably paint its own tool gizmo while
    // unattended, so the node's axes are drawn as scene LineRenderers,
    // which render in every view: three lines along the node's local
    // axes in Unity's gizmo colours, with TextMesh labels.
    static GameObject MakeAxes(Transform node, float len)
    {
        var parent = new GameObject("RootFrameShotAxes");
        foreach (var (dir, col, name) in new (Vector3, Color, string)[] {
                     (node.right, Color.red, "x"),
                     (node.up, Color.green, "y"),
                     (node.forward, new Color(0.25f, 0.45f, 1f), "z") })
        {
            var go = new GameObject("axis_" + name);
            go.transform.SetParent(parent.transform, false);
            var lr = go.AddComponent<LineRenderer>();
            lr.material = new Material(Shader.Find("Sprites/Default"));
            lr.startColor = lr.endColor = col;
            lr.startWidth = lr.endWidth = 0.045f;
            lr.positionCount = 2;
            lr.SetPosition(0, node.position);
            lr.SetPosition(1, node.position + dir * len);
            var lgo = new GameObject("label_" + name);
            lgo.transform.SetParent(parent.transform, false);
            lgo.transform.position = node.position + dir * (len * 1.15f);
            var tm = lgo.AddComponent<TextMesh>();
            tm.text = name;
            tm.color = col;
            tm.fontSize = 64;
            tm.characterSize = 0.09f;
            tm.anchor = TextAnchor.MiddleCenter;
        }
        return parent;
    }

    static RootFrameShot()
    {
        if (!File.Exists(OnFlag)) return;
        EditorApplication.update += Tick;
    }

    static void State(string s)
    {
        if (EditorApplication.timeSinceStartup - lastState < 1.0) return;
        lastState = EditorApplication.timeSinceStartup;
        try { File.WriteAllText(StateFile, s + "\n"); } catch { }
    }

    static Transform RigRoot()
    {
        foreach (var t in Object.FindObjectsByType<Transform>(FindObjectsSortMode.None))
            if (t.name == "DEF-spine") return t.root;
        return null;
    }

    static void Tick()
    {
        if (phase == 2) return;
        if (EditorApplication.isCompiling || EditorApplication.isUpdating
            || EditorApplication.timeSinceStartup < SettleSeconds)
        {
            State("settling editor");
            return;
        }

        var rig = RigRoot();
        if (rig == null) { State("waiting for rig in scene"); return; }
        rigRootT = rig;

        // hide every other rendered object (SetActive, because the
        // SceneVisibilityManager affects Scene views only, not camera
        // renders); lights and cameras stay
        var scene = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
        Bounds pre = new Bounds(rig.position, Vector3.one * 0.2f);
        foreach (var rend in rig.GetComponentsInChildren<Renderer>())
            pre.Encapsulate(rend.bounds);
        var axes = MakeAxes(rig, pre.extents.y * 0.55f);
        foreach (var root in scene.GetRootGameObjects())
        {
            if (root == rig.gameObject || root == axes) continue;
            if (root.GetComponentInChildren<Renderer>() != null)
                root.SetActive(false);
        }

        // selection kept for fidelity with the manual recipe
        Selection.activeGameObject = rig.gameObject;
        Tools.current = Tool.Move;
        Tools.pivotRotation = PivotRotation.Local;

        // own camera, three-quarter front view (the model faces +z):
        // deterministic render, no editor window involved
        Bounds b = new Bounds(rig.position, Vector3.one * 0.2f);
        foreach (var rend in rig.GetComponentsInChildren<Renderer>())
            b.Encapsulate(rend.bounds);
        Vector3 pivot = new Vector3(b.center.x, b.center.y * 0.88f, b.center.z);
        var camGo = new GameObject("RootFrameShotCamera");
        var cam = camGo.AddComponent<Camera>();
        cam.fieldOfView = 38f;
        cam.nearClipPlane = 0.05f;
        cam.clearFlags = CameraClearFlags.Skybox;
        float dist = (b.extents.y + 0.9f) / Mathf.Tan(19f * Mathf.Deg2Rad);
        Vector3 offset = Quaternion.Euler(10f, 205f, 0f) * (Vector3.back * dist);
        camGo.transform.position = pivot + offset;
        camGo.transform.rotation = Quaternion.LookRotation(
            pivot - camGo.transform.position, Vector3.up);

        // labels face the camera
        foreach (var tm in axes.GetComponentsInChildren<TextMesh>())
            tm.transform.rotation = Quaternion.LookRotation(
                tm.transform.position - camGo.transform.position);

        var rt = new RenderTexture(1500, 1120, 24);
        cam.targetTexture = rt;
        cam.Render();
        RenderTexture.active = rt;
        var tex = new Texture2D(rt.width, rt.height, TextureFormat.RGB24, false);
        tex.ReadPixels(new Rect(0, 0, rt.width, rt.height), 0, 0);
        tex.Apply();
        RenderTexture.active = null;
        File.WriteAllBytes(OutPng, tex.EncodeToPNG());
        Object.DestroyImmediate(tex);
        Object.DestroyImmediate(rt);
        phase = 2;
        try { File.WriteAllText(StateFile, "done\n"); } catch { }
        Debug.Log("[RootFrameShot] wrote " + OutPng);
    }
}
