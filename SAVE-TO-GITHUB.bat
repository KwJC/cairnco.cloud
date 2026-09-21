@echo off
REM ---------------------------------------------------------------
REM  Saves your work to GitHub.
REM
REM    Step 1  CLEAN     clears stale git lock files
REM    Step 2  REVIEW    shows exactly what is about to be saved
REM    Step 3  DESCRIBE  you type a short note about the work
REM    Step 4  SAVE      commits it and sends it to GitHub
REM
REM  Nothing leaves your machine until step 4, and it asks first.
REM
REM  This does NOT touch the live website. Publishing is a separate
REM  button: BUILD-AND-DEPLOY.bat
REM ---------------------------------------------------------------
setlocal
cd /d "%~dp0"

echo.
echo   ================================================
echo    Save your work to GitHub
echo   ================================================
echo.

echo   [1/4] Clearing stale lock files...
if exist ".git\index.lock" del /f /q ".git\index.lock"
if exist ".git\objects\maintenance.lock" del /f /q ".git\objects\maintenance.lock"
for /r ".git\objects" %%F in (tmp_obj_*) do del /f /q "%%F" 2>nul

echo.
echo   [2/4] This is what will be saved:
echo.
git status --short
echo.
echo       M = changed      ?? = brand new      D = deleted
echo.
echo   Built files in dist\ and your .env are never included.
echo.

for /f %%C in ('git status --porcelain ^| find /c /v ""') do set changes=%%C
if "%changes%"=="0" (
  echo   Nothing has changed since your last save. Nothing to do.
  echo.
  pause
  exit /b 0
)

set /p ok=  Save all of the above to GitHub? [Y/N] 
if /i not "%ok%"=="Y" (
  echo.
  echo   Cancelled. Nothing was saved, nothing was changed.
  echo.
  pause
  exit /b 0
)

echo.
echo   [3/4] Describe the work in a few words.
echo         Example: added the loading screen to the home page
echo.
set "msg="
set /p msg=  What did you do?  
if "%msg%"=="" set "msg=Update site"

echo.
echo   [4/4] Saving and sending to GitHub...
echo.
git add -A
if errorlevel 1 goto failed
git commit -m "%msg%"
if errorlevel 1 goto failed
git push
if errorlevel 1 goto pushfailed

echo.
echo   ================================================
echo    Saved to GitHub.
echo   ================================================
echo.
echo   Your work is now backed up and Emmanuel can see it.
echo.
git log --oneline -1
echo.
pause
exit /b 0

:pushfailed
echo.
echo   ================================================
echo    Saved on this computer, but NOT sent to GitHub
echo   ================================================
echo.
echo   Your work is safely committed locally, so nothing is lost.
echo   GitHub refused it, which almost always means someone else
echo   (Emmanuel) saved something first.
echo.
echo   To fix it:
echo.
echo       1. Run PULL-LATEST.bat
echo       2. Run this button again
echo.
pause
exit /b 1

:failed
echo.
echo   ================================================
echo    Something went wrong. Nothing was sent.
echo   ================================================
echo.
echo   Copy the red text above and show it to Claude.
echo.
pause
exit /b 1
