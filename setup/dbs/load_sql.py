import json
import os
import uuid

import psycopg2

source_path = os.environ.get('OUTPUT_DIRECTORY', '/output')
temp_path = os.environ.get('TEMP_DIRECTORY', '/tmp')

postgres = {
    'db': os.environ.get('POSTGRES_DB', 'test'),
    'url': os.environ.get('POSTGRES_URL', 'localhost'),
    'port': os.environ.get('POSTGRES_PORT', 5432),
    'user': os.environ.get('POSTGRES_USER', 'test'),
    'password': os.environ.get('POSTGRES_PASSWORD', 'test'),
}


def init_tables(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users
    (
        uuid UUID PRIMARY KEY,
        username VARCHAR(255) NOT NULL
    );
    CREATE TABLE IF NOT EXISTS tags
    (
        uuid UUID PRIMARY KEY,
        name VARCHAR(255) NOT NULL
    );
    CREATE TABLE IF NOT EXISTS pictures
    (
        uuid UUID PRIMARY KEY,
        title VARCHAR(1024),
        uploader UUID references users(uuid)
    );
    CREATE TABLE IF NOT EXISTS tagged_pictures
    (
        tag_uuid UUID references tags(uuid),
        picture_uuid UUID references pictures(uuid)
    );
    CREATE TABLE IF NOT EXISTS liked_pictures
    (
        picture_uuid UUID references pictures(uuid),
        user_uuid UUID references users(uuid)
    );
    CREATE TABLE IF NOT EXISTS related_tags
    (
        original_tag UUID references tags(uuid),
        similar_tag UUID references tags(uuid)
    );
    """)


def user_to_insert(user: dict) -> str:
    # return f"""INSERT INTO users VALUES ('{user["uuid"]}', '{user["username"]}')"""
    return f"""{user['uuid']}\t{user['username']}"""


def tag_to_insert(tag: dict) -> str:
    # return f"""INSERT INTO tags VALUES ('{tag["uuid"]}', '{tag["name"]}')"""
    return f"""{tag['uuid']}\t{tag['name']}"""

def picture_to_insert(picture: dict) -> str:
    # return f"""INSERT INTO pictures VALUES ('{picture["uuid"]}', '{picture["title"]}', '{picture["uploader"]}')"""
    return f"""{picture["uuid"]}\t{picture["title"]}\t{picture["uploader"]}"""


def picture_tags_to_inserts(picture: dict) -> [str]:
    return [
        #f"""INSERT INTO tagged_pictures VALUES ('{tag}', '{picture["uuid"]}')"""
        f"""{tag}\t{picture["uuid"]}"""
        for tag in picture["isAbout"]
    ]


with open(os.path.join(source_path, 'output.json')) as source_file:
    contents = json.loads(source_file.read())
    sql_lines = []
    tagged_pictures = []

    # INIT DB
    conn = psycopg2.connect(f"host={postgres['url']} dbname={postgres['db']} user={postgres['user']} password={postgres['user']} port={postgres['port']}")
    with conn:
        with conn.cursor() as cur:
            # START TRANSACTION
            init_tables(cur)

    print(f"Initialized DB tables successfully")

    user_data = []
    for user in contents['users']:
        user_data.append(user_to_insert(user))
    with open(os.path.join(temp_path, 'users.txt'), mode='w') as users_file:
        users_file.write('\n'.join(user_data))
        sql_lines.append(f"""\COPY users FROM '{os.path.join(temp_path, 'users.txt')}'""")

    tag_data = []
    for tag in contents['tags']:
        tag_data.append(tag_to_insert(tag))
    with open(os.path.join(temp_path, 'tags.txt'), mode='w') as tags_file:
        tags_file.write('\n'.join(tag_data))
        sql_lines.append(f"""\COPY tags FROM '{os.path.join(temp_path, 'tags.txt')}'""")

    picture_data = []
    for picture in contents['pictures']:
        picture_data.append(picture_to_insert(picture))
        tagged_pictures += picture_tags_to_inserts(picture)
    with open(os.path.join(temp_path, 'pictures.txt'), mode='w') as pictures_file:
        pictures_file.write('\n'.join(picture_data))
        sql_lines.append(f"""\COPY pictures FROM '{os.path.join(temp_path, 'pictures.txt')}'""")
    with open(os.path.join(temp_path, 'pictures_tagged.txt'), mode='w') as tagged_file:
        tagged_file.write('\n'.join(tagged_pictures))
        sql_lines.append(f"""\COPY tagged_pictures FROM '{os.path.join(temp_path, 'pictures_tagged.txt')}'""")

    # sql_lines += tagged_pictures

    with open(os.path.join(temp_path, 'temp.sql'), mode='w') as sql_file:
        sql_file.write(';\n'.join(sql_lines))
