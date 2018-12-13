#!/usr/bin/env python3

import argparse
import subprocess
import os
import sys
import time
import re       # regex
import datetime
import requests
import ssl
from requests.exceptions import HTTPError
from urllib.request import urlopen
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
import hashlib
import logging

# Logging with append mode into logfile.txt
def setup_logger(logger_name, log_file, file_mode, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p')
    fileHandler = logging.FileHandler(log_file, mode=file_mode)
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler)  
    
setup_logger('log', 'logfile.txt', 'a')
setup_logger('pass', 'pass.txt', 'a')
setup_logger('fail', 'fail.txt', 'a')
logger_log = logging.getLogger('log')
logger_pass = logging.getLogger('pass')
logger_fail = logging.getLogger('fail')

# init of global variables
# List of mirrors
mirrors = ['https://dumps.wikimedia.org','https://dumps.wikimedia.your.org','http://wikipedia.c3sl.ufpr.br']

# Default projects
projects = ['wiki','wikibooks','wiktionary','wikiquote','wikimedia','wikisource','wikinews','wikiversity','wikivoyage']

# Get default locales extracted from wikimedia dumps from a file
locales = list()
with open('./wikilocale.txt', 'r') as filehandle:
    for line in filehandle:
        # remove linebreak which is the last character of the string
        currentPlace = line[:-1]
        locales.append(currentPlace)

# Set Mirror function
def select_mirrors(mirror):
    mirror_string = ''
    i = 1
    # toString function to prompt user selection of mirrors list
    for m in mirrors:
        mirror_string = mirror_string + str(i) + ': ' + m + ' '
        if i is 1:
            mirror_string += '(default)'
        mirror_string += '\n'
        i += 1

    # Error Handling if improper input given by user
    while True:
        if mirror is None:
            mirror = input('Select Mirrors: \n' + mirror_string + '(leave empty for default) \n').replace(' ','')

        # user leave empty by default
        mirror = str(mirror)
        if mirror is '':
            mirror = mirrors[0]
            break
        # user pick mirror 1 also default
        elif mirror == '1':
            mirror = mirrors[0]
            break
        # user pick mirror 2 which is from your.org server
        elif mirror == '2':
            mirror = mirrors[1]
            break
        # user pick mirror 3 which is from c3sl,ufpr.pr server
        elif mirror == '3':
            mirror = mirrors[2]
            break
        # restart back the loop, empty the variables
        else:
            mirror = None
            print('Invalid input. Please try again\n')
    # user that know what they're doing
    return mirror

# Set Date function
def select_dates(date):
    while True:
        # no date given in the command argument options
        if date is None:
            date = input('Enter Date in YYYYMMDD format: (leave empty for default)\n').replace(' ','')

        date = str(date)
        # default date is the first day of the month
        if date is '':
            date = datetime.date.today().replace(day=1)
            break
        # check the date format using length of the date
        elif len(str(date)) < 8 or len(str(date)) > 8:
            date = None
            print('\nWrong date format! Please enter as YYYYMMDD format.\n')
        # if the date given is from the future
        elif int(date) > int(datetime.date.today().strftime("%Y%m%d")):
            date = None
            print('\nUh Oh! Dumps are not from the future.\n')
        # simple check each piece of date in terms of year month day format
        elif (int(date[0:4]) < 2013) or  (int(date[4:6]) > 12) or (int(date[6:8]) > 31):
            date = None
            print('Your date might be incorrect somewhere. Try again.\n')
        else:
            break
    # user that knows how to rtfm
    return str(date).replace('-','')

# Set Projects function
def select_projects(project):
    # toString function to prompt user selection of mirrors list
    project_string = ''
    for p in projects:
        project_string = project_string + p + '\n'

    # prompt user until project is selected by typing the right project name
    while True:
        if project is None:
            project = input('Select projects:\n' + project_string + '(leave empty for default)\n').split()
            print(project)
            # empty input = default (all projects)
            if not project:
                return projects
            else:
                pass
        # if user state any projects
        else:
            # project name must be a string
            [project] = project
            if type(project) is str:
                project = project.split(' ')
            # check project given by user
            if checkProject(project):
                return project
            # invalid project or unsupported project input
            else:
                project = None
                print('\nInvalid selection of projects. Please try again.')

# Set Language/locale function
def select_locale(locale):
    while True:
        # locale is not defined in the command arguments
        if locale is None:
            locale = input('Select locale: (leave empty for default "en")\n').split()
            # default locale is 'en'
            if not locale:
                locale = []
                locale.append('en')
                return locale
            else:
                pass
        # user pass their own choice of locale(s)
        else:
            [locale] = locale
            if type(locale) is str:
                locale = locale.split(' ')
            # check locale given by user
            if checkLocale(locale):
                # return all proper locale
                return locale
            # maybe the user does not know what is locale
            else:
                locale = None
                print('\nInvalid selection of locales. Please try again.')

