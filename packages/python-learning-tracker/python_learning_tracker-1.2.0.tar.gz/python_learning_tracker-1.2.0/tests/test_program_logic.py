import pytest

from python_learning_tracker.learning_python import LearningReport


def calculate_time_wrapper(actual_time, score, min_score):
    """
    Допоміжна функція для виклику calculate_additional_time.
    """
    return LearningReport.calculate_additional_time(actual_time, score, min_score)


@pytest.fixture
def default_min_score():
    """Фікстура для мінімального прохідного балу."""
    return 8


@pytest.fixture
def test_cases():
    """Фікстура з тестовими кейсами для функції calculate_additional_time."""
    return [
        (10, 5, 15),  # Потрібно додати 6 хвилин, але округлиться до 15
        (38, 4, 45),  # Потрібно додати 45 хвилин
        (20, 0, 20),  # Оцінка = 0, має повернути actual_time
        (0, 5, 0),  # Якщо actual_time = 0, повертає 0
        (14, 6, 15),  # Заокруглення до 15
        (10, 8, 0),  # Оцінка дорівнює min_score, додатковий час не потрібен
        (12, 1, 90),  # Мінімальна оцінка, має розрахувати багато часу
    ]


def test_calculate_additional_time(test_cases, default_min_score):
    """Перевірка коректності розрахунків функції calculate_additional_time."""
    for actual_time, score, expected in test_cases:
        result = calculate_time_wrapper(actual_time, score, min_score=default_min_score)
        assert result == expected, (
            f"Помилка: для actual_time={actual_time}, "
            f"score={score} очікувалось {expected}, отримано {result}"
        )


@pytest.fixture
def recommendation_cases():
    """Фікстура для перевірки текстів рекомендацій."""
    return [
        (15, 9, "Молодець. Так тримати!"),  # Висока оцінка
        (38, 4, "Присвяти цій темі ще 45 хвилин"),  # Низька оцінка, розрахунок часу
        (10, 0, "Оцінка розуміння відсутня. Переглянь матеріал."),  # Оцінка = 0
        (10, None, "Оцінка розуміння відсутня. Переглянь матеріал."),  # Відсутня оцінка
    ]


def test_recommendation_texts(recommendation_cases, default_min_score):
    """Перевірка текстів рекомендацій при різних сценаріях."""
    for actual_time, score, expected_text in recommendation_cases:
        additional_time = (
            calculate_time_wrapper(actual_time, score, min_score=default_min_score)
            if score is not None
            else 0
        )

        recommendation = LearningReport.get_recomendation(additional_time, score)

        assert recommendation == expected_text, (
            f"Помилка: для actual_time={actual_time}, score={score} "
            f"очікувалось '{expected_text}', отримано '{recommendation}'"
        )


@pytest.fixture
def motivation_phrases():
    """Фікстура для перевірки мотиваційних фраз."""
    return [
        "Не варто боятися помилок — це частина навчання.",
        "Ти рухаєшся вперед, навіть якщо здається, що стоїш на місці.",
        "Кожен крок уперед — це новий рівень розуміння.",
    ]


def test_random_motivation(motivation_phrases):
    """Перевірка, чи рандомно вибираються мотиваційні фрази."""
    selected_phrases = {LearningReport.random_motivation(motivation_phrases) for _ in range(10)}
    assert len(selected_phrases) > 1, "Помилка: мотиваційні фрази не змінюються при виклику."


def test_empty_motivation():
    """Перевірка, що повертається повідомлення при відсутності мотиваційних фраз."""
    result = LearningReport.random_motivation([])
    assert result == "Мотиваційні фрази відсутні.", (
        "Помилка: некоректне повідомлення при порожньому списку фраз."
    )
