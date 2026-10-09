using System.IO;
using System.IO.MemoryMappedFiles;
using UnityEngine;

/// Pipeline B receiver (ARUCO_MODEL.md): reconstructs the ArUco scene in
/// Unity as REAL geometry from shared memory written by
/// aruco/send_scene_poses.py.
///
/// Static scene arrives ONCE via /dev/shm/aruco_scene (PSB3, 100 B):
/// desk/wall/camera poses + gravity up + tabletop drop + object cube size
/// + sensor FOV, all in the desk-anchored world already mapped to Unity
/// axes (mapped marker frame: x = right, normal = up, y = forward). The
/// moving object streams per frame via /dev/shm/aruco_object (PSB2, 44 B
/// seqlock); live=0 frames (object marker blocked) tint it red.
///
/// Geometry built from the measured numbers:
///  - the whole "ArucoWorld" parent is rotated so the depth-fit gravity
///    vector becomes scene up (the desk marker card sits on a ~27 deg
///    tilted stand, so the raw world frame is NOT level);
///  - wall: slab coplanar with the wall marker;
///  - desk top: horizontal (normal = gravity) slab whose top surface is
///    the depth-fit tabletop plane, sized/centered from the desk marker
///    and the object; legs + floor are decorative (standard desk height);
///  - object: cube of the calibrated edge (marker centered on its front
///    face, box resting on the desk -> center is half an edge behind the
///    marker along its normal);
///  - sensor: small RealSense-like box at the calibrated camera pose
///    (optical axis = mapped up, image-down = mapped forward).
///
/// Self-bootstrapping: entering play mode creates the receiver when
/// /dev/shm/aruco_scene exists. Applied stream frames are logged to
/// aruco/output/unity_aruco_log.csv for offline verification.
public class ArucoSceneReceiver : MonoBehaviour
{
    const uint MagicScene = 0x33425350;  // 'PSB3'
    const uint MagicObject = 0x32425350; // 'PSB2'
    const int ScenePacketSize = 100;
    const int ObjectPacketSize = 44;

    public string sceneShmPath = "/dev/shm/aruco_scene";
    public string objectShmPath = "/dev/shm/aruco_object";
    public string logPath = "Logs/unity_aruco_log.csv";

    [Header("Scene numbers (read from PSB3)")]
    public Vector3 gravityUpLocal;   // world-local Unity coords
    public float tabletopDrop;       // origin height above the tabletop (m)
    public float cubeSize;           // object cube edge (m)
    public float sensorFovY;         // vertical FOV (deg), for the POV view

    [Header("Debug (read-only)")]
    public int lastFrame = -1;
    public Vector3 lastObjectPos;
    public Vector3 lastObjectEuler;
    public int lastLive = 1;

    protected Transform world;   // "ArucoWorld" parent, gravity-aligned
    Transform wallNode, objectNode;
    Renderer objectCube, objectPlate;
    protected Vector3[] posesPos = new Vector3[3], posesEuler = new Vector3[3];
    protected bool deferredBuilt;
    MemoryMappedFile mmf;
    MemoryMappedViewAccessor view;
    StreamWriter log;

    const float DeskW = 1.4f, DeskThick = 0.03f, LegH = 0.69f;
    const float WallW = 3.0f, WallThick = 0.02f;

    static readonly Color WallCol = new Color(0.87f, 0.84f, 0.78f);
    static readonly Color DeskCol = new Color(0.55f, 0.40f, 0.25f);
    static readonly Color LegCol = new Color(0.32f, 0.24f, 0.16f);
    static readonly Color FloorCol = new Color(0.42f, 0.44f, 0.47f);
    static readonly Color CubeCol = new Color(0.90f, 0.55f, 0.15f);
    static readonly Color HeldCol = new Color(0.90f, 0.10f, 0.10f);
    static readonly Color PlateCol = new Color(0.95f, 0.95f, 0.95f);
    static readonly Color SensorCol = new Color(0.15f, 0.15f, 0.17f);

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    static void Bootstrap()
    {
        // The integrated receiver builds the same scene itself — never both.
        if (!File.Exists("/dev/shm/aruco_scene")) return;
        if (File.Exists("/dev/shm/integrated_scene_v2")) return;
        if (FindFirstObjectByType<ArucoSceneReceiver>() != null) return;
        new GameObject("ArucoSceneReceiver").AddComponent<ArucoSceneReceiver>();
    }

