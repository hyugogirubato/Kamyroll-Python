![Kamyroll_Python](https://github.com/hyugogirubato/Kamyroll-Python/raw/6c4908104ea278743152f3ac53015f8eab95b14e/Presentation/img_title.png)

## Description
Kamyroll-python is the python version of the program used in the application [Kamyroll](https://github.com/hyugogirubato/Kamyroll). This will allow you to download the videos and subtitles proposed by the Crunchyroll catalog or MP4 and ASS format to allow you to view the videos on all your devices without connection.
 
## Features
- Download videos in all resolutions
- Download subtitles in all languages
- Search for videos
- Compatible with or free or premium account
- Use a proxy to unblock the entire catalog
- Available for all platforms (macOS, Windows, Linux, etc.)
- Download all available episodes and movies
- Videos in mp4, mkv with or without Hardsub
- Download episodes by interval or number (bash download)

## Requirements
- [ffmpeg](https://www.ffmpeg.org)
- [Python](https://www.python.org/downloads) 3+

### Installation
Pypi: https://github.com/insidewhy/cuteroll

```bash
pip install -r requirements.txt
```

## Information
 - To use the script log in with your email or username and your Crunchyroll password.
 - Configure your configuration file according to your preferences.
 - If you don't have Python, you can use the compiler version for Windows.

## Preferences

#### Video resolution

Resolution | Quality
------------ | -------------
"1080" | FHD
"720" | HD
"480" | SD
"360" | SD
"240" | SD

#### Playlist selection

Resolution | Quality
------------ | -------------
"[3:]" | Take all episodes after 3
"[2:4]" | Take episodes 2 to 4 included
"[-2]" | Take the penultimate episode from the list
"[-2:]" | Take all the last episode from the penultimate
"[:-2]" | Take all episodes except the last 2
"8" | Take episode 8

#### Subtitle language 

Language | Title
------------ | -------------
"" | Without subtitles
"en-US" | English (US)
"en-GB" | English (UK)
"es-419" | Español
"es-ES" | Español (España)
"pt-BR" |Português (Brasil)
"pt-PT" | Português (Portugal)
"fr-FR" | Français (France)
"de-DE" | Deutsch
"ar-SA" | العربية
"it-IT" | Italiano
"ru-RU" | Русский

## Proxy configuration
Secure proxy compatible with Crunchyroll: https://github.com/Snawoot/hola-proxy
![proxy_example](/resources/img_proxy.png)

#### Command
- RED: Selected region
  
#### Proxy in $HOME/.config/kamyroll.json
- GREEN: uuid
- BLUE: agent\_key
- PURPLE: host
- YELLOW: port

## Examples

### Login with ID
```
kamyroll --login "MAIL:PASSWORD"
kamyroll -l "MAIL:PASSWORD"
```

### Login with configured ID
```
kamyroll --connect
kamyroll -c
```

### Search a series, films, episode
```
kamyroll --search "QUERY"
```

### Show seasons of a series
```
kamyroll --season "SERIES_ID"
kamyroll -s "SERIES_ID"
```

### Show episodes of a season
```
kamyroll --episode "SEASON_ID"
kamyroll -e "SEASON_ID"
```

### Show movies from a movie list
```
kamyroll --movie "MOVIE_ID"
kamyroll -m "MOVIE_ID"
```

### Download an episode or movie
```
kamyroll --download "EPISODE_ID or MOVIE_ID"
kamyroll -d "EPISODE_ID or MOVIE_ID"
```

### Download playlist (bash download)
```
kamyroll --download "SEASON_ID" --playlist "[START:END]"
kamyroll -d "SEASON_ID" -p "[START:END]"
```

### Get the video stream link (m3u8)
```bash
kamyroll --url "EPISODE_ID or MOVIE_ID"
kamyroll -u "EPISODE_ID or MOVIE_ID"
```

---
*This script was created by the [__Nashi Team__](https://sites.google.com/view/kamyroll/home).  
Find us on [discord](https://discord.com/invite/g6JzYbh) for more information on projects in development.*
