@ECHO off

REM This script makes the following assumptions:
REM - current user is Jonas Reich

PUSHD %~dp0

SET "USER_NAME=Jonas Reich"
SET USER_MAIL=jreich@grimloregames.com

CALL :UPDATE_SUBMODULE Plugins\OpenUnrealUtilities
CALL :UPDATE_SUBMODULE Plugins\OUUJsonDataAssets
CALL :UPDATE_SUBMODULE Plugins\OUUTags
CALL :UPDATE_SUBMODULE OpenUnrealAutomationTools

EXIT /B %ERRORLEVEL%


:UPDATE_SUBMODULE
REM change working directory to first param of subroutine
PUSHD %~dp0%1

git config --replace-all user.name "%USER_NAME%"
git config --replace-all user.email %USER_MAIL%
echo Set user to %USER_NAME% ^(%USER_MAIL%^) for %~dp0%1

POPD
