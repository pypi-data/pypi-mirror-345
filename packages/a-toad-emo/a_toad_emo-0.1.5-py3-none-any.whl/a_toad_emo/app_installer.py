import subprocess
import os

class AppInstaller:
    """Handles installing the app on a simulator or emulator."""

    def is_android_app_installed(self, package_id: str) -> bool:
        """
        Check whether the target android app is installed to the emulator.
        """
        try:
            output = subprocess.check_output(['adb', 'shell', 'pm', 'list', 'packages'], text=True)
            return f"package:{package_id}" in output
        except subprocess.CalledProcessError:
            return False

    def is_ios_app_installed(self, bundle_id: str) -> bool:
        """
        Check whether the target ios app is installed to the simulator.
        """
        try:
            result = subprocess.run(['xcrun', 'simctl', 'get_app_container', 'booted', bundle_id], 
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False

    def target_app_install(self, platform: str, device_name: str, app_path: str, app_id: str = None) -> None:
        """
        Installs the target app on the specified emulator or simulator.

        Args:
            platform (str): 'android' or 'ios'.
            device_name (str): Name of the emulator/simulator.
            app_path (str): Path to the .apk or .app/.ipa file.
            app_id (str, optional): Package ID or bundle ID. Used to check if the app is already installed.

        Raises:
            FileNotFoundError: If the app_path does not exist.
            subprocess.CalledProcessError: If install command fails.
        """
        if not os.path.exists(app_path):
            raise FileNotFoundError(f"App file not found at: {app_path}")

        if platform == 'android':
            if app_id and self.is_android_app_installed(app_id):
                print(f"Android app '{app_id}' already installed. Skipping install.")
                return
            subprocess.run(['adb', 'install', '-r', app_path], check=True)
            print(f"Installed Android app from: {app_path}")

        elif platform == 'ios':
            if app_id and self.is_ios_app_installed(app_id):
                print(f"iOS app '{app_id}' already installed. Skipping install.")
                return
            subprocess.run(['xcrun', 'simctl', 'install', device_name, app_path], check=True)
            print(f"Installed iOS app from: {app_path}")

        else:
            raise ValueError(f"Unsupported platform for app installation: {platform}")
