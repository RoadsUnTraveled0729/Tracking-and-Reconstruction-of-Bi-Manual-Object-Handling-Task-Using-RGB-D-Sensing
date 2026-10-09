using System.IO;
using System.IO.MemoryMappedFiles;
using UnityEngine;

/// v2 integration receiver: the Pipeline B scene (base class) plus the
/// Pipeline A person, driven from the v2 merger's delay-buffer output.
/// The v1 receiver (IntegratedSceneReceiver) is left untouched and stays
/// dormant: it bootstraps only when /dev/shm/integrated_scene exists,
/// which the v2 stack never creates.
///
/// Shared memory (v2/integration/v2_integrate.py):
///   /dev/shm/aruco_scene           PSB3, static scene, once (base class)
///   /dev/shm/integrated_scene_v2   PSI2, 112 B seqlock, per output tick:
///     u32 magic 'PSI2' | u32 seq | i32 tick | f32 tau
///     f32 pelvis xyz | f32 x13 angles (PSA5 order)
///     f32 object pos xyz + Euler xyz
///     u16 person live mask (104) | u16 object live (106)
///     u16 flags (108): bit0 person interp, bit1 object interp,
///                      bit2 person blend,  bit3 object blend,
///                      bit4 person bridge, bit5 object bridge
///     u16 tags (110): bits 2i..2i+1 = solver tag of live-mask group i
///                     (0 measured, 1 held, 2 constrained); 0 when the
///                     person pipeline writes the tagless PSR1 packet
///   (layout duplicated by hand from v2_integrate.py -- change both or
///    neither)
///
/// Visual vocabulary: red keeps its exact v1 meaning (held / not
/// measured: red joint spheres from the live mask, red cube when the
/// object live flag is 0). A red sphere turns BLUE when its group's
/// tag is CONSTRAINED -- the pose there is reconstructed geometry (in
/// this probe: the wrist recovered from the tracked object's pose plus
/// the grip offset, E-014), not a hold. Amber marks the v2 additions --
/// a pose that crossed a real dropout by interpolation (bridge) or is
/// ramping back after a long occlusion (blend): amber tint on the
/// object cube and plate, and an amber pelvis sphere for the person.
/// Routine resampling between adjacent measured frames (bit0/bit1
/// alone) is not marked; the honest record of it is the flags field
/// itself.
///
/// The person-driving mathematics is duplicated verbatim from
/// IntegratedSceneReceiver (its members are private; editing v1 is
/// forbidden by the freeze) -- see that file for the anchor/rest-pose
/// derivation and its failure-mode notes.
public class IntegratedSceneReceiverV2 : ArucoSceneReceiver
{
    const uint MagicIntegrated = 0x32495350; // 'PSI2'
    const int IntegratedPacketSize = 112;

    const int BitRoot = 1, BitRSwing = 2, BitRElbow = 8,
              BitLSwing = 16, BitLElbow = 64;
    const int FlagPersonBlend = 4, FlagObjectBlend = 8,
              FlagPersonBridge = 16, FlagObjectBridge = 32;

    static readonly Color AmberCol = new Color(0.9f, 0.65f, 0.1f);
    static readonly Color CubeColV2 = new Color(0.90f, 0.55f, 0.15f);
    static readonly Color PlateColV2 = new Color(0.95f, 0.95f, 0.95f);
    static readonly Color HeldCol = new Color(0.9f, 0.1f, 0.1f);
    static readonly Color RecoveredCol = new Color(0.15f, 0.5f, 0.95f);

    public string integratedShmPath = "/dev/shm/integrated_scene_v2";
    public string personLogPath = "/home/luo/Desktop/New_SandBox/v2/output/unity_person_log_v2.csv";
    public float personHeightM = 1.70f;

    [Header("Person debug (read-only)")]
    public Vector3 lastPelvis;
    public Vector3 lastRootEuler;
    public int lastMask = 127;
    public int lastFlags = 0;

