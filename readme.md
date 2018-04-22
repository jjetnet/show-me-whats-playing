# show me what's playing
python script to display media information on a chromecast TV of currently playing music on any local chomecast audio . The information is updated when a new stong starts. Works with spotify, google play music, etc.

Combined with a php script to start the service through a web request and a simple ifttt the voice command 'show me what's playing' on Google Home will display information on currently playing music on your TV (artist/album/song title/streaming service/almbum art).


I designed this to be run on a rapsberry pi. An apache web server must be running on the same computer. Files in www folder should go on apache's www/html folder (eg /var/www or /var/www/html depending on version and settings). The script needs to be run with sufficient privileges to be able to write on that folder.


# Usage:
### From command line:
 python showmewhatsplaying.py

### Using the php script:

You may need to edit it for correct installation paths and python path. This assumes the script is in /home/pi/pyautomation/.
To launch the script call the web page:
 http://raspberrypiIPaddress/showmedia.php?action=start

### Using Google Home: 

create an If This Then That:
 This: Google Assistant - phrase 'show me what's playing'
 That: Web request: http://raspberrypiIPaddress/showmedia.php?action=start 

This will require your raspberry pi to be accessible from the outside world (which is fraught with danger). You will either need a static IP address or a dynamic dns service, and set your router to let traffic through to your rapsberry pi. Anyone with your IP address could start this action remotely, there is no security. Be aware of what you're doing!
