from datetime import datetime
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from python_learning_tracker.learning_python import LearningReport


@pytest.fixture
def mock_data():
    return {
        "abbreviations.csv": "FN,Функції\nMOD,Модулі\nFL,Робота з файлами\n",
        "planned.csv": "FN,3\nMOD,4\nFL,2\n",
        "actual.csv": "2025-01-01,FN,2,4\n2025-01-02,MOD,5,3\n2025-01-03,FL,1,2\n",
    }


def fake_exists(p):
    """Мокована функція exists(), що підтверджує наявність папки та файлів."""
    return str(p) == "mocked" or p.name in ["abbreviations.csv", "planned.csv", "actual.csv"]


def mock_open_files(file_data):
    """Створює окремий мок `Path.open` для кожного файлу."""

    def mocked_open(file_path, *args, **kwargs):
        if isinstance(file_path, Path):
            file_name = file_path.name
            return mock_open(read_data=file_data[file_name])()
        raise TypeError(f"Expected Path, got {type(file_path)} instead")

    return patch("pathlib.Path.open", new=mocked_open)


def test_data_merging(mock_data):
    """Перевірка правильності об'єднання даних."""
    folder_path = Path("mocked")  # Фейкова папка

    with (
        patch("pathlib.Path.exists", new=fake_exists),
        patch("pathlib.Path.is_file", return_value=True),
        mock_open_files(mock_data),
    ):
        data, _ = LearningReport.read_abbr(folder_path)

        assert data, "Помилка: existing_data порожній після read_abbr!"

        data, _ = LearningReport.read_planned(data, folder_path)
        assert "FN" in data, "Помилка: FN не знайдено після read_abbr або read_planned!"

        data, _ = LearningReport.read_actual(data, folder_path)
        assert "FN" in data, "Помилка: FN не знайдено після read_actual!"

    assert data["FN"].theme == "Функції"
    assert data["FN"].planned == 3
    assert data["FN"].actual == 2
    assert data["FN"].score == 4
    assert isinstance(data["FN"].date, datetime)


@pytest.mark.parametrize(
    "start_date, end_date, expected_abbrs",
    [
        ("2025-01-01", "2025-01-02", {"FN", "MOD"}),  # Дати 2025-01-01 - 2025-01-02 (FN, MOD)
        ("2025-01-03", "2025-01-03", {"FL"}),  # Тільки 2025-01-03 (FL)
        ("2025-01-01", "2025-01-03", {"FN", "MOD", "FL"}),  # Весь доступний діапазон (всі теми)
        ("2025-01-04", "2025-01-10", set()),  # Немає записів у цьому діапазоні
    ],
)
def test_filter_by_date(start_date, end_date, expected_abbrs, mock_data):
    folder_path = Path("mocked")

    with (
        patch("pathlib.Path.exists", new=fake_exists),
        patch("pathlib.Path.is_file", return_value=True),
        mock_open_files(mock_data),
    ):
        data, errors = LearningReport.read_and_filter_data(folder_path, start_date, end_date, None)

    filtered_abbrs = set(data.keys())

    assert filtered_abbrs == expected_abbrs, (
        f"Очікувано {expected_abbrs}, але отримано {filtered_abbrs}"
    )


@pytest.mark.parametrize(
    "topic, expected_abbrs",
    [
        ("Функції", {"FN"}),  # Тільки "Функції"
        ("Модулі", {"MOD"}),  # Тільки "Модулі"
        ("Робота з файлами", {"FL"}),  # Тільки "Робота з файлами"
        ("Цикли", set()),  # Теми немає в даних
    ],
)
def test_filter_by_topic(topic, expected_abbrs, mock_data):
    folder_path = Path("mocked")

    with (
        patch("pathlib.Path.exists", new=fake_exists),
        patch("pathlib.Path.is_file", return_value=True),
        mock_open_files(mock_data),
    ):
        data, errors = LearningReport.read_and_filter_data(folder_path, None, None, topic)

    filtered_abbrs = set(data.keys())

    assert filtered_abbrs == expected_abbrs, (
        f"Очікувано {expected_abbrs}, але отримано {filtered_abbrs}"
    )


def test_abbreviations_mapping(mock_data):
    folder_path = Path("mocked")

    with (
        patch("pathlib.Path.exists", new=fake_exists),
        patch("pathlib.Path.is_file", return_value=True),
        mock_open_files(mock_data),
    ):
        data, _ = LearningReport.read_abbr(folder_path)

    expected_mapping = {"FN": "Функції", "MOD": "Модулі", "FL": "Робота з файлами"}

    actual_mapping = {abbr: report.theme for abbr, report in data.items()}

    assert actual_mapping == expected_mapping, (
        f"Очікувано {expected_mapping}, але отримано {actual_mapping}"
    )


