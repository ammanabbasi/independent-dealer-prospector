# Dealer Finder Android App

This is an Android WebView wrapper for the Dealer Finder Streamlit web application.

## Prerequisites

To build this app, you need:

1. **Java Development Kit (JDK) 11 or higher**
   - Download from: https://www.oracle.com/java/technologies/downloads/
   - Or use OpenJDK: https://adoptium.net/

2. **Android Studio (Recommended)**
   - Download from: https://developer.android.com/studio
   - This will install Android SDK and all necessary tools

   **OR**

   **Android Command Line Tools**
   - Download from: https://developer.android.com/studio#command-tools

## Building the APK

### Method 1: Using Android Studio (Easiest)

1. Open Android Studio
2. Click "Open" and select the `android-app` folder
3. Wait for the project to sync (this may take a few minutes)
4. Click on "Build" → "Build Bundle(s) / APK(s)" → "Build APK(s)"
5. Once built, click "locate" in the notification to find your APK
6. The APK will be at: `app/build/outputs/apk/debug/app-debug.apk`

### Method 2: Using Command Line

1. Open a terminal/command prompt in the `android-app` directory
2. Run the following commands:

```bash
# On Windows
gradlew.bat assembleDebug

# On Mac/Linux
chmod +x gradlew
./gradlew assembleDebug
```

3. The APK will be generated at: `app/build/outputs/apk/debug/app-debug.apk`

## Installing the APK on Your Android Device

### Method 1: Direct Transfer

1. Connect your Android device to your computer via USB
2. Enable "Developer Options" on your Android device:
   - Go to Settings → About Phone
   - Tap "Build Number" 7 times
   - Go back to Settings → Developer Options
   - Enable "USB Debugging"
3. Copy the APK file to your device
4. Use a file manager on your device to locate and install the APK
5. You may need to enable "Install from Unknown Sources" in your device settings

### Method 2: Using ADB (Android Debug Bridge)

1. Enable USB Debugging on your device (see above)
2. Connect your device via USB
3. Run: `adb install app/build/outputs/apk/debug/app-debug.apk`

### Method 3: Using Email or Cloud Storage

1. Email the APK to yourself or upload it to Google Drive/Dropbox
2. Open the email/file on your Android device
3. Download and install the APK
4. You may need to enable "Install from Unknown Sources"

## Building a Release APK (For Distribution)

To build a signed release APK for distribution:

1. Generate a keystore file (only needed once):
   ```bash
   keytool -genkey -v -keystore my-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias my-alias
   ```

2. Add signing configuration to `app/build.gradle`:
   ```gradle
   android {
       ...
       signingConfigs {
           release {
               storeFile file('my-release-key.jks')
               storePassword 'your-password'
               keyAlias 'my-alias'
               keyPassword 'your-password'
           }
       }
       buildTypes {
           release {
               ...
               signingConfig signingConfigs.release
           }
       }
   }
   ```

3. Build release APK:
   ```bash
   gradlew.bat assembleRelease
   ```

## Troubleshooting

### Gradle Build Failed
- Make sure you have JDK 11+ installed
- Check your internet connection (Gradle needs to download dependencies)
- Try: `gradlew.bat clean` then rebuild

### App Crashes on Launch
- Check your internet connection
- The app requires internet access to load the Streamlit web app

### WebView Not Loading
- Ensure the device has a stable internet connection
- Check if the Streamlit app URL is accessible: https://independent-dealer-prospector.streamlit.app/

## Features

- Full-screen WebView displaying the Dealer Finder web app
- Progress bar showing page load status
- Back button navigation support
- Internet connectivity checking
- Location permission support (if needed by the web app)

## Customization

To point the app to a different URL:
1. Open `app/src/main/java/com/dealerfinder/app/MainActivity.java`
2. Change the `APP_URL` constant to your desired URL

To change the app name:
1. Edit `app/src/main/res/values/strings.xml`
2. Modify the `app_name` value

To change the app icon:
1. Replace the icon files in `app/src/main/res/mipmap-*` directories
2. Or use Android Studio's Image Asset Studio (right-click on `res` → New → Image Asset) 