    protected static GameObject Slab(Transform parent, string name, Vector3 localPos,
                                     Quaternion localRot, Vector3 size, Color col)
    {
        var g = GameObject.CreatePrimitive(PrimitiveType.Cube);
        g.name = name;
        Destroy(g.GetComponent<Collider>());
        g.transform.SetParent(parent, false);
        g.transform.localPosition = localPos;
        g.transform.localRotation = localRot;
        g.transform.localScale = size;
        g.GetComponent<Renderer>().material.color = col;
        return g;
    }

    protected static void Label(Transform parent, string text, Vector3 localPos)
    {
        var tgo = new GameObject("label");
        tgo.transform.SetParent(parent, false);
        tgo.transform.localPosition = localPos;
        var tm = tgo.AddComponent<TextMesh>();
        tm.text = text;
        tm.fontSize = 48;
        tm.characterSize = 0.02f;
        tm.anchor = TextAnchor.MiddleCenter;
        tm.color = Color.white;
    }

    /// A pose node in ArucoWorld-local coordinates (mapped marker frame).
    protected Transform Node(string name, Vector3 pos, Vector3 euler)
    {
        var t = new GameObject($"aruco_{name}").transform;
        t.SetParent(world, false);
        t.localPosition = pos;
        t.localRotation = Quaternion.Euler(euler);
        return t;
    }

    // Rendered ArUco patterns (generated by eval/unity_check/
    // make_marker_textures.py; user request 2026-08-26). Absolute path,
    // consistent with the log paths this scene already uses; a missing
    // file falls back to the plain plate.
    public static string markerTexDir =
        "Assets/StreamingAssets/Markers";

    /// Thin plate marking a physical ArUco card (marker plane = local x/z,
    /// normal = local up). markerId >= 0 textures the plate with the real
    /// ArUco pattern when its PNG exists.
    protected Renderer MarkerPlate(Transform node, float sizeM, string label,
                                   int markerId = -1)
    {
        var p = Slab(node, $"plate_{label}", Vector3.up * 0.002f,
                     Quaternion.identity, new Vector3(sizeM, 0.003f, sizeM), PlateCol);
        if (markerId >= 0)
        {
            string f = Path.Combine(markerTexDir, $"aruco_id{markerId}.png");
            if (File.Exists(f))
            {
                var tex = new Texture2D(2, 2);
                tex.LoadImage(File.ReadAllBytes(f));
                tex.filterMode = FilterMode.Point;   // crisp black squares
                var r = p.GetComponent<Renderer>();
                // The desk card is drawn over the desk slab (no depth test):
                // its calibrated centre lies 0.4 cm below the fitted tabletop
                // plane on the rail calibration, so the slab cut the tilted
                // card in half in every sensor-view render. Nothing ever
                // stands between the sensor and the desk card, so no other
                // pixel changes. Assets/Shaders/PlateOverlay.shader.
                if (markerId == 2)
                {
                    var overlay = Shader.Find("Thesis/PlateOverlay");
                    if (overlay != null) r.material.shader = overlay;
                    else Debug.LogWarning("[ArucoSceneReceiver] Thesis/PlateOverlay shader not found; desk card may be cut by the desk slab");
                }
                r.material.mainTexture = tex;
                r.material.color = Color.white;
            }
        }
        Label(node, label, Vector3.up * 0.09f);
        return p.GetComponent<Renderer>();
    }

