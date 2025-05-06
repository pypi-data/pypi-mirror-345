"""
@file create_semaphore.py
@brief Command to create a FreeRTOS binary semaphore
@version 1.0.0
@date 2025-05-05
@license MIT
@author Efrain Reyes Araujo

@details
This module adds a binary semaphore definition and initialization logic to the FreeRTOS PlatformIO project.
"""

import os

PROJECT_CONFIG_PATH = "src/project_config.h"
MAIN_CPP_PATH = "src/main.cpp"
README_PATH = "README.md"

SEMAPHORE_DECLARATION_TEMPLATE = "extern SemaphoreHandle_t {semaphore_name};\n"
SEMAPHORE_DEFINITION_TEMPLATE = "SemaphoreHandle_t {semaphore_name};\n"
SEMAPHORE_INIT_TEMPLATE = "    {semaphore_name} = xSemaphoreCreateBinary();\n    configASSERT({semaphore_name} != NULL);\n"

def run(semaphore_name):
    add_semaphore_to_project_config(semaphore_name)
    add_semaphore_initialization_to_main(semaphore_name)
    update_readme(semaphore_name)
    print(f"Semaphore '{semaphore_name}' created and initialized.")

def add_semaphore_to_project_config(semaphore_name):
    if not os.path.exists(PROJECT_CONFIG_PATH):
        raise FileNotFoundError(f"{PROJECT_CONFIG_PATH} not found")

    with open(PROJECT_CONFIG_PATH, "r+") as f:
        content = f.read()
        if semaphore_name in content:
            print(f"Semaphore '{semaphore_name}' already declared in project_config.h")
            return
        f.seek(0, os.SEEK_END)
        f.write("\n// Semaphore declaration\n")
        f.write(SEMAPHORE_DEFINITION_TEMPLATE.format(semaphore_name=semaphore_name))

def add_semaphore_initialization_to_main(semaphore_name):
    if not os.path.exists(MAIN_CPP_PATH):
        raise FileNotFoundError(f"{MAIN_CPP_PATH} not found")

    with open(MAIN_CPP_PATH, "r") as f:
        lines = f.readlines()

    init_line = SEMAPHORE_INIT_TEMPLATE.format(semaphore_name=semaphore_name)
    updated_lines = []
    inserted = False

    for line in lines:
        updated_lines.append(line)
        if not inserted and "// INIT_RTOS_OBJECTS" in line:
            updated_lines.append(init_line)
            inserted = True

    with open(MAIN_CPP_PATH, "w") as f:
        f.writelines(updated_lines)

def update_readme(semaphore_name):
    with open(README_PATH, "a") as f:
        f.write(f"\n- Semaphore `{semaphore_name}` created with rtos_cli.\n")
