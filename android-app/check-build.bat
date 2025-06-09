@echo off
echo === Checking Android Build Prerequisites ===
echo.

echo Checking Java installation...
java -version 2>nul
if %errorlevel% neq 0 (
    echo [X] Java is NOT installed
    echo     Download from: https://www.oracle.com/java/technologies/downloads/
    echo.
    echo === Quick Alternative: Online APK Builders ===
    echo.
    echo 1. AppsGeyser.com - Free, no installation needed
    echo    - Go to https://appsgeyser.com
    echo    - Choose "Website" template  
    echo    - Enter: https://independent-dealer-prospector.streamlit.app/
    echo    - Download APK
    echo.
    echo 2. WebIntoApp.com - Free tier available
    echo    - Go to https://webintoapp.com
    echo    - Enter your Streamlit URL
    echo    - Customize and download
    echo.
    echo See QUICK_BUILD_GUIDE.md for more details
) else (
    echo [OK] Java is installed
    echo.
    echo You can try building with: .\gradlew.bat assembleDebug
    echo Note: First build will download dependencies
)

pause 