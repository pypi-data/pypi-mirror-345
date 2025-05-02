from contextlib import ExitStack
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from python_learning_tracker.learning_python import LearningReport


def setup_mocked_path(file_data="", path_exists=True):
    return (
        patch("pathlib.Path.exists", return_value=path_exists),
        patch("pathlib.Path.open", new_callable=mock_open, read_data=file_data),
    )


def read_and_validate(file_name, pattern, process_line, folder="mocked_path", errors=None):
    if errors is None:
        errors = []
    return LearningReport.read_all_files(
        folder_path=Path(folder),
        file_name=file_name,
        pattern=pattern,
        process_line=process_line,
        errors=errors,
    )


@pytest.mark.parametrize(
    "file_path, func",
    [
        ("non_existent_folder", LearningReport.verify_folder_data),
    ],
)
def test_file_not_found_generic(file_path, func):
    with pytest.raises(FileNotFoundError):
        func(Path(file_path))


@pytest.mark.parametrize(
    "file_path",
    [
        "data/non_existent_abbreviations.csv",
        "data/non_existent_planned.csv",
        "data/non_existent_actual.csv",
        "data/non_existent_motivation.txt",
    ],
)
def test_verify_folder_data_file_not_found(file_path):
    with pytest.raises(FileNotFoundError):
        LearningReport.verify_folder_data(Path(file_path))


@pytest.mark.parametrize(
    "file_name, pattern, process_line",
    [
        ("abbreviations.csv", LearningReport.PATTERN_ABBR, LearningReport.process_abbr_line),
        ("planned.csv", LearningReport.PATTERN_PLANNED, LearningReport.process_planned_line),
        ("actual.csv", LearningReport.PATTERN_ACTUAL, LearningReport.process_actual_line),
        ("motivation.txt", None, lambda line, pattern, errors: None),
    ],
)
def test_empty_files(file_name, pattern, process_line):
    errors = []

    patches = setup_mocked_path(path_exists=True)
    with ExitStack() as stack:
        for p in patches:
            stack.enter_context(p)

        result = read_and_validate(file_name, pattern, process_line, errors=errors)

    assert result == ({}, [f"Файл {file_name} порожній."])

    assert f"Файл {file_name} порожній." in errors


@pytest.mark.parametrize(
    "file_name, pattern, process_line, required_columns",
    [
        (
            "abbreviations.csv",
            LearningReport.PATTERN_ABBR,
            LearningReport.process_abbr_line,
            ["abbr", "theme"],
        ),
        (
            "planned.csv",
            LearningReport.PATTERN_PLANNED,
            LearningReport.process_planned_line,
            ["date", "theme", "planned"],
        ),
        (
            "actual.csv",
            LearningReport.PATTERN_ACTUAL,
            LearningReport.process_actual_line,
            ["date", "abbr", "actual", "score"],
        ),
        ("motivation.txt", None, lambda line, pattern, errors: None, []),
    ],
)
def test_file_required_columns(file_name, pattern, process_line, required_columns):
    errors = []

    patches = setup_mocked_path(path_exists=True)
    with ExitStack() as stack:
        for p in patches:
            stack.enter_context(p)

        result = read_and_validate(file_name, pattern, process_line, errors=errors)

        # Перевіряємо, що результат порожній
        assert result == ({}, [f"Файл {file_name} порожній."])

        # Перевіряємо, що для файлу додано помилку
        assert f"Файл {file_name} порожній." in errors

        # Додатковий мок для перевірки колонок
        with ExitStack() as column_stack:
            column_patches = setup_mocked_path(
                file_data=",".join(required_columns) + "\n", path_exists=True
            )
            for cp in column_patches:
                column_stack.enter_context(cp)

            result = read_and_validate(file_name, pattern, process_line, errors=errors)

            # Перевіряємо, що всі потрібні колонки є
            for column in required_columns:
                assert column in ",".join(required_columns), f"Відсутня колонка: {column}"


