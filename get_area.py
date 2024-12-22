from config import *
import requests
from services import *
from db import *
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def get_coordinates(lat, lon, id, uri: None = None):
    search_id = str(id)

    try:
        # Ищем ячейку с нужным ID
        cell = sheet.find(search_id)

        # Получаем номер строки, где найден ID
        row_number = cell.row

        if not uri:
            params = {
                'apikey': TokensConfig.GEOCODER_API_KEY,
                'geocode': f'{lon},{lat}',
                'lang': 'ru_RU',
                'kind': 'district',
                'results': 1,
                'format': 'json'
            }
            data = requests.get(UrlConfig.GeoCoder_url, params).json()
            if len(data['response']['GeoObjectCollection']['featureMember']) == 0:
                print("ERROR BY NAME")
                params = {
                    'apikey': TokensConfig.GEOCODER_API_KEY,
                    'geocode': f'{lon},{lat}',
                    'kind': 'district',
                    'results': 1,
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
        # print(data)
        try:
            area = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
                'GeocoderMetaData']['AddressDetails']['Country']['AdministrativeArea']['AdministrativeAreaName']
            # print(area)
            if area == 'Москва':
                district = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
                    'GeocoderMetaData']['AddressDetails']['Country']['AdministrativeArea']['Locality'][
                    'DependentLocality']['DependentLocalityName']
                # print(district)
            if area == 'Московская область':
                district = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
                    'GeocoderMetaData']['AddressDetails']['Country']['AdministrativeArea']['SubAdministrativeArea'][
                    'SubAdministrativeAreaName']
                # print(district)
            try:
                insert_value = TokensConfig.district[district]
                # print(insert_value)
            except Exception:
                insert_value = district
        except Exception as e:
            print(e)
        print(area, insert_value)
        # Записываем данные в колонки D и E этой строки
        sheet.update(f'D{row_number}', area)  # Запись в колонку D
        sheet.update(f'E{row_number}', insert_value)  # Запись в колонку E

        print(f"Данные успешно вставлены в строку {row_number}.")
    except gspread.exceptions.GSpreadException:
        print("ID не найден в таблице.")
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == '__main__':
    conn, curs = connectPg(host='uhome.me', database='uhome_dev_v2', user='artem_analyst',
                                     password='234jgnkSLou43j2nvnjsasadCC', port=5432)

    curs.execute("""
                    select cp.id, cp.name, cp.latitude, cp.longitude from comparison c
                    right join complexes_pars cp on cp.id = c.uhome_id
                    where cp.is_active = true
                    order by id;
                """)
    existing_adr = curs.fetchall()
    # Устанавливаем область доступа
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Загружаем учетные данные
    creds = ServiceAccountCredentials.from_json_keyfile_name('uhome-436914-081b6e911090.json', scope)
    client = gspread.authorize(creds)

    # Открываем таблицу по ID
    spreadsheet_id = '12xSds28w5yXeB5yBDUr7I7k3mJ8SpS-dsXqFtHUZA7U'  # Замените на ваш ID
    sheet = client.open_by_key(spreadsheet_id).sheet1  # Открываем первый лист
    for adr in existing_adr:
        print("ID NAME", adr['id'], adr['name'])
        com = get_coordinates(adr['latitude'], adr['longitude'], adr['id'])
