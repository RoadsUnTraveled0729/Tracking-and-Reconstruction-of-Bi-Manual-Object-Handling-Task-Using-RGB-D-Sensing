using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.IO.MemoryMappedFiles;
using UnityEngine;

/// Evaluation-stage integration (INTEGRATION.md): the Pipeline B real scene
/// (wall/desk/object cube/sensor, inherited from ArucoSceneReceiver) PLUS
/// the Pipeline A person, driven in the SAME desk-anchored world.
///
/// Shared memory (integration/send_integrated_scene.py):
///   /dev/shm/aruco_scene       PSB3, static scene, written once (base class)
///   /dev/shm/integrated_scene  PSI1, 108 B seqlock, per frame:
///     u32 magic 'PSI1' | u32 seq | i32 frame | f32 time_s
///     f32 pelvis xyz (Pipeline-A Unity space = camera frame, y flipped)
///     f32 x13 angles: root Euler xyz, R shoulder y/z/twist, R elbow y/z,
///                     L shoulder y/z/twist, L elbow y/z   (PSA5 order)
///     f32 object pos xyz + Euler xyz (desk world mapped to Unity, PSB2 pose)
///     u16 person live mask (PSA5 bits) | u16 object live
///
/// Person placement: Pipeline A solves in "Unity-from-sensor" space (camera
/// frame with y flipped); Pipeline B's world is the desk frame mapped by the
/// y/z swap P. The static map between them is a proper rotation
///   M = P * R_desk_cam * diag(1,-1,1) = R_unity(camera) * Rx(-90 deg),
/// so a "PersonAnchor" node at the calibrated camera pose composed with
/// Rx(-90) turns person-space coordinates into scene coordinates directly
/// (verified numerically against the independent depth-gravity seed).
/// Bones are driven like ArmAngleReceiver with the anchor PRE-multiplied:
///   bone.rotation = qA * qChain * C_rest
/// where C_rest is the authored rest captured at spawn (the rig spawns
/// unrotated, so its body axes coincide with scene axes; qA then carries
/// the whole person-space pose into the scene). NOT the conjugation
/// qA*qChain*qA^-1*C_rest — that cancels the camera orientation out of
/// the pose and faced the rig the wrong way; caught by
/// integration/plot_integrated_scene.py, where the DATA showed the person
/// facing the sensor to 4.5 deg while the rendered rig did not. The rig
/// root is translated so the hip bone lands on the streamed pelvis point.
/// Held joints (blocked landmarks) keep the red-marker convention.
public class IntegratedSceneReceiver : ArucoSceneReceiver
{
    const uint MagicIntegrated = 0x31495350; // 'PSI1'
    const int IntegratedPacketSize = 108;

    const int BitRoot = 1, BitRSwing = 2, BitRElbow = 8,
              BitLSwing = 16, BitLElbow = 64;

