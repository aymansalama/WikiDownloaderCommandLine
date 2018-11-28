# WikiDownloaderCommandLine
Download wiki content from command line

Prerequisites
------------
- Python 3 environment and requests, hashlib, datetime, urllib modules  
<!-- - wget  
- md5sum  

For Windows, install ![wget](https://sourceforge.net/projects/gnuwin32/files/wget/1.11.4-1/)
and [add into path](https://www.addictivetips.com/windows-tips/install-and-use-wget-in-windows-10/)   -->


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
- -t, --torrent &rarr; Use torrents instead of mirror to download dumb, all other arguments are the same.
```python wdcli.py -t```


Block Diagram
-------------
![blockdiagram](/Block%20diagram%20v4.png)
