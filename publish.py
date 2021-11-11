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
    return response.json()['response']['upload_url']


def upload_img_to_server(img_name, access_token, group_id):
    with open(img_name, 'rb') as file:
        url = get_upload_url(access_token, group_id)
        files = {
            'photo': file
        }
        response = requests.post(url, files=files)
    return response.json()


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
    group_response = group_response.json()
    owner_id = group_response['response'][0]['owner_id']
    media_id = group_response['response'][0]['id']
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
    requests.post('https://api.vk.com/method/wall.post', params=wall_params)


def publish_comics(access_token, group_id, user_id, comics_desc):

    img_name = comics_desc['img_name']
    comment = comics_desc['comment']
    
    server_response = upload_img_to_server(img_name, access_token, group_id)
    owner_id, media_id = upload_img_to_album(access_token, group_id, user_id, server_response)
    upload_img_on_wall(access_token, group_id, comment, owner_id, media_id)


def main():
    load_dotenv()
    access_token = os.environ['ACCESS_TOKEN']
    user_id = os.environ['USER_ID']
    group_id = os.environ['GROUP_ID']

    comics_desc = download_comics()
    publish_comics(access_token, group_id, user_id, comics_desc)
    os.remove(comics_desc['img_name'])


if __name__ == '__main__':
    main()
