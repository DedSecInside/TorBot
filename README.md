 <pre>

                           ████████╗ ██████╗ ██████╗     ██████╗  ██████╗ ████████╗
                           ╚══██╔══╝██╔═══██╗██╔══██╗    ██╔══██╗██╔═████╗╚══██╔══╝
                              ██║   ██║   ██║██████╔╝    ██████╔╝██║██╔██║   ██║
                              ██║   ██║   ██║██╔══██╗    ██╔══██╗████╔╝██║   ██║
                              ██║   ╚██████╔╝██║  ██║    ██████╔╝╚██████╔╝   ██║
                              ╚═╝    ╚═════╝ ╚═╝  ╚═╝    ╚═════╝  ╚═════╝    ╚═╝
		       
	           	        Open Source Intelligence Tool for the Dark Web
                                                     
</pre>
[![Build Status](https://travis-ci.org/DedSecInside/TorBot.svg?branch=dev)](https://travis-ci.org/DedSecInside/TorBoT)
[![](https://img.shields.io/badge/Donate-Bitcoin-blue.svg?style=flat)](https://blockchain.info/address/14st7SzDbQZuu8fpQ74x477WoRJ7gpHFaj)
[![](https://img.shields.io/badge/Built%20with-❤-orange.svg?style=flat)]()
[![](https://img.shields.io/badge/Made%20with-Python-red.svg?style=flat)]()

## Working Procedure/Basic Plan
The basic procedure executed by the web crawling algorithm takes a list of seed URLs as its input and repeatedly executes
the following steps:
<code>
 <pre>
URLs = input(url)
while(URLs is not empty) do
	dequeue url
	request page
	parse for Links
	for(link in Links) do 
		if (link islive && link is not visited) then 
			add link to URLs
	store page content
 </pre>
 </code>

### Features
1. Onion Crawler (.onion).(Completed)
2. Returns Page title and address with a short description about the site.(Partially Completed)
3. Save links to database.(PR to be reviewed)
4. Get emails from site.(Completed)
5. Save crawl info to JSON file.(Completed)
6. Crawl custom domains.(Completed)
7. Check if the link is live.(Completed)
8. Built-in Updater.(Completed)
9. Visualizer module.(Not started)
10. Social Media integration.(not Started)
...(will be updated)

## Contribute
Contributions to this project are always welcome.
To add a new feature fork the dev branch and give a pull request when your new feature is tested and complete.
If its a new module, it should be put inside the modules directory.
The branch name should be your new feature name in the format <Feature_featurename_version(optional)>. For example, <i>Feature_FasterCrawl_1.0</i>.
Contributor name will be updated to the below list. 😀
<br>
<b> NOTE : The PR should be made only to `dev` branch of TorBot. </b>

### OS Dependencies
- Tor
- Python 3.x
- Golang 1.x (Not Currently Used)

### Python Dependencies
- beautifulsoup4
- pyinstaller
- PySocks
- termcolor
- requests
- requests_mock
- yattag


## Basic setup
Before you run the torBot make sure the following things are done properly:

* Run tor service
`sudo service tor start`

* Make sure that your torrc is configured to SOCKS_PORT localhost:9050

* Install TorBot Python requirements
`pip3 install -r requirements.txt`

On Linux platforms, you can make an executable for TorBot by using the install.sh script.
You will need to give the script the correct permissions using `chmod +x install.sh`
Now you can run `./install.sh` to create the torBot binary.
Run `./torBot` to execute the program. 

An alternative way of running torBot is shown below, along with help instructions.

`python3 torBot.py or use the -h/--help argument`
<pre>
usage: torBot.py [-h] [-v] [--update] [-q] [-u URL] [-s] [-m] [-e EXTENSION]
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
- [ ] Visualization Module
- [x] Implement BFS Search for webcrawler
- [X] Multithreading for Get Links
- [ ] Improve stability (Handle errors gracefully, expand test coverage and etc.)
- [ ] Create a user-friendly GUI 
- [ ] Randomize Tor Connection (Random Header and Identity)
- [ ] Keyword/Phrase search
- [ ] Social Media Integration
- [ ] Increase anonymity and efficiency

### Have ideas?
If you have new ideas which is worth implementing, mention those by starting a new issue with the title [FEATURE_REQUEST].
If the idea is worth implementing, congratz, you are now a contributor.

## Related Works
OSINT and the Dark Web: The Dark Web has proven a very useful and reliable tool in the hands of individuals wishing to be involved in illegal, criminal or terrorist activities, setting sight on getting great economic or political benefits without being identified from government authorities and security agencies world-wide. To this end, LEAs need to become more agile when dealing with criminality on the Dark Web, and in particular on its Hidden Service Markets, and need to invest in new training and technology, if not to get ahead of the criminals, then at least to keep pace[1]. 

Using TOR for Open Source Intelligence: Although the use of Tor for OSINT does not raise specific legal concerns, there are a few interesting arguments that have been raised about using OSINT in general. One of them touches on the Council of Europe’s Convention on Cybercrime. Article 32 (a) of the Convention regulates transborder access to stored computer data with respect to ‘publicly available (open source) stored computer data, regardless of where the data is located geographically’[2].

OSINT in Social Networks: In summary, they examined and compared the needs of the Open Source Intelligence community with what social media has to offer investigators. They observed that a friends list of a given individual is a useful starting point for launching an investigation but found that several technical limitations (privacy and platform restrictions and data availability and longevity) may prevent investigators from accessing friend list information of a target account. They address privacy restrictions for the particular case of friends by creating a private friend discovery algorithm with hunter-seeker behaviours[3]. 

Data Mining in The Dark: This paper successfully explored an open-source intelligence automation toolset that scanned across the darknet. It described and shared the tools, process, and techniques to build a secure darknet connection, and then collected, processed, stored, and analysed data. This paper showed the viability of darknet open-source intelligence using the completed toolset. In the end, the toolset finds entities and links entities from the darknet thereby showing strong potential to aid the open source intelligence professional[4]. 

### References

    [1]	B. Akhgar, P. S. Bayerl, and F. Sampson, Open Source Intelligence Investigation. From strategy to implementation.     2016.
    [2]	T. Minárik and A.-M. Osula, “Tor does not stink: Use and abuse of the Tor anonymity network from the perspective of law,” Comput. Law Secur. Rev., vol. 32, no. 1, pp. 111–127, Feb. 2016.
    [3]	Benjamin Robert Holland, “Enabling Open Source Intelligence (OSINT) in private social networks,” 2012.
    [4]	Brian Nafziger, “Data Mining in the Dark: Darknet Intelligence Automation,” Secur. Home IoT Netw., no. Security 401, pp. 1–32, 2017.
    [5]	A. R. Behjat, A. Mustapha, H. Nezamabadi-Pour, M. N. Sulaiman, and N. Mustapha, “A New Binary Particle Swarm   Optimization for Feature Subset Selection with Support Vector Machine,” in Recent Advances on Soft Computing and Data   Mining, 2014, pp. 47–57.
    [6]	H. Parmar, S. Bhanderi, and G. Shah, “Sentiment Mining of Movie Reviews using Random Forest with Tuned Hyperparameters.” 2014.


## License
GNU Public License

## CREDITS

- [X] [P5N4PPZ](https://github.com/PSNAppz) - Owner
- [X] [KingAkeem](https://github.com/KingAkeem) - Experienced Contributor,Reviewer,Core Member
- [X] [agrepravin](https://github.com/agrepravin) - Contributor,Reviewer
- [X] [shivankar-madaan](https://github.com/shivankar-madaan) - Experienced Contributor
- [X] [y-mehta](https://github.com/y-mehta) - Contributor
- [X] [Manfredi Martorana](https://github.com/Agostinelli) - Contributor
- [X] [Evan Sia Wai Suan](https://github.com/waisuan) - New Contributor
- [X] [Lean](https://github.com/leaen) - New Contributor
- [X] [Gus](https://github.com/HotPushUpGuy420) - New Contributor
- [X] [SubaruSama](https://github.com/SubaruSama) - New Contributor
- [X] [robly78746](https://github.com/robly78746) - New Contributor

![](https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Opensource.svg/200px-Opensource.svg.png)
