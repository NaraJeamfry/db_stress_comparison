import json
import os

import faker

faker = faker.Faker()


def create_user():
    return {"username": faker.user_name(), "uuid": faker.uuid4()}


def create_tag():
    return {"name": faker.word(), "uuid": faker.uuid4()}


def create_picture(tags, users=None, user=None):
    return {
        "title": faker.sentence(), "uuid": faker.uuid4(),
        "isAbout": faker.random_elements(elements=tags, unique=True, length=faker.pyint(min_value=3, max_value=25)),
        "uploader": user['uuid'] if user else faker.random_element(elements=users)
    }


destination = os.environ.get('OUTPUT_DIRECTORY', '/output')

with open(os.path.join('/output', 'output.json'), 'w') as dest_file:
    # Generate all the data
    tags = []
    users = []
    pictures = []

    for i in range(1000):
        tags.append(create_tag())
    tag_uuids = {tag['uuid'] for tag in tags}
    tag_uuids_list = sorted(tag_uuids)

    for _ in range(100000):
        user = create_user()
        users.append(user)
        for _ in range(faker.pyint(1, 6)):
            pictures.append(create_picture(tag_uuids_list, user=user))
    user_uuids = {user['uuid'] for user in users}
    picture_uuids = {picture['uuid'] for picture in pictures}

    print(f'Added {len(tag_uuids)} tags, {len(user_uuids)} users and {len(picture_uuids)} pictures.')

    # Store data to file as JSON
    print(f'Adding data to JSON.')
    dest_file.write(json.dumps({"tags": tags, "users": users, "pictures": pictures}))
