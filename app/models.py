import os
import requests
import json
import dns.resolver
import boto3
import psycopg2
import psycopg2.extras


def get_environment_variables():
    """
    OSの環境変数を取得
    ※ただし /rds/で使用する POSTGRES_URL は除外
    """
    return dict(filter(lambda item: item[0] != "POSTGRES_URL", os.environ.items()))


def get_ecs_task_metadata_base_url():
    """
    タスクメタデータのURLを取得
    """
    return os.getenv('ECS_CONTAINER_METADATA_URI_V4', '')


def get_ecs_task_metadata(base_url, path):
    """
    タスクメタデータを取得
    """
    try:
        url = base_url
        if path != "":
            url = "{0}/{1}".format(base_url, path)
        response = requests.get(url)
        if response.status_code == 200:
            return json.dumps(json.loads(response.text), indent=2)
        else:
            return "{0} : {1}".format(response.status_code, response.text)
    except Exception as e:
        return e


def get_dns_name_servers():
    """
    コンテナローカルのDNSサーバーを取得
    """
    resolver = dns.resolver.Resolver()
    try:
        return resolver.nameservers
    except Exception as e:
        return e
    
def get_resolv_conf():
    """
    resolv.confの中身を取得
    """
    file_path = "/etc/resolv.conf"
    if not os.path.isfile(file_path):
        return str.format("'{}' was not found.", file_path)
    with open(file_path) as f:
        return f.read()


def execute_dns_query(hostname, record_type):
    """
    コンテナローカルから正引きで名前解決を行う
    """
    resolver = dns.resolver.Resolver()
    try:
        answers = resolver.query(hostname, record_type)
        return [str(rdata) for rdata in answers]
    except (dns.resolver.NoAnswer):
        return "No answer."
    except Exception as e:
        return e

def get_dynamodb_employees():
    """
    DynamoDBからサンプルデータを取得
    """
    dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_DEFAULT_REGION', 'ap-northeast-1'))
    # NoSQL WorkBenchのサンプルデータを取得
    #  * https://docs.aws.amazon.com/ja_jp/amazondynamodb/latest/developerguide/workbench.SampleModels.html#workbench.SampleModels.EmployeeDataModel
    table = dynamodb.Table('Employee')
    return table.scan()['Items']


def get_postgres_connection():
    """
    RDS for PostgreSQLへ接続
    """
    return psycopg2.connect(os.getenv('POSTGRES_URL', ''))


def get_pg_stat_activity():
    """
    RDS for PostgreSQLのデータを取得
    """
    with get_postgres_connection() as connection:
        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            # pg_stat_activity の内容を取得
            cursor.execute(
                r"""SELECT pid, backend_type, datname, application_name, client_addr, client_port, state
                      FROM pg_stat_activity
                     ORDER BY pid
                """)
            return cursor.fetchall()
