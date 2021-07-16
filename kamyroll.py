import argparse
import requests
import sys
import os
import json
import math
import random
import uuid


def main():
    global display
    global dl_root

    parser = argparse.ArgumentParser()
    parser.add_argument('--login')
    parser.add_argument('--us_unblocker', action="store_true")
    parser.add_argument('--session_id')
    parser.add_argument('--search')
    parser.add_argument('--limit')
    parser.add_argument('--seasons')
    parser.add_argument('--episodes')
    parser.add_argument('--movie')
    parser.add_argument('--formats')
    parser.add_argument('--download')
    parser.add_argument('--format')
    args = parser.parse_args()

    limit = 100
    display = True
    dl_root = "Downloads"
    if args.login:
        login(args.login, args.us_unblocker)
    elif args.session_id:
        start_session(args.session_id, False)
    else:
        if os.path.isfile("config.json"):
            if args.search:
                if args.limit:
                    limit = args.limit
                search(args.search, limit)
            elif args.seasons:
                get_seasons(args.seasons)
            elif args.episodes:
                get_episodes(args.episodes)
            elif args.movie:
                get_movie(args.movie)
            elif args.formats:
                get_formats(args.formats)
            elif args.download:
                if args.format:
                    display = False
                    download(args.download, args.format)
                else:
                    print("ERROR: Download format required.")
                    sys.exit(0)
        else:
            print("ERROR: Login or session required.")
            sys.exit(0)


def init_proxies(proxy):
    if os.path.isfile("proxy.json"):
        os.remove("proxy.json")

    if proxy:
        USER_AGENT = "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
        COUNTRY = "us"
        LIMIT = 3
        PING_ID = random.random()
        EXT_VER = "1.164.641"
        BROWSER = "chrome"
        PRODUCT = "cws"
        UUID = uuid.uuid4().hex
        IS_PREMIUM = 0

        session = requests.session()
        session.headers.update({"User-Agent": USER_AGENT})

        endpoint = "https://client.hola.org/client_cgi/background_init?uuid={}".format(UUID)
        data = {"login": "1", "ver": EXT_VER}
        r = session.post(endpoint, data=data)
        session_key = r.json().get("key")

        if session_key == None:
            print("ERROR: US-Unblocker unavailable.")
            sys.exit(0)

        endpoint = "https://client.hola.org/client_cgi/zgettunnels?country={}&limit={}&ping_id={}&ext_ver={}&browser={}&product={}&uuid={}&session_key={}&is_premium={}".format(
            COUNTRY, LIMIT, PING_ID, EXT_VER, BROWSER, PRODUCT, UUID, session_key, IS_PREMIUM)

        r = session.get(endpoint)

        object_title = get_object_title(COUNTRY, r.json().get("ztun"))
        if object_title == None:
            print("ERROR: US-Unblocker unavailable.")
            sys.exit(0)

        items = r.json().get("ztun").get(object_title)
        agent_types = r.json().get("agent_types").get(object_title)
        host = items[2].split(" ")[1].split(":")[0].strip()
        port = r.json().get("port").get("direct")
        ip = r.json().get("ip_list").get(host)
        protocol = r.json().get("protocol").get(host)
        vendor = r.json().get("vendor").get(host)
        agent_key = r.json().get("agent_key")

        file = open('proxy.json', 'w')
        json.dump({
            "uuid": UUID,
            "ip": ip,
            "host": host,
            "port": port,
            "agent_types": agent_types,
            "country": COUNTRY.upper(),
            "protocol": protocol,
            "vendor": vendor,
            "agent_key": agent_key
        }, file)
        file.close()


def get_object_title(country, object):
    title = None
    titles = ["{}.peer".format(country), country, "id"]
    for i in range(len(titles)):
        if titles[i] in object:
            return titles[i]


