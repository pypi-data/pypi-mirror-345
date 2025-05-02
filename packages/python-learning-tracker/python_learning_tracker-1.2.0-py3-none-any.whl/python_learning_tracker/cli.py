import argparse
from datetime import datetime, timedelta
from pathlib import Path

from python_learning_tracker.learning_python import LearningReport


def main():
    parser = argparse.ArgumentParser(
        description="Python Learning Tracker - Аналіз прогресу навчання"
    )

    # Значення за замовчуванням
    default_data_path = Path(__file__).resolve().parent.parent / "data"
    today = datetime.today()
    last_week = today - timedelta(days=7)

    # Аргументи
    parser.add_argument(
        "--files",
        type=str,
        default=str(default_data_path),
        help=f"Шлях до папки з файлами (за замовчуванням: {default_data_path})",
    )
    parser.add_argument(
        "--start",
        type=str,
        default=last_week.strftime("%Y-%m-%d"),
        help="Дата початку аналізу (за замовчуванням: 7 днів тому)",
    )
    parser.add_argument(
        "--end",
        type=str,
        default=today.strftime("%Y-%m-%d"),
        help="Дата завершення аналізу (за замовчуванням: сьогодні)",
    )
    parser.add_argument(
        "--topic", type=str, help="Аналіз конкретної теми (за замовчуванням: всі теми)"
    )
    parser.add_argument(
        "--motivate",
        action="store_true",
        help="Додати мотиваційну фразу (за замовчуванням: вимкнено)",
    )

    args = parser.parse_args()

    folder_path = Path(args.files)

    try:
        report = LearningReport.generate_report(
            folder_path=folder_path,
            start_date=args.start,
            end_date=args.end,
            topic=args.topic,
            motivate=args.motivate,
        )
        print(report)
    except FileNotFoundError as e:
        print(f"Помилка: {e}")
    except Exception as e:
        print(f"Невідома помилка: {e}")


if __name__ == "__main__":
    main()
