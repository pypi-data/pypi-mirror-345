from pathlib import Path
from unittest.mock import patch

from python_learning_tracker.cli import main


def test_cli_with_mocked_args():
    test_args = [
        "cli.py",
        "--files",
        "./data",
        "--start",
        "2025-12-01",
        "--end",
        "2025-12-03",
        "--motivate",
    ]

    with (
        patch("sys.argv", test_args),
        patch("python_learning_tracker.cli.LearningReport.generate_report") as mock_generate,
    ):
        main()
        mock_generate.assert_called_once_with(
            folder_path=Path("./data"),
            start_date="2025-12-01",
            end_date="2025-12-03",
            topic=None,
            motivate=True,
        )


def test_cli_file_not_found():
    test_args = [
        "cli.py",
        "--files",
        "./non_existent",
        "--start",
        "2025-12-01",
        "--end",
        "2025-12-03",
    ]

    with (
        patch("sys.argv", test_args),
        patch(
            "python_learning_tracker.cli.LearningReport.generate_report",
            side_effect=FileNotFoundError("Файл не знайдено"),
        ),
    ):
        with patch("builtins.print") as mock_print:  # Перехоплюємо вивід у консоль
            main()
            mock_print.assert_called_with("Помилка: Файл не знайдено")


def test_cli_unknown_error():
    test_args = ["cli.py", "--files", "./data", "--start", "2023-12-01", "--end", "2023-12-03"]

    with (
        patch("sys.argv", test_args),
        patch(
            "python_learning_tracker.cli.LearningReport.generate_report",
            side_effect=Exception("Щось пішло не так"),
        ),
    ):
        with patch("builtins.print") as mock_print:
            main()
            mock_print.assert_called_with("Невідома помилка: Щось пішло не так")