def get_proxies():
    if os.path.isfile("proxy.json"):
        file = open('proxy.json', 'r')
        proxy = json.load(file)
        file.close()
        proxies = {
            "http": "https://user-uuid-{}:{}@{}:{}".format(proxy.get("uuid"), proxy.get("agent_key"), proxy.get("host"),
                                                           proxy.get("port")),
            "https": "https://user-uuid-{}:{}@{}:{}".format(proxy.get("uuid"), proxy.get("agent_key"),
                                                            proxy.get("host"), proxy.get("port"))
        }

        return proxies
    else:
        print("ERROR: Proxy file not found.")
        sys.exit(0)


def login(args_login, us_unblocker):
    init_proxies(us_unblocker)

    try:
        email = args_login.split(':')[0].strip()
        password = args_login.split(':')[1].strip()
    except:
        print("ERROR: Invalid login format.")
        sys.exit(0)

    endpoint = "https://api.crunchyroll.com/start_session.0.json?version=1.0&access_token={}&device_type={}&device_id={}".format(
        "LNDJgOit5yaRIWN", "com.crunchyroll.windows.desktop", "Az2srGnChW65fuxYz2Xxl1GcZQgtGgI")
    session = requests.session()

    if us_unblocker:
        session.proxies.update(get_proxies())

    r = session.get(endpoint)
    if "<!DOCTYPE html>" in r.text:
        print("ERROR: Unable to connect to the site with this IP address.")
        sys.exit(0)

    session_id = r.json().get("data").get("session_id")

    endpoint = "https://api.crunchyroll.com/login.0.json"
    data = {"session_id": session_id, "account": email, "password": password}
    r = requests.post(endpoint, data=data)

    start_session(session_id, us_unblocker)


def start_session(session_id, us_unblocker):
    if not us_unblocker and os.path.isfile("proxy.json"):
        os.remove("proxy.json")
    
    endpoint = "https://api.crunchyroll.com/start_session.0.json?session_id={}".format(session_id)
    r = requests.get(endpoint)
    etp_rt = r.cookies.get("etp_rt")
    premium = r.json().get("data").get("user").get("premium")
    if premium == "":
        channel = "-"
    else:
        channel = "crunchyroll"
    country_code = r.json().get("data").get("country_code")

    file = open('config.json', 'w')
    json.dump({
        "session_id": session_id,
        "etp_rt": etp_rt,
        "us_unblocker": us_unblocker,
        "channel": channel,
        "country_code": country_code,
        "maturity_rating": "",
        "policy": "",
        "signature": "",
        "key_pair_id": "",
        "account_id": "",
        "external_id": ""
    }, file)
    file.close()

    headers = get_headers()

    endpoint = "https://beta-api.crunchyroll.com/index/v2"
    r = requests.get(endpoint, headers=headers)

    policy = r.json().get("cms").get("policy")
    signature = r.json().get("cms").get("signature")
    key_pair_id = r.json().get("cms").get("key_pair_id")

    endpoint = "https://beta-api.crunchyroll.com/accounts/v1/me"
    r = requests.get(endpoint, headers=headers)
    account_id = r.json().get("account_id")
    external_id = r.json().get("external_id")

    endpoint = "https://beta-api.crunchyroll.com/accounts/v1/me/profile"
    r = requests.get(endpoint, headers=headers)

    maturity_rating = r.json().get("maturity_rating")

    file = open('config.json', 'w')
    json.dump({
        "session_id": session_id,
        "etp_rt": etp_rt,
        "us_unblocker": us_unblocker,
        "channel": channel,
        "country_code": country_code,
        "maturity_rating": maturity_rating,
        "policy": policy,
        "signature": signature,
        "key_pair_id": key_pair_id,
        "account_id": account_id,
        "external_id": external_id
    }, file)
    file.close()


def get_headers():
    config = get_config()

    session = requests.session()
    endpoint = "https://beta-api.crunchyroll.com/auth/v1/token"
    data = {"grant_type": "etp_rt_cookie"}
    headers = {"Authorization": "Basic bm9haWhkZXZtXzZpeWcwYThsMHE6"}
    cookies = {"session_id": config.get("session_id"), "etp_rt": config.get("etp_rt")}

    session.headers.update(headers)
    session.cookies.update(cookies)
    if config.get("us_unblocker"):
        session.proxies.update(get_proxies())

    r = session.post(endpoint, data=data)

    access_token = r.json().get("access_token")
    token_type = r.json().get("token_type")
    return {"Authorization": "{} {}".format(token_type, access_token)}


