# rtos_cli/commands/create_queue.py
"""
@file create_queue.py
@brief Command to create a FreeRTOS queue and register it as a global resource
@author Efrain Reyes Araujo
@version 1.2.0
@date 2025-05-05
@license MIT
"""
import os
from rtos_cli.utils import file_utils, readme_updater, doxygen

def run(queue_name, item_type="int", length=10):
    print(f"\n📬 Creating FreeRTOS queue '{queue_name}' (type: {item_type}, length: {length})...")

    decl = f"extern QueueHandle_t {queue_name};"
    defn = f"QueueHandle_t {queue_name} = NULL;"
    init = f"{queue_name} = xQueueCreate({length}, sizeof({item_type}));"

    # Insert declarations and initializations
    file_utils.insert_in_file("src/project_config.h", decl, anchor="// -- GLOBAL QUEUES --")
    file_utils.insert_in_file("src/main.cpp", defn, anchor="// -- GLOBAL DEFINITIONS --")
    file_utils.insert_in_file("src/main.cpp", init, anchor="// -- GLOBAL INIT --")

    # Update README
    readme_updater.append_section("## Queues\n", f"- `{queue_name}` - type: `{item_type}`, length: `{length}`\n")

    print(f"✅ Queue '{queue_name}' created and globally registered.")
