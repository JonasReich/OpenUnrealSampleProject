@ECHO off

REM This script makes the following assumptions:
REM - git-p4j is installed
REM - current user is Jonas Reich
REM - commandline has authenticated access to TQ2 Perforce repo
REM - checkin messages should be manually groomed with interactive rebase after the import

SET "GIT_BRANCH=p4/tq2-code"
SET "GIT_BRANCH_BACKUP=%GIT_BRANCH%-backup"

PUSHD %~dp0

CALL :UPDATE_SUBMODULE Plugins\OpenUnrealUtilities
REM if this failed (e.g. because connection to p4 failed), we should not try again with Json Asset lib
IF %ERRORLEVEL%==1 ( EXIT /B 1 )

CALL :UPDATE_SUBMODULE Plugins\OUUJsonDataAssets

EXIT /B %ERRORLEVEL%


:UPDATE_SUBMODULE
REM change working directory to first param of subroutine
PUSHD %~dp0%1

git config --replace-all user.name "Jonas Reich"
REM all updates originating from TQ2 should be signed by my Grimlore work mail
git config --replace-all user.email jreich@grimloregames.com

git checkout %GIT_BRANCH%
git checkout -b %GIT_BRANCH_BACKUP%

git p4j %GIT_BRANCH%
SET P4J_STATUS=%ERRORLEVEL%

git checkout %GIT_BRANCH%
git rebase -f %GIT_BRANCH_BACKUP%
git branch --delete %GIT_BRANCH_BACKUP%

POPD

EXIT /B %P4J_STATUS%