def get_config():
    if os.path.isfile("config.json"):
        file = open('config.json', 'r')
        config = json.load(file)
        file.close()
        return config
    else:
        print("Config file not found")
        sys.exit(0)


def get_locale():
    config = get_config()
    locale = "en-US"
    countries = ["", "JP", "US", "LA", "ES", "FR", "BR", "IT", "DE", "RU", "ME"]
    locales = ["", "ja-JP", "en-US", "es-LA", "es-ES", "fr-FR", "pt-BR", "it-IT", "de-DE", "ru-RU", "ar-ME"]
    for i in range(len(countries)):
        if config.get("country_code") == countries[i]:
            locale = locales[i]
            break
    return locale


def search(args_search, args_limit):
    query = args_search
    limit = args_limit

    headers = get_headers()
    endpoint = "https://beta-api.crunchyroll.com/content/v1/search?q={}&n={}&type=&locale={}".format(query, limit,
                                                                                                     get_locale())
    r = requests.get(endpoint, headers=headers)
    items = r.json().get("items")

    for item in items:
        type = item.get("type")
        total = item.get("total")
        if type == "series":
            if total != 0:
                search_series(item.get("items"))
            else:
                print("\n[debug] No results for: series")
        elif type == "movie_listing":
            if total != 0:
                search_movie_listing(item.get("items"))
            else:
                print("\n[debug] No results for: movie_listing")


def search_series(items):
    id = list()
    episode_count = list()
    season_count = list()
    title = list()
    for item in items:
        id.append(item.get("id"))
        episode_count.append(item.get("series_metadata").get("episode_count"))
        season_count.append(item.get("series_metadata").get("season_count"))
        title.append(item.get("title"))

    print("\n[debug] Result for: series")
    print("{0:<15} {1:<40} {2:<10} {3:<10}".format("ID", "Title", "Season", "Episode"))
    for i in range(len(id)):
        print("{0:<15} {1:<40} {2:<10} {3:<10}".format(id[i], title[i], season_count[i], episode_count[i]))


def search_movie_listing(items):
    id = list()
    movie_release_year = list()
    title = list()
    for item in items:
        id.append(item.get("id"))
        movie_release_year.append(item.get("movie_listing_metadata").get("movie_release_year"))
        title.append(item.get("title"))

    print("\n[debug] Result for: movie_listing")
    print("{0:<15} {1:<40} {2:<10}".format("ID", "Title", "Year"))
    for i in range(len(id)):
        print("{0:<15} {1:<40} {2:<10}".format(id[i], title[i], movie_release_year[i]))


def get_seasons(args_seasons):
    series_id = args_seasons

    config = get_config()
    endpoint = "https://beta-api.crunchyroll.com/cms/v2/{}/{}/{}/seasons?series_id={}&locale={}&Signature={}&Policy={}&Key-Pair-Id={}".format(
        config.get("country_code"), config.get("maturity_rating"), config.get("channel"), series_id, get_locale(),
        config.get("signature"), config.get("policy"), config.get("key_pair_id"))
    r = requests.get(endpoint)
    if "message" in r.json():
        print("ERROR: {}.".format(r.json().get("message")))
        sys.exit(0)

    items = r.json().get("items")

    id = list()
    title = list()
    season_number = list()
    for item in items:
        id.append(item.get("id"))
        title.append(item.get("title"))
        season_number.append(item.get("season_number"))

    print("\n[debug] Seasons for {}:".format(series_id))
    print("{0:<15} {1:<10} {2:<40}".format("ID", "Season", "Title"))
    for i in range(len(id)):
        print("{0:<15} {1:<10} {2:<40}".format(id[i], season_number[i], title[i]))


