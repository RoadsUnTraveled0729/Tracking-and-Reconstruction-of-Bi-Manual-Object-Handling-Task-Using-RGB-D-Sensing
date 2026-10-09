// V3 person receiver: draws the V3 pipeline's skeleton with per-group
// honesty coloring. V3-ONLY code (V3_DECISIONS.md D-007): lives in
// Scripts/V3/, reads only V3 shared memory (/dev/shm/v3_person), and
// never touches the v1/v2 receivers or their shm names. Used by
// Scenes/V3Scene.unity; in the v1/v2 scenes it stays dormant because
// the v3 stack's shm file does not exist there.
//
// PSV3 packet (little-endian, 172 bytes, seqlock; canonical spec and
// writer: v3/replay/psv3.py -- change both files or neither):
//   0   u32 magic 'PSV3' (0x33565350)
//   4   u32 seq        (even = stable, odd = writer mid-update)
//   8   i32 frame index
//   12  f32 time_s     (session clock)
//   16  8 x f32[3] landmark xyz, Unity frame, meters, order:
//         L_Shoulder R_Shoulder L_Elbow R_Elbow L_Wrist R_Wrist
//         L_Hip R_Hip
//   112 13 x f32 angles deg (v1 PSA order: root xyz | R sh y,z,tau |
//         R elb ey,ez | L sh y,z,tau | L elb ey,ez)
//   164 7 x u8 per-group status, v1 live-mask bit order (root,
//         R_swing, R_twist, R_elbow, L_swing, L_twist, L_elbow):
//         0 = MEASURED, 1 = ESTIMATED, 2 = LOST
//   171 u8 pad
//
// Color vocabulary (consistent with the v2 scene): normal side colors
// = MEASURED; AMBER = ESTIMATED (the strategy is reconstructing this
// group honestly); RED = LOST (no trustworthy estimate). Sphere <->
// group mapping: shoulders show the swing groups, elbows the twist
// groups, wrists the elbow groups, hips the root.

using System;
using System.IO;
using System.IO.MemoryMappedFiles;
using UnityEngine;

public class V3PersonReceiver : MonoBehaviour
{
    [Header("Transport")]
    public string shmPath = "/dev/shm/v3_person";

    [Header("Placement")]
    public bool autoCenter = true;
    public Vector3 displayOffset = new Vector3(0f, 1.0f, 0f);

    [Header("Appearance")]
    public float markerRadius = 0.04f;
    public Color leftColor = new Color(0.23f, 0.44f, 0.71f);
    public Color rightColor = new Color(0.76f, 0.35f, 0.12f);
    public Color torsoColor = new Color(0.45f, 0.45f, 0.45f);
    public Color estimatedColor = new Color(0.9f, 0.65f, 0.1f);   // amber
    public Color lostColor = new Color(0.85f, 0.1f, 0.1f);        // red

    const uint Magic = 0x33565350; // 'PSV3'
    const int PacketSize = 172;
    const int NLandmarks = 8;
    const int NAngles = 13;
    const int NGroups = 7;

    static readonly string[] Names = { "L_Shoulder", "R_Shoulder", "L_Elbow",
                                       "R_Elbow", "L_Wrist", "R_Wrist",
                                       "L_Hip", "R_Hip" };
    // landmark slot -> status group index (v1 bit order)
    static readonly int[] SphereGroup = { 4, 1, 5, 2, 6, 3, 0, 0 };
    // bones: a, b, side (0 torso 1 left 2 right), status group
    static readonly int[,] Bones = {
        { 0, 1, 0, 0 }, { 6, 7, 0, 0 }, { 0, 6, 0, 0 }, { 1, 7, 0, 0 },
        { 0, 2, 1, 4 }, { 2, 4, 1, 6 },
        { 1, 3, 2, 1 }, { 3, 5, 2, 3 },
    };

    MemoryMappedFile mmf;
    MemoryMappedViewAccessor acc;
    readonly byte[] packet = new byte[PacketSize];

    Transform[] markers = new Transform[NLandmarks];
    Renderer[] markerRenderers = new Renderer[NLandmarks];
    LineRenderer[] boneLines = new LineRenderer[8];
    readonly Vector3[] positions = new Vector3[NLandmarks];
    readonly float[] angles = new float[NAngles];
    readonly int[] status = new int[NGroups];

    Vector3 centerOffset;
    bool centered;
    int lastFrame = -1;

    [Header("Debug (read-only)")]
    public int lastFrameSeen = -1;
    public float lastTimeS;

    void Start()
    {
        BuildSkeleton();
        Open();
    }

