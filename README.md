<img src="https://github.com/hyugogirubato/Kamyroll-python/blob/main/Presentation/img_title.png" width="20%"></img>

## Description
Kamyroll-python is the python version of the program used in the application [Kamyroll](https://github.com/hyugogirubato/Kamyroll). This will allow you to download the videos and subtitles proposed by the crunchyroll catalog or MP4 and ASS format to allow you to view the videos on all your devices without connection.
 
## Features
- Download videos in all resolutions
- Download subtitles in all languages
- Search for videos
- Compatible with or free or premium account
- US-Unblocker for full access to the catalogue
- Available for all platforms (macOS, Windows, Linux, etc.)

## Requirements
- [youtube-dl](https://youtube-dl.org/)
- [Python](https://www.python.org/downloads/) 3+

### Installation
`pip install requests`

## Information
 - The use of the script requires a user to log in. The user can either log in to his session id or account crunchyroll.
 - Each command requires a particular id, if it is not respected, it will be impossible to load valid data.
 - You can change the location of downloads by changing the "dl_root" variable in the script to choose a custom output folder.
 - US unlocking is only available when the user logs in with their credentials.
 - Easy to use guided mode.

## Examples

Login with ID
```
kamyroll.py --login "MAIL:PASSWORD"
```

Login with ID with US unlock
```
kamyroll.py --login "MAIL:PASSWORD" --us_unblocker
```

Connecting with session_id
```
kamyroll.py --session_id "SESSION_ID"
```

### After logging in, you can use the command line or use the guided mode: 

    
    kamyroll.py --guided
    
or


    kamyroll.py -g
    

### Add the link-only flag to skip the download and print the download URL to stdout

    kamyroll.py --link_only

or

    kamyroll.py -l
    
Limited search
```
kamyroll.py --search "TITLE" --limit 10
```

Unlimited search
```
kamyroll.py --search "TITLE"
```

Display the seasons of a series
```
kamyroll.py --seasons "SERIES_ID"
```

Show episodes of a season
```
kamyroll.py --episodes "SEASON_ID"
```

View movies from the movie list
```
kamyroll.py --movie "MOVIE_LISTING_ID"
```

View available formats for streams
```
kamyroll.py --formats "EPISODE_ID or MOVIE_ID"
```

Download the video or subtitles
```
kamyroll.py --download "EPISODE_ID or MOVIE_ID" --format "SUBTITLES_FORMAT or VIDEO_FORMAT"
```

-----------------
*This script was created by the [__Nashi Team__](https://sites.google.com/view/kamyroll/home).  
Find us on [discord](https://discord.com/invite/g6JzYbh) for more information on projects in development.*