def get_episodes(args_episodes):
    season_id = args_episodes

    config = get_config()
    endpoint = "https://beta-api.crunchyroll.com/cms/v2/{}/{}/{}/episodes?season_id={}&locale={}&Signature={}&Policy={}&Key-Pair-Id={}".format(
        config.get("country_code"), config.get("maturity_rating"), config.get("channel"), season_id, get_locale(),
        config.get("signature"), config.get("policy"), config.get("key_pair_id"))
    r = requests.get(endpoint)
    if "message" in r.json():
        print("ERROR: {}.".format(r.json().get("message")))
        sys.exit(0)

    items = r.json().get("items")

    id = list()
    episode = list()
    title = list()
    is_premium_only = list()

    for item in items:
        episode.append(item.get("episode"))
        title.append(item.get("title"))
        is_premium_only.append(item.get("is_premium_only"))
        if "playback" in item:
            id.append(item.get("__links__").get("streams").get("href").split("videos/")[1].split("/")[0].strip())
        else:
            id.append("Unavailable")

    print("\n[debug] Episodes for {}:".format(season_id))
    print("{0:<15} {1:<10} {2:<10} {3:<40}".format("ID", "Episode", "Premium only", "Title"))
    for i in range(len(id)):
        print("{0:<15} {1:<10} {2:<10} {3:<40}".format(id[i], episode[i], get_boolean(is_premium_only[i]), title[i]))


def get_boolean(boolean):
    if boolean:
        return "True"
    else:
        return "False"


def get_formats(arg_formats):
    global streams_id, audio_locale
    streams_id = arg_formats

    config = get_config()
    endpoint = "https://beta-api.crunchyroll.com/cms/v2/{}/{}/{}/videos/{}/streams?locale={}&Signature={}&Policy={}&Key-Pair-Id={}".format(
        config.get("country_code"), config.get("maturity_rating"), config.get("channel"), streams_id, get_locale(),
        config.get("signature"), config.get("policy"), config.get("key_pair_id"))
    r = requests.get(endpoint)
    if "message" in r.json():
        print("ERROR: {}.".format(r.json().get("message")))
        sys.exit(0)

    href = r.json().get("__links__").get("resource").get("href")
    if "movies" in href:
        type = "movies"
        id = href.split("movies/")[1].split("/")[0].strip()
    else:
        type = "episodes"
        id = href.split("episodes/")[1].split("/")[0].strip()

    init_download(type, id)
    audio_locale = r.json().get("audio_locale")
    formats_subtitles(get_items(r.json().get("subtitles")))
    formats_videos(get_items(r.json().get("streams").get("adaptive_hls")))


def init_download(type, id):
    global dl_path, dl_title, dl_cover

    config = get_config()
    endpoint = "https://beta-api.crunchyroll.com/cms/v2/{}/{}/{}/{}/{}?locale={}&Signature={}&Policy={}&Key-Pair-Id={}".format(
        config.get("country_code"), config.get("maturity_rating"), config.get("channel"), type, id, get_locale(),
        config.get("signature"), config.get("policy"), config.get("key_pair_id"))
    r = requests.get(endpoint)
    if type == "movies":
        title = r.json().get("title")
        thumbnails = json.dumps(r.json().get("images").get("thumbnail")).replace("[", "").replace("]", "")
        thumbnail = json.loads("[{}]".format(thumbnails))

        dl_path = check_characters(title)
        dl_title = check_characters(title)
        dl_cover = thumbnail[len(thumbnail) - 1].get("source")
    else:
        series_id = r.json().get("series_id")
        series_title = r.json().get("series_title")
        season_title = r.json().get("season_title")
        season_number = r.json().get("season_number")
        episode = r.json().get("episode")
        title = r.json().get("title")

        endpoint = "https://beta-api.crunchyroll.com/cms/v2/{}/{}/{}/series/{}?locale={}&Signature={}&Policy={}&Key-Pair-Id={}".format(
            config.get("country_code"), config.get("maturity_rating"), config.get("channel"), series_id, get_locale(),
            config.get("signature"), config.get("policy"), config.get("key_pair_id"))
        r = requests.get(endpoint)
        poster_tall = json.dumps(r.json().get("images").get("poster_tall")).replace("[", "").replace("]", "")
        poster = json.loads("[{}]".format(poster_tall))

        dl_path = "{}\\S{} - {}".format(check_characters(series_title), season_number, check_characters(season_title))
        dl_title = "[S{}.Ep{}] {} - {}".format(season_number, episode, check_characters(series_title),
                                               check_characters(title))
        dl_cover = poster[len(poster) - 1].get("source")


