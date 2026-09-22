@echo off
REM ---------------------------------------------------------------
REM  Look at the site on this computer before it goes live.
REM
REM  Double-clicking dist\index.html does NOT work. Every link in
REM  the site starts with "/", which means "the top of the site".
REM  A browser reading straight off the disk has no site, so it
REM  treats "/" as the top of your C: drive and every link dies.
REM
REM  Serving the folder over http fixes that, and shows you exactly
REM  what Cloudflare will serve.
REM ---------------------------------------------------------------
setlocal
cd /d "%~dp0.."

if not exist "dist\index.html" (
  echo.
  echo   ================================================
  echo    There is no built site in dist\ yet
  echo   ================================================
  echo.
  echo   Run BUILD-AND-DEPLOY.bat first. When it asks
  echo   "Publish now?" answer N. That builds the pages
  echo   without touching the live site.
  echo.
  pause
  exit /b 1
)

echo.
echo   ================================================
echo    Preview cairnco.cloud on this computer
echo   ================================================
echo.
echo   Starting a small web server on dist\ ...
echo.

start "CairnCo preview server - CLOSE THIS WINDOW TO STOP" /d "%~dp0..\dist" cmd /k python -m http.server 8000

timeout /t 2 /nobreak >nul
start "" http://localhost:8000

echo   The site is now at:
echo.
echo       http://localhost:8000
echo.
echo   Your browser should have opened it. If it did not,
echo   type that address in yourself.
echo.
echo   A second window called "CairnCo preview server" is
echo   what is running it. CLOSE THAT WINDOW when you are
echo   finished, or the address stays occupied.
echo.
echo   Two things that are normal, not faults:
echo.
echo     - The first page takes about 6 seconds to appear.
echo       That is the loading screen.
echo     - Click to another page and back and you get the
echo       shorter 4 second version instead.
echo.
pause
exit /b 0
