import os

import requests
from dotenv import load_dotenv

from download import download_random_comics


class VKError(Exception):
    pass


def check_for_errors(response_description):
    if response_description.get('error'):
        raise VKError(response_description['error']['error_msg'])


def get_upload_url(vk_access_token, group_id):

    params = {
        'access_token': vk_access_token,
        'group_id': group_id,
        'v': 5.131,
    }
    response = requests.get(
        'https://api.vk.com/method/photos.getWallUploadServer',
        params=params
    )
    response.raise_for_status()
    response_description = response.json()
    check_for_errors(response_description)
    return response_description['response']['upload_url']


def upload_img_to_server(img_name, vk_access_token, group_id):
    with open(img_name, 'rb') as file:
        url = get_upload_url(vk_access_token, group_id)
        files = {
            'photo': file
        }
        response = requests.post(url, files=files)
    response.raise_for_status()
    response_description = response.json()
    check_for_errors(response_description)
    return response_description


def add_img_to_album(vk_access_token, group_id, user_id,
                     photo_description, server, hash_code):
    group_params = {
        'access_token': vk_access_token,
        'user_id': user_id,
        'group_id': group_id,
        'photo': photo_description,
        'server': server,
        'hash': hash_code,
        'v': 5.131,
    }
    group_response = requests.post(
        'https://api.vk.com/method/photos.saveWallPhoto',
        params=group_params
    )
    group_response.raise_for_status()
    group_response_description = group_response.json()
    check_for_errors(group_response_description)
    owner_id = group_response_description['response'][0]['owner_id']
    media_id = group_response_description['response'][0]['id']
    return owner_id, media_id


def add_img_on_wall(vk_access_token, group_id, comment, owner_id, media_id):
    wall_params = {
        'access_token': vk_access_token,
        'owner_id': '-{}'.format(group_id),
        'from_group': 1,
        'message': comment,
        'attachments': 'photo{}_{}'.format(owner_id, media_id),
        'v': 5.131,
    }
    response = requests.post(
        'https://api.vk.com/method/wall.post',
        params=wall_params
    )
    response.raise_for_status()
    response_description = response.json()
    check_for_errors(response_description)


def publish_comics(vk_access_token, group_id, user_id, img_name, comment):

    server_response = upload_img_to_server(img_name, vk_access_token, group_id)
    photo_description = server_response['photo']
    server = server_response['server']
    hash_code = server_response['hash']
    owner_id, media_id = add_img_to_album(
        vk_access_token, group_id, user_id, photo_description, server, hash_code
    )
    add_img_on_wall(vk_access_token, group_id, comment, owner_id, media_id)


def main():
    load_dotenv()
    vk_access_token = os.environ['VK_ACCESS_TOKEN']
    user_id = os.environ['VK_USER_ID']
    group_id = os.environ['VK_GROUP_ID']
    img_name, comment = download_random_comics()
    try:
        publish_comics(vk_access_token, group_id, user_id, img_name, comment)
    except VKError as err:
        print('Проблемы с VK:', err)
    except requests.exceptions.RequestException as err:
        print('Проблемы с соединением:', err)
    finally:
        os.remove(img_name)


if __name__ == '__main__':
    main()
