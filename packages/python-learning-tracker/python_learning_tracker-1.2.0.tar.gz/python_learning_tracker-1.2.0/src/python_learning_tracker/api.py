import sys
from pathlib import Path

from flasgger import Swagger
from flask import Flask, jsonify, make_response, request
from flask_restful import Api, Resource

sys.path.append(str(Path(__file__).resolve().parents[1]))
import xml.etree.ElementTree as ET
from functools import wraps
from pathlib import Path

from werkzeug.exceptions import BadRequest

from python_learning_tracker.learning_python import LearningReport

# Ініціалізація Flask-додатку
app = Flask(__name__)
api = Api(app)
swagger = Swagger(app)

# Визначаємо шлях до папки з даними
data_folder = Path(__file__).resolve().parent / "data"


def to_xml(data_dict):
    # Перетворення списку словників у XML-формат
    root = ET.Element("report")
    if isinstance(data_dict, dict):
        data_dict = [data_dict]
    for item in data_dict:
        block = ET.SubElement(root, "item")
        if isinstance(item, dict):
            for key, value in item.items():
                el = ET.SubElement(block, key)
                el.text = str(value)
        else:
            el = ET.SubElement(block, "value")
            el.text = str(item)
    return ET.tostring(root, encoding="utf-8")


def format_output(func):
    """
    Декоратор, який форматує відповідь залежно від параметра ?format=json/xml
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        fmt = request.args.get("format", "json")
        if fmt == "xml":
            response = make_response(to_xml(result))
            response.headers["Content-Type"] = "application/xml"
            return response
        return jsonify(result)

    return wrapper


class ReportAPI(Resource):
    @format_output
    def get(self):
        """Отримати загальний звіт
        ---
        parameters:
          - name: start_date
            in: query
            type: string
            required: false
            description: Початкова дата (YYYY-MM-DD)
          - name: end_date
            in: query
            type: string
            required: false
            description: Кінцева дата (YYYY-MM-DD)
          - name: topic
            in: query
            type: string
            required: false
            description: Фільтр по темі
          - name: format
            in: query
            type: string
            enum: [json, xml]
            default: json
            description: Формат відповіді
        responses:
          200:
            description: Успішна відповідь
        """
        # Отримуємо параметри з запиту
        start = request.args.get("start_date")
        end = request.args.get("end_date")
        topic = request.args.get("topic")

        # Зчитування та фільтрація даних
        data, errors = LearningReport.read_and_filter_data(
            folder_path=data_folder, start_date=start, end_date=end, topic=topic
        )

        # Побудова звіту у вигляді списку словників
        report = [
            {
                "theme": r.theme,
                "planned": r.planned,
                "actual": r.actual,
                "score": r.score,
                "recommendation": LearningReport.get_recomendation(
                    LearningReport.calculate_additional_time(r.actual or 0, r.score or 0), r.score
                ),
            }
            for r in data.values()
        ]

        return report


# Реєструємо ендпоінт
api.add_resource(ReportAPI, "/api/v1/reports")


class TopicsAPI(Resource):
    @format_output
    def get(self):
        """
        Отримати список тем
        ---
        parameters:
          - name: order
            in: query
            type: string
            enum: [asc, desc]
            required: false
            description: Порядок сортування тем
          - name: format
            in: query
            type: string
            enum: [json, xml]
            required: false
            description: Формат відповіді
        responses:
          200:
            description: Успішна відповідь
        """
        topics_data, errors = LearningReport.read_abbr(folder_path=data_folder)
        topics = list(topics_data.values())

        order = request.args.get("order", "asc")
        topics.sort(key=lambda x: x.theme, reverse=(order == "desc"))

        return [{"abbr": t.abbr, "theme": t.theme} for t in topics]


api.add_resource(TopicsAPI, "/api/v1/topics")


class TopicDetailAPI(Resource):
    @format_output
    def get(self, abbr):
        """
        Отримати детальну інформацію про тему за абревіатурою
        ---
        parameters:
          - name: abbr
            in: path
            type: string
            required: true
            description: Абревіатура теми
          - name: format
            in: query
            type: string
            enum: [json, xml]
            required: false
            description: Формат відповіді
        responses:
          200:
            description: Успішна відповідь
          404:
            description: Тема не знайдена
        """
        topics_data, _ = LearningReport.read_abbr(folder_path=data_folder)
        topics_data, _ = LearningReport.read_planned(topics_data, folder_path=data_folder)
        topics_data, _ = LearningReport.read_actual(topics_data, folder_path=data_folder)

        if abbr not in topics_data:
            return {"error": f"Тема '{abbr}' не знайдена"}, 404

        topic = topics_data[abbr]
        additional_time = LearningReport.calculate_additional_time(
            topic.actual or 0, topic.score or 0
        )
        recommendation = LearningReport.get_recomendation(additional_time, topic.score)

        return {
            "abbr": topic.abbr,
            "theme": topic.theme,
            "planned": topic.planned,
            "actual": topic.actual,
            "score": topic.score,
            "recommendation": recommendation,
        }


api.add_resource(TopicDetailAPI, "/api/v1/topics/<string:abbr>")


class SearchAPI(Resource):
    @format_output
    def get(self):
        query = request.args.get("q")
        if not query:
            raise BadRequest("Missing 'q' parameter")

        """
        Пошук тем за ключовим словом у назві або абревіатурі
        ---
        parameters:
          - name: q
            in: query
            type: string
            required: true
            description: Пошуковий запит (частина теми або абревіатури)
          - name: format
            in: query
            type: string
            enum: [json, xml]
            required: false
            description: Формат відповіді
        responses:
          200:
            description: Успішна відповідь
        """
        query = request.args.get("q", "").lower()
        results = []

        if not query:
            return {"error": "Параметр 'q' є обов'язковим"}, 400

        topics_data, _ = LearningReport.read_abbr(folder_path=data_folder)

        for abbr, report in topics_data.items():
            if query in report.theme.lower() or query in abbr.lower():
                results.append({"abbr": abbr, "theme": report.theme})

        return results


api.add_resource(SearchAPI, "/api/v1/search")


@app.route("/")
def home():
    return {
        "message": "Welcome to the Python Learning Tracker API",
        "available_endpoints": [
            "/api/v1/reports",
            "/api/v1/topics",
            "/api/v1/topics/<abbr>",
            "/api/v1/search",
            "/apidocs",
        ],
    }


@app.errorhandler(400)
def bad_request(error):
    return {"error": "Bad request", "details": str(error)}, 400


@app.errorhandler(404)
def not_found(error):
    return {"error": "Not found"}, 404


@app.errorhandler(500)
def internal_server_error(error):
    return {"error": "Internal server error", "details": str(error)}, 500


@app.errorhandler(ValueError)
def handle_value_error(error):
    return {"error": "Invalid input", "details": str(error)}, 400


# Запуск сервера
def main():
    app.run(debug=True)