def test_missing_data():
    """Перевірка обробки порожніх файлів."""
    mock_empty_data = {"abbreviations.csv": "", "planned.csv": "", "actual.csv": ""}

    folder_path = Path("mocked")

    with (
        patch("pathlib.Path.exists", new=fake_exists),
        patch("pathlib.Path.is_file", return_value=True),
        mock_open_files(mock_empty_data),
    ):
        data, errors = LearningReport.read_and_filter_data(folder_path, None, None, None)

    assert data == {}, "Очікується порожній словник, але отримано дані!"
    assert len(errors) > 0, "Очікується список помилок про відсутні файли, але він порожній!"

    # Перевіряємо, що у списку помилок є очікувані повідомлення
    assert any("Файл abbreviations.csv порожній." in err for err in errors), (
        "Очікуваний запис про порожній abbreviations.csv відсутній"
    )
    assert any("Файл planned.csv порожній." in err for err in errors), (
        "Очікуваний запис про порожній planned.csv відсутній"
    )
    assert any("Файл actual.csv порожній." in err for err in errors), (
        "Очікуваний запис про порожній actual.csv відсутній"
    )


@pytest.mark.parametrize(
    "file_name, file_data, pattern, process_line, expected_errors",
    [
        (
            "actual.csv",
            "date,abbr,actual,score\n2025-01-01,FN,abc,4\n",
            LearningReport.PATTERN_ACTUAL,
            LearningReport.process_actual_line,
            ["Некоректний рядок: 2025-01-01,FN,abc,4"],
        ),
        (
            "planned.csv",
            "abbr,planned\nFN,xyz\n",
            LearningReport.PATTERN_PLANNED,
            LearningReport.process_planned_line,
            ["Некоректний рядок: FN,xyz"],
        ),
        (
            "abbreviations.csv",
            "abbr,theme\n123,Функції\n",
            LearningReport.PATTERN_ABBR,
            LearningReport.process_abbr_line,
            ["Некоректний рядок: 123,Функції"],
        ),
    ],
)
def test_invalid_parameters(file_name, file_data, pattern, process_line, expected_errors):
    errors = []

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("pathlib.Path.open", new_callable=mock_open, read_data=file_data),
    ):
        LearningReport.read_all_files(
            folder_path=Path("mocked_path"),
            file_name=file_name,
            pattern=pattern,
            process_line=process_line,
            errors=errors,
        )

    for error in expected_errors:
        assert error in errors, f"Очікувана помилка {error} не знайдена у {errors}"


@pytest.mark.parametrize(
    "file_data, expected_errors",
    [
        ("date,abbr,actual,score\n2025-01-01,FN,-5,4\n", ["Некоректний рядок: 2025-01-01,FN,-5,4"]),
        ("date,abbr,actual,score\n2025-01-02,FN,0,6\n", ["Некоректний рядок: 2025-01-02,FN,0,6"]),
        ("date,abbr,actual,score\n2025-01-03,FN,3,11\n", ["Некоректний рядок: 2025-01-03,FN,3,11"]),
        ("date,abbr,actual,score\n2025-01-04,FN,2,-2\n", ["Некоректний рядок: 2025-01-04,FN,2,-2"]),
    ],
)
def test_conflict_data(file_data, expected_errors):
    errors = []

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("pathlib.Path.open", new_callable=mock_open, read_data=file_data),
    ):
        LearningReport.read_all_files(
            folder_path=Path("mocked_path"),
            file_name="actual.csv",
            pattern=LearningReport.PATTERN_ACTUAL,
            process_line=LearningReport.process_actual_line,
            errors=errors,
        )

    for expected_error in expected_errors:
        assert any(expected_error in error for error in errors), (
            f"Очікувана помилка {expected_error} не знайдена у {errors}"
        )


@pytest.mark.parametrize(
    "method, mock_data, expected_field",
    [
        (LearningReport.read_planned, "XX,5\nFN,3\n", "planned"),  # Для planned.csv
        (
            LearningReport.read_actual,
            "2025-01-01,XX,2,4\n2025-01-01,FN,3,5\n",
            "actual",
        ),  # Для actual.csv
    ],
)
def test_read_missing_abbr(method, mock_data, expected_field):
    """Перевіряє, чи додається помилка, якщо абревіатура не знайдена в existing_data."""
    mock_existing_data = {
        "FN": LearningReport(abbr="FN", theme="Функції", errors=[]),
    }

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("pathlib.Path.open", new_callable=mock_open, read_data=mock_data),
    ):
        updated_data, errors = method(mock_existing_data, Path("mocked_path"))

    assert "XX" not in updated_data, "Помилка: Відсутня абревіатура XX не повинна додаватись"
    assert "Абревіатуру XX не знайдено в існуючих даних." in errors, (
        "Очікувана помилка про відсутню абревіатуру не додана"
    )

    expected_value = 3 if expected_field == "planned" else 3
    assert getattr(updated_data["FN"], expected_field) == expected_value, (
        f"Поле {expected_field} для FN має бути оновлене до {expected_value}"
    )
