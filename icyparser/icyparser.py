#!/usr/bin/python3
# -*- coding: utf-8 -*-

## Author:          Gijs Timmers: https://github.com/GijsTimmers

## Licence:         CC-BY-SA-4.0
##                  http://creativecommons.org/licenses/by-sa/4.0/

## This work is licensed under the Creative Commons
## Attribution-ShareAlike 4.0 International License. To  view a copy of
## this license, visit http://creativecommons.org/licenses/by-sa/4.0/ or
## send a letter to Creative Commons, PO Box 1866, Mountain View,
## CA 94042, USA.

## Documentation on ICY in Icecast streams:
## http://www.smackfu.com/stuff/programming/shoutcast.html

## TODO:
## - fix channels causing BadStatusLine. When streamed with mplayer, it
##   appears that these channels do emit a StreamTitle. I have to find out
##   how it can be extracted. Known channels causing BadStatusLine:
##   * pinguin
##
## - one of the following:
##   * write the audio bytes to a local server, allow the user to stream this
##     server
##   * create a byte object containing all audio, allow this object to be read

import os
import re
import sys
import time
import threading
import tempfile
import urllib.parse
import urllib.request
import http

class IcyParser(object):
    def __init__(self):
        self.cache_control   = ""
        self.content_type    = ""
        self.date            = ""
        self.expires         = ""
        self.pragma          = ""
        self.server          = ""
        self.ice_audio_info  = ""
        self.icy_br          = ""
        self.icy_genre       = ""
        self.icy_metaint     = ""
        self.icy_name        = ""
        self.icy_pub         = ""
        self.icy_url         = ""
        self.icy_streamtitle = ""
        
    def getIcyInformation(self, url):
        ## Use this function as entry point to icyInformation.
        ## By executing this function, a thread will be started that updates
        ## the icy values. You can parse these, e.g.
        ## ip = icyparser.IcyParser()
        ## ip.getIcyInformation(URL)
        ## print(ip.icy_streamtitle)
        ##
        ## Also, you can stop the thread by switching thread_should_be_running
        ## to False.
        
        self.url = url
        self.thread_should_be_running = True
        t1 = threading.Thread(target=self.icyInformation)
        t1.start()
        
    def icyInformation(self):
        ## request the metadata headers: otherwise we won't get them.
        extra_headers = {"Icy-MetaData":1}

        try:
            rq  = urllib.request.Request(url=self.url, headers=extra_headers)
        except ValueError:
            print("Faulty URL. Please check URL and run again.")
            sys.exit(1)
        
        
        try:
            rsp = urllib.request.urlopen(rq)

            rsp_headers = rsp.getheaders()
            headers_dict = dict(rsp_headers)
            
            try:
                self.cache_control  = headers_dict["Cache-Control"]
            except KeyError:
                pass
            
            try:
                self.content_type   = headers_dict["Content-Type"]
            except KeyError:
                pass
            
            try:
                self.date           = headers_dict["Date"]
            except KeyError:
                pass
                
            try:
                self.expires        = headers_dict["Expires"]
            except KeyError:
                pass
            
            try:
                self.pragma         = headers_dict["Pragma"]
            except KeyError:
                pass
            
            try:
                self.icy_url        = headers_dict["icy-url"] 
            except KeyError:
                pass
            
            try:
                self.icy_genre      = headers_dict["icy-genre"]
            except KeyError:
                pass
            
            try:
                self.server         = headers_dict["Server"]
            except KeyError:
                pass
            
            try:
                self.ice_audio_info = headers_dict["ice-audio-info"]
            except KeyError:
                pass
            
            try:
                self.icy_name       = headers_dict["icy-name"]
            except KeyError:
                pass
            
            try:
                self.icy_pub        = headers_dict["icy-pub"]
            except KeyError:
                pass
            
            self.icy_br         = int(headers_dict["icy-br"])
            self.icy_metaint    = int(headers_dict["icy-metaint"])
            
            self.icystream = tempfile.NamedTemporaryFile(mode="w+", delete=False)
        
            ## Turn on to write all the non-ICY bytes to a playable MP3 file.
            #self.audiostream = open("audiostream.mp3", "w+b", buffering=0)
            
            while self.thread_should_be_running:
                ## All the bytes before the metaint are pure audio.
                ## Just read bytes until we get at the ICY message.
                bytes = rsp.read(self.icy_metaint)    
                ## Turn this on to write all the non-ICY bytes to a playable 
                ## MP3 file.
                
                #if bytes != b"":
                    #self.audiostream.seek(0)
                    #self.audiostream.write(bytes)
                    #self.audiobuffer = self.audiobuffer + bytes
                    #print(self.audiobuffer)
                
                
                ## When we get at the metaint, the first byte will
                ## tell us the length of the StreamTitle. We read out
                ## this number of bytes, and afterwards the cycle restarts.
                ## Sometimes, no new StreamTitle is sent.
                
                try:
                    length_specifier = ord(rsp.read(1))*16
                except TypeError:
                    ## Will appear at times, I don't know why.
                    length_specifier = 0
                if length_specifier != 0:
                    streamtitle = rsp.read(length_specifier).\
                    decode("utf-8", "ignore")
                    self.icy_streamtitle = \
                    re.findall("(?<=StreamTitle=').*(?=';)", streamtitle)[0]
                    #print(self.icy_streamtitle)
                    self.icystream.write("{} {}".format(time.strftime("%d-%m-%Y %H:%M:%S"), \
                    self.icy_streamtitle + "\n"))
                    self.icystream.flush()
        
        except http.client.BadStatusLine as e:
            ## This exception will occur on servers that don't properly
            ## implement headers.
            ## We'll return a dict without values so that scripts implementing
            ## this won't get messed up.
            print(e)
            pass
    
    def stop(self):
        self.thread_should_be_running = False

## Usage as a separate program is turned off for now.
"""
def entry_point():
    try:
        url = sys.argv[1]
    except IndexError:
        print("Usage: icyparser URL")
        sys.exit(1)
    ip = IcyParser()
    ip.getIcyInformation(url)
"""
