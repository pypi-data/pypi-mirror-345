"""
@file create_timer.py
@brief Comando CLI para crear un temporizador FreeRTOS en un proyecto basado en ESP32.
@author Efrain Reyes Araujo
@version 1.0
@date 2025-05-05

Este módulo crea un temporizador FreeRTOS e integra su definición y uso en los archivos
principales del proyecto, incluyendo project_config.h y main.cpp.
"""

import os
from rtos_cli.utils.file_utils import append_to_file, insert_in_file
from rtos_cli.utils.project_paths import get_project_config_path, get_main_cpp_path, update_readme


def create_timer(timer_name: str, period_ms: int, mode: str):
    """
    @brief Crea un temporizador FreeRTOS y lo integra en el proyecto
    @param timer_name Nombre del temporizador
    @param period_ms  Periodo en milisegundos
    @param mode       Tipo de temporizador ('oneshot' o 'periodic')
    """
    timer_handle = f"xTimer_{timer_name}"
    project_config = get_project_config_path()
    main_cpp = get_main_cpp_path()

    # Validaciones
    if mode not in ["oneshot", "periodic"]:
        raise ValueError("El modo debe ser 'oneshot' o 'periodic'")

    # 1. Agregar definición global
    definition = f"/// @brief Timer for {timer_name}\nextern TimerHandle_t {timer_handle};\n"
    append_to_file(project_config, definition)

    # 2. Inicialización en main.cpp
    auto_reload = "pdTRUE" if mode == "periodic" else "pdFALSE"
    init_code = f"""
    // Initialize {timer_name} timer
    {timer_handle} = xTimerCreate(\"{timer_name}\", pdMS_TO_TICKS({period_ms}), {auto_reload}, NULL, [](TimerHandle_t xTimer) {{
        // TODO: Handler code for {timer_name}
    }});
    if ({timer_handle} != NULL) {{
        xTimerStart({timer_handle}, 0);
    }}
    """
    insert_into_file(main_cpp, init_code, marker="// ## INIT_TIMERS_MARKER")

    # 3. Agregar a README
    update_readme("Temporizadores", f"- `{timer_name}`: {period_ms} ms, modo: {mode}")

    print(f"✅ Temporizador '{timer_name}' creado correctamente.")
