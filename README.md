 <pre>
    

                              ████████╗ ██████╗ ██████╗     ██████╗  ██████╗ ████████╗ 
                              ╚══██╔══╝██╔═══██╗██╔══██╗    ██╔══██╗██╔═████╗╚══██╔══╝ 
                                 ██║   ██║   ██║██████╔╝    ██████╔╝██║██╔██║   ██║ 
                                 ██║   ██║   ██║██╔══██╗    ██╔══██╗████╔╝██║   ██║
                                 ██║   ╚██████╔╝██║  ██║    ██████╔╝╚██████╔╝   ██║ 
                                 ╚═╝    ╚═════╝ ╚═╝  ╚═╝    ╚═════╝  ╚═════╝    ╚═╝ 
                                                            
                            
                                                                              
                                                           `.` `     
                                                       ``.:.--.`     
                                                      .-+++/-`       
                                                     `+sso:`         
                                                  `` /yy+.           
                                                  -+.oho.            
                                                   o../+y            
                                                  -s.-/:y:`          
                                               .:o+-`--::oo/-`       
                                            `/o+:.```---///oss+-     
                                          .+o:.``...`-::-+++++sys-   
                                         :y/```....``--::-yooooosh+  
                                        -h-``--.```..-:-::ssssssssd+ 
                                        h:``:.``....`--:-++hsssyyyym.
                                       .d.`/.``--.```:--//odyyyyyyym/
                                       `d.`+``:.```.--/-+/smyyhhhhhm:
                                        os`./`/````/`-/:+oydhhhhhhdh`
                                        `so.-/-:``./`.//osmddddddmd. 
                                          /s/-/:/.`/..+/ydmdddddmo`
                                           `:oosso/:+/syNmddmdy/. 
                                               `-/++oosyso+/.` 
                            
                            
          ██████╗ ███████╗██████╗ ███████╗██████╗  ██████╗    ██╗███╗   ██╗███████╗██╗██████╗ ███████╗
          ██╔══██╗██╔════╝██╔══██╗██╔════╝╚════██╗██╔════╝    ██║████╗  ██║██╔════╝██║██╔══██╗██╔════╝
          ██║  ██║█████╗  ██║  ██║███████╗ █████╔╝██║         ██║██╔██╗ ██║███████╗██║██║  ██║█████╗ 
          ██║  ██║██╔══╝  ██║  ██║╚════██║ ╚═══██╗██║         ██║██║╚██╗██║╚════██║██║██║  ██║██╔══╝ 
          ██████╔╝███████╗██████╔╝███████║██████╔╝╚██████╗    ██║██║ ╚████║███████║██║██████╔╝███████╗
          ╚═════╝ ╚══════╝╚═════╝ ╚══════╝╚═════╝  ╚═════╝    ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝╚═════╝ ╚══════╝
                                                                                            


</pre>

## OSINT tool for Deep and Dark Web.
[![Build Status](https://travis-ci.org/DedSecInside/TorBoT.svg?branch=master)](https://travis-ci.org/DedSecInside/TorBoT)
[![](https://img.shields.io/badge/Donate-Bitcoin-blue.svg?style=flat)](https://blockchain.info/address/14st7SzDbQZuu8fpQ74x477WoRJ7gpHFaj)
[![](https://img.shields.io/badge/Built%20with-❤-orange.svg?style=flat)]()
[![](https://img.shields.io/badge/Made%20with-Python-red.svg?style=flat)]()


### Working Procedure/Basic Plan
The basic procedure executed by the web crawling algorithm takes a list of seed URLs as its input and repeatedly executes
the following steps:

1. Remove a URL from the URL list.
2. Check existence of the page.
3. Download the corresponding page.
4. Check the Relevancy of the page.
5. Extract any links contained in it.
6. Check the cache if the links are already in it.
7. Add the unique links back to the URL list.
8. After all URLs are processed, return the most relevant page.

### Features
1. Onion Crawler (.onion).(Completed)
2. Returns Page title and address with a short description about the site.(Partially Completed)
3. Save links to database.(Not Started)
4. Get emails from site.(Completed)
5. Save crawl info to JSON file.(Completed)
6. Crawl custom domains.(Completed)
7. Check if the link is live.(Completed)
8. Built-in Updater.(Completed)
...(will be updated)

## Contribute
Contributions to this project are always welcome. 
To add a new feature fork the dev branch and give a pull request when your new feature is tested and complete.
If its a new module, it should be put inside the modules directory and imported to the main file.
The branch name should be your new feature name in the format <Feature_featurename_version(optional)>. For example, <i>Feature_FasterCrawl_1.0</i>.
Contributor name will be updated to the below list. :D

## Dependencies 
1. Tor 
2. Python 3.x (Make sure pip3 is installed)
3. requests
4. Beautiful Soup 4
5. Socket
6. Sock
7. Argparse
8. Git
9. termcolor
10. tldextract

## Basic setup
Before you run the torBot make sure the following things are done properly:

* Run tor service
`sudo service tor start`

* Make sure that your torrc is configured to SOCKS_PORT localhost:9050 

`python3 torBot.py or use the -h/--help argument`
<pre>
`usage: torBot.py [-h] [-v] [--update] [-q] [-u URL] [-s] [-m] [-e EXTENSION]
                 [-l] [-i]

optional arguments:
  -h, --help            Show this help message and exit
  -v, --version         Show current version of TorBot.
  --update              Update TorBot to the latest stable version
  -q, --quiet           Prevent header from displaying
  -u URL, --url URL     Specifiy a website link to crawl, currently returns links on that page
  -s, --save            Save results to a file in json format
  -m, --mail            Get e-mail addresses from the crawled sites
  -e EXTENSION, --extension EXTENSION
                        Specifiy additional website extensions to the
                        list(.com or .org etc)
  -l, --live            Check if websites are live or not (slow)
  -i, --info            Info displays basic info of the scanned site (very
                        slow)` </pre>

* NOTE: All flags under -u URL, --url URL must also be passed a -u flag.

Read more about torrc here : [Torrc](https://github.com/DedSecInside/TorBoT/blob/master/Tor.md)

## TO-DO
- [ ] Implement A\* Search for webcrawler
- [ ] Multithreading
- [ ] Optimization
- [ ] Randomize Tor Connection (Random Header and Identity)

### Have ideas?
If you have new ideas which is worth implementing, mention those by starting a new issue with the title [FEATURE_REQUEST].
If the idea is worth implementing, congratz you are now a contributor.

## License
GNU Public License

## CREDITS

- [X] [P5N4PPZ](https://github.com/PSNAppz) - Owner
- [X] [agrepravin](https://github.com/agrepravin) - Contributor,Reviewer
- [X] [y-mehta](https://github.com/y-mehta) - Contributor
- [X] [Manfredi Martorana](https://github.com/Agostinelli) - Contributor
- [X] [KingAkeem](https://github.com/KingAkeem) - Contributor
- [X] [Evan Sia Wai Suan](https://github.com/waisuan) - New Contributor
- [X] [Lean](https://github.com/leaen) - New Contributor

![](https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Opensource.svg/200px-Opensource.svg.png)

