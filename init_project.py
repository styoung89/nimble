from kafka.admin import KafkaAdminClient, NewTopic
from kafka import BrokerConnection
from sqlalchemy import create_engine
import requests

HOST = 'localhost'
POSTGRES_PORT = '5433'


def create_database():
    engine = create_engine(f'postgresql+psycopg2://postgres:postgres@{HOST}:{POSTGRES_PORT}/postgres')

    query = '''
    CREATE DATABASE nimble;
    '''

    with engine.connect() as connection:
        connection.execution_options(isolation_level="AUTOCOMMIT")
        connection.execute(query)


def create_tables():
    engine = create_engine(f'postgresql+psycopg2://postgres:postgres@{HOST}:{POSTGRES_PORT}/nimble')
    query = '''
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    '''

    robot_query = '''
    CREATE TABLE IF NOT EXISTS robot (
    uuid        UUID UNIQUE  DEFAULT uuid_generate_v4() NOT NULL,
    robot_id    UUID,
    event_id    UUID,
    timestamp   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    '''

    teleop_query = '''
        CREATE TABLE IF NOT EXISTS teleop (
    uuid        UUID UNIQUE NOT NULL  DEFAULT uuid_generate_v4(),
    robot_id    UUID,
    event_id    UUID DEFAULT uuid_generate_v4(),
    teleop_id   UUID DEFAULT uuid_generate_v4(),
    timestamp   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )'''

    images_query = '''
    CREATE TABLE IF NOT EXISTS image (
    uuid        UUID   UNIQUE NOT NULL DEFAULT uuid_generate_v4(),
    robot_id    UUID,
    link        VARCHAR(500),
    timestamp   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    '''
    with engine.connect() as connection:
        connection.execute(query)
        connection.execute(robot_query)
        connection.execute(teleop_query)
        connection.execute(images_query)


def create_topic():
    admin_client = KafkaAdminClient(
        bootstrap_servers=f"{HOST}:9092",
        client_id='test'
    )

    topic_list = [NewTopic(name="nimble", num_partitions=1, replication_factor=1)]
    admin_client.create_topics(new_topics=topic_list, validate_only=False)


def create_connector(name: str):
    payload = {
        "name": f"{name}-connector",
        "config": {
            "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
            "plugin.name": "pgoutput",
            "database.hostname": f"host.docker.internal",
            "database.port": f"{POSTGRES_PORT}",
            "database.user": "postgres",
            "database.password": "postgres",
            "database.dbname": "nimble",
            "database.server.name": "postgres",
            "table.include.list": f"public.{name}"
        }
    }
    response = requests.post(f'http://{HOST}:8083/connectors', json=payload)
    if response.status_code == 409:
        pass
    elif response.status_code != 201:
        raise Exception(response.json())


if __name__ == "__main__":
    # create_database()
    # create_tables()
    for item in ('robot', 'image', 'teleop'):
        create_connector(item)
