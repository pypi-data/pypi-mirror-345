import random
import re
from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

FilteredData = Tuple[Dict[str, "LearningReport"], List[str]]


@dataclass(frozen=True)
class LearningReport:
    PATTERN_ABBR = re.compile(r"^(?P<abbr>[A-Z]+),(?P<theme>.+)$")
    PATTERN_PLANNED = re.compile(r"^(?P<abbr>[A-Z]+),(?P<planned>\d+)$")
    PATTERN_ACTUAL = re.compile(
        r"^(?P<date>\d{4}-\d{2}-\d{2}),(?P<abbr>[A-Z]+),(?P<actual>\d+),(?P<score>\d+)$"
    )

    abbr: str | None = None
    theme: str | None = None
    planned: int | None = None
    actual: int | None = None
    date: datetime | None = None
    motivation: list[str] | None = None
    score: int | None = None
    errors: list[str] | None = None

    @staticmethod
    def verify_folder_data(folder_path: Path) -> Path:
        # Перевіряє існування папки та повертає підтверджений шлях
        if not folder_path.exists():
            raise FileNotFoundError(f"Папка {folder_path} не знайдена.")
        return folder_path

    @staticmethod
    def check_file_exists(file_path: Path, errors: list[str]) -> bool:
        """Перевіряє, чи існує файл, та додає помилку у разі його відсутності."""
        if not file_path.exists():
            errors.append(f"Файл {file_path} не знайдено.")
            return False
        return True

    @staticmethod
    def parse_line(line: str, pattern: re.Pattern, errors: list[str]) -> re.Match | None:
        match = pattern.match(line.strip())
        if not match:
            errors.append(f"Некоректний рядок: {line.strip()}")
            return None
        return match

    @staticmethod
    def read_all_files(
        folder_path: Path, file_name: str, pattern: re.Pattern, process_line, errors: list[str]
    ) -> FilteredData:
        folder_path = LearningReport.verify_folder_data(folder_path)
        file_path = folder_path / file_name

        if not LearningReport.check_file_exists(file_path, errors):
            return {}, errors

        with file_path.open("r", encoding="utf-8") as file:
            lines = file.readlines()

        if not lines:
            errors.append(f"Файл {file_name} порожній.")
            return {}, errors

        data = {}
        for line in lines:
            result = process_line(line.strip(), pattern, errors)
            if result:
                data[result[0]] = result[1]

        return data, errors

    @staticmethod
    def process_abbr_line(
        line: str, pattern: re.Pattern, errors: list[str]
    ) -> tuple[str, "LearningReport"] | None:
        match = LearningReport.parse_line(line, pattern, errors)
        if not match:
            return None
        return match.group("abbr"), LearningReport(
            abbr=match.group("abbr"), theme=match.group("theme"), errors=errors
        )

    @classmethod
    def read_abbr(
        cls, folder_path: Path = Path("data"), file_name: str = "abbreviations.csv"
    ) -> dict[str, "LearningReport"]:
        errors = []
        abbr_data, file_errors = cls.read_all_files(
            folder_path, file_name, cls.PATTERN_ABBR, cls.process_abbr_line, errors
        )
        errors.extend(file_errors)
        return abbr_data, errors

    @staticmethod
    def process_planned_line(
        line: str, pattern: re.Pattern, errors: list[str]
    ) -> tuple[str, int] | None:
        match = LearningReport.parse_line(line, pattern, errors)
        if not match:
            return None
        return match.group("abbr"), int(match.group("planned"))

    @classmethod
    def read_planned(
        cls,
        existing_data: dict[str, "LearningReport"],
        folder_path: Path = Path("data"),
        file_name: str = "planned.csv",
    ) -> FilteredData:
        errors = []
        planned_data, file_errors = cls.read_all_files(
            folder_path, file_name, cls.PATTERN_PLANNED, cls.process_planned_line, errors
        )
        errors.extend(file_errors)

        for abbr, planned_time in planned_data.items():
            if abbr not in existing_data:
                errors.append(f"Абревіатуру {abbr} не знайдено в існуючих даних.")
                continue

            existing_data[abbr] = replace(existing_data[abbr], planned=planned_time)

        return existing_data, errors

    @staticmethod
    def calculate_additional_time(actual_time: int, score: int, min_score: int = 8) -> int:
        """Розраховує додатковий час для досягнення мінімальної прохідної оцінки."""
        if score == 0:
            return actual_time

        if score >= min_score:
            return 0

        needed_score = min_score - score
        time_per_point = actual_time / score
        additional_time = needed_score * time_per_point

        # Заокруглення до найближчого більшого кратного 15
        return int((additional_time + 14) // 15) * 15

    @staticmethod
    def get_recomendation(additional_time: int, score: int | None) -> str:
        if score is None or score == 0:
            return "Оцінка розуміння відсутня. Переглянь матеріал."
        if additional_time == 0:
            return "Молодець. Так тримати!"
        return f"Присвяти цій темі ще {additional_time} хвилин"

    @staticmethod
    def process_actual_line(
        line: str, pattern: re.Pattern, errors: list[str]
    ) -> tuple[str, dict] | None:
        match = LearningReport.parse_line(line, pattern, errors)
        if not match:
            return None

        actual = int(match.group("actual"))
        score = int(match.group("score"))

        # Перевірка на конфліктні значення
        if actual <= 0:
            errors.append(f"Некоректний рядок: {line.strip()} (actual має бути більше 0)")
            return None  # Відкидаємо некоректний рядок

        if score < 0 or score > 10:
            errors.append(f"Некоректний рядок: {line.strip()} (score має бути між 0 і 10)")
            return None

        return match.group("abbr"), {
            "date": datetime.strptime(match.group("date"), "%Y-%m-%d"),
            "actual_time": int(match.group("actual")),
            "score": int(match.group("score")),
        }

    @classmethod
    def read_actual(
        cls,
        existing_data: dict[str, "LearningReport"],
        folder_path: Path = Path("data"),
        file_name: str = "actual.csv",
    ) -> FilteredData:
        errors = []
        actual_data, file_errors = cls.read_all_files(
            folder_path, file_name, cls.PATTERN_ACTUAL, cls.process_actual_line, errors
        )

        for abbr, actual_info in actual_data.items():
            if abbr not in existing_data:
                errors.append(f"Абревіатуру {abbr} не знайдено в існуючих даних.")
                continue

            existing_data[abbr] = replace(
                existing_data[abbr],
                actual=actual_info["actual_time"],
                date=actual_info["date"],
                score=actual_info["score"],
            )

        return existing_data, errors

    @classmethod
    def read_motivation(
        cls, folder_path: Path = Path("data"), file_name: str = "motivation.txt"
    ) -> list[str]:
        errors = []
        file_path = folder_path / file_name

        if not cls.check_file_exists(file_path, errors):
            return []

        with file_path.open("r", encoding="utf-8") as file:
            lines = [line.strip() for line in file if line.strip()]

        if not lines:
            errors.append(f"Файл {file_name} порожній.")
            return []

        return lines

    @staticmethod
    def random_motivation(motivations: list[str]) -> str:
        if not motivations:
            return "Мотиваційні фрази відсутні."
        return random.choice(motivations)

    @classmethod
    def read_and_filter_data(
        cls, folder_path: Path, start_date: str | None, end_date: str | None, topic: str | None
    ) -> FilteredData:
        """Зчитує дані, обробляє помилки та фільтрує їх."""
        errors = []

        data, file_errors = cls.read_abbr(folder_path)
        errors.extend(file_errors)

        data, file_errors = cls.read_planned(data, folder_path)
        errors.extend(file_errors)

        data, file_errors = cls.read_actual(data, folder_path)
        errors.extend(file_errors)

        # Фільтр за періодом
        if start_date or end_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else datetime.min
                end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.max
            except ValueError as e:
                raise ValueError("Invalid date format. Expected YYYY-MM-DD.") from e

            data = {
                abbr: report
                for abbr, report in data.items()
                if report.date and start <= report.date <= end
            }

        # Фільтр за темою
        if topic:
            data = {abbr: report for abbr, report in data.items() if report.theme == topic}

        print(f"DEBUG (read_and_filter_data): errors = {errors}")

        return data, errors

    @classmethod
    def generate_report(
        cls,
        folder_path: Path = Path("data"),
        start_date: str | None = None,
        end_date: str | None = None,
        topic: str | None = None,
        motivate: bool = False,
    ) -> str:
        """Генерує звіт за заданим періодом або темою."""
        data, errors = cls.read_and_filter_data(folder_path, start_date, end_date, topic)

        motivations = cls.read_motivation(folder_path)

        report_lines = cls.generate_main_report(data)

        if errors:
            report_lines.append("Помилки під час обробки даних:")
            report_lines.extend(errors)
            report_lines.append("-" * 30)

        if motivate:
            report_lines.append(f"Мотивація: {cls.random_motivation(motivations)}")

        return "\n".join(report_lines)

    @classmethod
    def generate_main_report(cls, data: dict[str, "LearningReport"]) -> list[str]:
        report_lines = []
        for _abbr, report in data.items():
            report_lines.append(f"Тема: {report.theme}")
            report_lines.append(f"Плановий час: {report.planned or 0} хв")
            report_lines.append(f"Фактичний час: {report.actual or 0} хв")
            report_lines.append(f"Оцінка розуміння: {report.score or 'Невідомо'}")

            actual_time = report.actual or 0
            score = report.score if report.score is not None else 0
            additional_time = cls.calculate_additional_time(actual_time, score)
            recommendation = cls.get_recomendation(additional_time, score)

            report_lines.append(f"Рекомендація: {recommendation}")
            report_lines.append("-" * 30)
        return report_lines