def check_characters(title):
    characters = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    for character in characters:
        if character in title:
            title = title.replace(character, '#')
    return title


def get_items(item):
    locales = ["", "ja-JP", "en-US", "es-LA", "es-ES", "fr-FR", "pt-BR", "it-IT", "de-DE", "ru-RU", "ar-ME"]
    items = list()
    for i in range(len(locales)):
        if locales[i] in item:
            items.append(item.get(locales[i]))
    return items


def formats_subtitles(items):
    global subtitles_format_code, subtitles_url, subtitles_extension
    subtitles_format_code = list()
    locale = list()
    subtitles_url = list()
    subtitles_extension = list()

    for item in items:
        locale.append(item.get("locale"))
        subtitles_url.append(item.get("url"))
        subtitles_extension.append(item.get("format"))
        subtitles_format_code.append("{}-subtitles-{}".format(streams_id, item.get("locale")))

    if display:
        print("\n[debug] Subtitles for {}:".format(streams_id))
        print("{0:<40} {1:<20} {2:<20}".format("Format code", "Extension", "Language"))
        for i in range(len(locale)):
            print("{0:<40} {1:<20} {2:<20}".format(subtitles_format_code[i], subtitles_extension[i],
                                                   get_locale_title(locale[i])))


def formats_videos(items):
    global videos_format_code, videos_url
    videos_format_code = list()
    resolutions = list()
    note = list()
    videos_url = list()

    index = 1
    for item in items:
        hardsub_locale = item.get("hardsub_locale")
        r = requests.get(item.get("url"))

        streams = r.text.split('#EXT-X-STREAM')

        for stream in streams:
            if "RESOLUTION" in stream:
                bandwidth = stream.split("BANDWIDTH=")[1].split(",")[0].strip()
                resolution = stream.split("RESOLUTION=")[1].split(",")[0].strip()
                frame_rate = stream.split("FRAME-RATE=")[1].split(",")[0].strip()
                codecs = stream.split("CODECS=\"")[1].split("\"")[0].strip()
                url = "http{}".format(stream.split("http")[1].strip())

                format = "{}-video".format(streams_id)
                if hardsub_locale != "":
                    format = "{}-hardsub-{}".format(format, hardsub_locale)

                format = "{}-{}".format(format, index)

                videos_format_code.append(format)
                resolutions.append(resolution)

                note.append(
                    "[{}] {}k , {}, {}, {}".format(audio_locale, bandwidth, codecs.split(",")[0].strip(), frame_rate,
                                                   codecs.split(",")[1].strip()))
                videos_url.append(url)
                index += 1

    if display:
        print("\n[debug] Videos for {}:".format(streams_id))
        print("{0:<40} {1:<20} {2:<20} {3:<40}".format("Format code", "Extension", "Resolution", "Note"))
        for i in range(len(videos_format_code)):
            print("{0:<40} {1:<20} {2:<20} {3:<40}".format(videos_format_code[i], "mp4", resolutions[i], note[i]))


def get_locale_title(locale):
    title = "Disabled"
    titles = ["Disabled", "Japanese", "English (US)", "Spanish (Latin America)", "Spanish (Spain)",
              "French (France)", "Portuguese (Brazil)", "Italian", "German", "Russian", "Arabic"]
    locales = ["", "ja-JP", "en-US", "es-LA", "es-ES", "fr-FR", "pt-BR", "it-IT", "de-DE", "ru-RU",
               "ar-ME"]
    for i in range(len(titles)):
        if locale == locales[i]:
            title = titles[i]
            break
    return title


