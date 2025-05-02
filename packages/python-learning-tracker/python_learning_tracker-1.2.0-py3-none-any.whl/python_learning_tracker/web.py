from importlib.resources import files

from flask import Flask, render_template, request

from python_learning_tracker.learning_python import LearningReport

template_path = files("python_learning_tracker").joinpath("templates")
data_folder = files("python_learning_tracker").joinpath("data")

app = Flask(__name__, template_folder=str(template_path))


@app.route("/")
def home():
    return render_template("index.html", title="Головна")


@app.route("/search")
def search():
    query = request.args.get("q", "").lower()
    results = []

    if query:
        topics, errors = LearningReport.read_abbr(folder_path=data_folder)

        for abbr, report in topics.items():
            if query in report.theme.lower() or query in abbr.lower():
                results.append({"title": report.theme, "url": f"/report/topics/{abbr}"})

    return render_template("search.html", title="Результати пошуку", query=query, results=results)


@app.route("/report")
def report():
    report_content = LearningReport.generate_report(folder_path=data_folder, motivate=True)
    return render_template("report.html", report_content=report_content)


@app.route("/report/topics/")
def topics():
    topics_data, errors = LearningReport.read_abbr(folder_path=data_folder)

    topics_data, planned_errors = LearningReport.read_planned(topics_data, folder_path=data_folder)
    topics_data, actual_errors = LearningReport.read_actual(topics_data, folder_path=data_folder)

    errors.extend(planned_errors)
    errors.extend(actual_errors)

    return render_template("topics.html", topics=topics_data, errors=errors)


@app.route("/report/topics/", defaults={"abbr": None})
@app.route("/report/topics/<abbr>")
def topic_detail(abbr):
    if not abbr:
        return "Тема не вказана", 400

    topics_data, _ = LearningReport.read_abbr(folder_path=data_folder)
    topics_data, _ = LearningReport.read_planned(topics_data, folder_path=data_folder)
    topics_data, _ = LearningReport.read_actual(topics_data, folder_path=data_folder)

    if abbr not in topics_data:
        return f"Тема {abbr} не знайдена", 404

    topic = topics_data[abbr]
    additional_time = LearningReport.calculate_additional_time(topic.actual or 0, topic.score or 0)
    recommendation = LearningReport.get_recomendation(additional_time, topic.score)

    return render_template("topic_detail.html", topic=topic, recommendation=recommendation)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


def main():
    app.run(debug=False)


if __name__ == "__main__":
    app.run(debug=True)
