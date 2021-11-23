import os

import requests
from dotenv import load_dotenv

from download import download_comics


def get_upload_url(access_token, group_id):

    params = {
        'access_token': access_token,
        'group_id': group_id,
        'v': 5.131,
    }
    response = requests.get('https://api.vk.com/method/photos.getWallUploadServer', params=params)
    response.raise_for_status()
    response_description = response.json()
    if response_description.get('error'):
        raise Exception(response_description['error']['error_msg'])
    return response_description['response']['upload_url']


def upload_img_to_server(img_name, access_token, group_id):
    with open(img_name, 'rb') as file:
        url = get_upload_url(access_token, group_id)
        files = {
            'photo': file
        }
        response = requests.post(url, files=files)
    response.raise_for_status()
    response_description = response.json()
    if response_description.get('error'):
        raise Exception(response_description['error']['error_msg'])
    return response_description


def upload_img_to_album(access_token, group_id, user_id, server_response):
    group_params = {
        'access_token': access_token,
        'user_id': user_id,
        'group_id': group_id,
        'photo': server_response['photo'],
        'server': server_response['server'],
        'hash': server_response['hash'],
        'v': 5.131,
    }
    group_response = requests.post('https://api.vk.com/method/photos.saveWallPhoto', params=group_params)
    group_response.raise_for_status()
    group_response_description = group_response.json()
    if group_response_description.get('error'):
        raise Exception(group_response_description['error']['error_msg'])
    owner_id = group_response_description['response'][0]['owner_id']
    media_id = group_response_description['response'][0]['id']
    return owner_id, media_id


def upload_img_on_wall(access_token, group_id, comment, owner_id, media_id):
    wall_params = {
        'access_token': access_token,
        'owner_id': '-{}'.format(group_id),
        'from_group': 1,
        'message': comment,
        'attachments': 'photo{}_{}'.format(owner_id, media_id),
        'v': 5.131,
    }
    response = requests.post('https://api.vk.com/method/wall.post', params=wall_params)
    response_description = response.json()
    if response_description.get('error'):
        raise Exception(response_description['error']['error_msg'])


def publish_comics(access_token, group_id, user_id, img_name, comment):
    
    server_response = upload_img_to_server(img_name, access_token, group_id)
    owner_id, media_id = upload_img_to_album(access_token, group_id, user_id, server_response)
    upload_img_on_wall(access_token, group_id, comment, owner_id, media_id)


def main():
    load_dotenv()
    access_token = os.environ['ACCESS_TOKEN']
    user_id = os.environ['USER_ID']
    group_id = os.environ['GROUP_ID']
    img_name, comment = download_comics()
    try:
        publish_comics(access_token, group_id, user_id, img_name, comment)
    except Exception as Err:
        print(Err)
    finally:
        os.remove(img_name)


if __name__ == '__main__':
    main()
