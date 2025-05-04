import argparse
from a_toad_emo.emulator_launcher import EmulatorLauncher
from a_toad_emo.config_loader import load_config
from a_toad_emo.app_installer import AppInstaller
from a_toad_emo.app_runner import AppRunner

def main():
    parser = argparse.ArgumentParser(description="A Toad Emo - Launch and Run Emulator.")
    parser.add_argument(
        "--headless",
        type=str,
        choices=["true", "false"],
        default="true",
        help="Run emulator in headless mode (default: true)"
    )
    args = parser.parse_args()

    config = load_config()
    platform = config.get("platform")
    device_name = config.get("device_name")
    app_path = config.get("app_path")
    install_app = config.get("install_app", True)
    app_id = config.get("app_id")

    if not platform or not device_name:
        raise ValueError("Config must include 'platform' and 'device_name'.")

    # 1. Launch Emulator
    launcher = EmulatorLauncher()
    launcher.launch(platform=platform, device_name=device_name, headless=args.headless)

    # 2. Install the target app
    if install_app:
        if not app_path:
            raise ValueError("Config must include 'app_path' when install_app is true.")
        installer = AppInstaller()
        installer.target_app_install(platform=platform, device_name=device_name, app_path=app_path)

    # 3. Run the target app
    runner = AppRunner()
    runner.run_app(platform=platform, app_path=app_path, app_id=app_id)

if __name__ == "__main__":
    main()