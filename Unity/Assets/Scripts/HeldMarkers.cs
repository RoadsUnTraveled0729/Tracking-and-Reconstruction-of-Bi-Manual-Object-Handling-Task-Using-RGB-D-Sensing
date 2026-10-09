using System.Collections.Generic;
using UnityEngine;

/// Placement of the status spheres that mark a joint group the record does
/// not carry as measured (IntegratedSceneReceiver, IntegratedSceneReceiverV2,
/// ArmAngleReceiver; the amber pelvis sphere of the V2 receiver uses it too).
///
/// A sphere sits at the origin of its bone, pushed 20 cm toward the camera
/// so the mesh does not bury it. The push has to run along the ray to the
/// camera that RENDERS the image: pushed toward the editor's main camera
/// and rendered from another one, the sphere projects away from its joint.
/// The thesis captures of frames 114 and 700 (Figures 6.3 and 7.9, before
/// 2026-09-07) showed exactly that from SensorPOVCamera: the spheres
/// floated beside the head and the hips. The receivers register each
/// (marker, bone) pair here on every tick; EvalFrameDump calls PlaceAll
/// for the camera it is about to render from and restores the main-camera
/// placement afterwards, so the editor view is unchanged.
public static class HeldMarkers
{
    const float Push = 0.2f;
    static readonly Dictionary<GameObject, Transform> bones = new Dictionary<GameObject, Transform>();

    /// Register the marker's bone and place it for the given camera.
    public static void Place(GameObject marker, Transform bone, Transform cam)
    {
        if (marker == null || bone == null) return;
        bones[marker] = bone;
        Set(marker, bone, cam);
    }

    /// Re-place every registered marker for the camera that renders next.
    public static void PlaceAll(Transform cam)
    {
        foreach (var kv in bones)
            if (kv.Key != null && kv.Value != null) Set(kv.Key, kv.Value, cam);
    }

    static void Set(GameObject marker, Transform bone, Transform cam)
    {
        var pos = bone.position;
        if (cam != null) pos += (cam.position - pos).normalized * Push;
        marker.transform.position = pos;
    }
}