# check if the user input right/wrong project name
def checkProject(project):
    for p in project:
        if p not in projects:
            return False
    return True

# check if the user input right/wrong locales compared to default locales
def checkLocale(locale):
    for l in locale:
        if l not in locales:
            return False
    return True

# Direct Download dumps function
# url_link is the file link from the server
# path is download directory to save the file
# dumpfilename is derived from the dumps file name
def DownloadFile(url_link, path, dumpfilename):
    done = 0
    total = 0

    # error handling in case the link does not work
    try:
        url = requests.get(url_link, stream = True)
        # to use as total percentage counter when downloading the file
        total = float(url.headers.get('content-length'))
    except:
        print('link not found')
        return False

    # if the url sucessfully retrieved, download the file
    # also updates the download progress percentage counter
    if url.status_code == 200:
        with open('%s/%s' % (path, dumpfilename), 'wb') as f:
            for chunk in url.iter_content(1024):
                done += len(chunk)
                f.write(chunk)
                sys.stdout.write('\r%s [%.2f]' % (dumpfilename, done*100/total))
        # log when complete download a dump file
        logger_log.info('%s [Completed]' % (dumpfilename))
        print('\n%s [Completed]' % (dumpfilename))
        return True

# Torrent Download dumps function
# url_link is the link from torrent domain
# path is download directory for torrent file
def DownloadTorrentFile(url_link, path):
    file = url_link.split('/')[-1]
    done = 0
    total = 0

    # error handling in case the link does not work
    try:
        url = requests.get(url_link, stream = True)
        # to use as total percentage counter when downloading the file
        total = float(url.headers.get('content-length'))
    except:
        print('link not found')
        return False

    # if the url sucessfully retrieved, download the torrent file
    # also updates the download progress percentage counter
    if url.status_code == 200:
        with open('%s/%s' % (path, file), 'wb') as f:
            for chunk in url.iter_content(1024):
                done += len(chunk)
                f.write(chunk)
                sys.stdout.write('\r%s [%.2f]' % (file, done*100/total))

        sys.stdout.write('\r%s completed' % (file))
        return True

# Download md5 hash file from the wikimedia to check md5
def GetMD5sums(url):
	try:
		raw = urlopen(url).read().decode('utf-8')
	except:
		return ''

	return raw

# Compare MD5 hash from downloaded file with the MD5 from wikimedia
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


# This function disables SSL certificate verification when opening links.
def get_context():
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context