    public string integratedShmPath = "/dev/shm/integrated_scene";
    public string personLogPath = "/home/luo/Desktop/New_SandBox/v1/integration/output/unity_person_log.csv";
    // The FBX rig is authored ~2.2x human size (OBJECT_OFFSET.md §6); it is
    // display-scaled at spawn so it stands this tall next to the metric
    // desk/object. Uniform scale leaves world bone ROTATIONS (and thus the
    // whole angle transfer) untouched; the per-frame root translation still
    // pins the hip to the mapped pelvis point.
    public float personHeightM = 1.70f;
    // Subject segment lengths (m) of the recording being replayed. They
    // are not authored here: Awake() reads them from the sizing file the
    // capture launchers write (SizingOverridePath below, E-036), so no
    // recording's constants live in this class and every replay is sized
    // from its own record. The arm values are the offset-fit medians of
    // the recording (eval/reports/<alias>_rig_sizing.json, built from
    // the recording's offset-fit report); the trunk value follows the
    // E-035 rule, the median distance from the pelvis point the record
    // carries to the measured mid-shoulder on torso-clean frames.
    // Why the match matters: the rig's authored proportions differ from
    // the subject's (upper arm 15 percent short, forearm 17 percent long
    // on R5), which lands the rendered wrist centimeters away from the
    // tracked one and reads as "the hand does not reach the cube".
    // The match moves the elbow and wrist joints along their bones to
    // these lengths rather than scaling the bones themselves (E-038), so
    // the joint distances change while the mesh keeps its authored
    // thickness; 0 (the default, and what stays when no sizing file is
    // accepted) disables the match and leaves the rig proportions as
    // authored.
    public float upperArmRM = 0f, forearmRM = 0f;
    public float upperArmLM = 0f, forearmLM = 0f;
    // Hip-to-mid-shoulder length (m). The rig's authored torso was 5.6 cm
    // longer than the loop recording's subject, which raised the
    // shoulder anchor and shifted the whole rendered arm chain (measured
    // about 12 cm wrist offset at a raised-arm pose). Scaling the spine
    // bone corrects it; the arm match in Start() runs after and
    // re-normalizes the arm lengths. The length is the distance from the
    // pelvis point the RECORD carries to the measured mid-shoulder, not
    // an anatomical torso, so it changes with the pelvis definition of
    // the recording: the raw hip midpoint on the loop recording, the
    // hip-depth-corrected point of the recovery layer on the rail
    // recordings, which sits deeper than the raw hips. Replaying one
    // recording with another's trunk length put the shoulders 10 cm
    // below the measured ones and the reaching hand under the desk slab
    // (2026-09-07), which is why the value is now taken per recording
    // from the sizing file.
    public float torsoM = 0f;

    [Header("Person debug (read-only)")]
    public Vector3 lastPelvis;      // person space, as received
    public Vector3 lastRootEuler;
    public int lastMask = 127;

    Transform anchor;               // camera pose * Rx(-90): person -> scene
    Transform rigRoot, hip, upperArm, forearm, lUpperArm, lForearm;
    Transform rHand, lHand;         // logged only (offset analysis), not driven
    float rigRestHeightRaw, appliedScale = 1f;
    Quaternion cHip, cUpperArm, cForearm, cLUpperArm, cLForearm; // anchor-relative rest
    GameObject heldHip, heldRUpper, heldRFore, heldLUpper, heldLFore;
    MemoryMappedFile imf;
    MemoryMappedViewAccessor iview;
    StreamWriter personLog;

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    static void BootstrapIntegrated()
    {
        if (!File.Exists("/dev/shm/integrated_scene")
            || !File.Exists("/dev/shm/aruco_scene")) return;
        if (FindFirstObjectByType<IntegratedSceneReceiver>() != null) return;
        new GameObject("IntegratedSceneReceiver").AddComponent<IntegratedSceneReceiver>();
    }

    // Per-recording rig sizing for an unattended capture (E-036). The
    // capture launchers (eval/unity_check/run_unity_capture.py, and the
    // presentation renders that drive the editor the same way) write
    // this file from eval/reports/<alias>_rig_sizing.json before the
    // editor launches and remove it afterwards, so the lengths reach the
    // receiver as a side channel and no recording's numbers are typed
    // into this class. Format: key=value lines; blank lines and lines
    // starting with # are ignored; keys stem, upper_arm_R, forearm_R,
    // upper_arm_L, forearm_L and torso (metres; the trunk by the E-035
    // rule). All five lengths must be present and positive, and the
    // file must be younger than SizingMaxAgeS, because a file left
    // behind by an earlier capture must not size a later one. A file
    // that fails either test is rejected with an error and the fields
    // above stay 0, which leaves the rig proportions as authored; the
    // same happens, with a warning, when the file is absent, so a
    // capture launched without it is detectable in the editor log.
    const string SizingOverridePath = "/tmp/r5_rig_sizing";
    const double SizingMaxAgeS = 3600.0;
    static readonly string[] SizingKeys =
        { "upper_arm_R", "forearm_R", "upper_arm_L", "forearm_L", "torso" };
    string sizingSource = "none", sizingStem = "";

    void Awake()
    {
        // Keep the standalone Pipeline B artifacts untouched.
        logPath = "/home/luo/Desktop/New_SandBox/v1/integration/output/unity_object_log.csv";
        LoadSizingOverride();
    }

