#!/usr/bin/env python

from asyncio import get_event_loop, sleep
from datetime import datetime
from minio import Minio
from random import randrange, choice
from sqlalchemy import create_engine
from uuid import uuid4
import os

robots = [
    '39350daa-cf1c-4130-8c86-b2e1f0e436f7',
    'a46a59f8-9a7e-4f24-9456-dfe0c013e11b',
    '7b1e9d73-c70d-4d43-84de-74ce383d1aa4'
]
HOST = 'localhost'
PORT = '5433'
engine = create_engine(f'postgresql+psycopg2://postgres:postgres@{HOST}:{PORT}/nimble')


async def random_robot():
    while True:
        robot_id = choice(robots)
        delay = randrange(1, 60)

        query = f'''
        INSERT INTO robot (robot_id, timestamp)
        VALUES ('{robot_id}', '{datetime.now()}')
        '''
        with engine.connect() as connection:
            connection.execute(query)
        print('robot', robot_id)
        await sleep(delay)


async def random_teleop():
    while True:
        robot_id = choice(robots)
        delay = randrange(30, 90)
        query = f'''
        INSERT INTO teleop (robot_id, timestamp)
        VALUES ('{robot_id}', '{datetime.now()}')
        '''
        with engine.connect() as connection:
            connection.execute(query)
        print('teleop', robot_id)
        await sleep(delay)


async def random_image():
    while True:
        robot_id = choice(robots)
        delay = 5
        link = minio_call(robot_id)

        query = f'''
        INSERT INTO image (robot_id, link, timestamp)
        VALUES ('{robot_id}', '{link}', '{datetime.now()}')
        '''

        with engine.connect() as connection:
            connection.execute(query)
        print('image', robot_id, link)
        await sleep(delay)


def minio_call(robot_id, bucket='nimble'):
    client = Minio(
        f'{HOST}:9000',
        secure=False,
        access_key='minio',
        secret_key='miniominio'
    )

    found = client.bucket_exists(bucket)
    if not found:
        client.make_bucket(bucket)

    pictures = get_pictures()
    path = choice(pictures)
    end = path.split('.')[-1]
    key = f'{robot_id}/{str(uuid4())}.{end}'

    client.fput_object(
        bucket, key, path
    )
    return key


def get_pictures():
    files = []
    for (dirpath, dirnames, filenames) in os.walk('static'):
        for file in filenames:
            files.append(os.path.join(dirpath, file))
    return files


def main():
    loop = get_event_loop()
    loop.create_task(random_teleop())
    loop.create_task(random_robot())
    loop.create_task(random_image())
    loop.run_forever()


if __name__ == '__main__':
    main()