    protected bool ReadScenePacket()
    {
        byte[] raw;
        try { raw = File.ReadAllBytes(sceneShmPath); }
        catch (IOException e)
        {
            Debug.LogError($"[ArucoSceneReceiver] scene shm unreadable: {e.Message}");
            return false;
        }
        if (raw.Length < ScenePacketSize
            || System.BitConverter.ToUInt32(raw, 0) != MagicScene)
        {
            Debug.LogError("[ArucoSceneReceiver] bad scene packet (need PSB3)");
            return false;
        }
        for (int i = 0; i < 3; i++)
        {
            int o = 4 + i * 24;
            posesPos[i] = new Vector3(System.BitConverter.ToSingle(raw, o),
                                      System.BitConverter.ToSingle(raw, o + 4),
                                      System.BitConverter.ToSingle(raw, o + 8));
            posesEuler[i] = new Vector3(System.BitConverter.ToSingle(raw, o + 12),
                                        System.BitConverter.ToSingle(raw, o + 16),
                                        System.BitConverter.ToSingle(raw, o + 20));
        }
        gravityUpLocal = new Vector3(System.BitConverter.ToSingle(raw, 76),
                                     System.BitConverter.ToSingle(raw, 80),
                                     System.BitConverter.ToSingle(raw, 84)).normalized;
        tabletopDrop = System.BitConverter.ToSingle(raw, 88);
        cubeSize = System.BitConverter.ToSingle(raw, 92);
        sensorFovY = System.BitConverter.ToSingle(raw, 96);
        return true;
    }

    /// Builds everything that does not need the object's position yet.
    /// posesPos/posesEuler order: 0 desk, 1 wall, 2 camera.
    protected void BuildStaticScene()
    {
        world = new GameObject("ArucoWorld").transform;
        // Level the reconstruction: rotate the parent so the depth-fit
        // gravity direction becomes scene up. Poses are applied as LOCAL
        // pose, so the parent transform is purely presentational; the x
        // offset keeps the standalone reconstruction beside the T-posed rig
        // at the scene origin.
        world.rotation = Quaternion.FromToRotation(gravityUpLocal, Vector3.up);
        world.position = WorldOffset();

        // Wall marker card; the slab itself is sized down to the floor in
        // BuildDeferredScene once the floor level is known.
        wallNode = Node("wall", posesPos[1], posesEuler[1]);
        MarkerPlate(wallNode, 0.15f, "wall id0", 0);

        // Desk marker card on its (tilted) stand at the world origin.
        var deskNode = Node("desk", posesPos[0], posesEuler[0]);
        MarkerPlate(deskNode, 0.05f, "desk id2", 2);

        // Sensor body at the calibrated camera pose. Mapped camera frame:
        // optical axis = local up, image-down = local forward.
        var sensorNode = Node("sensor", posesPos[2], posesEuler[2]);
        Slab(sensorNode, "sensor_body", Vector3.zero, Quaternion.identity,
             new Vector3(0.09f, 0.025f, 0.025f), SensorCol);
        Slab(sensorNode, "sensor_lens", new Vector3(0.018f, 0.0125f, 0f),
             Quaternion.identity, new Vector3(0.014f, 0.004f, 0.014f),
             new Color(0.35f, 0.55f, 0.75f));
        Label(sensorNode, "sensor", Vector3.up * 0.09f);

        // Sensor POV: a second camera at the sensor pose looking along the
        // optical axis (mapped camera frame: optical = local up, image-down
        // = local forward) with the CALIBRATED vertical FOV, rendered as a
        // picture-in-picture inset (top right, real 4:3 sensor aspect).
        // The sensor body/lens sit inside the near clip, so they never
        // occlude their own view.
        var pov = new GameObject("SensorPOVCamera").AddComponent<Camera>();
        pov.transform.SetParent(sensorNode, false);
        pov.transform.localRotation = Quaternion.LookRotation(Vector3.up, -Vector3.forward);
        pov.fieldOfView = sensorFovY;
        pov.nearClipPlane = 0.05f;
        pov.depth = 10f;                    // draw after (on top of) the main view
        float hFrac = 0.42f;
        float wFrac = (4f / 3f) * hFrac * Screen.height / Screen.width;
        pov.rect = new Rect(0.985f - wFrac, 0.975f - hFrac, wFrac, hFrac);

        // Streamed object: cube body is half an edge behind the marker
        // along its normal (marker centered on the front face).
        objectNode = Node("object", Vector3.zero, Vector3.zero);
        var cube = Slab(objectNode, "object_cube", Vector3.down * (cubeSize / 2f),
                        Quaternion.identity, Vector3.one * cubeSize, CubeCol);
        objectCube = cube.GetComponent<Renderer>();
        objectPlate = MarkerPlate(objectNode, 0.05f, "object id1", 1);
        objectNode.gameObject.SetActive(false); // until the first stream frame
    }