    void LoadSizingOverride()
    {
        if (!File.Exists(SizingOverridePath))
        {
            Debug.LogWarning($"[IntegratedSceneReceiver] no rig sizing file at "
                             + $"{SizingOverridePath}; rig proportions left as authored");
            return;
        }
        double ageS = (System.DateTime.UtcNow
                       - File.GetLastWriteTimeUtc(SizingOverridePath)).TotalSeconds;
        if (ageS > SizingMaxAgeS)
        {
            Debug.LogError($"[IntegratedSceneReceiver] rig sizing file {SizingOverridePath} "
                           + $"is {ageS:F0} s old (limit {SizingMaxAgeS:F0} s); "
                           + "ignored, rig proportions left as authored");
            return;
        }
        var values = new Dictionary<string, float>();
        string stem = "";
        foreach (string raw in File.ReadAllLines(SizingOverridePath))
        {
            string line = raw.Trim();
            if (line.Length == 0 || line.StartsWith("#")) continue;
            int eq = line.IndexOf('=');
            if (eq < 0) continue;
            string key = line.Substring(0, eq).Trim();
            string val = line.Substring(eq + 1).Trim();
            if (key == "stem") { stem = val; continue; }
            float v;
            if (float.TryParse(val, NumberStyles.Float, CultureInfo.InvariantCulture, out v))
                values[key] = v;
            else if (System.Array.IndexOf(SizingKeys, key) >= 0)
            {
                Debug.LogError($"[IntegratedSceneReceiver] rig sizing file {SizingOverridePath}: "
                               + $"key {key} has the non-numeric value '{val}'; "
                               + "ignored, rig proportions left as authored");
                return;
            }
        }
        foreach (string key in SizingKeys)
        {
            float v;
            if (!values.TryGetValue(key, out v))
            {
                Debug.LogError($"[IntegratedSceneReceiver] rig sizing file {SizingOverridePath}: "
                               + $"key {key} missing; ignored, rig proportions left as authored");
                return;
            }
            if (!(v > 0f) || float.IsInfinity(v))
            {
                Debug.LogError($"[IntegratedSceneReceiver] rig sizing file {SizingOverridePath}: "
                               + $"key {key}={v} is not a positive length; "
                               + "ignored, rig proportions left as authored");
                return;
            }
        }
        upperArmRM = values["upper_arm_R"];
        forearmRM = values["forearm_R"];
        upperArmLM = values["upper_arm_L"];
        forearmLM = values["forearm_L"];
        torsoM = values["torso"];
        sizingSource = SizingOverridePath;
        sizingStem = stem;
        Debug.Log($"[IntegratedSceneReceiver] rig sizing override from {SizingOverridePath}: "
                  + $"stem={stem} upper_arm_R={upperArmRM:F4} forearm_R={forearmRM:F4} "
                  + $"upper_arm_L={upperArmLM:F4} forearm_L={forearmLM:F4} torso={torsoM:F4}");
    }

    protected override Vector3 WorldOffset() { return Vector3.zero; }

    static Transform FindBone(string name)
    {
        foreach (var t in FindObjectsByType<Transform>(FindObjectsSortMode.None))
            if (t.name == name) return t;
        return null;
    }

    static GameObject HeldMarker(string name)
    {
        var s = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        s.name = $"held_{name}";
        Destroy(s.GetComponent<Collider>());
        s.GetComponent<Renderer>().material.color = new Color(0.9f, 0.1f, 0.1f);
        // 4.5 cm: visible next to the 7 cm cube without covering the
        // joint it marks (was 12 cm; user review 2026-08-26).
        s.transform.localScale = Vector3.one * 0.045f;
        s.SetActive(false);
        return s;
    }

