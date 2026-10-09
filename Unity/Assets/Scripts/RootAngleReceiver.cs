// Receives root-frame Euler angles (Unity ZXY order, degrees) from the Python
// side via shared memory and applies them to the rig's hip/pelvis bone.
//
// Packet layout (little-endian, 32 bytes, /dev/shm/pose_angles):
//   0  u32 magic 'PSA1' (0x31415350)
//   4  u32 seq   (seqlock: odd = writer mid-update, even = stable)
//   8  i32 frame index
//   12 f32 time_s
//   16 f32 euler_x  20 f32 euler_y  24 f32 euler_z
//   28 padding
//
// The streamed angles follow KINEMATIC_MODEL.md: a person standing upright
// facing the sensor is (0, 180, 0). The bone's rest world rotation q0 is
// generally NOT identity (Blender rig), so a constant calibration is
// composed at Start: rotation = Euler(e) * inverse(Euler(reference)) * q0,
// where reference is the CHARACTER's authored rest facing in Euler terms
// ((0,0,0) for a rig authored facing world +Z). The calibration then only
// absorbs the bone's local axis convention, and the streamed absolute yaw
// is honored — a person facing the sensor (y=180) turns the rig to face
// the scene camera. (Anchoring reference to the person's pose instead
// would discard absolute yaw and leave the rig at its authored facing.)

using System;
using System.IO;
using System.IO.MemoryMappedFiles;
using UnityEngine;

public class RootAngleReceiver : MonoBehaviour
{
    [Header("Transport")]
    public string shmPath = "/dev/shm/pose_angles";

    [Header("Target")]
    [Tooltip("Bone to drive. If empty, found by name below.")]
    public Transform targetBone;
    public string boneName = "DEF-spine";
    [Tooltip("The character's authored rest facing: (0,0,0) for a rig authored facing world +Z.")]
    public Vector3 referenceEuler = Vector3.zero;

    [Header("Debug (read-only)")]
    public int lastFrame = -1;
    public Vector3 lastEuler;

    const uint Magic = 0x31415350; // 'PSA1'
    const int PacketSize = 32;

    MemoryMappedFile mmf;
    MemoryMappedViewAccessor acc;
    byte[] packet = new byte[PacketSize];
    Quaternion calibration;

    void Start()
    {
        if (targetBone == null) targetBone = FindBone(boneName);
        if (targetBone == null)
        {
            Debug.LogError($"[RootAngle] Bone '{boneName}' not found; disabling.");
            enabled = false;
            return;
        }
        calibration = Quaternion.Inverse(Quaternion.Euler(referenceEuler)) * targetBone.rotation;
        Debug.Log($"[RootAngle] Driving '{targetBone.name}' (rest world rotation "
                  + $"{targetBone.rotation.eulerAngles}).");
        OpenSharedMemory();
    }

    static Transform FindBone(string name)
    {
        foreach (var t in FindObjectsByType<Transform>(FindObjectsSortMode.None))
            if (t.name == name) return t;
        return null;
    }

    void OpenSharedMemory()
    {
        try
        {
            mmf = MemoryMappedFile.CreateFromFile(shmPath, FileMode.Open, null, 0,
                                                  MemoryMappedFileAccess.Read);
            acc = mmf.CreateViewAccessor(0, PacketSize, MemoryMappedFileAccess.Read);
            Debug.Log($"[RootAngle] Shared memory opened: {shmPath}");
        }
        catch (Exception e)
        {
            Debug.LogWarning($"[RootAngle] Could not open {shmPath} ({e.Message}). "
                             + "Start the Python sender first. Retrying...");
        }
    }

    void Update()
    {
        if (acc == null)
        {
            if (Time.frameCount % 60 == 0) OpenSharedMemory();
            if (acc == null) return;
        }
        if (!ReadStable()) return;

        if (BitConverter.ToUInt32(packet, 0) != Magic) return;
        int frame = BitConverter.ToInt32(packet, 8);
        if (frame == lastFrame) return;
        lastFrame = frame;
        lastEuler = new Vector3(BitConverter.ToSingle(packet, 16),
                                BitConverter.ToSingle(packet, 20),
                                BitConverter.ToSingle(packet, 24));
        targetBone.rotation = Quaternion.Euler(lastEuler) * calibration;
    }

    bool ReadStable()
    {
        for (int attempt = 0; attempt < 3; attempt++)
        {
            uint seqBefore = acc.ReadUInt32(4);
            if ((seqBefore & 1) != 0) continue;
            acc.ReadArray(0, packet, 0, PacketSize);
            uint seqAfter = BitConverter.ToUInt32(packet, 4);
            if (seqAfter == seqBefore && acc.ReadUInt32(4) == seqBefore) return true;
        }
        return false;
    }

    void OnDestroy()
    {
        acc?.Dispose();
        mmf?.Dispose();
    }
}
