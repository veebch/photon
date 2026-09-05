import unittest
from pathlib import Path

from tools.upload_pico import build_upload_commands


class BuildUploadCommandsTest(unittest.TestCase):
    def test_builds_recursive_and_file_copy_commands_for_auto_connection(self):
        root = Path("/project")

        commands = build_upload_commands(root, "auto")

        self.assertEqual(
            commands,
            [
                ["connect", "auto", "fs", "cp", "-r", "/project/drivers", ":"],
                ["connect", "auto", "fs", "cp", "-r", "/project/gui", ":"],
                ["connect", "auto", "fs", "cp", "/project/color_setup.py", ":color_setup.py"],
                ["connect", "auto", "fs", "cp", "/project/battery.py", ":battery.py"],
                ["connect", "auto", "fs", "cp", "/project/main.py", ":main.py"],
                ["connect", "auto", "soft-reset"],
            ],
        )

    def test_uses_an_explicit_serial_port(self):
        commands = build_upload_commands(Path("/project"), "/dev/cu.usbmodem101")

        self.assertTrue(all(command[1] == "/dev/cu.usbmodem101" for command in commands))


if __name__ == "__main__":
    unittest.main()