    Transform anchor;
    Transform rigRoot, hip, upperArm, forearm, lUpperArm, lForearm;
    Transform rHand, lHand;
    float rigRestHeightRaw, appliedScale = 1f;
    Quaternion cHip, cUpperArm, cForearm, cLUpperArm, cLForearm;
    GameObject heldHip, heldRUpper, heldRFore, heldLUpper, heldLFore;
    GameObject amberPelvis;
    Renderer cubeRend, plateRend;
    MemoryMappedFile imf;
    MemoryMappedViewAccessor iview;
    float lastFreshTime;
    StreamWriter personLog;

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    static void BootstrapIntegratedV2()
    {
        if (!File.Exists("/dev/shm/integrated_scene_v2")
            || !File.Exists("/dev/shm/aruco_scene")) return;
        if (FindFirstObjectByType<IntegratedSceneReceiverV2>() != null) return;
        new GameObject("IntegratedSceneReceiverV2").AddComponent<IntegratedSceneReceiverV2>();
    }

    void Awake()
    {
        logPath = "/home/luo/Desktop/New_SandBox/v2/output/unity_object_log_v2.csv";
    }

    protected override Vector3 WorldOffset() { return Vector3.zero; }

    static Transform FindBone(string name)
    {
        foreach (var t in FindObjectsByType<Transform>(FindObjectsSortMode.None))
            if (t.name == name) return t;
        return null;
    }

    static GameObject Marker(string name, Color col, float scale)
    {
        var s = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        s.name = name;
        Destroy(s.GetComponent<Collider>());
        s.GetComponent<Renderer>().material.color = col;
        s.transform.localScale = Vector3.one * scale;
        s.SetActive(false);
        return s;
    }

    protected override void Start()
    {
        base.Start();   // PSB3 scene: wall/desk marker/sensor/object cube
        if (!enabled) return;

        // No other receiver may drive the same bones or cube.
        foreach (var b in FindObjectsByType<MonoBehaviour>(FindObjectsSortMode.None))
            if (b != this && (b is ArmAngleReceiver
                              || b is IntegratedSceneReceiver
                              || b.GetType().Name == "PoseStreamReceiver"
                              || b.GetType().Name == "RootAngleReceiver"))
                b.enabled = false;

        anchor = new GameObject("PersonAnchor").transform;
        anchor.SetParent(world, false);
        anchor.localPosition = posesPos[2];                       // camera pose
        anchor.localRotation = Quaternion.Euler(posesEuler[2])
                             * Quaternion.Euler(-90f, 0f, 0f);    // * Rx(-90)

        hip = FindBone("DEF-spine");
        upperArm = FindBone("DEF-upper_arm.R");
        forearm = FindBone("DEF-forearm.R");
        lUpperArm = FindBone("DEF-upper_arm.L");
        lForearm = FindBone("DEF-forearm.L");
        rHand = FindBone("DEF-hand.R");
        lHand = FindBone("DEF-hand.L");
        if (hip == null || upperArm == null || forearm == null
            || lUpperArm == null || lForearm == null
            || rHand == null || lHand == null)
        {
            Debug.LogError("[IntegratedSceneReceiverV2] rig bones not found");
            enabled = false;
            return;
        }
        rigRoot = hip.root;

        var headEnd = FindBone("DEF-head_end");
        rigRestHeightRaw = headEnd != null ? headEnd.position.y : 0f;
        if (rigRestHeightRaw < 0.1f)
        {
            var smr = rigRoot.GetComponentInChildren<SkinnedMeshRenderer>();
            if (smr != null) rigRestHeightRaw = smr.bounds.size.y;
        }
        if (rigRestHeightRaw > 0.1f)
        {
            appliedScale = personHeightM / rigRestHeightRaw;
            rigRoot.localScale *= appliedScale;
        }

        cHip = hip.rotation;
        cUpperArm = upperArm.rotation;
        cForearm = forearm.rotation;
        cLUpperArm = lUpperArm.rotation;
        cLForearm = lForearm.rotation;
        heldHip = Marker("held_hip", new Color(0.9f, 0.1f, 0.1f), 0.12f);
        heldRUpper = Marker("held_upper_arm.R", new Color(0.9f, 0.1f, 0.1f), 0.12f);
        heldRFore = Marker("held_forearm.R", new Color(0.9f, 0.1f, 0.1f), 0.12f);
        heldLUpper = Marker("held_upper_arm.L", new Color(0.9f, 0.1f, 0.1f), 0.12f);
        heldLFore = Marker("held_forearm.L", new Color(0.9f, 0.1f, 0.1f), 0.12f);
        amberPelvis = Marker("interp_pelvis", AmberCol, 0.10f);

        Directory.CreateDirectory(Path.GetDirectoryName(personLogPath));
        personLog = new StreamWriter(personLogPath, false);
        personLog.WriteLine("tick,tau,mask,flags,tags,pel_x,pel_y,pel_z,"
                            + "hip_x,hip_y,hip_z,rh_x,rh_y,rh_z,lh_x,lh_y,lh_z");
        personLog.Flush();
        Debug.Log($"[IntegratedSceneReceiverV2] person anchored at {anchor.position} "
                  + $"euler {anchor.rotation.eulerAngles}");
    }

