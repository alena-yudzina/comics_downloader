import random
from pathlib import Path
from urllib.parse import unquote, urlsplit

import requests


def get_extension(link):
    path = urlsplit(link).path
    return unquote(Path(path).suffix)


def download_image(link, path):
    response = requests.get(link)
    response.raise_for_status()
    with open(path, 'wb') as img:
        img.write(response.content)


def get_comics_amount():
    response = requests.get('https://xkcd.com/info.0.json')
    response.raise_for_status()
    return response.json()['num']


def download_comics():

    comics_num = get_comics_amount()
    random_id = random.randint(1, comics_num)

    response = requests.get('https://xkcd.com/{}/info.0.json'.format(random_id))
    response.raise_for_status()
    response_json = response.json()

    img_link = response_json['img']
    comment = response_json['alt']

    img_ext = get_extension(img_link)
    img_name = '{}{}'.format(random_id, img_ext)

    download_image(img_link, img_name)

    return {
        'img_name': img_name,
        'comment': comment
    }
