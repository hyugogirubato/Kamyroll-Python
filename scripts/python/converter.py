#!/usr/bin/env python
"""
Script: Kamyroll-Pyhton
Name: Converter
Version: v2021.11.23
"""

import os
import sys
import requests
import utils


class Subtitles:
    def __init__(self, output, language):
        self.output = output[:251]
        self.language = language

    def download(self, subtitles_url):
        output = '{}{}.{}'.format(self.output, utils.get_language_title(self.language), 'ass')
        if os.path.exists(output):
            os.remove(output)

        r = requests.get(subtitles_url)
        file = open(output, 'wb')
        file.write(r.content)
        file.close()

    def convert(self, extension):
        output = '{}{}.{}'.format(self.output, utils.get_language_title(self.language), extension)
        if os.path.exists('{}{}.{}'.format(self.output, utils.get_language_title(self.language), 'ass')):
            if os.path.exists(output):
                os.remove(output)

            command = [
                'ffmpeg',
                '-hide_banner',
                '-loglevel',
                'error',
                '-i',
                '"{}{}.{}"'.format(
                    self.output, utils.get_language_title(self.language), 'ass'
                ),
                '"{}"'.format(output),
                '-n',
            ]
            try:
                os.system(' '.join(command))
            except KeyboardInterrupt:
                utils.print_msg('KeyboardInterrupt', 1)
                sys.exit(0)
            except Exception as e:
                utils.print_msg(e, 1)
                sys.exit(0)
        else:
            utils.print_msg('WARRING: Source subtitle file is unavailable.', 2)