    bool ReadIntegrated(out int tick, out float tau, out Vector3 pelvis,
                        out float[] v, out Vector3 objPos, out Vector3 objEuler,
                        out int mask, out int objLive, out int flags,
                        out int tags)
    {
        tick = 0; tau = 0; pelvis = objPos = objEuler = Vector3.zero;
        v = new float[13]; mask = 127; objLive = 1; flags = 0; tags = 0;
        if (iview == null)
        {
            try
            {
                imf = MemoryMappedFile.CreateFromFile(integratedShmPath, FileMode.Open);
                iview = imf.CreateViewAccessor(0, IntegratedPacketSize);
            }
            catch { return false; }
        }
        for (int attempt = 0; attempt < 3; attempt++)
        {
            uint seq0 = iview.ReadUInt32(4);
            if ((seq0 & 1) != 0) continue;
            if (iview.ReadUInt32(0) != MagicIntegrated)
            {
                // The merger recreates the region at launch; a mapping
                // made before that sees stale/zero pages forever. Drop
                // it and re-map on the next frame.
                iview.Dispose(); imf.Dispose();
                iview = null; imf = null;
                return false;
            }
            tick = iview.ReadInt32(8);
            tau = iview.ReadSingle(12);
            pelvis = new Vector3(iview.ReadSingle(16), iview.ReadSingle(20), iview.ReadSingle(24));
            for (int i = 0; i < 13; i++) v[i] = iview.ReadSingle(28 + 4 * i);
            objPos = new Vector3(iview.ReadSingle(80), iview.ReadSingle(84), iview.ReadSingle(88));
            objEuler = new Vector3(iview.ReadSingle(92), iview.ReadSingle(96), iview.ReadSingle(100));
            mask = iview.ReadUInt16(104);
            objLive = iview.ReadUInt16(106);
            flags = iview.ReadUInt16(108);
            tags = iview.ReadUInt16(110);
            if (iview.ReadUInt32(4) == seq0) return true;
        }
        return false;
    }

    static void SetHeldColor(GameObject marker, int tags, int group)
    {
        int tag = (tags >> (2 * group)) & 3;
        marker.GetComponent<Renderer>().material.color =
            tag == 2 ? RecoveredCol : HeldCol;
    }

    void ApplyPerson(float tau, int tick, Vector3 pelvis, float[] v,
                     int mask, int flags, int tags)
    {
        lastPelvis = pelvis;
        lastRootEuler = new Vector3(v[0], v[1], v[2]);
        lastMask = mask;
        lastFlags = flags;

        Quaternion qA = anchor.rotation;
        Quaternion qRoot = Quaternion.Euler(v[0], v[1], v[2]);
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

        hip.rotation = qA * qRoot * cHip;
        upperArm.rotation = qA * qRoot * qSh * cUpperArm;
        forearm.rotation = qA * qRoot * qSh * qElb * cForearm;
        lUpperArm.rotation = qA * qRoot * qShL * cLUpperArm;
        lForearm.rotation = qA * qRoot * qShL * qElbL * cLForearm;

        Vector3 target = anchor.TransformPoint(pelvis);
        rigRoot.position += target - hip.position;

        // tag groups: 0 root, 1 R swing, 3 R elbow, 4 L swing, 6 L elbow
        SetHeldColor(heldHip, tags, 0);
        SetHeldColor(heldRUpper, tags, 1);
        SetHeldColor(heldRFore, tags, 3);
        SetHeldColor(heldLUpper, tags, 4);
        SetHeldColor(heldLFore, tags, 6);
        heldHip.SetActive((mask & BitRoot) == 0);
        heldRUpper.SetActive((mask & BitRSwing) == 0);
        heldRFore.SetActive((mask & BitRElbow) == 0);
        heldLUpper.SetActive((mask & BitLSwing) == 0);
        heldLFore.SetActive((mask & BitLElbow) == 0);
        var camT = Camera.main != null ? Camera.main.transform : null;
        PlaceHeld(heldHip, hip, camT);
        PlaceHeld(heldRUpper, upperArm, camT);
        PlaceHeld(heldRFore, forearm, camT);
        PlaceHeld(heldLUpper, lUpperArm, camT);
        PlaceHeld(heldLFore, lForearm, camT);

        // amber pelvis sphere: the person pose is a bridge or blend
        bool personAmber = (flags & (FlagPersonBlend | FlagPersonBridge)) != 0;
        amberPelvis.SetActive(personAmber);
        if (personAmber) PlaceHeld(amberPelvis, hip, camT);

        if (personLog != null)
        {
            Vector3 h = hip.position;
            Vector3 rh = rHand.position, lh = lHand.position;
            personLog.WriteLine($"{tick},{tau:F6},{mask},{flags},{tags},"
                                + $"{pelvis.x:F6},{pelvis.y:F6},{pelvis.z:F6},"
                                + $"{h.x:F6},{h.y:F6},{h.z:F6},"
                                + $"{rh.x:F6},{rh.y:F6},{rh.z:F6},{lh.x:F6},{lh.y:F6},{lh.z:F6}");
            personLog.Flush();
        }
    }

