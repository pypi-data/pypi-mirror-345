"""
@file create_mutex.py
@brief Command to create a FreeRTOS mutex
@version 1.0.0
@date 2025-05-05
@license MIT
@author Efrain Reyes Araujo

@details
This module adds a mutex definition and initialization logic to the FreeRTOS PlatformIO project.
"""

import os

PROJECT_CONFIG_PATH = "src/project_config.h"
MAIN_CPP_PATH = "src/main.cpp"
README_PATH = "README.md"

MUTEX_DECLARATION_TEMPLATE = "extern SemaphoreHandle_t {mutex_name};\n"
MUTEX_DEFINITION_TEMPLATE = "SemaphoreHandle_t {mutex_name};\n"
MUTEX_INIT_TEMPLATE = "    {mutex_name} = xSemaphoreCreateMutex();\n    configASSERT({mutex_name} != NULL);\n"

def run(mutex_name):
    add_mutex_to_project_config(mutex_name)
    add_mutex_initialization_to_main(mutex_name)
    update_readme(mutex_name)
    print(f"Mutex '{mutex_name}' created and initialized.")

def add_mutex_to_project_config(mutex_name):
    if not os.path.exists(PROJECT_CONFIG_PATH):
        raise FileNotFoundError(f"{PROJECT_CONFIG_PATH} not found")

    with open(PROJECT_CONFIG_PATH, "r+") as f:
        content = f.read()
        if mutex_name in content:
            print(f"Mutex '{mutex_name}' already declared in project_config.h")
            return
        f.seek(0, os.SEEK_END)
        f.write("\n// Mutex declaration\n")
        f.write(MUTEX_DEFINITION_TEMPLATE.format(mutex_name=mutex_name))


def add_mutex_initialization_to_main(mutex_name):
    if not os.path.exists(MAIN_CPP_PATH):
        raise FileNotFoundError(f"{MAIN_CPP_PATH} not found")

    with open(MAIN_CPP_PATH, "r") as f:
        lines = f.readlines()

    init_line = MUTEX_INIT_TEMPLATE.format(mutex_name=mutex_name)
    updated_lines = []
    inserted = False

    for line in lines:
        updated_lines.append(line)
        if not inserted and "// INIT_RTOS_OBJECTS" in line:
            updated_lines.append(init_line)
            inserted = True

    with open(MAIN_CPP_PATH, "w") as f:
        f.writelines(updated_lines)

def update_readme(mutex_name):
    with open(README_PATH, "a") as f:
        f.write(f"\n- Mutex `{mutex_name}` created with rtos_cli.\n")
