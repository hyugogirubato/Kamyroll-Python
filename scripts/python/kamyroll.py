#!/usr/bin/env python
"""
Script: Kamyroll-Pyhton
Name: Kamyroll
Version: v2021.11.23
"""

import argparse
import sys
from colorama import init
import api
import downloader
import utils


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reset',    '-r',  action='store_true', help='Reset and generate the configuration file')
    parser.add_argument('--login',    '-l',  type=str, help='Login with ID')
    parser.add_argument('--connect',  '-c',  action='store_true', help='Login with configured ID')
    parser.add_argument('--search',          type=str, help='Search a series, films, episode')
    parser.add_argument('--season',   '-s',  type=str, help='Show seasons of a series')
    parser.add_argument('--episode',  '-e',  type=str, help='Show episodes of a season')
    parser.add_argument('--movie',    '-m',  type=str, help='Show movies from a movie list')
    parser.add_argument('--download', '-d',  type=str, help='Download an episode or movie')
    parser.add_argument('--url',      '-u',  type=str, help='Show m3u8 url of episode or movie')
    parser.add_argument('--playlist', '-p',  type=str, help='Download episode list')
    parser.add_argument('--all-subs', '-A',  action='store_true', help='Encode all the subs into the downloaded episodes')
    parser.add_argument('--copy-codec', action='store_true', help='Copy the default codec instead of re-encoding')

    args = parser.parse_args()

    try:
        config = utils.get_config()
    except Exception as e:
        parser.print_help()
        utils.print_msg(e, 1)
        sys.exit(0)

    cr_api = api.crunchyroll(config)

    if args.reset:
        utils.create_config()
        sys.exit(0)
    elif args.login:
        (username, password) = utils.get_login_form(args.login)
        cr_api.login(username, password)
    elif args.connect:
        base64_email = config.get('configuration').get('account').get('email')
        base64_password = config.get('configuration').get('account').get('password')
        if base64_email is None or base64_password is None:
            utils.print_msg('ERROR: No login is configured.', 1)
            sys.exit(0)

        email = utils.base64_to_ascii(base64_email)
        password = utils.base64_to_ascii(base64_password)
        cr_api.login(email, password)
    elif args.search:
        cr_api.search(args.search)
    elif args.season:
        cr_api.season(args.season)
    elif args.episode:
        cr_api.episode(args.episode)
    elif args.movie:
        cr_api.movie(args.movie)
    elif args.download:
        cr_dl = downloader.crunchyroll(config)
        if args.playlist:
            cr_dl.download_season(args.download, args.playlist, args.all_subs, args.copy_codec)
        else:
            cr_dl.download(args.download, args.all_subs, args.copy_codec)
    elif args.url:
        cr_dl = downloader.crunchyroll(config)
        cr_dl.url(args.url)
    else:
        parser.print_help()


if __name__ == '__main__':
    init()
    main()
