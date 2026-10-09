using System.IO.MemoryMappedFiles;
using UnityEngine;

/// Reads root + BOTH arms' joint angles (shoulder swing-twist, elbow
/// swing) from shared memory and drives the rig's hip and arm bones.
/// Packet layout mirrors kinematics/send_arm_angles.py (72 bytes,
/// seqlock). Conventions: KINEMATIC_MODEL.md §3-10.
///
/// PSA5 adds a per-joint live mask (u16 at byte 68): a clear bit means the
/// sender is HOLDING that joint's last valid angle because its landmarks
/// are blocked (occlusion). Held joints get a red marker sphere so blocked
/// limbs are visible in captures.
///
/// Bone world rotations (person-basis joint matrices composed left to
/// right; quaternions are Unity-API intermediates only):
///   hip        = R_root · C_hip
///   R upperArm = R_root · Ry(θy)·Rz(θz)·Rx(θτ) · C
///   R forearm  = R_root · Ry(θy)·Rz(θz)·Rx(θτ) · Ry(ey)·Rz(ez) · C
///   L upperArm = R_root · Ry(−θy)·Rz(−θz)·Rx(θτ) · C      (§9 mirror:
///   L forearm  = ... · Ry(−ey)·Rz(−ez) · C     flip y/z signs, keep twist)
/// where each C is the bone's authored rest world rotation (calibration
/// anchored to the character's authored facing — see §3.4 pitfall).
public class ArmAngleReceiver : MonoBehaviour
{
    const uint Magic = 0x35415350; // 'PSA5'
    const int PacketSize = 72;

    // Live-mask bits (kinematics/occlusion.py): set = solved live,
    // clear = held at the last valid angle (blocked landmark).
    const int BitRoot = 1, BitRSwing = 2, BitRTwist = 4, BitRElbow = 8,
              BitLSwing = 16, BitLTwist = 32, BitLElbow = 64;
    const int MaskAll = 127;

    public string shmPath = "/dev/shm/pose_arm";
    public string hipBoneName = "DEF-spine";
    public string upperArmBoneName = "DEF-upper_arm.R";
    public string forearmBoneName = "DEF-forearm.R";
    public string leftUpperArmBoneName = "DEF-upper_arm.L";
    public string leftForearmBoneName = "DEF-forearm.L";

    [Header("Debug (read-only)")]
    public int lastFrame = -1;
    public Vector3 lastRootEuler;
    public Vector3 lastShoulder;  // R (θy, θz, θτ)
    public Vector2 lastElbow;     // R (ey, ez); ez ≡ 0 under the §6 twist convention
    public Vector3 lastLShoulder; // L, mirror convention
    public Vector2 lastLElbow;
    public int lastLiveMask = MaskAll;

    Transform hip, upperArm, forearm, lUpperArm, lForearm;
    Quaternion cHip, cUpperArm, cForearm, cLUpperArm, cLForearm;
    GameObject heldHip, heldRUpper, heldRFore, heldLUpper, heldLFore;
    MemoryMappedFile mmf;
    MemoryMappedViewAccessor view;

    static Transform FindBone(string name)
    {
        foreach (var t in FindObjectsByType<Transform>(FindObjectsSortMode.None))
            if (t.name == name) return t;
        return null;
    }

    // NOT parented to the bone: a primitive child of a skinned-mesh bone is
    // never rendered here (URP skips it) — verified empirically. The marker
    // lives at scene root and is re-positioned onto the bone every Update.
    static GameObject MakeHeldMarker(Transform bone)
    {
        var s = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        s.name = $"held_{bone.name}";
        Destroy(s.GetComponent<Collider>());
        s.GetComponent<Renderer>().material.color = new Color(0.9f, 0.1f, 0.1f);
        s.transform.localScale = Vector3.one * 0.14f;
        s.SetActive(false);
        return s;
    }

    void Start()
    {
        hip = FindBone(hipBoneName);
        upperArm = FindBone(upperArmBoneName);
        forearm = FindBone(forearmBoneName);
        lUpperArm = FindBone(leftUpperArmBoneName);
        lForearm = FindBone(leftForearmBoneName);
        if (hip == null || upperArm == null || forearm == null
            || lUpperArm == null || lForearm == null)
        {
            Debug.LogError("[ArmAngleReceiver] bones not found");
            enabled = false;
            return;
        }
        cHip = hip.rotation;
        cUpperArm = upperArm.rotation;
        cForearm = forearm.rotation;
        cLUpperArm = lUpperArm.rotation;
        cLForearm = lForearm.rotation;
        heldHip = MakeHeldMarker(hip);
        heldRUpper = MakeHeldMarker(upperArm);
        heldRFore = MakeHeldMarker(forearm);
        heldLUpper = MakeHeldMarker(lUpperArm);
        heldLFore = MakeHeldMarker(lForearm);
        try
        {
            mmf = MemoryMappedFile.CreateFromFile(shmPath, System.IO.FileMode.Open);
            view = mmf.CreateViewAccessor(0, PacketSize);
        }
        catch (System.Exception e)
        {
            Debug.LogWarning($"[ArmAngleReceiver] shm not available yet: {e.Message}");
        }
    }