# Main function
def main():
    # setup arguments
    parser = argparse.ArgumentParser(description='Downloader of Wikimedia Dumps')
    # mirror, pass only one or nothing as options in int
    parser.add_argument('-m', '--mirrors', nargs='?', type=int, help='Use mirror links instead of wikimedia. Such as 1:https://dumps.wikimedia.your.org 2:http://wikipedia.c3sl.ufpr.br', required=False)
    # torrent, if -t options is passed. mirror will use torrent
    parser.add_argument('-t', '--torrent', help="Use torrent to download data", action='store_true')
    # dates, pass only one or nothing as options in int
    parser.add_argument('-d', '--dates', nargs='?', type=int, help='Set the date of the dumps. (e.g. 20181101). Default = 1st day of current month', required=False)
    # projects, pass 1 or more as options in string
    parser.add_argument('-p', '--projects', nargs='*', help='Choose which wikimedia projects to download (e.g. wiki wikibooks wiktionary wikimedia wikinews wikiversity wikiquote wikisource wikivoyage)', required=False)
    # maxretries, pass one or nothing as options in int
    parser.add_argument('-r', '--maxretries', nargs='?', type=int, help='Max retries to download a dump when md5sum doesn\'t fit. Default: 3', required=False)
    # locales, pass one or more as options in str
    parser.add_argument('-l', '--locales', nargs='*', help='Choose which language dumps to download (e.g en my ar)', required=False)
    # script-testing, if -s options is passed, dumps link status return without download file
    parser.add_argument('-s', '--script', help="For automated testing using script that will return link status in output file", action='store_true')
    args = parser.parse_args()

    # Dumps Domain and Mirror
    if not args.torrent:
        dumpsdomain = select_mirrors(args.mirrors)
    else:
        dumpsdomain = 'https://tools.wmflabs.org'

    # Dumps Date, default latest
    dates = select_dates(args.dates)

    # Projects selection
    proj = select_projects(args.projects)

    # Retry downloads when MD5 checker not match
    # Default = 3
    maxretries = 3
    if args.maxretries and int(args.maxretries) >= 0:
        maxretries = int(args.maxretries)

    # Set the locale
    locale = select_locale(args.locales)

    # Show users all the selected options
    print ('-' * 50, '\n', 'Checking')
    print("Max retries set to:", maxretries)
    print("Dumps Domain use:", dumpsdomain)
    print("Dates selected:", dates)
    print("Project selected:",proj)
    print("Locale selected:", locale)
    print('\n', '-' * 50)

    # check download via direct or torrent
    # download via torrent
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

        # Create torrent downloads folder
        downloads_dir = "DownloadTorrent"
        if not os.path.exists(downloads_dir):
            os.mkdir(downloads_dir)

        torrent_file_paths = []
        print("Length: ", len(links))
        for link in links:
            print(link)

            ctxt = get_context()

            with urlopen(link, context=get_context()) as url:
                html = url.read().decode('utf-8')

            parsedPage = BeautifulSoup(html, "html.parser")

            for a in parsedPage.findAll(href=re.compile("pages-articles")):
                file_url = '{}{}'.format(dumpsdomain, a.get('href'))
                file = '{}/{}'.format(downloads_dir, file_url.split('/')[-1])

                if DownloadTorrentFile(file_url, downloads_dir):
                    print(file, "-- Downloaded")
                    torrent_file_paths.append(file)
                else:
                    print(file, "-- Skipped")

        # Download torrents using torrent client
        for torrent_file in torrent_file_paths:
            if sys.platform.startswith('darwin'):
                subprocess.call(('open', torrent_file))
            elif os.name == 'nt':
                # Windows
                os.startfile(torrent_file)
            elif os.name == 'posix':
                # Linux & Macintosh
                subprocess.call(('xdg-open', torrent_file))


    # When torrent is not selected
    else:
        fulldumps = []
        downloadlink = ""
        # check links status for each locale and project
        for l in locale:
            for p in proj:
                try:
                    downloadlink = '{}/{}{}/{}'.format(dumpsdomain, l, p, dates)
                    r = requests.get(downloadlink)
                    r.raise_for_status()
                    fulldumps.append([l,p,dates])   # live link will be added to array
                    print(downloadlink, '--  Link Ready')
                    if args.script:
                        logger_pass.info('Pass Automation Test Link: %s-> Mirror:%s, Project:%s, Date:%s, Locale:%s' % (downloadlink, dumpsdomain, p, dates, l))
                        sys.exit(0)
                except HTTPError:
                    print(downloadlink, '--  Not Exist')
                    if args.script:
                        logger_fail('Error Automation Test Link: %s-> Mirror:%s, Project:%s, Date:%s, Locale:%s' % (downloadlink, dumpsdomain, p, dates, l))
                        sys.exit(0)

        # Exit application if no file can be download
        if fulldumps == []:
            print("\nRequested dumps are not available.\nIf server are updating, try again later.\
            \nEnsure the argument passed are correct.","\n" *3)
            sys.exit(0)

        # extract live links and loop each link to download the file
        for locale, project, date in fulldumps:
            print ('-' * 50, '\n', 'Preparing to download', '\n', '-' * 50)
            time.sleep(1)  # ctrl-c
            downloadlink = '{}/{}{}/{}'.format(dumpsdomain, locale, project, date)
            print(downloadlink)
            with urlopen(downloadlink, context=get_context()) as url:
                htmlproj = url.read().decode('utf-8')

            # refer "/enwiki/20181101/enwiki-20181101-pages-articles2.xml-p30304p88444.bz2"
            # some dumps have multiple files, loop each file found in the html page using regex
            for dumptypes in ['pages-articles\d*\.xml[^\.]*\.bz2']:
                corrupted = True
                maxRetriesCheck = maxretries
                # loop until finished retries and no corrupted file
                while (corrupted) and maxRetriesCheck > 0:
                    maxRetriesCheck -=1
                    m = re.compile(r'<a href="/(?P<urldump>%s%s/%s/%s%s-%s-%s)">' %  (locale,project,date,locale,project,date,dumptypes))
                    urldumps = []
                    for match in re.finditer(m, htmlproj):
                        urldumps.append('%s/%s' % (dumpsdomain, match.group('urldump')))

                    # Download Directory
                    path = 'Download/%s/%s%s' % (locale, locale, project)

                    # Create downloads folder
                    if not os.path.exists(path):
                        os.makedirs(path)

                    # Get MD5Sums from wikimedia related to the dumps that will are downloaded
                    md5raw = GetMD5sums('%s/%s%s/%s/%s%s-%s-md5sums.txt' % (dumpsdomain, locale, project, date, locale, project, date))
                    if not md5raw:
                        logger_log.error("md5sums link not found")
                    else:
                        logger_log.info("md5sums link found")

                    for urldump in urldumps:
                        dumpfilename = urldump.split('/')[-1]
                        # start download the dumps
                        DownloadFile(urldump, path, dumpfilename)

                        # md5check
                        if MatchMD5('%s/%s' % (path, dumpfilename), md5raw):
                            # log info
                            logger_log.info("Matching MD5")
                            corrupted = False
                        else:
                            # md5 not match , log error
                            logger_log.error("Not matching MD5")
                            # remove corrupted file
                            os.remove('%s/%s' % (path, dumpfilename))


if __name__ == '__main__':
    main()
