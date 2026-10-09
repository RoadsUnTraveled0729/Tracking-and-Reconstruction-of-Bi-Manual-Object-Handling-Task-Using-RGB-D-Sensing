using System;
using System.Threading.Tasks;
using MCPForUnity.Editor.Services;
using MCPForUnity.Editor.Services.Transport;
using UnityEditor;

// Starts the MCP-for-Unity local HTTP server and connects the bridge on
// editor load, replacing the manual Start Server click in the MCP window.
// Calls the same public services as the window button. Idempotent: does
// nothing when the bridge is already running or the server is reachable.
[InitializeOnLoad]
internal static class McpAutoStart
{
    // SessionState survives domain reloads but resets per editor process,
    // so this runs once per launch; the package's own HttpBridgeReloadHandler
    // covers resume-after-reload.
    private const string SessionKey = "McpAutoStart.Initialized";

    static McpAutoStart()
    {
        if (UnityEngine.Application.isBatchMode) return;
        if (SessionState.GetBool(SessionKey, false)) return;
        SessionState.SetBool(SessionKey, true);

        EditorApplication.delayCall += () =>
        {
            // Keep the package's built-in auto-start enabled as a second path.
            EditorPrefs.SetBool("MCPForUnity.AutoStartOnLoad", true);
            _ = StartAsync();
        };
    }

    private static async Task StartAsync()
    {
        try
        {
            if (MCPServiceLocator.TransportManager.IsRunning(TransportMode.Http)) return;

            var server = MCPServiceLocator.Server;
            if (!server.IsLocalHttpServerReachable())
            {
                if (!server.StartLocalHttpServer(quiet: true))
                {
                    UnityEngine.Debug.LogWarning("McpAutoStart: local HTTP server failed to launch");
                    return;
                }
            }

            double start = EditorApplication.timeSinceStartup;
            const double capSeconds = 300;
            while (EditorApplication.timeSinceStartup - start < capSeconds)
            {
                if (MCPServiceLocator.TransportManager.IsRunning(TransportMode.Http)) return;
                if (server.IsLocalHttpServerReachable())
                {
                    if (await MCPServiceLocator.Bridge.StartAsync())
                    {
                        UnityEngine.Debug.Log("McpAutoStart: MCP server up, session connected");
                        return;
                    }
                }
                if (!server.IsManagedServerLaunchProcessAlive()
                    && EditorApplication.timeSinceStartup - start > 5)
                {
                    server.LogLocalHttpServerLaunchFailure();
                    return;
                }
                await Task.Delay(500);
            }
            UnityEngine.Debug.LogWarning("McpAutoStart: timed out waiting for MCP server");
        }
        catch (Exception e)
        {
            UnityEngine.Debug.LogWarning($"McpAutoStart: {e.Message}");
        }
    }
}
