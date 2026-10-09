// Receives per-frame landmark packets from the Python side and draws them as
// a marker/bone skeleton. Two transports:
//   SharedMemory (default, Linux): Python writes a fixed 180-byte record into
//     /dev/shm/pose_stream; reads are guarded by a seqlock (seq odd = writer
//     mid-update, re-read next frame on mismatch).
//   Udp: the same 180-byte packet sent to a local port (packets are atomic,
//     no seqlock needed).
//
// Packet layout (little-endian, 180 bytes total):
//   0  u32 magic 'PSE1' (0x31455350)
//   4  u32 seq        (shared memory only; even = stable)
//   8  i32 frame index
//   12 f32 time_s
//   16 i32 landmark count (8)
//   20 8 x { i32 mediapipe_id, f32 x, f32 y, f32 z, i32 valid }  (20 B each)
//
// Coordinates arrive in the RealSense camera frame (X right, Y down, Z forward,
// meters) and are mapped to Unity as (x, -y, z).

using System;
using System.IO;
using System.IO.MemoryMappedFiles;
using System.Net;
using System.Net.Sockets;
using UnityEngine;

public class PoseStreamReceiver : MonoBehaviour
{
    public enum Transport { SharedMemory, Udp }

    [Header("Transport")]
    public Transport transport = Transport.SharedMemory;
    public string shmPath = "/dev/shm/pose_stream";
    public int udpPort = 9750;

    [Header("Placement")]
    [Tooltip("Subtract the first frame's hip midpoint so the skeleton appears at this object's position.")]
    public bool autoCenter = true;
    public Vector3 displayOffset = new Vector3(1.2f, 0.95f, 0f);

    [Header("Appearance")]
    public float markerRadius = 0.04f;
    public Color leftColor = new Color(0.23f, 0.44f, 0.71f);
    public Color rightColor = new Color(0.76f, 0.35f, 0.12f);
    public Color torsoColor = new Color(0.45f, 0.45f, 0.45f);

    const uint Magic = 0x31455350; // 'PSE1'
    const int PacketSize = 180;
    const int MaxLandmarks = 8;
    static readonly int[] Ids = { 11, 12, 13, 14, 15, 16, 23, 24 };
    static readonly string[] Names = { "L_Shoulder", "R_Shoulder", "L_Elbow", "R_Elbow",
                                       "L_Wrist", "R_Wrist", "L_Hip", "R_Hip" };
    // Pairs of mediapipe ids; color: 0 torso, 1 left, 2 right.
    static readonly int[,] BonePairs = { { 11, 12, 0 }, { 23, 24, 0 }, { 11, 23, 0 }, { 12, 24, 0 },
                                         { 11, 13, 1 }, { 13, 15, 1 }, { 12, 14, 2 }, { 14, 16, 2 } };

    MemoryMappedFile mmf;
    MemoryMappedViewAccessor acc;
    UdpClient udp;
    byte[] packet = new byte[PacketSize];
    bool hasPacket;

    Transform[] markers = new Transform[MaxLandmarks];
    LineRenderer[] bones = new LineRenderer[BonePairs.GetLength(0)];
    readonly Vector3[] positions = new Vector3[MaxLandmarks];
    readonly bool[] valid = new bool[MaxLandmarks];
    Vector3 centerOffset;
    bool centered;
    int lastFrame = -1;
    float lastPacketTime;

    void Start()
    {
        BuildSkeletonObjects();
        if (transport == Transport.SharedMemory) OpenSharedMemory();
        else OpenUdp();
    }

    void BuildSkeletonObjects()
    {
        var mat = new Material(Shader.Find("Sprites/Default"));
        for (int i = 0; i < MaxLandmarks; i++)
        {
            var s = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            s.name = Names[i];
            s.transform.SetParent(transform, false);
            s.transform.localScale = Vector3.one * (markerRadius * 2f);
            Destroy(s.GetComponent<Collider>());
            var c = Names[i][0] == 'L' ? leftColor : Names[i][0] == 'R' ? rightColor : torsoColor;
            s.GetComponent<Renderer>().material.color = c;
            markers[i] = s.transform;
            s.SetActive(false);
        }
        for (int b = 0; b < bones.Length; b++)
        {
            var go = new GameObject($"Bone_{Ids[IndexOf(BonePairs[b, 0])]}_{BonePairs[b, 1]}");
            go.transform.SetParent(transform, false);
            var lr = go.AddComponent<LineRenderer>();
            lr.material = mat;
            lr.startWidth = lr.endWidth = 0.015f;
            lr.positionCount = 2;
            lr.useWorldSpace = true;
            var col = BonePairs[b, 2] == 1 ? leftColor : BonePairs[b, 2] == 2 ? rightColor : torsoColor;
            lr.startColor = lr.endColor = col;
            lr.enabled = false;
            bones[b] = lr;
        }
    }

