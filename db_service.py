import json
import os

def get_department_data(dept_name: str) -> dict | None:
    # Загружаем базу из JSON файла
    base_path = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base_path, 'database.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Приводим к нижнему регистру для гибкости поиска
    dept_name_clean = dept_name.strip().lower()
    
    # Ищем отдел в базе
    dept_info = data["departments"].get(dept_name_clean)
    
    if dept_info:
        return {
            "company_name": data["company_info"]["company_name"],
            "director": data["company_info"]["director_name"],
            "dept_full_name": dept_info["full_name"],
            "mentor": dept_info["mentor"],
            "ethics": dept_info["ethics_officer"]
        }
    return None