    bool ReadStable(out int frame, out float[] v, out int mask)
    {
        frame = 0; v = new float[13]; mask = MaskAll;
        if (view == null)
        {
            try
            {
                mmf = MemoryMappedFile.CreateFromFile(shmPath, System.IO.FileMode.Open);
                view = mmf.CreateViewAccessor(0, PacketSize);
            }
            catch { return false; }
        }
        for (int attempt = 0; attempt < 3; attempt++)
        {
            uint seq0 = view.ReadUInt32(4);
            if ((seq0 & 1) != 0) continue;
            if (view.ReadUInt32(0) != Magic) return false;
            frame = view.ReadInt32(8);
            for (int i = 0; i < 13; i++) v[i] = view.ReadSingle(16 + 4 * i);
            mask = view.ReadUInt16(68);
            if (view.ReadUInt32(4) == seq0) return true;
        }
        return false;
    }

    void Update()
    {
        if (!ReadStable(out int frame, out float[] v, out int mask)) return;
        if (frame == lastFrame) return;
        lastFrame = frame;
        lastRootEuler = new Vector3(v[0], v[1], v[2]);
        lastShoulder = new Vector3(v[3], v[4], v[5]);
        lastElbow = new Vector2(v[6], v[7]);
        lastLShoulder = new Vector3(v[8], v[9], v[10]);
        lastLElbow = new Vector2(v[11], v[12]);
        lastLiveMask = mask;

        // Held-joint markers: the sender still supplies (held) angles, so
        // the bones keep posing below; the marker flags the frozen joints.
        // (R/L twist-only holds are normal at a straight elbow — no marker.)
        heldHip.SetActive((mask & BitRoot) == 0);
        heldRUpper.SetActive((mask & BitRSwing) == 0);
        heldRFore.SetActive((mask & BitRElbow) == 0);
        heldLUpper.SetActive((mask & BitLSwing) == 0);
        heldLFore.SetActive((mask & BitLElbow) == 0);
        // Nudged toward the camera so the sphere is not buried in the mesh.
        var camT = Camera.main != null ? Camera.main.transform : null;
        PlaceMarker(heldHip, hip, camT);
        PlaceMarker(heldRUpper, upperArm, camT);
        PlaceMarker(heldRFore, forearm, camT);
        PlaceMarker(heldLUpper, lUpperArm, camT);
        PlaceMarker(heldLFore, lForearm, camT);

        Quaternion qRoot = Quaternion.Euler(lastRootEuler);
        Quaternion qSh = Quaternion.AngleAxis(v[3], Vector3.up)
                       * Quaternion.AngleAxis(v[4], Vector3.forward)
                       * Quaternion.AngleAxis(v[5], Vector3.right);
        Quaternion qElb = Quaternion.AngleAxis(v[6], Vector3.up)
                        * Quaternion.AngleAxis(v[7], Vector3.forward);
        Quaternion qShL = Quaternion.AngleAxis(-v[8], Vector3.up)
                        * Quaternion.AngleAxis(-v[9], Vector3.forward)
                        * Quaternion.AngleAxis(v[10], Vector3.right);
        Quaternion qElbL = Quaternion.AngleAxis(-v[11], Vector3.up)
                         * Quaternion.AngleAxis(-v[12], Vector3.forward);

        // hip first: the arm bones are its children, then overwritten in
        // world space below.
        hip.rotation = qRoot * cHip;
        upperArm.rotation = qRoot * qSh * cUpperArm;
        forearm.rotation = qRoot * qSh * qElb * cForearm;
        lUpperArm.rotation = qRoot * qShL * cLUpperArm;
        lForearm.rotation = qRoot * qShL * qElbL * cLForearm;
    }

    // The push toward the camera is per rendering camera (HeldMarkers):
    // EvalFrameDump re-places the spheres for the sensor-view capture.
    static void PlaceMarker(GameObject marker, Transform bone, Transform cam)
        => HeldMarkers.Place(marker, bone, cam);

    void OnDestroy()
    {
        view?.Dispose();
        mmf?.Dispose();
    }
}