    /// Desk top + legs + floor need a point on the desk besides the world
    /// origin — built on the first streamed object frame.
    protected void BuildDeferredScene(Vector3 objPosLocal)
    {
        deferredBuilt = true;
        Vector3 g = gravityUpLocal;
        Vector3 onPlane = -g * tabletopDrop;            // tabletop point below the origin
        Vector3 projO = ProjectOntoPlane(Vector3.zero, onPlane, g);
        Vector3 projB = ProjectOntoPlane(objPosLocal, onPlane, g);
        Vector3 span = projB - projO;
        Vector3 x = span.sqrMagnitude > 1e-8f ? span.normalized
                                              : Vector3.ProjectOnPlane(Vector3.right, g).normalized;
        Quaternion flat = Quaternion.LookRotation(Vector3.Cross(x, g), g);
        // Desk depth is DATA-driven, not a fixed box: from a margin behind
        // the desk marker to just past the object's projection. The person
        // stands/sits at the far edge, so a fixed centered slab ran into
        // their (untracked) legs — caught in plot_integrated_scene.py
        // (pelvis clears this far edge by +23 cm on the 20260224 data).
        Vector3 near = projO - x * 0.30f;
        Vector3 far = projB + x * 0.05f;
        float deskLen = Vector3.Distance(near, far);
        Vector3 center = (near + far) / 2f;

        var deskTop = Slab(world, "desk_top", center - g * (DeskThick / 2f),
                           flat, new Vector3(deskLen, DeskThick, DeskW), DeskCol);
        // Decorative below the measured tabletop plane: standard-height
        // legs and a floor slab (the recording never sees the floor).
        for (int sx = -1; sx <= 1; sx += 2)
            for (int sz = -1; sz <= 1; sz += 2)
            {
                Vector3 corner = center
                    + flat * new Vector3(sx * (deskLen / 2f - 0.05f), 0f, sz * (DeskW / 2f - 0.05f))
                    - g * (DeskThick + LegH / 2f);
                Slab(world, $"desk_leg_{sx}_{sz}", corner, flat,
                     new Vector3(0.05f, LegH, 0.05f), LegCol);
            }
        Slab(world, "floor", center - g * (DeskThick + LegH + 0.005f), flat,
             new Vector3(8f, 0.01f, 8f), FloorCol);

        // Wall slab: marker plane, extended down to the floor and 0.8 m
        // above the marker (in-plane vertical = wall-node forward, ~plumb).
        Vector3 floorPt = center - g * (DeskThick + LegH);
        float markerHeight = Vector3.Dot(wallNode.localPosition - floorPt, g);
        float wallH = markerHeight + 0.8f;
        Slab(wallNode, "wall_slab",
             new Vector3(0f, -(WallThick / 2f + 0.004f), (0.8f - markerHeight) / 2f),
             Quaternion.identity, new Vector3(WallW, WallThick, wallH), WallCol);

        // Drop the whole reconstruction so the floor sits at scene y = 0.
        float floorY = world.TransformPoint(center - g * (DeskThick + LegH)).y;
        world.position += Vector3.down * floorY;

        FrameCamera(center);
    }

    protected virtual Vector3 WorldOffset() { return new Vector3(2.5f, 0f, 0f); }

    static Vector3 ProjectOntoPlane(Vector3 p, Vector3 onPlane, Vector3 n)
    {
        return p - n * Vector3.Dot(p - onPlane, n);
    }

