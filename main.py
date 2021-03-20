# Metal Injection albums search via RSS Feed


import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import json
import datetime
from refresh import Refresh

class MINRWeekly:
    def __init__(self):
        load_dotenv()
        self.suid = os.getenv('SUID')
        self.scid = os.getenv('SCID')
        self.sscret = os.getenv('SSCRET')
        self.suid = os.getenv('SUID')
        self.stoken = ""

    
    def WeeklyLink():
        print("Finding this week's new-releases link...")
        url = "https://metalinjection.net/category/upcoming-releases/heavy-new-releases/feed"

        resp = requests.get(url)

        soup = BeautifulSoup(resp.content, features="xml")
        links = soup.find_all(["link"])
        link = links[4]
        linkt = link.text
        return linkt           

    def new_releases(WeeklyLink):
        print("scraping site for artists...")
        r = requests.get(WeeklyLink)
        r = r.text
        soup = BeautifulSoup(r, 'html.parser')
        uls = soup.find_all("ul")
        uls = uls[15]

        lis = uls.find_all("li")
        item = []
        x = 0
        for i in lis:
            data = lis[x]
            datat = data.text
            sep = ' –'
            datats = datat.split(sep, 1)[0]
            nonos = "/"
            if datats.find(nonos) >= 0:
                x += 1
            else:
                item += [datats]
                x += 1
        #Big Links
        h3s = soup.find_all("h3")
        y = 1
        for i in h3s:
            data = h3s[y]
            datat = data.text
            sep = 'Genre:'
            if datat.find(sep) != -1:
                datats = datat.split(sep, 1)[0]
                sep2 = ' –'
                dataf = datats.split(sep2, 1)[0]
                nonos = "/"
                if dataf.find(nonos) >= 0:
                    y += 1
                else:
                    item += [dataf]
                    y += 1
            else:
                continue
            
        itemcount = (y+x)-1
        ni = str(itemcount)
        print("Scraped # " + ni + " new releases this week...")
        return item

    # Search for Artist
    # https://developer.spotify.com/console/get-search-item/
    def search_artist(artist,stoken):
        print("searching spotify for artist: " + artist + " ...")
        query = "https://api.spotify.com/v1/search?q={}&type=artist&market=us".format(
            artist
        )
        response = requests.get(
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(stoken)
            }
        )
        
        response_json = response.json()
        artists = response_json["artists"]["items"]
        asc = len(artists)
        if asc >= 0:
            aid = artists[0]["id"]
            print("found artist id :" + aid + " ...")
            return aid
        else: aid = 0

    # Search artist's albums
    # https://developer.spotify.com/console/get-artist-albums/
    def search_albums(aid,stoken):
        print("Searching artist " + aid + " for lastest albums")
        query = "https://api.spotify.com/v1/artists/{}/albums".format(
            aid
        )
        response = requests.get(
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(stoken)   
            }
        )
        response_json = response.json()
        aalbums = response_json["items"]
        albumid = aalbums[0]["id"]
        print("Found artist album:" + albumid + " ...")
        return albumid

    # Get album tracks
    def album_tracks(albumid,stoken):
        print("Collection tracks from " + albumid + " ...")
        query = "https://api.spotify.com/v1/albums/{}/tracks?offset=0&limit=20&market=US".format(
            albumid
        )
        response = requests.get(
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(stoken)   
            }
        )
        response_json = response.json()
        tracks = ""
        z = 0 
        items = response_json["items"]
        acount = (len(items))
        for i in items:
            track = items[z]["uri"]
            tracks += (track + ",")
            z += 1
        turis = tracks


        print("Found " + str(acount) + " tracks off of " + str(albumid) + " ...")
        return turis





    # Create playlist
    # https://developer.spotify.com/console/post-playlists/

    def create_playlist(suid,stoken):
        # format for playlist name:  %b %d (month abbreviated, day of month)
        dtn = datetime.datetime.now()
        dname = dtn.strftime("%b%d")
        dyn = dtn.strftime("%y")
        dfname = dname + "-" + dyn
        pname = "MetalWeekly-" + dfname
        print("Creating playlist " + pname + " ...")
        reqHeader = {'Authorization': 'Bearer {}'.format(stoken), 'Content-Type': 'application/json'}
        reqBody = {'name': pname, 'description': 'Weekly metal new releases', 'public': 'false'}
        r = requests.post('https://api.spotify.com/v1/users/{}/playlists'.format(suid), headers=reqHeader, json=reqBody)
        if r.status_code in [200, 201]:
            pid = r.json()['id']
            print("Playlist " + pname + " - " + pid + " has been created...")
            return pid


    # Add album to playlist
    #https://developer.spotify.com/console/post-playlist-tracks/
    def add_to_playlist(pid,turis,stoken):
        print("Adding " + turis + " to playlist ")
        reqHeader = {'Authorization': 'Bearer {}'.format(stoken), 'Content-Type': 'application/json'}
        r = requests.post('https://api.spotify.com/v1/playlists/{}/tracks?=uris={}'.format(pid,turis), headers=reqHeader)
        if r.status_code in [200, 201]:
            print("Added songs from " + turis + " to playlist")


    def call_refresh():
            print("Running token refresh ...")
            Refresh_Caller = Refresh()
            stoken = Refresh_Caller.refresh()
            return stoken

    def main():
        print("Starting script ...")
        load_dotenv()
        suid = os.getenv('SUID')
        suid = os.getenv('SUID')
        stoken = MINRWeekly.call_refresh()
        WeeklyLink = MINRWeekly.WeeklyLink()
        nr = MINRWeekly.new_releases(WeeklyLink)
        snr = str(nr)
        print("Artists with new releases: " + snr)
        pid = MINRWeekly.create_playlist(suid,stoken)
        for i in nr:
            aid = MINRWeekly.search_artist(i,stoken)
            if (aid == 0):
                break
            albumid = MINRWeekly.search_albums(aid,stoken)
            turis = MINRWeekly.album_tracks(albumid,stoken)
            MINRWeekly.add_to_playlist(pid,turis,stoken)
            print("Successfully added " + i + " to " + pid + " ...")



MINRWeekly.main()
