// Draws the measured body root frame on the driven rig, plus the Unity
// world frame at the scene origin, for the Chapter 3 frame figure
// (thesis round of 2026-08-31).
//
// Armed by the flag file /tmp/r5_rootaxes_on, following the same
// self-bootstrap pattern as EvalFrameDump / IntegratedSceneReceiver.
// Axis colours follow Unity's own gizmo convention: x red, y green,
// z blue. The ROOT frame (thick lines, at the hip bone) is the measured
// torso frame as the solver streams it, placed in the scene exactly as
// the receiver places it: PersonAnchor.rotation * Euler(root angles).
// The WORLD frame (thin lines, at the world node) is the Unity world
// the scene is built in. No receiver code is touched.

using System.IO;
using UnityEngine;

public class RootFrameAxes : MonoBehaviour
{
    const string FlagFile = "/tmp/r5_rootaxes_on";
    const float RootLen = 0.38f, WorldLen = 0.5f;
    const float RootWidth = 0.014f, WorldWidth = 0.007f;

    IntegratedSceneReceiver receiver;
    Transform anchor, hip, world;
    LineRenderer[] rootAxes, worldAxes;

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    static void Bootstrap()
    {
        if (!File.Exists(FlagFile)) return;
        new GameObject("RootFrameAxes").AddComponent<RootFrameAxes>();
    }

    static LineRenderer MakeLine(string name, Color c, float width)
    {
        var go = new GameObject(name);
        var lr = go.AddComponent<LineRenderer>();
        lr.material = new Material(Shader.Find("Sprites/Default"));
        lr.startColor = lr.endColor = c;
        lr.startWidth = lr.endWidth = width;
        lr.positionCount = 2;
        lr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        return lr;
    }

    static LineRenderer[] MakeTriad(string prefix, float width)
    {
        return new[]
        {
            MakeLine(prefix + "_x", new Color(0.9f, 0.1f, 0.1f), width),
            MakeLine(prefix + "_y", new Color(0.1f, 0.8f, 0.1f), width),
            MakeLine(prefix + "_z", new Color(0.15f, 0.35f, 1f), width),
        };
    }

    void LateUpdate()
    {
        if (receiver == null)
        {
            receiver = FindFirstObjectByType<IntegratedSceneReceiver>();
            var anchorGo = GameObject.Find("PersonAnchor");
            if (receiver == null || anchorGo == null) return;
            anchor = anchorGo.transform;
            world = anchor.parent;
            hip = FindDeep(anchor.root, "DEF-spine");
            rootAxes = MakeTriad("RootAxis", RootWidth);
            worldAxes = MakeTriad("WorldAxis", WorldWidth);
        }
        if (hip == null)
            hip = FindDeep(null, "DEF-spine");
        if (hip == null || rootAxes == null) return;

        // the measured root frame, composed exactly as the receiver
        // composes it for the hip bone (before the rig rest rotation)
        Quaternion q = anchor.rotation * Quaternion.Euler(receiver.lastRootEuler);
        Vector3 o = hip.position;
        SetTriad(rootAxes, o, q, RootLen);

        if (world != null)
            SetTriad(worldAxes, world.position, world.rotation, WorldLen);
    }

    static void SetTriad(LineRenderer[] axes, Vector3 o, Quaternion q, float len)
    {
        axes[0].SetPosition(0, o); axes[0].SetPosition(1, o + q * Vector3.right * len);
        axes[1].SetPosition(0, o); axes[1].SetPosition(1, o + q * Vector3.up * len);
        axes[2].SetPosition(0, o); axes[2].SetPosition(1, o + q * Vector3.forward * len);
    }

    static Transform FindDeep(Transform root, string name)
    {
        foreach (var t in FindObjectsByType<Transform>(FindObjectsSortMode.None))
            if (t.name == name) return t;
        return null;
    }
}
