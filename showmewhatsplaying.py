from __future__ import print_function
import pychromecast as pcc
import requests
import sys
from io import BytesIO
from threading import Timer
from time import sleep
from time import time
import socket
import pychromecast.controllers.dashcast as dashcast


class ccmediainfo:
    """Class to keep track of what is currently playing on any of the chromecast 
audio, including groups, on local network, and display media information on a 
Chromecast TV. The class scans for chromecasts on __init__ and then every minute. 
The class scans for currently played media every 2 seconds. If any chromecast is 
playing music, an html page with media info (artist, album, title, album cover image, 
media service and currently playing chromecast) is cast onto the chromecast TV. The 
computer needs to run a web server (which is used to cast the html page to the chromecast TV).
Installation:
currentlyplaying.css must be in apache www/html folder

Usage:
Needs to be run with sufficient privileges to write file in apache www/html folder, and have network access
run class using 
with ccmediainfo() as ccmi:
    ccmi.start()

"""
    # if IP addresses are static, IP addresses of chromecast devices can be defined here, and can be used for faster discovery
    # However, fast discovery doesn't find Groups. Currently not used.
    cc_ips=['192.168.2.80','192.168.2.81','192.168.2.82','192.168.2.83','192.168.2.84','192.168.2.85','192.168.2.86']
    
    cclist=[] #will contain list of chromcast devices
    showonTV=True #display media content on TV if True
    localDisplay=False # unused - in prepareation for displaying media info on local computer's screen 
    displayed_track=''

    # name of chromecast TV on which to display media info:
    screenCastName="Living Room TV" 

    # full path of file that will be cast to
    htmlname='/var/www/currentlyplaying.html' 

    
    def __init__(self):
        #first get own IP address - this will be the www server's address used for casting webpage to chromecast TV
        #get servers ip address - taken from https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
        self.ip=(([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]
        #self.fast_discover(self.cc_ips)
        # discover chromecats - this takes a few seconds
        self.discovercc(0)
        # make sure the target chromecast TV has been found, or else exit.
        try:
            cast = next(cc for cc in self.cclist if cc.device.friendly_name == self.screenCastName) 
        except:
            print("could not find "+self.screenCastName)
            sys.exit()
            
        # kill current app on chromecast TV and wait 3 seconds. This will ensure correect behavour when casting html page and switch on the TV/switching of the TV to chromecast TV input. 
        print("Killing current running app")
        cast.quit_app()
        sleep(3)    
         
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.updatemediaTimer.cancel()
        self.discovertimer.cancel()
        print("clean exit")
    
        
    def start(self):
        print("service started")
        self.update_media_info(2)
        self.discovercc(60)

        
        while True:
            sleep(1)
            
    def discovercc(self,delay):
        """ discovers chromecasts - an relaunches after delay seconds if delay>0
        """
        self.cclist = pcc.get_chromecasts()
        if(delay>0):
            self.discovertimer=Timer(delay,lambda : self.discovercc(delay))
            self.discovertimer.start()


    def fast_discover(self,iplist):
        """ creates list of cc based on list of ip addresses, but does not discover groups
            Experimental and not currently used.
        """
        cclist=[]
        for ip in iplist:
            try:
                cclist.append(pcc.Chromecast(ip))
            except pcc.ChromecastConnectionError:
                print(ip+" not found")
                pass    
            
        friendlynames=[(cc.host, cc.device.friendly_name) for cc in cclist]
        #print(friendlynames)
        self.cclist= cclist

    def addTextLine(self,text):
        """ adds "text" as a new line to html file 
        """
        textsurface= self.myfont.render(text, True, (255, 255, 255))
        self.screen.blit(textsurface,(self.picWidth,self.ch))
        self.ch=self.ch+self.linespacing
    
    
    def display_media_content(self,cc):
        """ Gathers media information of currently playing chromecast, creates html file with media info, and casts it to
        chromecast TV
        """
        st=cc.media_controller.status
        if(self.displayed_track!=st.title):
            #print(st.title)
            if(cc.media_controller.thumbnail):
                thumbURL=cc.media_controller.thumbnail
                with open(self.htmlname,'w') as htmlf:
                    htmlf.write('<html><head><title>Now playing</title>\n<link rel="stylesheet" type="text/css" href="currentlyplaying.css"></head>\n<body>\n<img src="'+thumbURL+'">\n')
                    htmlf.write('<p>Title: <span class="description">'+st.title.encode('ascii','xmlcharrefreplace')+'</span></p>\n')
                    htmlf.write('<p>Artist: <span class="description"> '+st.artist.encode('ascii','xmlcharrefreplace')+'</span></p>\n')
                    htmlf.write('<p>Album: <span class="description">'+st.album_name.encode('ascii','xmlcharrefreplace')+'</span></p>\n')
                    htmlf.write('<p>Service: <span class="description">' + cc.app_display_name.encode('ascii','xmlcharrefreplace')+'</span></p>\n')
                    htmlf.write('<p>Playing on: <span class="description">' + cc.device.friendly_name.encode('ascii','xmlcharrefreplace')+'</span></p>\n')
                    htmlf.write('</body></html>')
                    htmlf.close()
            else:
                with open(self.htmlname,'w') as htmlf:
                    htmlf.write('<html><head><title>Now playing</title>\n<link rel="stylesheet" type="text/css" href="currentlyplaying.css"></head>\n<body>')
                    htmlf.write('<p> </p><p><span class="description">Error loading media info</span></p>')
                    htmlf.write('</body></html>')
                    htmlf.close()
            
            self.displayed_track=st.title
            
            if(self.showonTV):
                cast = next(cc for cc in self.cclist if cc.device.friendly_name == self.screenCastName) 
                cast.wait()
                d = dashcast.DashCastController()
                cast.register_handler(d)
                cast.wait()
                d.load_url('http://'+self.ip+'/currentlyplaying.html?'+str(int(time())))
                mc = cast.media_controller 
                self.mc=mc #useful for debugging
            
                

    def display_nothing(self):
        with open(self.htmlname,'w') as htmlf:
            htmlf.write('<html><head><title>Now playing</title>\n<link rel="stylesheet" type="text/css" href="currentlyplaying.css"></head>\n<body>')
            htmlf.write('<p> </p><p><span class="description">nothing playing</span></p>')
            htmlf.write('</body></html>')
            htmlf.close()
            
        if(self.showonTV and self.displayed_track!='-'):
            try:
                cast = next(cc for cc in self.cclist if cc.device.friendly_name == self.screenCastName) 
            except:
                print("no tv found")
                raise
            else:
                cast.wait() 
                d = dashcast.DashCastController()
                cast.register_handler(d)
                cast.wait()
                d.load_url('http://'+self.ip+'/currentlyplaying.html?'+str(int(time())))
                mc = cast.media_controller 
                self.mc=mc #useful for debugging
                self.displayed_track='-'
            

            


    #chromecasts=fast_discover(cc_ips)
    def update_media_info(self,delay):
        hasmedia=False
        try:
            currently_playing_cc= next(cc for cc in self.cclist if (cc.media_controller.is_playing and cc.device.friendly_name!="Living Room TV"))
            hasmedia=True
        except:
            print("nothing currently playing")
            hasmedia=False

        if(hasmedia):
            mc=currently_playing_cc.media_controller

            currently_playing_cc.wait()
            #castaudio.wait()
            #print("app: "+currently_playing_cc.app_display_name)
            #print("playing: "+mc.title)

            self.display_media_content(currently_playing_cc)
        else:
            self.display_nothing()

            
        if(delay>0):
            self.updatemediaTimer=Timer(delay,lambda : self.update_media_info(delay))
            self.updatemediaTimer.start()



with ccmediainfo() as ccmi:
    ccmi.start()
    



