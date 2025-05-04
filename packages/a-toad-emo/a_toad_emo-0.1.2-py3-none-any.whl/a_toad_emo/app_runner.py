import subprocess
import os
import plistlib

class AppRunner:
    """Launches the installed mobile app on an emulator or simulator."""

    def get_android_package_id(self, apk_path: str) -> str:
        try:
            output = subprocess.check_output(['aapt', 'dump', 'badging', apk_path], text=True)
            for line in output.splitlines():
                if line.startswith("package: name="):
                    return line.split("'")[1]
        except Exception as e:
            raise RuntimeError(f"Failed to extract Android package name: {e}")
        raise RuntimeError("Package name not found in APK.")

    def get_ios_bundle_id(self, app_path: str) -> str:
        info_plist_path = os.path.join(app_path, 'Info.plist')
        if not os.path.exists(info_plist_path):
            raise RuntimeError(f"Info.plist not found at {info_plist_path}")

        with open(info_plist_path, 'rb') as f:
            plist = plistlib.load(f)
            bundle_id = plist.get('CFBundleIdentifier')
            if bundle_id:
                return bundle_id
        raise RuntimeError("CFBundleIdentifier not found in Info.plist.")

    def run_app(self, platform: str, app_path: str, app_id: str = None) -> None:
        """
        Launches the app on the booted emulator or simulator.

        Args:
            platform (str): 'android' or 'ios'.
            app_path (str): Path to the installed app file (.apk or .app).
            app_id (str, optional): Package or bundle ID. If not provided, attempts detection.

        Raises:
            RuntimeError: If ID is not provided and cannot be detected.
        """
        if platform == 'android':
            package_id = app_id or self.get_android_package_id(app_path)
            if not package_id:
                raise RuntimeError("Android package ID is missing and could not be detected.")
            subprocess.run(['adb', 'shell', 'monkey', '-p', package_id, '-c', 'android.intent.category.LAUNCHER', '1'], check=True)
            print(f"Launched Android app: {package_id}")

        elif platform == 'ios':
            bundle_id = app_id or self.get_ios_bundle_id(app_path)
            if not bundle_id:
                raise RuntimeError("iOS bundle ID is missing and could not be detected.")
            subprocess.run(['xcrun', 'simctl', 'launch', 'booted', bundle_id], check=True)
            print(f"Launched iOS app: {bundle_id}")

        else:
            raise ValueError(f"Unsupported platform: {platform}")