    void OpenSharedMemory()
    {
        try
        {
            mmf = MemoryMappedFile.CreateFromFile(shmPath, FileMode.Open, null, 0,
                                                  MemoryMappedFileAccess.Read);
            acc = mmf.CreateViewAccessor(0, PacketSize, MemoryMappedFileAccess.Read);
            Debug.Log($"[PoseStream] Shared memory opened: {shmPath}");
        }
        catch (Exception e)
        {
            Debug.LogWarning($"[PoseStream] Could not open {shmPath} ({e.Message}). " +
                             "Start the Python sender first, or switch transport to Udp. Retrying...");
        }
    }

    void OpenUdp()
    {
        udp = new UdpClient(udpPort);
        udp.Client.Blocking = false;
        Debug.Log($"[PoseStream] Listening on UDP :{udpPort}");
    }

    void Update()
    {
        hasPacket = transport == Transport.SharedMemory ? ReadSharedMemory() : ReadUdp();
        if (!hasPacket) return;

        uint magic = BitConverter.ToUInt32(packet, 0);
        if (magic != Magic) return;
        int frame = BitConverter.ToInt32(packet, 8);
        if (frame == lastFrame) return;
        lastFrame = frame;
        lastPacketTime = Time.time;

        int count = Math.Min(BitConverter.ToInt32(packet, 16), MaxLandmarks);
        for (int i = 0; i < count; i++)
        {
            int off = 20 + i * 20;
            int id = BitConverter.ToInt32(packet, off);
            int slot = IndexOf(id);
            if (slot < 0) continue;
            float x = BitConverter.ToSingle(packet, off + 4);
            float y = BitConverter.ToSingle(packet, off + 8);
            float z = BitConverter.ToSingle(packet, off + 12);
            valid[slot] = BitConverter.ToInt32(packet, off + 16) != 0;
            positions[slot] = new Vector3(x, -y, z); // camera frame -> Unity
        }

        if (autoCenter && !centered && valid[6] && valid[7])
        {
            centerOffset = (positions[6] + positions[7]) * 0.5f;
            centered = true;
        }

        for (int i = 0; i < MaxLandmarks; i++)
        {
            markers[i].gameObject.SetActive(valid[i]);
            if (valid[i])
                markers[i].position = transform.position + displayOffset + positions[i] - centerOffset;
        }
        for (int b = 0; b < bones.Length; b++)
        {
            int a = IndexOf(BonePairs[b, 0]), c = IndexOf(BonePairs[b, 1]);
            bool ok = valid[a] && valid[c];
            bones[b].enabled = ok;
            if (ok)
            {
                bones[b].SetPosition(0, markers[a].position);
                bones[b].SetPosition(1, markers[c].position);
            }
        }
    }

    bool ReadSharedMemory()
    {
        if (acc == null)
        {
            // Sender may not have created the file yet; retry once a second.
            if (Time.frameCount % 60 == 0) OpenSharedMemory();
            if (acc == null) return false;
        }
        for (int attempt = 0; attempt < 3; attempt++)
        {
            uint seqBefore = acc.ReadUInt32(4);
            if ((seqBefore & 1) != 0) continue; // writer mid-update
            acc.ReadArray(0, packet, 0, PacketSize);
            uint seqAfter = BitConverter.ToUInt32(packet, 4);
            uint seqNow = acc.ReadUInt32(4);
            if (seqAfter == seqBefore && seqNow == seqBefore) return true;
        }
        return false;
    }

    bool ReadUdp()
    {
        bool got = false;
        try
        {
            IPEndPoint ep = null;
            while (udp.Available > 0)
            {
                var data = udp.Receive(ref ep); // drain; keep newest
                if (data.Length == PacketSize) { Buffer.BlockCopy(data, 0, packet, 0, PacketSize); got = true; }
            }
        }
        catch (SocketException) { }
        return got;
    }

    static int IndexOf(int mediapipeId)
    {
        for (int i = 0; i < Ids.Length; i++) if (Ids[i] == mediapipeId) return i;
        return -1;
    }

    void OnDestroy()
    {
        acc?.Dispose();
        mmf?.Dispose();
        udp?.Close();
    }
}
