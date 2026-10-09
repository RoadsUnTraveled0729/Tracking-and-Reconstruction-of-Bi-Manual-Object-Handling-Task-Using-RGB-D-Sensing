using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

// Unattended play-mode driver for the offline evaluation captures
// (eval/unity_check/): lets a script outside Unity enter and leave play
// mode, and quit the editor, without a human pressing Play.
//
// Everything is driven by flag files so the outside half stays a plain
// shell/Python step and nothing here depends on the MCP bridge:
//
//   /tmp/r5_autoplay_on     present -> enter play mode once the editor is
//                           idle (absent -> this file does nothing at all,
//                           so ordinary editor sessions are unaffected)
//   /tmp/r5_autoplay_stop   present -> leave play mode
//   /tmp/r5_autoplay_quit   present -> quit the editor after play mode ends
//   /tmp/r5_autoplay_state  written here ~1/s: the editor's live state, so
//                           the outside half can wait on facts instead of
//                           sleeping a guessed number of seconds
//
// Entering play mode reloads the domain; [InitializeOnLoad] re-runs and
// re-registers the tick, so the state file keeps flowing across the reload.
[InitializeOnLoad]
internal static class EvalPlayBootstrap
{
    const string OnFlag = "/tmp/r5_autoplay_on";
    const string StopFlag = "/tmp/r5_autoplay_stop";
    const string QuitFlag = "/tmp/r5_autoplay_quit";
    const string StateFile = "/tmp/r5_autoplay_state";
    const string ScenePath = "Assets/Scenes/rig.unity";

    // The editor is still importing/compiling for a while after load; do
    // not touch play mode before it has settled.
    const double SettleSeconds = 20.0;

    static double lastState;

    static EvalPlayBootstrap()
    {
        EditorApplication.update += Tick;
    }

    static bool Busy()
    {
        return EditorApplication.isCompiling || EditorApplication.isUpdating
               || EditorApplication.isPlayingOrWillChangePlaymode != EditorApplication.isPlaying;
    }

    static void WriteState()
    {
        if (EditorApplication.timeSinceStartup - lastState < 1.0) return;
        lastState = EditorApplication.timeSinceStartup;
        var scene = EditorSceneManager.GetActiveScene();
        string s = "{"
            + $"\"uptime_s\": {EditorApplication.timeSinceStartup:F1}, "
            + $"\"playing\": {(EditorApplication.isPlaying ? "true" : "false")}, "
            + $"\"changing\": {(EditorApplication.isPlayingOrWillChangePlaymode != EditorApplication.isPlaying ? "true" : "false")}, "
            + $"\"compiling\": {(EditorApplication.isCompiling ? "true" : "false")}, "
            + $"\"updating\": {(EditorApplication.isUpdating ? "true" : "false")}, "
            + $"\"scene\": \"{scene.path}\", "
            + $"\"scene_dirty\": {(scene.isDirty ? "true" : "false")}"
            + "}";
        try { File.WriteAllText(StateFile, s); } catch (IOException) { }
    }

    static void Tick()
    {
        if (!File.Exists(OnFlag)) return;
        WriteState();
        if (Busy()) return;

        if (EditorApplication.isPlaying)
        {
            if (File.Exists(StopFlag))
            {
                Debug.Log("[EvalPlayBootstrap] stop flag -> leaving play mode");
                EditorApplication.isPlaying = false;
            }
            return;
        }

        if (File.Exists(StopFlag))
        {
            if (File.Exists(QuitFlag))
            {
                Debug.Log("[EvalPlayBootstrap] quit flag -> exiting editor");
                EditorApplication.Exit(0);
            }
            return;
        }

        if (EditorApplication.timeSinceStartup < SettleSeconds) return;

        // The capture needs the rig scene. Only switch when the open scene
        // is a different, clean one — never discard unsaved work.
        var scene = EditorSceneManager.GetActiveScene();
        if (scene.path != ScenePath)
        {
            if (scene.isDirty)
            {
                Debug.LogWarning("[EvalPlayBootstrap] active scene is dirty and is "
                                 + $"not {ScenePath}; not switching, not playing");
                return;
            }
            Debug.Log($"[EvalPlayBootstrap] opening {ScenePath}");
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            return;   // resume next tick with the scene loaded
        }

        Debug.Log("[EvalPlayBootstrap] entering play mode");
        EditorApplication.isPlaying = true;
    }
}
