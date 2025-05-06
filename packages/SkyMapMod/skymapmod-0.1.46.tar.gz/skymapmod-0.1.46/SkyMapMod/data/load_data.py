import numpy as np
import os
from pathlib import Path

def load_star_temperatures():
    # Определяем путь к файлу данных
    data_dir = Path(__file__).parent
    file_path = data_dir / "star_temperatures.npy"
    
    # Проверяем, существует ли файл
    if not file_path.exists():
        raise FileNotFoundError(f"Файл данных не найден: {file_path}")
    
    # Загружаем данные
    return np.load(file_path)

def load_star_brightness():
    # Определяем путь к файлу данных
    data_dir = Path(__file__).parent
    file_path = data_dir / "star_brightness.npy"
    
    # Проверяем, существует ли файл
    if not file_path.exists():
        raise FileNotFoundError(f"Файл данных не найден: {file_path}")
    
    # Загружаем данные
    return np.load(file_path)