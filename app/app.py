import sys
from flask import Flask, render_template, request
from models import *

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html', message="Classmethod", python_version=sys.version)


@app.route("/variables/")
def variables():
    variables = get_environment_variables()
    return render_template('variables.html', variables=variables)


@app.route("/metadata/", methods=["GET", "POST"])
def metadata():
    base_url = get_ecs_task_metadata_base_url()
    path = ""
    metadata = ""
    if request.method == "POST":
        path = request.form["path"]
        metadata = get_ecs_task_metadata(base_url, path) 
    return render_template('metadata.html', base_url=base_url, path=path, metadata=metadata)


@app.route("/dynamodb/")
def dynamodb():
    employees = get_dynamodb_employees()
    return render_template('dynamodb.html', employees=employees)


@app.route("/rds/")
def rds():
    sessions = get_pg_stat_activity()
    return render_template('rds.html', sessions=sessions)


if __name__ == "__main__":
    app.run()
