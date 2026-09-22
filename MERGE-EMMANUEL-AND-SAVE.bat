@echo off
REM ---------------------------------------------------------------
REM  ONE-TIME script. Run this once, then delete it.
REM
REM  Why it exists:
REM    Emmanuel pushed mobile-navigation fixes to GitHub while your
REM    own FAQ work was still only on this computer. Claude has
REM    already combined the two by hand, in src\, and checked the
REM    result. This script tells Git about that, safely.
REM
REM    Step 1  CLEAN    clears stale git lock files
REM    Step 2  FETCH    downloads Emmanuel's commit (changes nothing)
REM    Step 3  REVIEW   shows exactly what is about to be saved
REM    Step 4  SAVE     commits your work
REM    Step 5  JOIN     records Emmanuel's commit as merged
REM    Step 6  SEND     pushes everything to GitHub
REM
REM  DO NOT run PULL-LATEST.bat instead. It would throw away the
REM  FAQ wiring in src\build.py.
REM ---------------------------------------------------------------
setlocal
cd /d "%~dp0"

echo.
echo   ================================================
echo    Combine Emmanuel's work with yours
echo   ================================================
echo.

echo   [1/6] Clearing stale lock files...
if exist ".git\index.lock" del /f /q ".git\index.lock"
if exist ".git\objects\maintenance.lock" del /f /q ".git\objects\maintenance.lock"
for /r ".git\objects" %%F in (tmp_obj_*) do del /f /q "%%F" 2>nul

echo   [2/6] Fetching from GitHub...
git fetch origin
if errorlevel 1 goto failed

echo.
echo   Emmanuel's commit that is not yet on this computer:
echo.
git log --oneline HEAD..origin/main
echo.
echo   [3/6] This is what will be saved from your side:
echo.
git status --short
echo.
echo   ------------------------------------------------
echo   Claude has already put Emmanuel's changes into
echo   src\index.template.html and src\nav.js and
echo   rebuilt every page. Nothing of his is lost.
echo   ------------------------------------------------
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
echo   [4/6] Saving your work...
git add -A
if errorlevel 1 goto failed
git commit -m "FAQ page, contact cards, social links; merge Emmanuel's mobile nav fixes"
if errorlevel 1 goto failed

echo   [5/6] Recording Emmanuel's commit as merged...
git merge -s ours origin/main -m "Merge Emmanuel's mobile nav fixes (already applied by hand in src)"
if errorlevel 1 goto failed

echo   [6/6] Sending to GitHub...
git push
if errorlevel 1 goto failed

echo.
echo   ================================================
echo    Done. GitHub now has both sides.
echo   ================================================
echo.
git log --oneline -4
echo.
echo   Next: run BUILD-AND-DEPLOY.bat to publish the
echo   combined site, then delete this script.
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
