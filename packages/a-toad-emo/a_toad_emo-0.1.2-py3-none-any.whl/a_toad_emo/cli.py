import argparse
from a_toad_emo.emulator_launcher import EmulatorLauncher
from a_toad_emo.config_loader import load_config
from a_toad_emo.app_installer import AppInstaller

def main():
    parser = argparse.ArgumentParser(description="A Toad Emo - Launch and Run Emulator.")
    parser.add_argument('--headless', action='store_true', help='Run emulator in headless mode')
    args = parser.parse_args()

    config = load_config()
    platform = config.get("platform")
    device_name = config.get("device_name")
    app_path = config.get("app_path")
    install_app = config.get("install_app", True)

    if not platform or not device_name:
        raise ValueError("Config must include 'platform' and 'device_name'.")

    launcher = EmulatorLauncher()
    launcher.launch(platform=platform, device_name=device_name, headless=args.headless)

    if install_app:
        if not app_path:
            raise ValueError("Config must include 'app_path' when install_app is true.")
        installer = AppInstaller()
        installer.target_app_install(platform=platform, device_name=device_name, app_path=app_path)

if __name__ == "__main__":
    main()