    /// Point the main camera at the desk area from a raised oblique spot.
    protected virtual void FrameCamera(Vector3 deskCenterLocal)
    {
        var cam = Camera.main;
        if (cam == null) return;
        Vector3 center = world.TransformPoint(deskCenterLocal) + Vector3.up * 0.35f;
        Vector3 wall = world.TransformPoint(posesPos[1]);
        Vector3 away = center - wall;                    // look toward the wall
        away.y = 0f;
        away = away.sqrMagnitude > 1e-6f ? away.normalized : Vector3.back;
        Vector3 side = Vector3.Cross(Vector3.up, away);  // oblique, off the rig axis
        cam.transform.position = center + away * 1.9f + side * 1.7f + Vector3.up * 1.0f;
        cam.transform.LookAt(center);
    }

    protected virtual void Start()
    {
        // Keep the play loop alive when the editor loses focus during
        // ffmpeg captures (FINDINGS 2026-07-13).
        Application.runInBackground = true;
        if (!ReadScenePacket()) { enabled = false; return; }
        BuildStaticScene();
        Debug.Log($"[ArucoSceneReceiver] scene built: gravity {gravityUpLocal}, "
                  + $"drop {tabletopDrop:F3} m, cube {cubeSize:F3} m, FOVy {sensorFovY:F1}");

        Directory.CreateDirectory(Path.GetDirectoryName(logPath));
        log = new StreamWriter(logPath, false);
        log.WriteLine("frame,time_s,live,px,py,pz,ex,ey,ez");
        log.Flush();
    }

    bool ReadObject(out int frame, out float t, out Vector3 pos, out Vector3 euler, out int live)
    {
        frame = 0; t = 0; pos = euler = Vector3.zero; live = 1;
        if (view == null)
        {
            try
            {
                mmf = MemoryMappedFile.CreateFromFile(objectShmPath, FileMode.Open);
                view = mmf.CreateViewAccessor(0, ObjectPacketSize);
            }
            catch { return false; }
        }
        for (int attempt = 0; attempt < 3; attempt++)
        {
            uint seq0 = view.ReadUInt32(4);
            if ((seq0 & 1) != 0) continue;
            if (view.ReadUInt32(0) != MagicObject) return false;
            frame = view.ReadInt32(8);
            t = view.ReadSingle(12);
            pos = new Vector3(view.ReadSingle(16), view.ReadSingle(20), view.ReadSingle(24));
            euler = new Vector3(view.ReadSingle(28), view.ReadSingle(32), view.ReadSingle(36));
            live = view.ReadUInt16(40);
            if (view.ReadUInt32(4) == seq0) return true;
        }
        return false;
    }

    protected void ApplyObject(int frame, float t, Vector3 pos, Vector3 euler, int live)
    {
        lastFrame = frame;
        lastObjectPos = pos;
        lastObjectEuler = euler;
        lastLive = live;
        if (!deferredBuilt) BuildDeferredScene(pos);

        objectNode.gameObject.SetActive(true);
        objectNode.localPosition = pos;
        objectNode.localRotation = Quaternion.Euler(euler);
        objectCube.material.color = live == 1 ? CubeCol : HeldCol;
        objectPlate.material.color = live == 1 ? PlateCol : HeldCol;

        if (log != null)
        {
            log.WriteLine($"{frame},{t:F6},{live},{pos.x:F6},{pos.y:F6},{pos.z:F6},"
                          + $"{euler.x:F6},{euler.y:F6},{euler.z:F6}");
            log.Flush();
        }
    }

    protected virtual void Update()
    {
        if (!ReadObject(out int frame, out float t, out Vector3 pos,
                        out Vector3 euler, out int live)) return;
        if (frame == lastFrame) return;
        ApplyObject(frame, t, pos, euler, live);
    }

    protected virtual void OnDestroy()
    {
        log?.Dispose();
        view?.Dispose();
        mmf?.Dispose();
    }
}
