@echo off
REM ---------------------------------------------------------------
REM  Brings this folder up to date with GitHub.
REM
REM  What it does, in order:
REM    1. Clears stale git lock files
REM    2. Backs up your current src\build.py
REM    3. Discards local changes to src\build.py only
REM    4. Pulls the latest code from GitHub
REM
REM  Your Google verification files are untracked and are NOT touched.
REM  Your .gitignore change is NOT touched.
REM ---------------------------------------------------------------
setlocal
cd /d "%~dp0"

echo.
echo   ================================================
echo    Update from GitHub
echo   ================================================
echo.
echo   Incoming commits:
echo.
git log --oneline HEAD..origin/main
echo.
echo   This will DISCARD your local changes to:
echo.
echo       src\build.py
echo.
echo   A backup is saved first to:
echo.
echo       src\_superseded\build.py.before-merge
echo.
echo   Nothing else is discarded.
echo.
set /p ok=  Continue? [Y/N] 
if /i not "%ok%"=="Y" (
  echo.
  echo   Cancelled. Nothing changed.
  echo.
  pause
  exit /b 0
)

echo.
echo   [1/4] Clearing stale lock files...
if exist ".git\index.lock" del /f /q ".git\index.lock"
if exist ".git\objects\maintenance.lock" del /f /q ".git\objects\maintenance.lock"
for /r ".git\objects" %%F in (tmp_obj_*) do del /f /q "%%F" 2>nul

echo   [2/4] Backing up src\build.py...
if not exist "src\_superseded" mkdir "src\_superseded"
copy /y "src\build.py" "src\_superseded\build.py.before-merge" >nul

echo   [3/4] Discarding local changes to src\build.py...
git checkout -- src/build.py
if errorlevel 1 goto failed

echo   [4/4] Pulling from GitHub...
git pull --ff-only
if errorlevel 1 goto failed

echo.
echo   ================================================
echo    Done. You are now on the latest code.
echo   ================================================
echo.
echo   Now on:
git log --oneline -1
echo.
echo   Remaining local changes (these are yours, kept on purpose):
git status --short
echo.
echo   Tell Claude "pulled" and it will re-apply the
echo   Search Console changes to the new build script.
echo.
pause
exit /b 0

:failed
echo.
echo   SOMETHING WENT WRONG. Nothing further was done.
echo   Copy the message above and send it to Claude.
echo.
pause
exit /b 1
