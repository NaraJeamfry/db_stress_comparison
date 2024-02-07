import json
import os

import pydgraph

source_path = os.environ.get('OUTPUT_DIRECTORY', '/output')
temp_path = os.environ.get('TEMP_DIRECTORY', '/tmp')


def transform_picture(old_picture, tags_dict, users_dict):
    new_picture = {f'Picture.{key}': value for key, value in old_picture.items()}
    new_picture['uid'] = f"_:{old_picture['uuid']}"
    new_picture['Picture.uploader'] = {"uid": f"_:{new_picture['Picture.uploader']}"}
    new_picture['Picture.isAbout'] = [{"uid": f"_:{tag_uuid}"} for tag_uuid in new_picture['Picture.isAbout']]

    # Update users and tags
    users_dict[old_picture['uploader']]['User.uploadedPictures'] += [{"uid": f"_:{old_picture['uuid']}"}]
    for tag_uuid in old_picture['isAbout']:
        tags_dict[tag_uuid]['Tag.taggedPictures'] += [{"uid": f"_:{old_picture['uuid']}"}]

    return [new_picture]


with open(os.path.join(source_path, 'output.json')) as source_file:
    contents = json.loads(source_file.read())
    # transaction = client.txn()
    try:
        partial_mutation = []

        tags_dict = {}
        for count, tag in enumerate(contents['tags'], 1):
            tags_dict[tag['uuid']] = {
                'uid': f"_:{tag['uuid']}",
                'Tag.taggedPictures': [],
                **{f'Tag.{key}': value for key, value in tag.items()}
            }
            if count % 10 == 0:
                print(f'Prepared {count} tags.')
        print(f'Successfully (?) prepared {len(tags_dict)} tags.')

        users_dict = {}
        for count, user in enumerate(contents['users'], 1):
            users_dict[user['uuid']] = {
                'uid': f"_:{user['uuid']}",
                'User.uploadedPictures': [],
                **{f'User.{key}': value for key, value in user.items()}
            }
            if count % 1000 == 0:
                print(f'Prepared {count} users.')
        print(f'Successfully (?) prepared {len(contents["users"])} users.')

        for count, picture in enumerate(contents['pictures'], 1):
            partial_mutation += transform_picture(picture, tags_dict, users_dict)
            if count % 1000 == 0:
                # transaction.mutate(set_obj=partial_mutation)
                print(f'Mutated {count} pictures.')
                # partial_mutation = []
        if partial_mutation:
            # transaction.mutate(set_obj=partial_mutation)
            # partial_mutation = []
            pass
        print(f'Successfully (?) mutated {len(contents["pictures"])} pictures.')

        # Update users and tags with relations
        for uuid, user in users_dict.items():
            partial_mutation += [user]
            if len(partial_mutation) >= 1000:
                # transaction.mutate(set_obj=partial_mutation)
                print(f'Mutated {len(partial_mutation)} users.')
                # partial_mutation = []

        for uuid, tag in tags_dict.items():
            partial_mutation += [tag]
            if len(partial_mutation) >= 100:
                # transaction.mutate(set_obj=partial_mutation)
                print(f'Mutated {len(partial_mutation)} tags.')
                # partial_mutation = []

        if partial_mutation:
            # transaction.mutate(set_obj=partial_mutation)
            with open(os.path.join(temp_path, 'live_json.json'), mode='w') as save_file:
                save_file.write(json.dumps(partial_mutation))

        print(f'Committing to DB.')
        # transaction.commit()
        print(f'Committed successfully to the DB.')
    finally:
        # transaction.discard()
        pass
