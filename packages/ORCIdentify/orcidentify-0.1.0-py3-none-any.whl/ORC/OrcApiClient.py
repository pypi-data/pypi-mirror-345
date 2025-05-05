import json
import random
import string
import requests


class OCRAPIClient:
    def __init__(self):
        self.session_hash = self.generate_session_hash()
        self.upload_id = self.generate_upload_id()

    def generate_session_hash(self):
        def base36encode(number):
            alphabet = string.digits + string.ascii_lowercase
            base36 = ''
            while number:
                number, i = divmod(number, 36)
                base36 = alphabet[i] + base36
            return base36 or alphabet[0]

        random_float = random.random()
        base36_string = base36encode(int(random_float * (36 ** 10)))
        return base36_string[2:]

    def generate_upload_id(self):
        temp_str = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(15))
        return temp_str[2:]

    def upload_file(self, file_path):
        url = f"https://ocr.kgtools.cn/upload?upload_id={self.upload_id}"
        params = {
            "upload_id": self.upload_id,
        }
        files = {
            "files": (
                "example.png",
                open(file_path, 'rb'),
                "application/octet-stream"
            )
        }
        response = requests.request("POST", url, files=files, params=params)
        return response.json()[0]

    def get_query_key(self, file_path_response):
        url = "https://ocr.kgtools.cn/queue/join?"
        data = {
            "data": [
                {
                    "mime_type": "",
                    "orig_name": "enhanced_example.png",
                    "path": file_path_response,
                    "size": 3138,
                    "url": f"https://ocr.kgtools.cn/file={file_path_response}"
                },
                "免费数英验证码识别"
            ],
            "event_data": None,
            "fn_index": 0,
            "session_hash": self.session_hash,
            "trigger_id": 12
        }
        response = requests.request("POST", url, json=data)
        return response

    def get_captcha_data(self):
        url = f"https://ocr.kgtools.cn/queue/data?session_hash={self.session_hash}"
        response = requests.request("GET", url)
        return response

    def process_response(self, response):
        data = json.loads(response.text.split("data: ")[-1])
        return data["output"]["data"][0]


if __name__ == "__main__":
    client = OCRAPIClient()
    file_path = "../captcha.jpg"
    file_path_response = client.upload_file(file_path)
    query_key_response = client.get_query_key(file_path_response)
    captcha_response = client.get_captcha_data()
    result = client.process_response(captcha_response)
    print(result)
