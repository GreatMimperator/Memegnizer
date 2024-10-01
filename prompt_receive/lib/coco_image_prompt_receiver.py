import os.path
from typing import Optional

import requests
from PIL import Image
from requests import Response
from retrying import retry

RECEIVE_PROMPT_MAX_DELAY_SECS = 10


def bad_response_status_check(response: Response, extected_status_code: int):
    if response.status_code != extected_status_code:
        raise Exception(f"Bad response status (should be {extected_status_code} - got {response.status_code}, "
                        f"full response is: {response.json()}")


def setup_file_path(path_on_server: str) -> str:
    """Вернет токен, подтвердит установку пути, по которому будет загружена картинка"""
    url = "https://cococlip.ai/api/v1/upload"

    # Заголовки запроса (если необходимы)
    headers = {
        'Content-Type': 'application/json',
    }

    # Полезная нагрузка
    payload = {
        "type": "blob.generate-client-token",
        "payload": {
            "pathname": path_on_server,
            "callbackUrl": "https://cococlip.ai/api/v1/upload",
            "clientPayload": None,
            "multipart": False
        }
    }

    # Отправка POST-запроса
    response = requests.post(url, json=payload, headers=headers)

    bad_response_status_check(response, 200)

    return response.json()["clientToken"]


def load_image(path_on_server: str, token: str, file_path: str) -> str:
    """Вернет ссылку на url генерирующегося промпта"""
    url = f"https://blob.vercel-storage.com/{path_on_server}"

    # Заголовки запроса
    headers = {
        'Authorization': f"Bearer {token}"
    }

    with open(file_path, "rb") as file:
        file_bytes = file.read()
    # Отправка PUT-запроса с изображением
    response = requests.put(url, headers=headers, data=file_bytes)

    bad_response_status_check(response, 200)

    return response.json()["url"]


def get_prompt_id_query(prompt_url: str) -> str:
    """Получит по ссылке текст промпта"""
    base_url = "https://cococlip.ai/api/v1/imagetoprompt/imageclip"

    # Параметры запроса
    params = {
        'image': prompt_url
    }

    # Отправка GET-запроса
    response = requests.get(base_url, params=params)

    bad_response_status_check(response, 200)

    response_json = response.json()

    return response_json["id"]


@retry(stop_max_delay=RECEIVE_PROMPT_MAX_DELAY_SECS * 1000)
def receive_prompt_by_id(prompt_id: str):
    base_url = "https://cococlip.ai/api/v1/imagetoprompt/imageclippoll"

    params = {
        'promptId': prompt_id,
    }

    response = requests.get(base_url, params=params)

    bad_response_status_check(response, 200)

    response_json = response.json()

    return response_json["prompt"]


def receive_prompt(file_path: str, server_image_name: str) -> str:
    """Получит промпт для переданной картинки"""
    path_on_server = f"temp/ImageToPrompt-{server_image_name}"
    token = setup_file_path(path_on_server)
    generated_prompt_url = load_image(path_on_server, token, file_path)
    prompt_id = get_prompt_id_query(generated_prompt_url)
    return receive_prompt_by_id(prompt_id)
