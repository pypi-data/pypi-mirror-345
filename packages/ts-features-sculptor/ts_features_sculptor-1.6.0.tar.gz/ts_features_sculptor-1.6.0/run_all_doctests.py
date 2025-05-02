"""
Запускает доктесты для всех трансформеров в библиотеке 
ts_features_sculptor.

"""

import doctest
import importlib
import sys
from io import StringIO
import contextlib

TRANSFORMER_MODULES = [
    "active_to_inactive",
    "activity_range_classifier",
    "date_time_decomposer",
    "days_of_life",
    "expression",
    "interval_events_merge",
    "is_holidays",
    "time_validator",
    "long_holiday",
    "row_expanding"
]

def run_doctests():
    """Запускает доктесты для всех трансформеров."""

    total_failures = 0
    total_tests = 0
    error_summary = {}
    
    print("Запуск доктестов для всех трансформеров")
    
    for module_name in TRANSFORMER_MODULES:
        full_module_name = f"ts_features_sculptor.transformers.{module_name}"
        
        try:
            module = importlib.import_module(full_module_name)
            
            print(f"\nТестирование {module_name}...")
            
            output = StringIO()
            with contextlib.redirect_stdout(output):
                result = doctest.testmod(module, verbose=True)
            
            output_text = output.getvalue()
            
            total_failures += result.failed
            total_tests += result.attempted
            
            if result.failed == 0:
                print(f"✅ Доктесты для {module_name} прошли успешно")
            else:
                print(
                    f"❌ Доктесты для {module_name} содержат ошибки: 
                    {result.failed} из {result.attempted}")

                error_lines = []
                for line in output_text.split('\n'):
                    if '***Test Failed***' in line or 'Expected:' in line:
                        error_lines.append(line.strip())
                
                if error_lines:
                    error_summary[module_name] = error_lines
                
        except ImportError as e:
            print(f"⚠️ Не удалось импортировать модуль {module_name}: {e}")
            error_summary[module_name] = [f"Ошибка импорта: {str(e)}"]
        except Exception as e:
            print(f"⚠️ Ошибка при тестировании модуля {module_name}: {e}")
            error_summary[module_name] = [f"Ошибка выполнения: {str(e)}"]
    
    print(
        f"Итоги тестирования: {total_tests - total_failures} успешно, "
        f"{total_failures} ошибок из {total_tests} тестов")
    
    if error_summary:
        print("КРАТКИЙ ОТЧЕТ ОБ ОШИБКАХ:")
        for module, errors in error_summary.items():
            print(f"{module}:")
            for i, error in enumerate(errors):
                if i < 2:
                    print(f"  - {error}")
            if len(errors) > 2:
                print(f"  ... и еще {len(errors) - 2} ошибок")
        
    return total_failures

if __name__ == "__main__":
    failures = run_doctests()
    sys.exit(min(failures, 1)) 