import base64
import math
from datetime import datetime
import os
import json
import sys
from termcolor import colored
import requests


def get_config():
    if os.path.exists('config.json'):
        file = open('config.json', 'r')
        config = json.load(file)
        file.close()
        return config
    else:
        print('ERROR: Configuration file not found.')
        sys.exit(0)


def get_login_form(args_login):
    try:
        username = args_login.split(':')[0].strip()
        password = args_login.split(':')[1].strip()
        return username, password
    except Exception as e:
        print_msg("ERROR: Invalid login form.", 1)
        sys.exit(0)


def get_bypass():
    base64_key = 'only_compiled_version'
    key_bytes = base64_key.encode('ascii')
    base64_bytes = base64.b64decode(key_bytes)
    bypass_key = base64_bytes.decode('ascii')
    username = bypass_key.split(':')[0].strip()
    password = bypass_key.split(':')[1].strip()
    return username, password


def print_msg(msg, tp):
    if tp == 0 or tp is None:
        msg = colored(msg, 'white')
    elif tp == 1:
        msg = colored(msg, 'red')
    elif tp == 2:
        msg = colored(msg, 'yellow')
    elif tp == 3:
        msg = colored(msg, 'green')
    elif tp == 4:
        msg = colored(msg, 'cyan')
    elif tp == 5:
        msg = colored(msg, 'magenta')
    print(msg)


def get_authorization(config, refresh):
    if refresh:
        session = get_session(config)

        refresh_token = config.get('configuration').get('token').get('refresh_token')
        data = {
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
            "scope": "offline_access"
        }

        session.headers.update(get_authorization(config, False))
        r = session.post('https://beta-api.crunchyroll.com/auth/v1/token', data=data).json()
        if get_error(r):
            sys.exit(0)

        access_token = r.get('access_token')
        refresh_token = r.get('refresh_token')
        token_type = r.get('token_type')
        json_token = config.get('configuration').get('token')
        json_token['refresh_token'] = refresh_token
        config.get('configuration')['token'] = json_token
        save_config(config)
    else:
        token_type = config.get('configuration').get('token').get('token_type')
        access_token = config.get('configuration').get('token').get('access_token')
    return {'Authorization': '{} {}'.format(token_type, access_token)}


def get_error(json_request):
    if 'error' in json_request:
        error_code = json_request.get('error')

        msg = 'ERROR: Status code: {}'.format(error_code)
        if error_code == 'invalid_grant':
            msg = 'ERROR: Invalid login information.'

        print_msg(msg, 1)
        return True
    elif 'message' in json_request and 'code' in json_request:
        print_msg('ERROR: {}.'.format(json_request.get('message')), 1)
        return True
    else:
        return False


def get_headers(config):
    return {'User-Agent': config.get('configuration').get('user_agent'), 'Content-Type': 'application/x-www-form-urlencoded'}


def save_config(config):
    file = open('config.json', 'w', encoding='utf8')
    file.write(json.dumps(config, indent=4, sort_keys=False, ensure_ascii=False))
    file.close()


def get_locale(config):
    bucket = config.get('configuration').get('token').get('bucket')
    country_code = bucket.split('/')[1]
    items = ['en-US', 'en-GB', 'es-419', 'es-ES', 'pt-BR', 'pt-PT', 'fr-FR', 'de-DE', 'ar-SA', 'it-IT', 'ru-RU']
    locale = items[0]
    for item in items:
        country = item.split('-')[1].strip()
        if country_code == country:
            locale = item
            break
    return locale


def get_metadata_genre(config):
    bucket = config.get('configuration').get('token').get('bucket')
    country_code = bucket.split('/')[1]
    list_language = ['en-US', 'en-GB', 'es-419', 'es-ES', 'pt-BR', 'pt-PT', 'fr-FR', 'de-DE', 'ar-SA', 'it-IT', 'ru-RU']
    list_genre = ['Animation', 'Animation', 'Animación', 'Animación', 'Animação', 'Animação', 'Animation', 'Animation', 'أنيميشن', 'Animazione', 'Анимация']
    genre = list_genre[0]
    for i in range(len(list_language)):
        country = list_language[i].split('-')[1].strip()
        if country_code == country:
            genre = list_genre[i]
            break
    return genre


