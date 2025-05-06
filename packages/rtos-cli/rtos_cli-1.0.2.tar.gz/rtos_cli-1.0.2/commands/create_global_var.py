# rtos_cli/commands/create_global_var.py
"""
@file create_global_var.py
@brief Command to create a FreeRTOS-safe global variable using mutex or semaphore
@author Efrain Reyes Araujo
@version 1.2.0
@date 2025-05-05
@license MIT
"""
import os
from utils import file_utils, readme_updater, doxygen

def run(var_name, var_type="int", sync_type="mutex"):
    print(f"\n🔐 Creating global variable '{var_name}' ({sync_type})...")

    decl = ""
    init = ""

    if sync_type == "mutex":
        decl = f"extern {var_type} {var_name};\nextern SemaphoreHandle_t {var_name}_mutex;"
        init = f"{var_type} {var_name} = 0;\nSemaphoreHandle_t {var_name}_mutex = NULL;"
    elif sync_type == "semaphore":
        decl = f"extern SemaphoreHandle_t {var_name}_sem;"
        init = f"SemaphoreHandle_t {var_name}_sem = NULL;"
    else:
        raise ValueError("Invalid sync_type. Must be 'mutex' or 'semaphore'.")

    # Add declaration to project_config.h
    file_utils.insert_in_file("src/project_config.h", decl, anchor="// -- GLOBAL VARS --")

    # Add definition to main.cpp
    file_utils.insert_in_file("src/main.cpp", init, anchor="// -- GLOBAL DEFINITIONS --")

    # Initialize sync object
    init_code = ""
    if sync_type == "mutex":
        init_code = f"{var_name}_mutex = xSemaphoreCreateMutex();"
    elif sync_type == "semaphore":
        init_code = f"{var_name}_sem = xSemaphoreCreateBinary();"

    file_utils.insert_in_file("src/main.cpp", init_code, anchor="// -- GLOBAL INIT --")

    # Update README
    readme_updater.append_section("## Global Variables\n", f"- `{var_name}` ({sync_type}) - type: `{var_type}`\n")

    print(f"✅ Global variable '{var_name}' created with {sync_type} protection.")