@pytest.mark.parametrize(
    "file_name, required_columns, file_data",
    [
        (
            "planned.csv",
            ["date", "theme", "planned"],
            "date,theme,planned\n2023-12-01,Functions,3\n",
        ),
        ("abbreviations.csv", ["abbr", "theme"], "abbr,theme\nFN,Functions\n"),
    ],
)
def test_required_columns_general(file_name, required_columns, file_data):
    errors = []

    patches = setup_mocked_path(file_data=file_data, path_exists=True)
    with ExitStack() as stack:
        for p in patches:
            stack.enter_context(p)

        read_and_validate(file_name, None, lambda line, pattern, errors: None, errors=errors)

        file_headers = file_data.split("\n")[0].split(",")
        for column in required_columns:
            assert column in file_headers, f"Колонка {column} відсутня в {file_name}."


@pytest.mark.parametrize(
    "file_name, required_columns, file_data",
    [
        (
            "actual.csv",
            ["date", "abbr", "actual", "score"],
            "date,abbr,actual,score\n2023-12-01,FN,2,4\n",
        ),
    ],
)
def test_required_columns_actual(file_name, required_columns, file_data):
    errors = []

    patches = setup_mocked_path(file_data=file_data, path_exists=True)
    with ExitStack() as stack:
        for p in patches:
            stack.enter_context(p)

        read_and_validate(file_name, None, lambda line, pattern, errors: None, errors=errors)

        file_headers = file_data.split("\n")[0].split(",")
        for column in required_columns:
            assert column in file_headers, f"Колонка {column} відсутня в {file_name}."


@pytest.mark.parametrize(
    "file_name, pattern, process_line, file_data, invalid_line",
    [
        (
            "planned.csv",
            LearningReport.PATTERN_PLANNED,
            LearningReport.process_planned_line,
            "date,theme,planned\n2023-12-01,Functions,3\nInvalid,Line\n",
            "Некоректний рядок: Invalid,Line",
        ),
        (
            "actual.csv",
            LearningReport.PATTERN_ACTUAL,
            LearningReport.process_actual_line,
            "date,abbr,actual,score\n2023-12-01,FN,2,4\n2023-12-02,XX,5\n",
            "Некоректний рядок: 2023-12-02,XX,5",
        ),
    ],
)
def test_invalid_data_handling(file_name, pattern, process_line, file_data, invalid_line):
    errors = []

    patches = setup_mocked_path(file_data=file_data, path_exists=True)
    with ExitStack() as stack:
        for p in patches:
            stack.enter_context(p)

        read_and_validate(file_name, pattern, process_line, errors=errors)

    assert invalid_line in errors


def test_check_file_exists():
    """Перевіряє, що check_file_exists правильно обробляє відсутній файл."""
    errors = []
    folder_path = Path("mocked_path")
    file_path = folder_path / "missing_file.txt"

    with patch.object(Path, "exists", return_value=False):
        result = LearningReport.check_file_exists(file_path, errors)

    assert result is False, "Очікується False, якщо файл не існує."
    assert errors == [f"Файл {file_path} не знайдено."], (
        f"Очікуваний список помилок: {[f'Файл {file_path} не знайдено.']}, отримано: {errors}"
    )


@pytest.mark.parametrize(
    "file_name",
    [
        "abbreviations.csv",
        "planned.csv",
        "actual.csv",
    ],
)
def test_read_all_files_file_not_found(file_name):
    """Перевіряє, що read_all_files повертає {}, якщо файл відсутній."""
    errors = []
    folder_path = Path("mocked_path")
    file_path = folder_path / file_name

    def mock_path_exists(self):
        return self == folder_path  # Папка існує, файли ні

    with patch.object(Path, "exists", mock_path_exists):
        data, errors = LearningReport.read_all_files(folder_path, file_name, None, None, errors)

    assert data == {}, "Очікується {}, оскільки файл відсутній."
    assert errors == [f"Файл {file_path} не знайдено."], (
        f"Очікується повідомлення про помилку, отримано: {errors}"
    )


def test_read_motivation_file_not_found():
    """Перевіряє, що read_motivation повертає [], якщо файл відсутній."""
    folder_path = Path("mocked_path")
    folder_path / "motivation.txt"

    with patch.object(Path, "exists", return_value=False):
        motivations = LearningReport.read_motivation(folder_path, "motivation.txt")

    assert motivations == [], "Очікується [], якщо файл мотивації відсутній."
