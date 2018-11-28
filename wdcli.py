#!/usr/bin/env python3

import argparse
import os
import sys
import time
import re       # regex
import datetime
import requests
from requests.exceptions import HTTPError
from urllib.request import urlopen
from urllib.request import urlretrieve
import hashlib
from bs4 import BeautifulSoup
from gi.repository import GLib
### TODOLIST
# interactive
# error generator
# log

"""
def DownloadTorrentFile(url_link, path):
    file = '{}/{}'.format(path, url_link.split('/')[-1])
    print(url_link)
    urlretrieve(url_link, file) """

def DownloadFile(url_link, path):
    file = url_link.split('/')[-1]
    done = 0
    total = 0
    
    try:
        url = requests.get(url_link, stream = True)
        total = int(url.headers.get('content-length'))
    except:
        print('link not found')
        return False

    if url.status_code == 200:
        with open('%s/%s' % (path, file), 'wb') as f:
            for chunk in url.iter_content(1024):
                done += len(chunk)
                f.write(chunk)
                sys.stdout.write('\r%s [%.2f]' % (file, done/total*100))

        sys.stdout.write('\r%s completed' % (file))
        return True

def GetMD5sums(url):
	try:
		raw = urlopen(url).read().decode('utf-8')
	except:
		return ''
	
	return raw

def MatchMD5(file, md5raw):
	hash_md5 = hashlib.md5()
	try:
		with open(file, "rb") as f:
			for chunk in iter(lambda: f.read(4096), b""):
				hash_md5.update(chunk)
	except:
		return False

	f = hash_md5.hexdigest()

	if re.search(f, md5raw):
		return True
	else:
		return False

