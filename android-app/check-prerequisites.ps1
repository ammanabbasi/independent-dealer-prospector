Write-Host "=== Checking Android Build Prerequisites ===" -ForegroundColor Cyan
Write-Host ""

# Check Java
Write-Host "Checking Java installation..." -ForegroundColor Yellow
$javaInstalled = $false
try {
    $javaVersion = java -version 2>&1 | Select-String "version"
    if ($javaVersion) {
        Write-Host "✓ Java is installed: $javaVersion" -ForegroundColor Green
        $javaInstalled = $true
    }
} catch {
    Write-Host "✗ Java is NOT installed" -ForegroundColor Red
    Write-Host "  Download from: https://www.oracle.com/java/technologies/downloads/#java11-windows" -ForegroundColor Gray
}

Write-Host ""

# Check JAVA_HOME
Write-Host "Checking JAVA_HOME environment variable..." -ForegroundColor Yellow
if ($env:JAVA_HOME) {
    Write-Host "✓ JAVA_HOME is set to: $env:JAVA_HOME" -ForegroundColor Green
} else {
    Write-Host "✗ JAVA_HOME is NOT set" -ForegroundColor Red
    Write-Host "  This may cause build issues" -ForegroundColor Gray
}

Write-Host ""

# Check Android SDK
Write-Host "Checking Android SDK..." -ForegroundColor Yellow
if ($env:ANDROID_HOME -or $env:ANDROID_SDK_ROOT) {
    $sdkPath = if ($env:ANDROID_HOME) { $env:ANDROID_HOME } else { $env:ANDROID_SDK_ROOT }
    Write-Host "✓ Android SDK found at: $sdkPath" -ForegroundColor Green
} else {
    Write-Host "✗ Android SDK is NOT installed or configured" -ForegroundColor Red
    Write-Host "  Install Android Studio from: https://developer.android.com/studio" -ForegroundColor Gray
}

Write-Host ""

# Check if local.properties exists
Write-Host "Checking local.properties..." -ForegroundColor Yellow
if (Test-Path "local.properties") {
    Write-Host "✓ local.properties exists" -ForegroundColor Green
} else {
    Write-Host "⚠ local.properties not found" -ForegroundColor Yellow
    Write-Host "  This file will be created automatically by Android Studio" -ForegroundColor Gray
    Write-Host "  Or create it manually using local.properties.template" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan

if (-not $javaInstalled) {
    Write-Host "❌ Cannot build: Java is required" -ForegroundColor Red
    Write-Host ""
    Write-Host "🚀 Quick Alternative: Use an online APK builder service" -ForegroundColor Cyan
    Write-Host "   - AppsGeyser.com (free, no installation needed)" -ForegroundColor White
    Write-Host "   - WebIntoApp.com (free tier available)" -ForegroundColor White
} else {
    Write-Host "✅ You can try building with: .\gradlew.bat assembleDebug" -ForegroundColor Green
    Write-Host "   Note: First build will download dependencies (may take time)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "See QUICK_BUILD_GUIDE.md for detailed instructions" -ForegroundColor Yellow 