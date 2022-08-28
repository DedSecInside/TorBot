 <pre>

                         ████████╗ ██████╗ ██████╗     ██████╗  ██████╗ ████████╗
                         ╚══██╔══╝██╔═══██╗██╔══██╗    ██╔══██╗██╔═████╗╚══██╔══╝
                            ██║   ██║   ██║██████╔╝    ██████╔╝██║██╔██║   ██║
                            ██║   ██║   ██║██╔══██╗    ██╔══██╗████╔╝██║   ██║
                            ██║   ╚██████╔╝██║  ██║    ██████╔╝╚██████╔╝   ██║
                            ╚═╝    ╚═════╝ ╚═╝  ╚═╝    ╚═════╝  ╚═════╝    ╚═╝

                            Open Source Intelligence Tool for the Dark Web

</pre>

<p align="center">
   <img src="https://user-images.githubusercontent.com/4481429/94646151-43167180-030b-11eb-823d-dc0d79889b14.png" width="160" title="Hacktoberfest 2020">
    <img src="https://user-images.githubusercontent.com/4481429/94646312-9dafcd80-030b-11eb-9824-73aa2414cf58.png" width="100" title="OpenSource">
  <img src="https://user-images.githubusercontent.com/4481429/94645022-65f35680-0308-11eb-8dce-a4ceba8db660.png" width="270" title="OWASP Foundation">
</p>


