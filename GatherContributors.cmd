@ECHO off

REM This script makes the following assumptions:
REM - "git thanks" is supported
PUSHD %~dp0

CALL :GIT_THANKS Plugins\OpenUnrealUtilities
CALL :GIT_THANKS Plugins\OUUJsonDataAssets
CALL :GIT_THANKS Plugins\OUUTags
CALL :GIT_THANKS OpenUnrealAutomationTools
EXIT /B 0

:GIT_THANKS
pushd %1
echo -------------------
echo %1
echo -------------------
git shortlog -s --group=author --group=trailer:co-authored-by
popd
EXIT /B 0
