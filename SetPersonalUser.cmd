@ECHO off

REM This script makes the following assumptions:
REM - current user is Jonas Reich

PUSHD %~dp0

CALL :UPDATE_SUBMODULE Plugins\OpenUnrealUtilities
CALL :UPDATE_SUBMODULE Plugins\OUUJsonDataAssets
CALL :UPDATE_SUBMODULE OpenUnrealAutomationTools

EXIT /B %ERRORLEVEL%


:UPDATE_SUBMODULE
REM change working directory to first param of subroutine
PUSHD %~dp0%1

git config --replace-all user.name "Jonas Reich"
git config --replace-all user.email mail@jonasreich.de

POPD