### Status/Social links
[![Build Status](https://travis-ci.org/DedSecInside/TorBot.svg?branch=dev)](https://travis-ci.org/DedSecInside/TorBoT)
[![Slack Invite](https://img.shields.io/badge/Join-Slack-informational?style=flat-square&logo=slack)](https://join.slack.com/t/dedsec-inside/shared_invite/zt-i4jcgj8w-1ecHiSdRubwuppAzz8~yfg)
[![Code Triage](https://www.codetriage.com/dedsecinside/torbot/badges/users.svg)](https://www.codetriage.com/dedsecinside/torbot)
[![](https://img.shields.io/badge/Built%20with-❤-orange.svg?style=flat-square)]()
[![](https://img.shields.io/badge/Made%20with-Python-red.svg?style=flat-square)]()

### Features
1. Onion Crawler (.onion).(Completed)
2. Returns Page title and address with a short description about the site.(Partially Completed)
3. Save links to database.(PR to be reviewed)
4. Get emails from site.(Completed)
5. Save crawl info to JSON file.(Completed)
6. Crawl custom domains.(Completed)
7. Check if the link is live.(Completed)
8. Built-in Updater.(Completed)
9. TorBot GUI (In progress)
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
- Python ^3.7
- Golang 1.16

### Python Dependencies

(see requirements.txt for more details)
altgraph==0.17.2
beautifulsoup4==4.11.1
certifi==2022.5.18.1
charset-normalizer==2.0.12
decorator==5.1.1
ete3==3.1.2
idna==3.3
macholib==1.16
numpy==1.22.4
progress==1.6
pyinstaller==5.1
pyinstaller-hooks-contrib==2022.7
PySocks==1.7.1
python-dotenv==0.20.0
requests==2.28.0
requests-mock==1.9.3
six==1.16.0
soupsieve==2.3.2.post1
termcolor==1.1.0
threadsafe==1.0.0
urllib3==1.26.9
validators==0.20.0
yattag==1.14.0
pyqt5==5.15.6 (Install using apt/brew if pip installation fails.)
### Golang Dependencies
- https://github.com/KingAkeem/gotor (This service needs to be ran in tandem with TorBot)

## Installation

### From source
Before you run the torBot make sure the following things are done properly:

* Run tor service
`sudo service tor start`

* Make sure that your torrc is configured to SOCKS_PORT localhost:9050

* Open a new terminal and run `cd gotor && go run main.go -server`

* Install TorBot Python requirements using
`pip install -r requirements.txt`

Finally run the following command

`python3 run.py -h`
<pre>
usage: torBot.py [-h] [-v] [--update] [-q] [-u URL] [-s] [-m] [-e EXTENSION]
                 [-i]

optional arguments:
  -h, --help            Show this help message and exit
  -v, --version         Show current version of TorBot.
  --update              Update TorBot to the latest stable version
  -q, --quiet           Prevent header from displaying
  -u URL, --url URL     Specifiy a website link to crawl, currently returns links on that page (if used alone e.g. python3 torBot.py -u https://www.github.com)
  -s, --save            Save results to a file in json format
  -m, --mail            Get e-mail addresses from the crawled sites
  -e EXTENSION, --extension EXTENSION
                        Specifiy additional website extensions to the
                        list(.com or .org etc)
  -i, --info            Info displays basic info of the scanned site (very
                        slow)` </pre>

* NOTE: All flags under -u URL, --url URL must also be passed a -u flag.

Read more about torrc here : [Torrc](https://github.com/DedSecInside/TorBoT/blob/master/Tor.md)

### Using Docker

- Ensure than you have a tor container running on port 9050.
- Build the image using following command (in the root directory):

    `docker build -f docker/Dockerfile -t dedsecinside/torbot .`
- Run the container (make sure to link the tor container as `tor`):

    `docker run --link tor:tor --rm -ti dedsecinside/torbot`

### Using executable (Linux Only)

On Linux platforms, you can make an executable for TorBot by using the install.sh script.
You will need to give the script the correct permissions using `chmod +x install.sh`
Now you can run `./install.sh` to create the torBot binary.
Run `./torBot` to execute the program.


## TO-DO
- [x] Visualization Module
- [x] Implement BFS Search for webcrawler
- [x] Use Golang service for concurrent webcrawling
- [x] Improve stability (Handle errors gracefully, expand test coverage and etc.)
- [x] Create a user-friendly GUI
- [ ] Randomize Tor Connection (Random Header and Identity)
- [ ] Keyword/Phrase search
- [ ] Social Media Integration
- [ ] Increase anonymity
- [x] Increase efficiency

### Have ideas?
If you have new ideas which is worth implementing, mention those by creating a new issue with the title [FEATURE_REQUEST].



### References

    1.  M. Glassman and M. J. Kang, “Intelligence in the internet age: The emergence and evolution of Open Source Intelligence (OSINT),” Comput. Human Behav., vol. 28, no. 2, pp. 673–682, 2012.
    2.  D. Bradbury, “In plain view: open source intelligence,” Comput. Fraud Secur., vol. 2011, no. 4, pp. 5–9, 2011.
    3.  B. Butler, B. Wardman, and N. Pratt, “REAPER: an automated, scalable solution for mass credential harvesting and OSINT,” 2016 APWG Symp. Electron. Crime Res., pp. 1–10, 2016.
    4.  B. Zantout and R. A. Haraty, “I2P Data Communication System I2P Data Communication System,” no. April 2002, 2014.
    5.  J. Qin, Y. Zhou, G. Lai, E. Reid, M. Sageman, and H. Chen, “The dark web portal project: collecting and analyzing the presence of terrorist groups on the web,” in Proceedings of the 2005 IEEE international conference on Intelligence and Security Informatics, 2005, pp. 623–624.
    6.  D. Moore, T. Rid, D. Moore, and T. Rid, “Cryptopolitik and the Darknet Cryptopolitik and the Darknet,” vol. 6338, 2016.
    7.  G. Weimann, “Going dark: Terrorism on the dark Web,” Stud. Confl. Terror., vol. 39, no. 3, pp. 195–206, 2016.
    8.  A. T. Zulkarnine, R. Frank, B. Monk, J. Mitchell, and G. Davies, “Surfacing collaborated networks in dark web to find illicit and criminal content,” in Intelligence and Security Informatics (ISI), 2016 IEEE Conference on, 2016, pp. 109–114.
    9.  T. Minárik and A.-M. Osula, “Tor does not stink: Use and abuse of the Tor anonymity network from the perspective of law,” Comput. Law Secur. Rev., vol. 32, no. 1, pp. 111–127, 2016.
    10. K. Loesing, S. J. Murdoch, and R. Dingledine, “A Case Study on Measuring Statistical Data in the {T}or Anonymity Network,” in Proceedings of the Workshop on Ethics in Computer Security Research (WECSR 2010), 2010.
    11. B. Nafziger, “Data Mining in the Dark : Darknet Intelligence Automation,” 2017.
    12. I. Sanchez-Rola, D. Balzarotti, and I. Santos, “The onions have eyes: A comprehensive structure and privacy analysis of tor hidden services,” in Proceedings of the 26th International Conference on World Wide Web, 2017, pp. 1251–1260.
    13. Mouli VR, Jevitha KP. “Web Services Attacks and Security-A Systematic Literature Review.”, Procedia Computer Science. 2016 Jan 1;93:870-7.
    14. Cova M, Felmetsger V, Vigna G. "Vulnerability analysis of web-based applications. InTest and Analysis of Web Services" 2007 (pp. 363-394). Springer, Berlin, Heidelberg.
    15. B. R. Holland, “Enabling Open Source Intelligence (OSINT) in private social networks,” 2012.
    16. S. Nakamoto, “Bitcoin: A Peer-to-Peer Electronic Cash System,” Cryptogr. Mail. List https//metzdowd.com, 2009.
    17. M. Wesam, A. Nabki, E. Fidalgo, E. Alegre, and I. De Paz, “Classifying Illegal Activities on Tor Network Based on Web Textual Contents”, vol. 1, pp. 35–43, 2017.
    18. Sathyadevan S, Gangadharan S.“Crime analysis and prediction using data mining”. In Networks & Soft Computing (ICNSC), 2014 First International Conference on 2014 Aug 19 (pp. 406-412). IEEE.
    19. Chau M, Chen H. "A machine learning approach to web page filtering using content and structure analysis. Decision Support Systems." 2008 Jan 1;44(2):482-94.
    20. Ani R, Jose J, Wilson M, Deepa OS. “Modified Rotation Forest Ensemble Classifier for Medical Diagnosis in Decision Support Systems”, In Progress in Advanced Computing and Intelligent Engineering 2018 (pp. 137-146). Springer, Singapore.
    21. Ani R, Augustine A, Akhil N.C. and Deepa O.S., 2016. “Random Forest Ensemble Classifier to Predict the Coronary Heart Disease Using Risk Factors”, In Proceedings of the International Conference on Soft Computing Systems (pp. 701-710). Springer, New Delhi.



## License
GNU Public License

## CREDITS

- [X] [P5N4PPZ](https://github.com/PSNAppz) - Co-owner
- [X] [KingAkeem](https://github.com/KingAkeem) - Co-owner
- [X] [masterugwee](https://github.com/masterugwee) - Contributor,Core Member
- [X] [soorajsomans](https://github.com/soorajsomans) - Contributor,Core Member
- [X] [agrepravin](https://github.com/agrepravin) - Contributor,Reviewer
- [X] [shivankar-madaan](https://github.com/shivankar-madaan) - Experienced Contributor
- [X] [y-mehta](https://github.com/y-mehta) - Contributor
- [X] [Manfredi Martorana](https://github.com/Agostinelli) - Contributor
- [X] [Evan Sia Wai Suan](https://github.com/waisuan) - New Contributor
- [X] [Lean](https://github.com/leaen) - New Contributor
- [X] [Gus](https://github.com/HotPushUpGuy420) - New Contributor
- [X] [SubaruSama](https://github.com/SubaruSama) - New Contributor
- [X] [robly78746](https://github.com/robly78746) - New Contributor

... see all contributors here (https://github.com/DedSecInside/TorBot/graphs/contributors)


