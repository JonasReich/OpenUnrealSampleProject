@ECHO off

REM This script makes the following assumptions:
REM - git-p4j is installed
REM - current user is Jonas Reich
REM - commandline has authenticated access to TQ2 Perforce repo
REM - checkin messages should be manually groomed with interactive rebase after the import


PUSHD %~dp0

CALL :UPDATE_SUBMODULE Plugins\OpenUnrealUtilities p4/tq2-code
IF %ERRORLEVEL%==1 ( EXIT /B 1 )

CALL :UPDATE_SUBMODULE Plugins\OUUJsonDataAssets p4/tq2-code
IF %ERRORLEVEL%==1 ( EXIT /B 1 )

CALL :UPDATE_SUBMODULE Plugins\OUUTags p4/tq2-code
IF %ERRORLEVEL%==1 ( EXIT /B 1 )

CALL :UPDATE_SUBMODULE OpenUnrealAutomationTools p4/tq2-main

EXIT /B %ERRORLEVEL%


:UPDATE_SUBMODULE

SET "REPO_RELATIVE_PATH=%1"
SET "GIT_BRANCH=%2"
SET "GIT_BRANCH_BACKUP=%GIT_BRANCH%-backup"

ECHO --------------------------------------------------------------
ECHO UPDATING SUBMODULE %REPO_RELATIVE_PATH%
ECHO --------------------------------------------------------------

PUSHD %~dp0%REPO_RELATIVE_PATH%

REM weird bash stuff: get name of the repo directory
for %%F in ("%REPO_RELATIVE_PATH%") do set "REPO_NAME=%%~nxF"
ECHO REPO_NAME = %REPO_NAME%

git config --replace-all user.name "Jonas Reich"
REM all updates originating from TQ2 should be signed by my Grimlore work mail
git config --replace-all user.email jreich@grimloregames.com

git checkout %GIT_BRANCH%
git checkout -b %GIT_BRANCH_BACKUP%

ECHO git p4j %GIT_BRANCH% --repo-name %REPO_NAME%
git p4j %GIT_BRANCH% --repo-name %REPO_NAME%
SET P4J_STATUS=%ERRORLEVEL%

git checkout %GIT_BRANCH%
:: Do NOT rebase to sign commits anymore. This messes too much with auto-created merge commits and we usually have to do an interactive rebase to adjust imported messages anyways.
:: git rebase -f %GIT_BRANCH_BACKUP%
git branch --delete %GIT_BRANCH_BACKUP%

POPD

EXIT /B %P4J_STATUS%
