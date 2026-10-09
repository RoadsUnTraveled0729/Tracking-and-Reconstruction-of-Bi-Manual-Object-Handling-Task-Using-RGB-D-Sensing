using System.IO;
using System.Globalization;
using UnityEngine;

// Capture-only instrumentation. Kinematic axes precede authored bone rest offsets.
public static class DefenseAxes
{
    static LineRenderer[] lines;
    static StreamWriter log;
    static int sourceFrame;
    static float sourceTime;
    static Matrix4x4[] frames;
    static Matrix4x4[] bones;
    static readonly string[] names = {"Pelvis_parallel_L24", "Shoulder_R", "Elbow_R", "Shoulder_L", "Elbow_L"};
    static readonly Color[] colors = {new Color(1f,64f/255f,64f/255f), new Color(64f/255f,224f/255f,112f/255f), new Color(64f/255f,140f/255f,1f)};
    public static void Update(int frame, float time, Transform hip, Transform shoulderR, Transform elbowR,
        Transform shoulderL, Transform elbowL, Quaternion root, Quaternion armR, Quaternion armL)
    {
        if (lines == null)
        {
            lines = new LineRenderer[15];
            var shader = Shader.Find("Defense/AxesOverlay");
            if (shader == null) shader = Shader.Find("Sprites/Default");
            for (int i=0;i<15;i++)
            {
                lines[i] = new GameObject("DefenseAxis_"+i).AddComponent<LineRenderer>();
                lines[i].material = new Material(shader);
                lines[i].material.color = colors[i%3];
                lines[i].startColor = lines[i].endColor = colors[i%3];
                lines[i].startWidth = lines[i].endWidth = 0.004f;
                lines[i].positionCount = 2;
                lines[i].useWorldSpace = true;
            }
            log = new StreamWriter("/tmp/defense_axes_capture/runtime/axes_matrices.csv", false);
            log.WriteLine("frame,time_s,name,origin_x,origin_y,origin_z,r00,r01,r02,r10,r11,r12,r20,r21,r22,b00,b01,b02,b10,b11,b12,b20,b21,b22,camera_world_4x4,projection_4x4,width,height");
        }
        sourceFrame=frame;sourceTime=time;
        Transform[] joints={hip,shoulderR,elbowR,shoulderL,elbowL};
        Quaternion[] rotations={root,root,armR,root,armL};
        frames=new Matrix4x4[5];bones=new Matrix4x4[5];
        for(int j=0;j<5;j++)
        {
            frames[j]=Matrix4x4.TRS(joints[j].position,rotations[j],Vector3.one);
            bones[j]=Matrix4x4.Rotate(joints[j].rotation);
            for(int a=0;a<3;a++)
            {
                Vector3 v=a==0?Vector3.right:a==1?Vector3.up:Vector3.forward;
                lines[j*3+a].SetPosition(0,joints[j].position);
                lines[j*3+a].SetPosition(1,joints[j].position+rotations[j]*v*0.12f);
            }
        }
    }
    static string N(float n) { return n.ToString("R",CultureInfo.InvariantCulture); }
    static string Matrix(Matrix4x4 m) { string s="";for(int r=0;r<4;r++)for(int c=0;c<4;c++)s+=(s==""?"":";")+N(m[r,c]);return s; }
    public static void Record(Camera camera,int frame,int width,int height)
    {
        if(log==null||frame!=sourceFrame)return;
        for(int j=0;j<5;j++)
        {
            var m=frames[j];string s=frame+","+N(sourceTime)+","+names[j]+","+N(m.m03)+","+N(m.m13)+","+N(m.m23);
            for(int r=0;r<3;r++)for(int c=0;c<3;c++)s+=","+N(m[r,c]);
            for(int r=0;r<3;r++)for(int c=0;c<3;c++)s+=","+N(bones[j][r,c]);
            log.WriteLine(s+",\""+Matrix(camera.transform.localToWorldMatrix)+"\",\""+Matrix(camera.projectionMatrix)+"\","+width+","+height);
        }
        log.Flush();
    }
}