def get_movie(arg_movie):
    movie_listing_id = arg_movie

    config = get_config()
    endpoint = "https://beta-api.crunchyroll.com/cms/v2/{}/{}/{}/movies?movie_listing_id={}&locale={}&Signature={}&Policy={}&Key-Pair-Id={}".format(
        config.get("country_code"), config.get("maturity_rating"), config.get("channel"), movie_listing_id,
        get_locale(),
        config.get("signature"), config.get("policy"), config.get("key_pair_id"))
    r = requests.get(endpoint)

    items = r.json().get("items")

    id = list()
    title = list()
    duration_ms = list()
    is_premium_only = list()
    for item in items:
        title.append(item.get("title"))
        duration_ms.append(item.get("duration_ms"))
        is_premium_only.append(item.get("is_premium_only"))
        if "playback" in item:
            id.append(item.get("__links__").get("streams").get("href").split("videos/")[1].split("/")[0].strip())
        else:
            id.append("Unavailable")

    print("\n[debug] Movies for {}:".format(movie_listing_id))
    print("{0:<15} {1:<20} {2:<20} {3:<40}".format("ID", "Premium only", "Duration", "Title"))
    for i in range(len(id)):
        print(
            "{0:<15} {1:<20} {2:<20} {3:<40}".format(id[i], get_boolean(is_premium_only[i]),
                                                     get_duration(duration_ms[i]), title[i]))


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


def download(args_download, args_format):
    global dl_url, dl_extension, dl_format

    stream_id = args_download
    dl_format = args_format

    print("[debug] Loading formats")
    get_formats(stream_id)
    dl_url = ""
    dl_extension = ""
    if "video" in dl_format:
        for i in range(len(videos_format_code)):
            if dl_format == videos_format_code[i]:
                dl_url = videos_url[i]
                dl_extension = "mp4"
                break
    elif "subtitles" in dl_format:
        for i in range(len(subtitles_format_code)):
            if dl_format == subtitles_format_code[i]:
                dl_url = subtitles_url[i]
                dl_extension = subtitles_extension[i]
                break
    else:
        print("ERROR: Format not found")
        sys.exit(0)

    if dl_url != "" and dl_extension != "":
        create_folder()
        download_cover()
        if "video" in dl_format:
            download_video()
        else:
            download_subtitles()
    else:
        print("ERROR: Data loading error")
        sys.exit(0)


def download_cover():
    if os.path.isfile("{}\\{}\\cover.jpg".format(dl_root, dl_path)):
        os.remove("{}\\{}\\cover.jpg".format(dl_root, dl_path))

    print("[debug] Cover download")
    response = requests.get(dl_cover)
    file = open("{}\\{}\\cover.jpg".format(dl_root, dl_path), "wb")
    file.write(response.content)
    file.close()


def create_folder():
    if not os.path.exists("{}\\{}".format(dl_root, dl_path)):
        os.makedirs("{}\\{}".format(dl_root, dl_path))


def download_video():
    print("[debug] Video download")
    try:
        os.system('youtube-dl -o "{}\\{}\\{}.%(ext)s" "{}"'.format(dl_root, dl_path, dl_title, dl_url))
    except:
        print("ERROR: Download error")
        sys.exit(0)


def download_subtitles():
    output = "{} [{}]".format(dl_title, get_locale_title(dl_format.split("subtitles-")[1].strip()))

    if os.path.isfile("{}/{}/{}.{}".format(dl_root, dl_path, output, dl_extension)):
        os.remove("{}/{}/{}.{}".format(dl_root, dl_path, output, dl_extension))

    print("[debug] Subtitles download")
    response = requests.get(dl_url)
    file = open("{}/{}/{}.{}".format(dl_root, dl_path, output, dl_extension), "wb")
    file.write(response.content)
    file.close()
    sys.exit(0)


if __name__ == '__main__':
    main()