    protected override void Start()
    {
        base.Start();   // PSB3 scene: wall/desk marker/sensor/object cube
        if (!enabled) return;

        // The standalone receivers must not fight over the same bones.
        foreach (var b in FindObjectsByType<MonoBehaviour>(FindObjectsSortMode.None))
            if (b != this && (b is ArmAngleReceiver || b.GetType().Name == "PoseStreamReceiver"
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
            Debug.LogError("[IntegratedSceneReceiver] rig bones not found");
            enabled = false;
            return;
        }
        rigRoot = hip.root;

        // Scale the rig to a personHeightM-tall human BEFORE measuring
        // dimensions or capturing rest rotations. Rest height from the
        // head-end bone (rig spawns standing at the origin, feet at y=0);
        // renderer bounds as fallback.
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
            Debug.Log($"[IntegratedSceneReceiver] rig rest height "
                      + $"{rigRestHeightRaw:F3} m -> scaled x{appliedScale:F3} "
                      + $"to {personHeightM:F2} m");
        }

        // Match the rig's torso and arm segment lengths to the
        // subject's before rest capture and dimension dump. Uniform
        // per-bone scales, so world rotations (the whole angle
        // transfer) are untouched; the hand compensates the forearm's
        // factor and keeps the upper-arm factor, so a subject with
        // longer arms also gets a proportionally larger hand toward
        // the held object. Torso first (it moves the shoulder
        // anchors), arms after (they re-measure the scaled rig).
        // Force an exact model T-pose before anything is measured or
        // captured: the angle transfer composes streamed rotations
        // with the spawn pose, so it is only exact if the spawn arms
        // lie along the model's rest axes (+x right arm, -x left). An
        // authored deviation (A-pose droop, slight elbow bend) would
        // otherwise ride along into every rendered frame. Minimal
        // rotations; a rig that already spawns in T-pose is untouched.
        AlignArm(upperArm, forearm, rHand, Vector3.right);
        AlignArm(lUpperArm, lForearm, lHand, Vector3.left);

        if (torsoM > 0f)
        {
            Vector3 midSh0 = (upperArm.position + lUpperArm.position) / 2f;
            float rigTorso = Vector3.Distance(hip.position, midSh0);
            if (rigTorso > 1e-4f)
            {
                float st = torsoM / rigTorso;
                hip.localScale *= st;
                Debug.Log($"[IntegratedSceneReceiver] torso "
                          + $"{rigTorso:F3} -> {torsoM:F3} m (x{st:F3})");
            }
        }
        MatchArm(upperArm, forearm, rHand, upperArmRM, forearmRM);
        MatchArm(lUpperArm, lForearm, lHand, upperArmLM, forearmLM);

        DumpRigDimensions();   // post-scale, with the raw height on record

        // Authored rest, captured with the rig spawned unrotated (body
        // axes = scene axes) — the anchor is PRE-multiplied per frame.
        cHip = hip.rotation;
        cUpperArm = upperArm.rotation;
        cForearm = forearm.rotation;
        cLUpperArm = lUpperArm.rotation;
        cLForearm = lForearm.rotation;
        heldHip = HeldMarker("hip");
        heldRUpper = HeldMarker("upper_arm.R");
        heldRFore = HeldMarker("forearm.R");
        heldLUpper = HeldMarker("upper_arm.L");
        heldLFore = HeldMarker("forearm.L");

        Directory.CreateDirectory(Path.GetDirectoryName(personLogPath));
        personLog = new StreamWriter(personLogPath, false);
        personLog.WriteLine("frame,time_s,mask,pel_x,pel_y,pel_z,hip_x,hip_y,hip_z,"
                            + "rh_x,rh_y,rh_z,lh_x,lh_y,lh_z,"
                            + "rsh_x,rsh_y,rsh_z,lsh_x,lsh_y,lsh_z,"
                            + "rel_x,rel_y,rel_z,lel_x,lel_y,lel_z");
        personLog.Flush();
        Debug.Log($"[IntegratedSceneReceiver] person anchored at {anchor.position} "
                  + $"euler {anchor.rotation.eulerAngles}");
    }

    static void AlignArm(Transform up, Transform fore, Transform hand,
                         Vector3 axis)
    {
        Vector3 d1 = (fore.position - up.position).normalized;
        float dev1 = Vector3.Angle(d1, axis);
        up.rotation = Quaternion.FromToRotation(d1, axis) * up.rotation;
        Vector3 d2 = (hand.position - fore.position).normalized;
        float dev2 = Vector3.Angle(d2, axis);
        fore.rotation = Quaternion.FromToRotation(d2, axis) * fore.rotation;
        Debug.Log($"[IntegratedSceneReceiver] {up.name} spawn pose vs "
                  + $"T-pose: upper {dev1:F1} deg, forearm {dev2:F1} deg "
                  + "(aligned)");
    }