    void BuildSkeleton()
    {
        var mat = new Material(Shader.Find("Sprites/Default"));
        for (int i = 0; i < NLandmarks; i++)
        {
            var s = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            s.name = "v3_" + Names[i];
            s.transform.SetParent(transform, false);
            s.transform.localScale = Vector3.one * (markerRadius * 2f);
            Destroy(s.GetComponent<Collider>());
            markerRenderers[i] = s.GetComponent<Renderer>();
            markerRenderers[i].material.color = SideColor(i);
            markers[i] = s.transform;
            s.SetActive(false);
        }
        for (int b = 0; b < Bones.GetLength(0); b++)
        {
            var go = new GameObject($"v3_bone_{Names[Bones[b, 0]]}_{Names[Bones[b, 1]]}");
            go.transform.SetParent(transform, false);
            var lr = go.AddComponent<LineRenderer>();
            lr.material = mat;
            lr.startWidth = lr.endWidth = 0.015f;
            lr.positionCount = 2;
            lr.useWorldSpace = true;
            lr.enabled = false;
            boneLines[b] = lr;
        }
    }

    Color SideColor(int slot)
    {
        char c = Names[slot][0];
        return c == 'L' ? leftColor : c == 'R' ? rightColor : torsoColor;
    }

    Color StatusColor(int group, Color measured)
    {
        int s = status[group];
        return s == 2 ? lostColor : s == 1 ? estimatedColor : measured;
    }

    void Open()
    {
        try
        {
            mmf = MemoryMappedFile.CreateFromFile(shmPath, FileMode.Open, null, 0,
                                                  MemoryMappedFileAccess.Read);
            acc = mmf.CreateViewAccessor(0, PacketSize, MemoryMappedFileAccess.Read);
            Debug.Log($"[V3Person] shared memory opened: {shmPath}");
        }
        catch (Exception)
        {
            // V3 stack not running yet; keep retrying quietly in Update.
        }
    }

    void Update()
    {
        if (acc == null)
        {
            if (Time.frameCount % 60 == 0 && File.Exists(shmPath)) Open();
            if (acc == null) return;
        }
        if (!ReadStable()) return;
        if (BitConverter.ToUInt32(packet, 0) != Magic) return;
        int frame = BitConverter.ToInt32(packet, 8);
        if (frame == lastFrame) return;
        lastFrame = frame;
        lastFrameSeen = frame;
        lastTimeS = BitConverter.ToSingle(packet, 12);

        for (int i = 0; i < NLandmarks; i++)
        {
            int off = 16 + i * 12;
            positions[i] = new Vector3(BitConverter.ToSingle(packet, off),
                                       BitConverter.ToSingle(packet, off + 4),
                                       BitConverter.ToSingle(packet, off + 8));
        }
        for (int i = 0; i < NAngles; i++)
            angles[i] = BitConverter.ToSingle(packet, 112 + i * 4);
        for (int g = 0; g < NGroups; g++)
            status[g] = packet[164 + g];

        if (autoCenter && !centered)
        {
            centerOffset = (positions[6] + positions[7]) * 0.5f;
            centered = true;
        }

        for (int i = 0; i < NLandmarks; i++)
        {
            markers[i].gameObject.SetActive(true);
            markers[i].position = transform.position + displayOffset
                                  + positions[i] - centerOffset;
            markerRenderers[i].material.color =
                StatusColor(SphereGroup[i], SideColor(i));
        }
        for (int b = 0; b < Bones.GetLength(0); b++)
        {
            var lr = boneLines[b];
            lr.enabled = true;
            lr.SetPosition(0, markers[Bones[b, 0]].position);
            lr.SetPosition(1, markers[Bones[b, 1]].position);
            int side = Bones[b, 2];
            Color baseC = side == 1 ? leftColor
                        : side == 2 ? rightColor : torsoColor;
            Color c = StatusColor(Bones[b, 3], baseC);
            lr.startColor = lr.endColor = c;
        }
    }

    bool ReadStable()
    {
        for (int attempt = 0; attempt < 3; attempt++)
        {
            uint seqBefore = acc.ReadUInt32(4);
            if ((seqBefore & 1) != 0) continue;
            acc.ReadArray(0, packet, 0, PacketSize);
            uint seqAfter = BitConverter.ToUInt32(packet, 4);
            uint seqNow = acc.ReadUInt32(4);
            if (seqAfter == seqBefore && seqNow == seqBefore) return true;
        }
        return false;
    }

    void OnDestroy()
    {
        acc?.Dispose();
        mmf?.Dispose();
    }
}
