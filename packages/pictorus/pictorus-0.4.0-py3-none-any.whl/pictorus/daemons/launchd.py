import subprocess
import os

from pictorus.daemons.daemon import Daemon

SYSTEMD_DIR = os.path.expanduser("~/Library/LaunchAgents/")
SYSTEMCTL_BIN = "launchctl"
PLIST_NAME = "us.pictor.dm.plist"
PLIST_PATH = os.path.join(SYSTEMD_DIR, PLIST_NAME)
SERVICE_LABEL = "pictorus_device_manager"

SERVICE_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
    <dict>
        <key>Label</key>
        <string>{service_label}</string>
        <key>Program</key>
        <string>{bin_path}</string>

        <key>StandardErrorPath</key>
        <string>/tmp/pictorus.err</string>
        <key>StandardOutPath</key>
        <string>/tmp/pictorus.out</string>
    </dict>
</plist>
"""  # noqa: E501 - Trying to format a system file


class Launchd(Daemon):
    def fill_service_template(self, bin_path):
        return SERVICE_TEMPLATE.format(service_label=SERVICE_LABEL, bin_path=bin_path)

    def create_service_file(self, service_name: str, description: str, bin_path: str):
        """Create a launchd service file"""
        service_content = self.fill_service_template(bin_path)
        with open(
            os.path.expanduser(os.path.join(SYSTEMD_DIR, PLIST_PATH)), "w", encoding="utf-8"
        ) as service_file:
            service_file.write(service_content)

    def stop_service(self, service_name: str):
        """Stop a given service"""
        self.run([SYSTEMCTL_BIN, "bootout", f"gui/{os.getuid()}", PLIST_PATH],
                 check=False, cwd=SYSTEMD_DIR)

    def start_service(self, service_name: str):
        """Start a given service"""
        self.run([SYSTEMCTL_BIN, "bootstrap", f"gui/{os.getuid()}", PLIST_PATH],
                 check=False, cwd=SYSTEMD_DIR)

    def enable_service(self, service_name: str):
        """Start a given service"""
        # This was obnoxious to figure out. The kickstart command references the "Label"
        # of the plist file and not the name of the file, unlike bootstrap and bootout.
        self.run([SYSTEMCTL_BIN, "kickstart", "-k", f"gui/{os.getuid()}/{SERVICE_LABEL}"],
                 check=False, cwd=SYSTEMD_DIR)

    def reload_daemon(self, service_name: str):
        """Reload the launchd daemon"""

    def run(self, cmd: list, check=True, cwd=None):
        subprocess.run(cmd, check=check, cwd=cwd)
