@echo off
REM ---------------------------------------------------------------
REM  Builds the website and publishes it to cairnco.cloud
REM
REM    Step 1  BUILD   turns src\ into finished pages in dist\
REM    Step 2  CHECK   confirms the key files came out
REM    Step 3  DEPLOY  uploads dist\ to Cloudflare (goes live)
REM
REM  Nothing reaches the internet until step 3, and step 3 asks first.
REM ---------------------------------------------------------------
setlocal
cd /d "%~dp0"

echo.
echo   ================================================
echo    Build and deploy cairnco.cloud
echo   ================================================
echo.

echo   [1/3] Building...
echo.
python src\build.py
if errorlevel 1 goto buildfailed

echo.
echo   [2/3] Checking what was produced...
echo.
set missing=0
call :check "dist\index.html"
call :check "dist\contact\index.html"
call :check "dist\zh\index.html"
call :check "dist\en\index.html"
call :check "dist\googlebac108922c07543e.html"
call :check "dist\favicon.ico"
call :check "dist\favicon-32.png"
call :check "dist\robots.txt"
call :check "dist\sitemap.xml"
echo.
if %missing% gtr 0 goto checkfailed
echo   All expected files present.
echo.

echo   ================================================
echo    Ready to publish. This changes the LIVE site.
echo   ================================================
echo.
set /p ok=  Publish now? [Y/N] 
if /i not "%ok%"=="Y" (
  echo.
  echo   Not published. The build is done and sitting in dist\
  echo   You can run this again later to publish it.
  echo.
  pause
  exit /b 0
)

echo.
echo   [3/3] Publishing to Cloudflare...
echo.
call npx.cmd wrangler deploy
if errorlevel 1 goto deployfailed

echo.
echo   ================================================
echo    Live. Tell Claude "deployed".
echo   ================================================
echo.
pause
exit /b 0

:check
if exist %1 (
  echo       OK       %~1
) else (
  echo       MISSING  %~1
  set /a missing+=1
)
exit /b 0

:buildfailed
echo.
echo   BUILD FAILED. Nothing was published.
echo   Copy the message above and send it to Claude.
echo.
pause
exit /b 1

:checkfailed
echo.
echo   Expected files are missing, so publishing was skipped
echo   on purpose. Send the list above to Claude.
echo.
pause
exit /b 1

:deployfailed
echo.
echo   PUBLISH FAILED. The live site is unchanged.
echo   Copy the message above and send it to Claude.
echo.
pause
exit /b 1