# class 
def main():
    parser = argparse.ArgumentParser(description='Downloader of Wikimedia Dumps')
    parser.add_argument('-m', '--mirrors', nargs='?', type=int, help='Use mirror links instead of wikimedia. Such as 1:https://dumps.wikimedia.your.org 2:http://wikipedia.c3sl.ufpr.br', required=False)
    parser.add_argument('-t', '--torrent', help="Use torrent to download data", action='store_true')
    parser.add_argument('-d', '--dates', nargs='?', type=int, help='Set the date of the dumps. (e.g. 20181101). Default = 1st day of current month', required=False)
    parser.add_argument('-p', '--projects', help='Choose which wikimedia projects to download (e.g. all, wikipedia, wikibooks, wiktionary, wikimedia, wikinews, wikiversity, wikiquote, wikisource, wikivoyage)', required=False)
    parser.add_argument('-r', '--maxretries', help='Max retries to download a dump when md5sum doesn\'t fit. Default: 3', required=False)
    parser.add_argument('-l', '--locales', nargs='+', help='Choose which language dumps to download (e.g en my ar)', required=False)
    args = parser.parse_args()

    # Dumps Domain and Mirror
    if args.mirrors == None:
        if args.torrent:
            dumpsdomain = "https://tools.wmflabs.org"
        else:
            dumpsdomain = 'https://dumps.wikimedia.org'
    elif args.mirrors == 1:
        dumpsdomain = 'https://dumps.wikimedia.your.org'
    elif args.mirrors == 2:
        dumpsdomain = 'http://wikipedia.c3sl.ufpr.br'
    else:
        # Exception Handling for wrong input for mirror choices
        while True:
            secondChance = input("Invalid input for mirror choice.\nInput 1 for dumps.wikimedia.your.org\nInput 2 for wikipedia.c3sl.ufpr.br \
            \nInput 3 for default: dumps.wikimedia.your.org\n")
            if secondChance == '1':
                print(secondChance)
                dumpsdomain = 'https://dumps.wikimedia.your.org'
                break
            elif secondChance == '2':
                dumpsdomain = 'http://wikipedia.c3sl.ufpr.br'
                break
            elif secondChance == '3':
                dumpsdomain = 'https://dumps.wikimedia.org'
                break   
                


    # Dumps Date, default latest 
    if args.dates:
        # Input format exception handling
        if  len(str(args.dates)) < 8 or\
            len(str(args.dates)) > 8:
                print(len(str(args.dates)))
                print("\nWrong date format! Please enter as YYYYMMDD format.\n")
                sys.exit(0)
        # Stop if the date not in the past
        if  args.dates > int(datetime.date.today().strftime("%Y%m%d")):
            print("\nUh Oh! Dumps are not from the future.\n")
            sys.exit(0)

        dates = args.dates
    else:
        # Default first day of the current month
        # todayDate = datetime.date.today().strftime("%Y%m%d")
        todayDate = datetime.date.today()
        dates = todayDate.replace(day=1).strftime("%Y%m%d")

    
    # Projects selection
    proj = []
    if args.projects:
        proj = [args.projects]
    else:
        proj = ['wiki','wikibooks','wiktionary','wikiquote','wikimedia','wikisource','wikinews','wikiversity','wikivoyage']

    # Retry downloads when MD5 checker not match
    # Default = 3
    maxretries = 3
    if args.maxretries and int(args.maxretries) >= 0:
        maxretries = int(args.maxretries)
    

    # Set the locale
    allLocale = []
    if args.locales:
        allLocale = args.locales
    else:
        with open('wikilocale.txt', 'r') as filehandle:
            for line in filehandle:
                # remove linebreak which is the last character of the string
                currentPlace = line[:-1]
                allLocale.append(currentPlace)       


    locale = allLocale
    print ('-' * 50, '\n', 'Checking')
    print("Max retries set to:", maxretries)
    print("Dumps Domain use:", dumpsdomain)
    print("Dates selected:", dates)
    print("Project selected:",proj)
    print("Locale selected:", locale)
    print('\n', '-' * 50)

    if not args.torrent:
        fulldumps = []
        downloadlink = ""
        for l in locale:
            for p in proj:
                try:
                    downloadlink = '{}/{}{}/{}'.format(dumpsdomain, l, p, dates)
                    r = requests.get(downloadlink)
                    r.raise_for_status()
                    fulldumps.append([l,p,dates])
                    print(downloadlink, '--  Link Ready')
                except HTTPError:
                    print(downloadlink, '--  Not Exist')
        # print(fulldumps)
    
    if args.torrent:
        # Retrieve torrent file using provided data
        # Source: https://tools.wmflabs.org/dump-torrents/
        links = []
        for l in locale:
            for p in proj:
                try:
                    downloadlink = '{}/dump-torrents/{}{}/{}'.format(dumpsdomain, l, p, dates)
                    r = requests.get(downloadlink)
                    r.raise_for_status()
                    links.append(downloadlink)
                    print(downloadlink, '-- Link Ready')
                except HTTPError:
                    print(downloadlink, '-- Not Exist')

    # Proceed to download all torrent files in above link
    print ('-' * 50, '\n', 'Preparing to download torrent files', '\n', '-' * 50)
    time.sleep(1)  # ctrl-c
    torrent_file_paths = []
    for link in links:
        print(link)

        with urlopen(link) as url:
            html = url.read().decode('utf-8')
   
        parsedPage = BeautifulSoup(html, "html.parser")
        
        for a in parsedPage.findAll(href=re.compile("\.torrent$")):
            file_url = '{}{}'.format(dumpsdomain, a.get('href'))
            downloads_dir = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOWNLOAD)
            file = '{}/{}'.format(downloads_dir, file_url.split('/')[-1])

            if DownloadFile(file_url, downloads_dir):
                print(file, "-- Downloaded")
                torrent_file_paths.append(file)
            else:
                print(file, "-- Skipped")




    # Exit application if no mirror file can be download
    if not args.torrent:
        if fulldumps == []:
            print("\nRequested dumps are not available.\nIf server are updating, try again later.\
            \nEnsure the argument passed are correct.","\n" *3)
            sys.exit(0)
        
        for locale, project, date in fulldumps:
            print ('-' * 50, '\n', 'Preparing to download', '\n', '-' * 50)
            time.sleep(1)  # ctrl-c
            print(downloadlink)
            with urlopen(downloadlink) as url:
                htmlproj = url.read().decode('utf-8')

            for dumptypes in ['pages-meta-history\d*\.xml[^\.]*\.7z']:
                corrupted = True
                maxRetriesCheck = maxretries
                while (corrupted) and maxRetriesCheck > 0:
                    maxRetriesCheck -=1
                    # refer "/enwiki/20181101/enwiki-20181101-pages-meta-history1.xml-p26584p28273.7z"
                    # enwiki is have many files, looping is required
                    m = re.compile(r'<a href="/(?P<urldump>%s%s/%s/%s%s-%s-%s)">' %  (locale,project,date,locale,project,date,dumptypes))
                    urldumps = []
                    for match in re.finditer(m, htmlproj):
                        print(match)
                        urldumps.append('%s/%s' % (dumpsdomain, match.group('urldump')))

                    path = 'Download/%s/%s%s' % (locale, locale, project)
                    
                    if not os.path.exists(path):
                        os.makedirs(path)

                    md5raw = GetMD5sums('%s/%s%s/%s/%s%s-%s-md5sums.txt' % (dumpsdomain, locale, project, date, locale, project, date))
                    if not md5raw:
                        print('md5sums link not found')
                    else:
                        print('md5sums link found')
                    
                    # print (urldumps)
                    for urldump in urldumps:
                        DownloadFile('%s' % (urldump), '%s' % (path))

                        # md5check
                        if MatchMD5('%s/%s' % (path, dumpfilename), md5raw):
                            print('Matching MD5')
                            corrupted = False
                        else:
                            os.remove('%s/%s' % (path, dumpfilename))               


if __name__ == '__main__':
    main()
