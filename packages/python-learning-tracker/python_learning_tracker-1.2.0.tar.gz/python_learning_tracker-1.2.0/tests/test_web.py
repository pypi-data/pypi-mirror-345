from pathlib import Path
from unittest.mock import patch

import pytest

from python_learning_tracker.web import app


@pytest.fixture
def client():
    """Тестовий клієнт для Flask-додатку"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_topics():
    """Фікстура для тестових тем"""
    return {
        "CLASS": type(
            "MockReport",
            (object,),
            {"theme": "Класи і екземпляри", "planned": 150, "actual": 120, "score": 8},
        ),
        "MOD": type(
            "MockReport",
            (object,),
            {
                "theme": "Модулі: підключення та використання",
                "planned": 100,
                "actual": 90,
                "score": 7,
            },
        ),
        "FOR": type(
            "MockReport",
            (object,),
            {"theme": "For: цикл для перебору", "planned": 80, "actual": 60, "score": 6},
        ),
        "WHILE": type(
            "MockReport",
            (object,),
            {"theme": "While: цикл з перевіркою умови", "planned": 70, "actual": 50, "score": 5},
        ),
    }


@pytest.fixture
def patch_learning_report(mock_topics):
    """Фікстура для мокування методів LearningReport"""
    with (
        patch(
            "src.python_learning_tracker.learning_python.LearningReport.verify_folder_data",
            return_value=Path("data"),
        ),
        patch(
            "src.python_learning_tracker.learning_python.LearningReport.read_abbr",
            return_value=(mock_topics, []),
        ),
        patch(
            "src.python_learning_tracker.learning_python.LearningReport.read_planned",
            return_value=(mock_topics, []),
        ),
        patch(
            "src.python_learning_tracker.learning_python.LearningReport.read_actual",
            return_value=(mock_topics, []),
        ),
    ):
        yield


@pytest.mark.parametrize(
    "route, expected_text",
    [("/report", "Загальний звіт про навчання"), ("/report/topics/", "Список вивчених тем")],
)
def test_pages(client, route, expected_text, patch_learning_report):
    """Перевірка основних сторінок"""
    response = client.get(route)
    assert response.status_code == 200, f"Помилка на {route}: {response.status_code}"
    assert expected_text in response.get_data(as_text=True), (
        f"Не знайдено '{expected_text}' на {route}"
    )


@pytest.mark.parametrize("abbr", ["CLASS", "MOD"])
def test_topic_detail(client, abbr, mock_topics, patch_learning_report):
    """Перевірка сторінки детальної інформації про тему"""
    response = client.get(f"/report/topics/{abbr}")
    assert response.status_code == 200, f"Помилка на /report/topics/{abbr}: {response.status_code}"
    assert mock_topics[abbr].theme in response.get_data(as_text=True), (
        f"Не знайдено '{mock_topics[abbr].theme}'"
    )


@pytest.mark.parametrize(
    "query, expected_results",
    [
        ("Класи", ["Класи і екземпляри"]),
        ("Модулі", ["Модулі: підключення та використання"]),
        ("цикл", ["While: цикл з перевіркою умови", "For: цикл для перебору"]),
    ],
)
def test_search(client, query, expected_results, patch_learning_report):
    """Перевірка сторінки пошуку"""
    response = client.get(f"/search?q={query}")
    assert response.status_code == 200, f"Помилка на /search?q={query}: {response.status_code}"
    for result in expected_results:
        assert result in response.get_data(as_text=True), (
            f"Не знайдено '{result}' у результатах пошукуза запитом '{query}'"
        )


def test_404_page(client):
    """Перевірка кастомної 404-сторінки"""
    response = client.get("/невідома-сторінка")
    assert response.status_code == 404, "Очікувався статус-код 404, але отримано інший"
    assert "404 - Сторінка не знайдена" in response.get_data(as_text=True), (
        "Текст сторінки 404 відсутній"
    )


def test_report_generation(client):
    """Перевірка генерації загального звіту"""
    mock_report = (
        "Звіт про навчання:\n- Класи і екземпляри: 120 хв, Оцінка: 8\n- Модулі: 90 хв, Оцінка: 7"
    )

    with patch(
        "src.python_learning_tracker.learning_python.LearningReport.generate_report",
        return_value=mock_report,
    ):
        response = client.get("/report")
        assert response.status_code == 200
        assert "Звіт про навчання" in response.get_data(as_text=True)


@pytest.mark.parametrize("abbr", ["CLASS", "MOD", "FOR"])
def test_topics_list(client, abbr, mock_topics, patch_learning_report):
    """Перевірка генерації списку всіх тем"""
    response = client.get("/report/topics/")
    assert response.status_code == 200
    assert mock_topics[abbr].theme in response.get_data(as_text=True), (
        f"Тема '{mock_topics[abbr].theme}' відсутня"
    )


def test_topics_sorting(client, patch_learning_report):
    """Перевірка сортування тем за оцінкою"""
    response = client.get("/report/topics/?order=desc")
    assert response.status_code == 200, "Очікувався статус-код 200, але отримано інший"

    page_content = response.get_data(as_text=True)
    expected_order = [
        "Класи і екземпляри",
        "Модулі: підключення та використання",
        "For: цикл для перебору",
    ]

    last_index = -1
    for theme in expected_order:
        current_index = page_content.find(theme)
        assert current_index > last_index, f"Тема '{theme}' не в правильному порядку!"
        last_index = current_index


def test_topic_not_found(client, patch_learning_report):
    """Перевірка, якщо тема не знайдена"""
    response = client.get("/report/topics/UNKNOWN")
    assert response.status_code == 404
    assert "не знайдена" in response.get_data(as_text=True)


def test_empty_search_query(client):
    """Порожній пошуковий запит"""
    response = client.get("/search?q=")
    assert response.status_code == 200
    assert "Результати пошуку" in response.get_data(as_text=True)


def test_report_empty_data(client):
    """Перевірка генерації порожнього звіту"""
    with patch(
        "src.python_learning_tracker.learning_python.LearningReport.generate_report",
        return_value="",
    ):
        response = client.get("/report")
        assert response.status_code == 200
        assert "Звіт про навчання" not in response.get_data(as_text=True)


def test_invalid_sort_param(client, patch_learning_report):
    """Сторінка повинна відпрацьовувати навіть при невідомому параметрі сортування"""
    response = client.get("/report/topics/?order=asdf")
    assert response.status_code == 200
    assert "Список вивчених тем" in response.get_data(as_text=True)
