@echo off
REM ---------------------------------------------------------------
REM  Brings Emmanuel's latest work DOWN from GitHub.
REM
REM    Step 1  CLEAN    clears stale git lock files
REM    Step 2  CHECK    refuses to run if you have unsaved work
REM    Step 3  FETCH    downloads what is on GitHub (changes nothing)
REM    Step 4  REVIEW   shows what is coming, and asks
REM    Step 5  APPLY    updates your files
REM
REM  This is the DOWNLOAD button. SAVE-TO-GITHUB.bat is the upload
REM  button. They go in opposite directions.
REM
REM  Rewritten 22 Sep 2026. The old version deleted your changes to
REM  src\build.py before pulling, which would have cost the whole
REM  FAQ page. This version never discards anything: if you have
REM  unsaved work it stops and sends you to the save button first.
REM ---------------------------------------------------------------
setlocal
cd /d "%~dp0.."

echo.
echo   ================================================
echo    Get the latest from GitHub
echo   ================================================
echo.

echo   [1/5] Clearing stale lock files...
if exist ".git\index.lock" del /f /q ".git\index.lock"
if exist ".git\objects\maintenance.lock" del /f /q ".git\objects\maintenance.lock"
for /r ".git\objects" %%F in (tmp_obj_*) do del /f /q "%%F" 2>nul

echo   [2/5] Checking for unsaved work...
for /f %%C in ('git status --porcelain ^| find /c /v ""') do set changes=%%C
if not "%changes%"=="0" goto unsaved
echo         Nothing unsaved. Safe to continue.

echo   [3/5] Fetching from GitHub...
git fetch origin
if errorlevel 1 goto failed

echo.
echo   [4/5] What is waiting for you:
echo.
git log --oneline HEAD..origin/main
for /f %%C in ('git rev-list --count HEAD..origin/main') do set incoming=%%C
if "%incoming%"=="0" goto uptodate
echo.
echo   Files that would change:
echo.
git diff --stat HEAD origin/main
echo.
set /p ok=  Bring these down? [Y/N] 
if /i not "%ok%"=="Y" (
  echo.
  echo   Cancelled. Nothing changed.
  echo.
  pause
  exit /b 0
)

echo.
echo   [5/5] Updating your files...
git merge --ff-only origin/main
if errorlevel 1 goto split

echo.
echo   ================================================
echo    Done. You are on the latest code.
echo   ================================================
echo.
git log --oneline -1
echo.
echo   The SOURCE files changed, but the built pages did
echo   not. Run BUILD-AND-DEPLOY.bat to rebuild them.
echo.
pause
exit /b 0

:uptodate
echo.
echo   ================================================
echo    Already up to date. Nothing to bring down.
echo   ================================================
echo.
pause
exit /b 0

:unsaved
echo.
echo   ================================================
echo    STOPPED. You have unsaved work.
echo   ================================================
echo.
git status --short
echo.
echo   Nothing has been changed. Downloading now could
echo   overwrite the files listed above.
echo.
echo   Do this instead:
echo.
echo       1. Run SAVE-TO-GITHUB.bat to save your work
echo       2. Then run this button again
echo.
echo   If the save is refused because Emmanuel pushed
echo   something first, stop there and tell Claude.
echo.
pause
exit /b 1

:split
echo.
echo   ================================================
echo    STOPPED. Your history and GitHub's have split
echo   ================================================
echo.
echo   Nothing was changed. You and Emmanuel have both
echo   saved work that the other does not have, which
echo   needs a proper merge. That is not something to
echo   do blind.
echo.
echo   Tell Claude: "pull stopped, histories have split"
echo.
pause
exit /b 1

:failed
echo.
echo   SOMETHING WENT WRONG. Nothing was changed.
echo   Copy the message above and show it to Claude.
echo.
pause
exit /b 1
