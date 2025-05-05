import json
import requests  # type: ignore

auth_url_postfix = "/api/auth/"
folio_url_postfix = "/api/v1/folio/"


def get_token(base_url: str, user: str, key: str):
    auth_url = base_url + auth_url_postfix
    resp, data = post_json(auth_url, data={'identity': user, 'password': key})
    return data["data"]['access_token']


def get_json(url: str, token=None, payload=None):
    headers = {'Content-Type':
               'application/json', 'Authorization': 'Bearer {}'.format(token)}
    resp = requests.get(url, headers=headers, params=payload)
    return resp, json.loads(resp.text)


def post_json(url, data=None, token=None):
    data = json.dumps(data)
    headers = {'Content-Type':
               'application/json', 'Authorization': 'Bearer {}'.format(token)}
    resp = requests.post(url, headers=headers, data=data)
    return resp, json.loads(resp.text)


def get_folios(base_url: str, token: str):
    folio_url = base_url + folio_url_postfix
    resp, data = get_json(folio_url, token)
    if resp.status_code == 200:
        return data['data']
    raise Exception(resp.text)


def get_folio(base_url: str, token: str, id: str):
    folio_url = base_url + folio_url_postfix
    resp, data = get_json(folio_url + "{}/".format(id), token)
    if resp.status_code == 200:
        return data['data']
    raise Exception(resp.text)
