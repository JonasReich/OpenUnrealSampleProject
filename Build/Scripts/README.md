Copy the following content into a `OUU.Automation.csproj.props` file next to this README,
and adjust the value of EngineDir to your local UE installation.
We can probably automate this at some point...

```xml
<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="Current" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
	<PropertyGroup>
		<EngineDir Condition="'$(EngineDir)' == ''">D:\EpicGames\UE_5.2\Engine</EngineDir>
	</PropertyGroup>
</Project>
```
