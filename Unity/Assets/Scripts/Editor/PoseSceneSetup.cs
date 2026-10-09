// One-click scene setup: Thesis > Setup Pose Scene
// Places the first model found in Assets/Models at the world origin and
// creates a PoseStreamReceiver object next to it.

using UnityEditor;
using UnityEngine;

public static class PoseSceneSetup
{
    [MenuItem("Thesis/Setup Pose Scene")]
    public static void Setup()
    {
        // Character model at the origin
        var guids = AssetDatabase.FindAssets("t:Model", new[] { "Assets/Models" });
        if (guids.Length == 0)
        {
            Debug.LogError("[Setup] No model found under Assets/Models");
        }
        else
        {
            var path = AssetDatabase.GUIDToAssetPath(guids[0]);
            var asset = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            var existing = GameObject.Find(asset.name);
            if (existing == null)
            {
                var instance = (GameObject)PrefabUtility.InstantiatePrefab(asset);
                instance.transform.position = Vector3.zero;
                instance.transform.rotation = Quaternion.identity;
                Undo.RegisterCreatedObjectUndo(instance, "Place character");
                Debug.Log($"[Setup] Placed {asset.name} at origin (from {path})");
            }
            else
            {
                existing.transform.position = Vector3.zero;
                Debug.Log($"[Setup] {asset.name} already in scene; moved to origin");
            }
        }

        // Landmark stream receiver
        if (Object.FindFirstObjectByType<PoseStreamReceiver>() == null)
        {
            var go = new GameObject("PoseStreamReceiver");
            go.AddComponent<PoseStreamReceiver>();
            Undo.RegisterCreatedObjectUndo(go, "Create PoseStreamReceiver");
            Debug.Log("[Setup] Created PoseStreamReceiver (shared memory, /dev/shm/pose_stream)");
        }

        EditorSceneManagerMarkDirty();
    }

    static void EditorSceneManagerMarkDirty()
    {
        var scene = UnityEditor.SceneManagement.EditorSceneManager.GetActiveScene();
        UnityEditor.SceneManagement.EditorSceneManager.MarkSceneDirty(scene);
    }
}