def get_token(config):
    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day
    hour = datetime.now().hour
    minute = datetime.now().minute
    second = datetime.now().second

    current_time = datetime.strptime('{}-{}-{}T{}:{}:{}Z'.format(year, month, day, hour, minute, second), '%Y-%m-%dT%H:%M:%SZ')
    expires_time = datetime.strptime(config.get('configuration').get('token').get('expires'), '%Y-%m-%dT%H:%M:%SZ')

    if current_time >= expires_time:
        policy = config.get('configuration').get('token').get('policy')
        signature = config.get('configuration').get('token').get('signature')
        key_pair_id = config.get('configuration').get('token').get('key_pair_id')
        return policy, signature, key_pair_id
    else:
        authorization = get_authorization(config, True)
        config = get_config()
        headers = get_headers(config)
        headers.update(authorization)

        session = get_session(config)
        session.headers = headers

        r = session.get('https://beta-api.crunchyroll.com/index/v2').json()
        if get_error(r):
            sys.exit(0)

        cms = r.get('cms')
        bucket = cms.get('bucket')
        policy = cms.get('policy')
        signature = cms.get('signature')
        key_pair_id = cms.get('key_pair_id')
        expires = cms.get('expires')

        json_token = config.get('configuration').get('token')
        json_token['bucket'] = bucket
        json_token['policy'] = policy
        json_token['signature'] = signature
        json_token['key_pair_id'] = key_pair_id
        json_token['expires'] = expires
        config.get('configuration')['token'] = json_token
        save_config(config)
        return policy, signature, key_pair_id


def boolean_to_str(boolean):
    if boolean:
        return 'True'
    else:
        return 'False'


def get_session(config):
    session = requests.session()
    if config.get('preferences').get('proxy').get('is_proxy'):
        uuid = config.get('preferences').get('proxy').get('uuid')
        agent_key = config.get('preferences').get('proxy').get('agent_key')
        host = config.get('preferences').get('proxy').get('host')
        port = config.get('preferences').get('proxy').get('port')

        proxies = {
            "http": "https://user-uuid-{}:{}@{}:{}".format(uuid, agent_key, host, port),
            "https": "https://user-uuid-{}:{}@{}:{}".format(uuid, agent_key, host, port)
        }
        session.proxies.update(proxies)

    return session


def get_premium(config):
    if 'crunchyroll' in config.get('configuration').get('token').get('bucket'):
        return True
    else:
        return False


def get_stream_id(json_stream):
    items = json_stream.get('__links__').get('streams').get('href').split('videos/')[1].split('/')
    id = 'None'
    for i in range(len(items)):
        if items[i + 1] == 'streams':
            id = items[i]
            break
    return id


def get_download_type(json_download):
    href = json_download.get('__links__').get('resource').get('href')
    type = None
    if 'episodes' in href:
        type = 'episodes'
    if 'movies' in href:
        type = 'movies'
    id = href.split('/')[-1]
    return type, id


def get_language_available(json_language):
    language_available = list()
    items = ['', 'en-US', 'en-GB', 'es-419', 'es-ES', 'pt-BR', 'pt-PT', 'fr-FR', 'de-DE', 'ar-SA', 'it-IT', 'ru-RU']
    for item in items:
        if item in json_language:
            language_available.append(item)
    return language_available


def check_characters(title):
    characters = ['\\', '/', ':', '*', '?', '"', '<', '>', '|', '\n', '\r']
    if not title: return title
    for character in characters:
        if character in title:
            title = title.replace(character, '')
    return title.strip()


def get_ffmpeg_language(code):
    language = 'jpn'
    language_code = ['en-US', 'en-GB', 'es-419', 'es-ES', 'pt-BR', 'pt-PT', 'fr-FR', 'de-DE', 'ar-SA', 'it-IT', 'ru-RU', 'jp-JP']
    ffmpeg_language = ['eng', 'bre', 'spa', 'spa', 'por', 'por', 'fra', 'deu', 'ara', 'ita', 'rus', 'jpn']
    for i in range(len(language_code)):
        if code == language_code[i]:
            language = ffmpeg_language[i]
            break
    return language


def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)


def get_language_title(code):
    language_code = ['en-US', 'en-GB', 'es-419', 'es-ES', 'pt-BR', 'pt-PT', 'fr-FR', 'de-DE', 'ar-SA', 'it-IT', 'ru-RU']
    language_titles = ['English (US)', 'English (UK)', 'Español', 'Español (España)', 'Português (Brasil)', 'Português (Portugal)', 'Français (France)', 'Deutsch', 'العربية', 'Italiano', 'Русский']
    language = ''
    for i in range(len(language_code)):
        if code == language_code[i]:
            language = ' [{}]'.format(language_titles[i])
            break
    return language


def get_duration(duration_ms):
    hours = duration_ms / 3.6e6
    minutes = duration_ms / 60000
    seconds = duration_ms / 1000
    while hours > 24:
        hours -= 24
    while minutes > 60:
        minutes -= 60
    while seconds > 60:
        seconds -= 60
    return "{} h {} min {} sec".format(math.floor(hours), math.floor(minutes), math.floor(seconds))
