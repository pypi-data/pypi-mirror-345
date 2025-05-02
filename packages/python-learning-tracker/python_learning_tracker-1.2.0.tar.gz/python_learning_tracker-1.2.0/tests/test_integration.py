from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from python_learning_tracker.learning_python import LearningReport


@pytest.fixture
def mock_folder_path():
    """Фікстура для мокованого шляху до папки з даними."""
    return Path("mocked_data")


@pytest.fixture
def mock_file_data():
    """Фікстура для мокованого вмісту файлів."""
    return {
        "abbreviations.csv": "FN,Функції\nMOD,Модулі\nFL,Робота з файлами\n",
        "planned.csv": "FN,3\nMOD,4\nFL,2\n",
        "actual.csv": "2025-01-01,FN,2,4\n2025-01-02,MOD,5,3\n2025-01-03,FL,1,2\n",
        "motivation.txt": "Не варто боятися помилок — це частина навчання.\n",
    }


def mock_open_files(mock_file_data):
    def mocked_open(file_path, *args, **kwargs):
        file_name = file_path.name
        return mock_open(read_data=mock_file_data.get(file_name, ""))()

    return patch("pathlib.Path.open", new=mocked_open)


def test_generate_report(mock_folder_path, mock_file_data):
    """Перевірка, чи коректно об'єднуються всі файли у звіт."""
    with patch("pathlib.Path.exists", return_value=True), mock_open_files(mock_file_data):
        report = LearningReport.generate_report(
            folder_path=mock_folder_path, motivate=True
        )  # Додаємо мотивацію

    assert "Тема:" in report, "Помилка: у звіті відсутня інформація про теми."
    assert "Плановий час:" in report, "Помилка: у звіті відсутній плановий час."
    assert "Фактичний час:" in report, "Помилка: у звіті відсутній фактичний час."
    assert "Оцінка розуміння:" in report, "Помилка: у звіті відсутня оцінка розуміння."
    assert "Рекомендація:" in report, "Помилка: у звіті відсутні рекомендації."
    assert "Мотивація:" in report, "Помилка: у звіті відсутня мотиваційна фраза."


def test_generate_report_with_filters(mock_folder_path, mock_file_data):
    """Перевірка, чи правильно працюють фільтри (дати, тема)."""
    with patch("pathlib.Path.exists", return_value=True), mock_open_files(mock_file_data):
        report = LearningReport.generate_report(
            folder_path=mock_folder_path, start_date="2025-01-02", end_date="2025-01-02"
        )

    assert "Тема: Модулі" in report, "Помилка: Фільтр за датою не працює, немає потрібної теми."
    assert "Тема: Функції" not in report, "Помилка: Фільтр за датою не працює, зайва тема присутня."
    assert "Тема: Робота з файлами" not in report, (
        "Помилка: Фільтр за датою не працює, зайва тема присутня."
    )

    with patch("pathlib.Path.exists", return_value=True), mock_open_files(mock_file_data):
        report = LearningReport.generate_report(folder_path=mock_folder_path, topic="Функції")

    assert "Тема: Функції" in report, "Помилка: Фільтр за темою не працює, немає потрібної теми."
    assert "Тема: Модулі" not in report, "Помилка: Фільтр за темою не працює, зайва тема присутня."
    assert "Тема: Робота з файлами" not in report, (
        "Помилка: Фільтр за темою не працює, зайва тема присутня."
    )


def test_generate_report_with_errors(mock_folder_path):
    """Перевірка, чи правильно формуються списки помилок при неправильних вхідних даних."""
    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("pathlib.Path.open", mock_open(read_data="")),
    ):
        report = LearningReport.generate_report(folder_path=mock_folder_path)

    assert "Помилки під час обробки даних:" in report, (
        "Помилка: звіт не містить секцію з помилками."
    )
    assert "Файл abbreviations.csv порожній." in report, (
        "Помилка: не виявлено повідомлення про порожній файл abbreviations.csv."
    )
    assert "Файл planned.csv порожній." in report, (
        "Помилка: не виявлено повідомлення про порожній файл planned.csv."
    )
    assert "Файл actual.csv порожній." in report, (
        "Помилка: не виявлено повідомлення про порожній файл actual.csv."
    )
