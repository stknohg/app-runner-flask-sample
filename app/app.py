import sys
from importlib.metadata import version
from flask import Flask, render_template, request
from models import *

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html', message="Classmethod", python_version=sys.version, flask_version=version("flask"), boto3_version=version("boto3"))


@app.route("/variables/")
def variables():
    variables = get_environment_variables()
    return render_template('variables.html', variables=variables)


@app.route("/dns/", methods=["GET", "POST"])
def dns():
    name_servers = get_dns_name_servers()
    resolv_conf = get_resolv_conf()
    hostname = "dev.classmethod.jp"
    record_type = "A"
    lookup_result = ""
    if request.method == "POST":
        hostname = request.form["hostname"]
        record_type = request.form["record_type"]
        lookup_result = execute_dns_query(hostname, record_type) 
    return render_template('dns.html', name_servers=name_servers, resolv_conf=resolv_conf, hostname=hostname, record_type=record_type, lookup_result=lookup_result)


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