    // The push toward the camera is per rendering camera (HeldMarkers):
    // EvalFrameDump re-places the spheres for the sensor-view capture.
    static void PlaceHeld(GameObject marker, Transform bone, Transform cam)
        => HeldMarkers.Place(marker, bone, cam);

    void TintObject(int objLive, int flags)
    {
        // The base ApplyObject already painted normal (live) or red
        // (held); amber overrides for bridge/blend, applied after it.
        if (cubeRend == null)
        {
            var cube = GameObject.Find("object_cube");
            if (cube != null) cubeRend = cube.GetComponent<Renderer>();
            var plate = GameObject.Find("plate_object id1");
            if (plate != null) plateRend = plate.GetComponent<Renderer>();
        }
        if (cubeRend == null) return;
        bool amber = objLive == 1
                     && (flags & (FlagObjectBlend | FlagObjectBridge)) != 0;
        if (amber)
        {
            cubeRend.material.color = AmberCol;
            if (plateRend != null) plateRend.material.color = AmberCol;
        }
        else if (objLive == 1)
        {
            cubeRend.material.color = CubeColV2;
            if (plateRend != null) plateRend.material.color = PlateColV2;
        }
    }

    protected override void FrameCamera(Vector3 deskCenterLocal)
    {
        var cam = Camera.main;
        if (cam == null) return;
        Vector3 center = world.TransformPoint(deskCenterLocal) + Vector3.up * 0.5f;
        Vector3 wall = world.TransformPoint(posesPos[1]);
        Vector3 away = center - wall;
        away.y = 0f;
        away = away.sqrMagnitude > 1e-6f ? away.normalized : Vector3.back;
        Vector3 side = Vector3.Cross(Vector3.up, away);
        cam.transform.position = center + away * 2.6f + side * 2.4f + Vector3.up * 1.1f;
        cam.transform.LookAt(center + Vector3.up * 0.15f);
    }

    protected override void Update()
    {
        if (!ReadIntegrated(out int tick, out float tau, out Vector3 pelvis,
                            out float[] v, out Vector3 objPos, out Vector3 objEuler,
                            out int mask, out int objLive, out int flags,
                            out int tags)) return;
        if (tick == lastFrame)
        {
            // No fresh tick for a while: the mapping may be a stale
            // pre-recreation view that still carries an old packet.
            // Re-map; harmless when the stream is simply idle.
            if (Time.realtimeSinceStartup - lastFreshTime > 5f && iview != null)
            {
                iview.Dispose(); imf.Dispose();
                iview = null; imf = null;
                lastFreshTime = Time.realtimeSinceStartup;
            }
            return;
        }
        lastFreshTime = Time.realtimeSinceStartup;
        ApplyObject(tick, tau, objPos, objEuler, objLive);
        TintObject(objLive, flags);
        ApplyPerson(tau, tick, pelvis, v, mask, flags, tags);
    }

    protected override void OnDestroy()
    {
        personLog?.Dispose();
        iview?.Dispose();
        imf?.Dispose();
        base.OnDestroy();
    }
}
