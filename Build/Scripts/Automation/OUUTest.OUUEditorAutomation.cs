// Copyright (c) 2024 Jonas Reich

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Gauntlet;
using System.Text.Json;

namespace OUUTest
{
	public class OUUTestConfig : UE.AutomationTestConfig
	{
		public static OUUTestConfig CopyFromBase(UE.AutomationTestConfig _Base)
		{
			// #HACK but the only way I found that works without engine mods.
			var s = JsonSerializer.Serialize(_Base);
			return JsonSerializer.Deserialize<OUUTestConfig>(s);
		}

		public override void ApplyToConfig(UnrealAppConfig AppConfig, UnrealSessionRole ConfigRole, IEnumerable<UnrealSessionRole> OtherRoles)
		{
			base.ApplyToConfig(AppConfig, ConfigRole, OtherRoles);

			// Always use the specified load map for tests.
			// Epic only sets it for Servers.
			AppConfig.CommandLineParams.GameMap = Map;
		}
	}

	// Modelled after UE.EditorAutomation
	public class OUUEditorAutomation : UE.EditorAutomation
	{
		public OUUEditorAutomation(UnrealTestContext InContext) : base(InContext)
		{
		}

		public override UE.AutomationTestConfig GetConfiguration()
		{
			UE.AutomationTestConfig BaseConfig = base.GetConfiguration();
			OUUTestConfig TestConfigResult = OUUTestConfig.CopyFromBase(BaseConfig);

			TestConfigResult.Map = "/OpenUnrealUtilities/Runtime/EmptyWorld";

			UnrealTestRole EditorRole = TestConfigResult.RequireRole(UnrealTargetRole.Editor);
			EditorRole.CommandLineParams.AddRawCommandline("-NoWatchdog -stdout -FORCELOGFLUSH -CrashForUAT -log");

			return TestConfigResult;
		}
	}
}
