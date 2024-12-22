import sys

import requests
import time
from managers import *
from config import *

def get_coordinates(complex_name, adr, uri: None = None):
    if not uri:
        params = {
            'apikey': TokensConfig.GEOCODER_API_KEY,
            'geocode': f'{complex_name + " " + adr}',
            'format': 'json'
        }
        data = requests.get(UrlConfig.GeoCoder_url, params).json()
        print("d", data)
        if len(data['response']['GeoObjectCollection']['featureMember']) == 0:
            print("ERROR BY NAME")
            params = {
                'apikey': TokensConfig.GEOCODER_API_KEY,
                'geocode': adr,
                'format': 'json'
            }
            data = requests.get(UrlConfig.GeoCoder_url, params).json()
    else:
        params = {
            'apikey': TokensConfig.GEOCODER_API_KEY,
            'uri': uri,
            'format': 'json'
        }
        data = requests.get(UrlConfig.GeoCoder_url, params).json()
    coordinates = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
    lon, lat = coordinates.split(' ')
    return lon, lat


def find_nearby_objects(lat, lon, category):
    global TokensConfig
    params = {
        'apikey' : TokensConfig.search_api_key[TokensConfig.search_index],
    'text' : category,
    'lang' : 'ru_RU',
    'll' : f"{lon}, {lat}",
    'spn' : '0.1, 0.1',
    'results' : 10,
    'type' : 'biz'
    }
    response = requests.get(UrlConfig.Search_url, params)
    if response['features']:
        return response.json()
    else:
        TokensConfig.search_index += 1
        if TokensConfig.search_index == len(TokensConfig.search_api_key):
            sys.exit()
        find_nearby_objects(lat, lon, category)


def find_path(name, full_address, lon, lat, res_lon, res_lat, mode, inf_id, id, curs, conn):
    #path_id = insert_path(curs, conn, mode, inf_id, id)
    params = {
        'api_key': TokensConfig.openserv_keys[TokensConfig.openserv_index],
        'start': f"{lon},{lat}",
        'end': f"{res_lon},{res_lat}"
    }
    response = requests.get(f"{UrlConfig.Direction_url}{mode}", params)

    if response.status_code == 200:
        data = response.json()
        if 'features' in data and len(data['features']) > 0:
            duration = data['features'][0]['properties']['segments'][0]['duration']
            duration_minutes = duration / 60

            time.sleep(1.51)
            print(f"{mode} name {name}, adress {full_address}, duration_minutes {duration_minutes}")

            #update_path(curs, conn, duration_minutes, path_id)
            insert_path(curs, conn, duration_minutes, mode, inf_id, id)
    else:
        print("ERROR", response.status_code, response.url, response.content)

    return response.status_code