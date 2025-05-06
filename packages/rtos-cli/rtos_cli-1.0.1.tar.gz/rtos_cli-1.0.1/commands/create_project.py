# rtos_cli/commands/create_project.py
"""
@file create_project.py
@brief Command to create a new PlatformIO project for ESP32 Eddie-W board.
@author Innervycs
@version 1.2.0
@date 2025-05-05
@license MIT
"""
import os
import shutil
from utils import file_utils, readme_updater

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates')

BOARD_JSON = """
{
  "build": {
    "arduino": {
      "ldscript": "esp32_out.ld"
    },
    "core": "esp32",
    "extra_flags": "-DARDUINO_ESP32_DEV",
    "f_cpu": "240000000L",
    "f_flash": "80000000L",
    "flash_mode": "qio",
    "hwids": [["0x0403", "0x6010"]],
    "mcu": "esp32",
    "variant": "esp32"
  },
  "connectivity": ["wifi", "bluetooth", "ethernet", "can"],
  "debug": {
    "default_tool": "ftdi",
    "onboard_tools": ["ftdi"],
    "openocd_board": "esp32-wrover.cfg"
  },
  "frameworks": ["arduino", "espidf"],
  "name": "MetaBridge Eddie W",
  "upload": {
    "flash_size": "16MB",
    "maximum_ram_size": 8388608,
    "maximum_size": 16777216,
    "protocols": ["esptool", "espota", "ftdi"],
    "require_upload_port": true,
    "speed": 921600
  },
  "url": "https://innervycs.com/",
  "vendor": "Innervycs"
}
"""

def run(project_name):
    print(f"\n🚀 Creating PlatformIO project '{project_name}'...")

    os.makedirs(project_name, exist_ok=True)

    subdirs = ["src", "include", "lib", "test", "boards"]
    for d in subdirs:
        os.makedirs(os.path.join(project_name, d), exist_ok=True)

    # Write board JSON
    board_path = os.path.join(project_name, "boards", "esp32-eddie-w.json")
    with open(board_path, "w") as f:
        f.write(BOARD_JSON)

    # Copy template files
    templates = ["main.cpp", "platformio.ini", "project_config.h"]
    for t in templates:
        file_utils.copy_template_to_project(t, project_name)

    # README.md
    readme_path = os.path.join(project_name, "README.md")
    with open(readme_path, "w") as f:
        f.write(f"# {project_name}\n\nGenerated with `rtos_cli` for ESP32 Eddie-W.\n")

    print("✅ Project created successfully.")