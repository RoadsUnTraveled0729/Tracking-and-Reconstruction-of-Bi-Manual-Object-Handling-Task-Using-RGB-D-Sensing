using System.Globalization;
using System.IO;
using System.Text;
using UnityEngine;

/// Per-frame verification logger for ArmAngleReceiver: whenever a new
/// stream frame is applied to the rig, samples the four arm bone segment
/// directions (world space) and appends a CSV line. A header line records
/// the rest directions captured BEFORE any packet, so offline analysis can
/// predict each frame's directions from the solved angles alone and
/// measure the actual rig error per frame.
public class ArmAngleLogger : MonoBehaviour
{
    public string outPath = "/home/luo/Desktop/New_SandBox/v1/kinematics/output/unity_frame_log.csv";
    public int logged;

    ArmAngleReceiver rx;
    Transform rua, rfa, rhand, lua, lfa, lhand;
    StreamWriter w;
    int lastLogged = int.MinValue;

    static Transform Find(string n)
    {
        foreach (var t in FindObjectsByType<Transform>(FindObjectsSortMode.None))
            if (t.name == n) return t;
        return null;
    }

    static string V(Vector3 v) =>
        v.x.ToString("G9", CultureInfo.InvariantCulture) + "," +
        v.y.ToString("G9", CultureInfo.InvariantCulture) + "," +
        v.z.ToString("G9", CultureInfo.InvariantCulture);

    Vector3 RUaDir() => (rfa.position - rua.position).normalized;
    Vector3 RFaDir() => (rhand.position - rfa.position).normalized;
    Vector3 LUaDir() => (lfa.position - lua.position).normalized;
    Vector3 LFaDir() => (lhand.position - lfa.position).normalized;

    void Start()
    {
        rx = FindFirstObjectByType<ArmAngleReceiver>();
        rua = Find("DEF-upper_arm.R"); rfa = Find("DEF-forearm.R"); rhand = Find("DEF-hand.R");
        lua = Find("DEF-upper_arm.L"); lfa = Find("DEF-forearm.L"); lhand = Find("DEF-hand.L");
        w = new StreamWriter(outPath, false) { AutoFlush = true };
        // rest directions before any packet is applied
        w.WriteLine("# rest," + V(RUaDir()) + "," + V(RFaDir()) + ","
                    + V(LUaDir()) + "," + V(LFaDir()));
        w.WriteLine("frame,rua_x,rua_y,rua_z,rfa_x,rfa_y,rfa_z,"
                    + "lua_x,lua_y,lua_z,lfa_x,lfa_y,lfa_z");
    }

    void LateUpdate()
    {
        if (rx == null || rx.lastFrame == lastLogged || rx.lastFrame < 0) return;
        lastLogged = rx.lastFrame;
        var sb = new StringBuilder();
        sb.Append(rx.lastFrame).Append(',').Append(V(RUaDir())).Append(',')
          .Append(V(RFaDir())).Append(',').Append(V(LUaDir())).Append(',')
          .Append(V(LFaDir()));
        w.WriteLine(sb.ToString());
        logged++;
    }

    void OnDestroy() { w?.Dispose(); }
}