    static void MatchArm(Transform up, Transform fore, Transform hand,
                         float upM, float foreM)
    {
        if (upM <= 0f || foreM <= 0f) return;
        float rigUp = Vector3.Distance(up.position, fore.position);
        float rigFore = Vector3.Distance(fore.position, hand.position);
        if (rigUp < 1e-4f || rigFore < 1e-4f) return;
        // Move the elbow and wrist joints along their bones instead of
        // scaling the bones (E-038). A uniform bone scale reached the same
        // joint distances but changed the mesh thickness with the length
        // (the rail recording's short forearm rendered abnormally thin), and
        // a scale along one axis only would shear the child bone once the
        // elbow bends. Scaling the child's local offset scales its world
        // distance by the same factor, since the parent map is linear, so
        // the joint positions are exactly those of the scaled rig.
        float s1 = upM / rigUp;                    // upper arm factor
        float s2 = foreM / rigFore;                // forearm factor
        fore.localPosition *= s1;
        hand.localPosition *= s2;
        Debug.Log($"[IntegratedSceneReceiver] {up.name}: upper "
                  + $"{rigUp:F3} -> {Vector3.Distance(up.position, fore.position):F3} m "
                  + $"(wanted {upM:F3}), forearm {rigFore:F3} -> "
                  + $"{Vector3.Distance(fore.position, hand.position):F3} m (wanted {foreM:F3})");
    }

    /// Rest-pose bone lengths, measured at spawn (rig unrotated at the
    /// scene origin, 1 unit = 1 m) with the same endpoints MediaPipe uses:
    /// shoulder joint = upper-arm head, elbow = forearm head, wrist = hand
    /// head. Consumed by integration/analyze_object_offset.py to compare
    /// the rig's proportions against the tracked person and the scene,
    /// and by the thesis verification scripts, which parse the meters
    /// column as floats: the segment,meters schema stays numeric. The
    /// companion rig_sizing_used.txt records where the sizing came from
    /// (E-036): the sizing file path or "none", the recording stem that
    /// file named, and the five requested lengths, so a capture folder
    /// shows which recording sized its rig (check_rig_sizing.py compares
    /// both files against the recording's sizing json).
    void DumpRigDimensions()
    {
        string path = "/home/luo/Desktop/New_SandBox/v1/integration/output/rig_dimensions.csv";
        Directory.CreateDirectory(Path.GetDirectoryName(path));
        using (var w = new StreamWriter(path, false))
        {
            w.WriteLine("segment,meters");
            w.WriteLine($"shoulder_width,{Vector3.Distance(upperArm.position, lUpperArm.position):F6}");
            w.WriteLine($"upper_arm_R,{Vector3.Distance(upperArm.position, forearm.position):F6}");
            w.WriteLine($"upper_arm_L,{Vector3.Distance(lUpperArm.position, lForearm.position):F6}");
            w.WriteLine($"forearm_R,{Vector3.Distance(forearm.position, rHand.position):F6}");
            w.WriteLine($"forearm_L,{Vector3.Distance(lForearm.position, lHand.position):F6}");
            Vector3 midSh = (upperArm.position + lUpperArm.position) / 2f;
            w.WriteLine($"torso_hip_to_midshoulder,{Vector3.Distance(hip.position, midSh):F6}");
            w.WriteLine($"hip_height_rest,{hip.position.y:F6}");
            w.WriteLine($"rig_rest_height_raw,{rigRestHeightRaw:F6}");
            w.WriteLine($"applied_scale,{appliedScale:F6}");
        }
        string used = Path.Combine(Path.GetDirectoryName(path), "rig_sizing_used.txt");
        using (var w = new StreamWriter(used, false))
        {
            w.WriteLine($"source={sizingSource}");
            w.WriteLine($"stem={sizingStem}");
            w.WriteLine($"requested_upper_arm_R={upperArmRM:F4}");
            w.WriteLine($"requested_forearm_R={forearmRM:F4}");
            w.WriteLine($"requested_upper_arm_L={upperArmLM:F4}");
            w.WriteLine($"requested_forearm_L={forearmLM:F4}");
            w.WriteLine($"requested_torso={torsoM:F4}");
        }
        Debug.Log($"[IntegratedSceneReceiver] rig dimensions -> {path} (sizing note {used})");
    }

