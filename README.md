# radio

Reqs:
discord.py (async)
icyparser (custom)

Todo:

-Play while playing now disconnects the stream and reconnects to play. Could end ffmpeg stream w/o disconnect.

-On play, check if the user is in a voice channel before trying to play. Catch the error where if the provided channel is text, it will prompt the user to join a voice channel.

-Add catch for not being able to use embeds in channel/add reactions. Determine full permissions needed for functions.

-The now playing announcement is tied into the play and nowplaying commands and will announce even if the ffmpeg thread init failed.

-play now has a fancy play reaction embed. nowplaying will need to be retooled for a similar embed with stop, next track, buttons. Preliminary work done to add song information to config.json, needs to be referenced in the code and a np embed built.

-needs a loop written to run nowplaying every 300 seconds and then place that information in the "Listening to..." status on the bot. (sort of already done, an example in the code that's not called anywhere yet)

I tend to find most public streams don't stream in mp3 format and don't provide streaminfo like name and artist. I was using a custom title fetcher using mutagen and may still use that in the future, but icyparser is compact and in a package and I like that. However, on Windows, I needed to modify the icyparser.py that was in my python packages to get it to work properly. I'm including that in the root directory of the bot so you can overwrite it once you pip install icyparser.

The issue with icyparser is that when you pip install icyparser on Windows, it uses an older version, and I wasn't successful in trying to get it installed directly from github. Use the version that's present on icyparser's github if anything: https://github.com/GijsTimmers/icyparser


