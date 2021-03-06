# WikiDownloaderCommandLine
Download wiki content via command line

Prerequisites
------------
- Python 3 environment and modules such as:   argparse, subprocess, os, sys, time, re, datetime, ssl, requests, bs4, hashlib, logging, modules  


Usage
-----

```
python wdcli.py [OPTION]
```
- -m, --mirrors &rarr; Number choice of mirror link consists of:  
                        1:<https://dumps.wikimedia.your.org>  
                        2:<http://wikipedia.c3sl.ufpr.br>  
                        3:<https://dumps.wikimedia.org>  
 ```python -m 1```

- -d, --dates   &rarr; A single date only  
```python wdcli.py -d 20181101 ```
- -p. --projects &rarr; Type of Projects such as wikipedia(wiki), wikibooks, wiktionary, wikimedia, wikinews,wikiversity, wikiquote, wikisource, wikivoyage  
```python wdcli.py -p "wiki wiktionary"```
- -r, --maxretries &rarr; Number of retries. Default = 3  
```python wdcli.py -r 5```
- -l, --locales &rarr; Languages  
```python wdcli.py -l "en my ar"```  
- -t, --torrent &rarr; Use torrents instead of mirror to download dump, all other arguments are the same.
```python wdcli.py -t```


Block Diagram
-------------
![blockdiagram](/Block%20diagram%20v4.png)

Automation Test

The linux shell script 'test.sh' tests around 39888 combinations of different mirrors, projects, locales and dates. The script only checks whether the links are available or not and then logs the results to log.txt.

Usage:

Invoke the command 'test.sh' or 'sh test.sh' on windows if you have git installed. 

Make sure you add the sh file into your environment varaibles.
