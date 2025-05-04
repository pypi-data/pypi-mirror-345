import subprocess

class EmulatorLauncher:
    """Launches a mobile emulator or simulator for Android or iOS platforms."""

    def launch(self, platform: str, device_name: str, headless: bool = False) -> None:
        """Launches the specified mobile emulator or simulator.

        Args:
            platform (str): The target platform. Either "android" or "ios".
            device_name (str): The name of the emulator (AVD) or simulator device to boot.
            headless (bool): Whether to run in headless mode (no GUI). Only applies to Android.

        Raises:
            ValueError: If an unsupported platform is specified.
            subprocess.CalledProcessError: If the emulator command fails.
        """
        try:
            if platform == 'android':
                args = ['emulator', '-avd', device_name]
                if headless:
                    args += ['-no-window', '-no-audio', '-no-boot-anim']
                subprocess.run(args, check=True)
                print(f"Android emulator '{device_name}' launched successfully.")

            elif platform == 'ios':
                subprocess.run(['xcrun', 'simctl', 'boot', device_name], check=True)
                print(f"iOS simulator '{device_name}' launched successfully.")

            else:
                raise ValueError(f"Unsupported platform: {platform}")
            
        except subprocess.CalledProcessError:
            print(f"Failed to launch {platform} emulator/simulator '{device_name}'.")
            raise
