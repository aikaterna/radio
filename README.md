# radio

Reqs:
discord.py (async)
icyparser (custom)

Todo:

-On play, check if player exists for that server, if so, stop player, then initialize next stream instead of requiring the user to disconnect the stream

-On play, check if the user is in a voice channel before trying to play, and catch the connect error.

-The now playing announcement is tied into the play and nowplaying commands and will announce even if the ffmpeg thread init failed.

-play and nowplaying need the url provided to the commands. Later these should be an embed player with reactions (play) and a nowplaying command with a nice output with possible additional song lookup, but not generally possible for the genre of music I intend to play if this bot goes public. Both play and nowplaying should probably reference a storage item where the currently playing url is stored.

-needs a loop written to run nowplaying every 300 seconds and then place that information in the "Listening to..." status on the bot.


URLs to test/use on the bot:

http://ice1.somafm.com/groovesalad-128-mp3
http://ice1.somafm.com/thetrip-128-mp3
http://ice1.somafm.com/fluid-128-mp3

If you want more, there are tons of streams at somafm.com

I tend to find most public streams don't stream in mp3 format and don't provide streaminfo like name and artist. I was using a custom title fetcher using mutagen and may still use that in the future, but icyparser is compact and in a package and I like that. However, on Windows, I needed to modify the icyparser.py that was in my python packages to get it to work properly. I'm including that in the root directory of the bot so you can overwrite it once you pip install icyparser.

