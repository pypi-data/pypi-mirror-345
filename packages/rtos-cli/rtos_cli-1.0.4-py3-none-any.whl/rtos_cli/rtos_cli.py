# rtos_cli.py
"""
@file rtos_cli.py
@brief Main CLI entry point for FreeRTOS + PlatformIO project automation
@version 1.2.0
@date 2025-05-05
@license MIT
@author Efrain Reyes Araujo

@details
RTOS CLI automates the setup and extension of FreeRTOS-based ESP32 projects using PlatformIO. It supports:
- Project creation with board configuration
- Task creation with FreeRTOS logic
- Global variable and queue management

@example
    python rtos_cli.py create_project MyProject
    python rtos_cli.py create_task sensor_reader
    python rtos_cli.py create_global_var counter int mutex
    python rtos_cli.py create_queue message_queue int 20
    python rtos_cli.py create_timer timer_1 1000 periodic
    python rtos_cli.py create_event_group event_group_1
"""

import argparse
import sys

from rtos_cli.utils import file_utils, readme_updater, doxygen

from rtos_cli.commands import (
    create_project,
    create_task,
    create_global_var,
    create_queue,
    create_timer,
    create_event_group,
    create_mutex,
    create_semaphore,
    create_module
)

def main():
    parser = argparse.ArgumentParser(
        description="RTOS CLI - Automate FreeRTOS Project Development (Develop Edition)",
        formatter_class=argparse.RawTextHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # create_project
    p_project = subparsers.add_parser("create_project", help="Create a new PlatformIO + FreeRTOS project")
    p_project.add_argument("project_name", help="Name of the new project")

    # create_task
    p_task = subparsers.add_parser("create_task", help="Create a new FreeRTOS task")
    p_task.add_argument("task_name", help="Name of the task to create")

    # create_global_var
    p_var = subparsers.add_parser("create_global_var", help="Declare a global FreeRTOS-safe variable")
    p_var.add_argument("var_name", help="Variable name")
    p_var.add_argument("var_type", help="Variable type (e.g., int, float, etc.)")
    p_var.add_argument("sync_type", choices=["mutex", "semaphore"], help="Synchronization type")

    # create_queue
    p_queue = subparsers.add_parser("create_queue", help="Declare a FreeRTOS queue")
    p_queue.add_argument("queue_name", help="Queue name")
    p_queue.add_argument("item_type", help="Item data type")
    p_queue.add_argument("length", type=int, help="Number of items in queue")

    # create_timer
    p_timer = subparsers.add_parser("create_timer", help="Create a FreeRTOS timer")
    p_timer.add_argument("timer_name", help="Name of the timer")
    p_timer.add_argument("period_ms", type=int, help="Period in milliseconds")
    p_timer.add_argument("mode", choices=["oneshot", "periodic"], help="Timer mode")

    # create_event_group
    p_event_group = subparsers.add_parser("create_event_group", help="Create a FreeRTOS event group")
    p_event_group.add_argument("group_name", help="Name of the event group")

    # create_mutex
    p_mutex = subparsers.add_parser("create_mutex", help="Create a FreeRTOS mutex")
    p_mutex.add_argument("mutex_name", help="Name of the mutex to create")

    # create_semaphore
    p_semaphore = subparsers.add_parser("create_semaphore", help="Create a FreeRTOS binary semaphore")
    p_semaphore.add_argument("semaphore_name", help="Name of the semaphore to create")

    # create_module
    p_module = subparsers.add_parser("create_module", help="Create a new C++ module (.h/.cpp)")
    p_module.add_argument("module_name", help="Name of the module to create")

    args = parser.parse_args()

    if args.command == "create_project":
        create_project.run(args.project_name)
    elif args.command == "create_task":
        create_task.run(args.task_name)
    elif args.command == "create_global_var":
        create_global_var.run(args.var_name, args.var_type, args.sync_type)
    elif args.command == "create_queue":
        create_queue.run(args.queue_name, args.item_type, args.length)
    elif args.command == "create_timer":
        create_timer.run(args.timer_name, args.period_ms, args.mode)
    elif args.command == "create_event_group":
        create_event_group.run(args.group_name)
    elif args.command == "create_mutex":
        create_mutex.run(args.mutex_name)
    elif args.command == "create_semaphore":
        create_semaphore.run(args.semaphore_name)
    elif args.command == "create_module":
        create_module.run(args.module_name)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()