    bool ReadIntegrated(out int frame, out float t, out Vector3 pelvis,
                        out float[] v, out Vector3 objPos, out Vector3 objEuler,
                        out int mask, out int objLive)
    {
        frame = 0; t = 0; pelvis = objPos = objEuler = Vector3.zero;
        v = new float[13]; mask = 127; objLive = 1;
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
            if (iview.ReadUInt32(0) != MagicIntegrated) return false;
            frame = iview.ReadInt32(8);
            t = iview.ReadSingle(12);
            pelvis = new Vector3(iview.ReadSingle(16), iview.ReadSingle(20), iview.ReadSingle(24));
            for (int i = 0; i < 13; i++) v[i] = iview.ReadSingle(28 + 4 * i);
            objPos = new Vector3(iview.ReadSingle(80), iview.ReadSingle(84), iview.ReadSingle(88));
            objEuler = new Vector3(iview.ReadSingle(92), iview.ReadSingle(96), iview.ReadSingle(100));
            mask = iview.ReadUInt16(104);
            objLive = iview.ReadUInt16(106);
            if (iview.ReadUInt32(4) == seq0) return true;
        }
        return false;
    }

    void ApplyPerson(float t, int frame, Vector3 pelvis, float[] v, int mask)
    {
        lastPelvis = pelvis;
        lastRootEuler = new Vector3(v[0], v[1], v[2]);
        lastMask = mask;

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

        // Translate the whole rig so the hip bone lands on the streamed
        // pelvis point (mapped through the anchor).
        Vector3 target = anchor.TransformPoint(pelvis);
        rigRoot.position += target - hip.position;

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

        if (personLog != null)
        {
            Vector3 h = hip.position;
            Vector3 rh = rHand.position, lh = lHand.position;
            Vector3 rs = upperArm.position, ls = lUpperArm.position;
            Vector3 re = forearm.position, le = lForearm.position;
            personLog.WriteLine($"{frame},{t:F6},{mask},{pelvis.x:F6},{pelvis.y:F6},{pelvis.z:F6},"
                                + $"{h.x:F6},{h.y:F6},{h.z:F6},"
                                + $"{rh.x:F6},{rh.y:F6},{rh.z:F6},{lh.x:F6},{lh.y:F6},{lh.z:F6},"
                                + $"{rs.x:F6},{rs.y:F6},{rs.z:F6},{ls.x:F6},{ls.y:F6},{ls.z:F6},"
                                + $"{re.x:F6},{re.y:F6},{re.z:F6},{le.x:F6},{le.y:F6},{le.z:F6}");
            personLog.Flush();
        }
    }

    // The push toward the camera is per rendering camera (HeldMarkers):
    // EvalFrameDump re-places the spheres for the sensor-view capture.
    static void PlaceHeld(GameObject marker, Transform bone, Transform cam)
        => HeldMarkers.Place(marker, bone, cam);

    /// Global "monitor" view: pulled back and up so wall, desk, object,
    /// sensor AND the person are all in frame.
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
        // Shallow pitch: a steeply pitched LookAt keystones every vertical
        // edge and makes the (actually plumb) wall look tilted on video.
        cam.transform.position = center + away * 2.6f + side * 2.4f + Vector3.up * 1.1f;
        cam.transform.LookAt(center + Vector3.up * 0.15f);
    }

    protected override void Update()
    {
        if (!ReadIntegrated(out int frame, out float t, out Vector3 pelvis,
                            out float[] v, out Vector3 objPos, out Vector3 objEuler,
                            out int mask, out int objLive)) return;
        if (frame == lastFrame) return;
        ApplyObject(frame, t, objPos, objEuler, objLive); // also builds deferred geometry
        ApplyPerson(t, frame, pelvis, v, mask);
    }

    protected override void OnDestroy()
    {
        personLog?.Dispose();
        iview?.Dispose();
        imf?.Dispose();
        base.OnDestroy();
    }
}
