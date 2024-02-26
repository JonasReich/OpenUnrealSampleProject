using Gauntlet;
using System;
using UnrealBuildTool;
using System.Linq;

namespace OUUTest
{
    public class MultiplayerTestConfig : UnrealTestConfiguration
    {

    }

    /// <summary>
    /// A simple Gauntlet test using the OUU test config
    /// </summary>
    public class MultiplayerTest : Gauntlet.UnrealTestNode<OUUTest.MultiplayerTestConfig>
    {
        public MultiplayerTest(Gauntlet.UnrealTestContext InContext)
            : base(InContext)
        {
        }

        public override MultiplayerTestConfig GetConfiguration()
        {
            var Config = base.GetConfiguration();

            string ControllerName = "OUUMultiplayerTestController";
            int NumClients = 2;
            var AllRoles = Config.RequireRoles(UnrealTargetRole.EditorGame, UnrealTargetPlatform.Win64, NumClients + 1).ToList();
            var ServerRole = AllRoles[0];

            var Server = Config.RequireRole(UnrealTargetRole.EditorGame, UnrealTargetPlatform.Win64);
            Server.Controllers.Add(ControllerName);
            Server.CommandLineParams.Add("OUUMPTestRole", "Server");
            Server.MapOverride = "FTest_Multiplayer";

            for (int ClientIdx = 0; ClientIdx < NumClients; ClientIdx = ClientIdx + 1)
            {
                var Role = AllRoles[ClientIdx + 1];
                Role.Controllers.Add(ControllerName);
                Role.CommandLineParams.Add("OUUMPTestRole", "Client");
                Role.CommandLineParams.Add("ClientIdx", ClientIdx);
            }

            Config.MaxDuration = 5 * 600; // 5 minutes
            return Config;
        }
    }
}
