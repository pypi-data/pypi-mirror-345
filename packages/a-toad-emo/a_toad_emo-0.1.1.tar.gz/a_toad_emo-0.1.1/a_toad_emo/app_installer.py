import subprocess
import os

class AppInstaller:
    """Handles installing the app on a simulator or emulator."""

    def install(self, platform: str, device_name: str, app_path: str) -> None:
        """
        Installs the app on the specified emulator or simulator.

        Args:
            platform (str): 'android' or 'ios'.
            device_name (str): Name of the emulator/simulator.
            app_path (str): Path to the .apk or .app/.ipa file.

        Raises:
            FileNotFoundError: If the app_path does not exist.
            subprocess.CalledProcessError: If install command fails.
        """
        if not os.path.exists(app_path):
            raise FileNotFoundError(f"App file not found at: {app_path}")

        if platform == 'android':
            result = subprocess.run(['adb', 'install', '-r', app_path], check=True)
            print(f"Installed Android app from: {app_path}")

        elif platform == 'ios':
            # Assumes app_path is a .app folder for simulator
            result = subprocess.run(['xcrun', 'simctl', 'install', device_name, app_path], check=True)
            print(f"Installed iOS app from: {app_path}")

        else:
            raise ValueError(f"Unsupported platform for app installation: {platform}")
