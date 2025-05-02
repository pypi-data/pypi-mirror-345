import json


def load_json_result(content: str):
    if content.startswith('```json'):
        return json.loads(content[7:-3])
    return json.loads(content)
