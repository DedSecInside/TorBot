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
   <a href="https://owasp.org/www-project-torbot/">
    <img src="https://user-images.githubusercontent.com/4481429/94645022-65f35680-0308-11eb-8dce-a4ceba8db660.png" width="270" title="OWASP Foundation">
   </a>
   <img src="https://github.com/DedSecInside/TorBot/assets/4481429/41f5e7ea-56fe-41b0-bd26-2788deeb5f10" width="250" title="Hacktoberfest 2022">
   <img src="https://user-images.githubusercontent.com/4481429/94646312-9dafcd80-030b-11eb-9824-73aa2414cf58.png" width="160" title="OpenSource">
</p>


### Status/Social links
[![Pytest](https://github.com/DedSecInside/TorBot/actions/workflows/pytest.yml/badge.svg)](https://github.com/DedSecInside/TorBot/actions/workflows/pytest.yml)
[![Flake8](https://github.com/DedSecInside/TorBot/actions/workflows/flake8.yml/badge.svg)](https://github.com/DedSecInside/TorBot/actions/workflows/flake8.yml)
[![Slack Invite](https://img.shields.io/badge/Join-Slack-informational?style=flat-square&logo=slack)](https://join.slack.com/t/dedsec-inside/shared_invite/zt-i4jcgj8w-1ecHiSdRubwuppAzz8~yfg)
[![Code Triage](https://www.codetriage.com/dedsecinside/torbot/badges/users.svg)](https://www.codetriage.com/dedsecinside/torbot)
[![](https://img.shields.io/badge/Built%20with-❤-orange.svg?style=flat-square)]()
[![](https://img.shields.io/badge/Made%20with-Python-red.svg?style=flat-square)]()

### Features
1. Onion Crawler (.onion)
2. Returns page title or host name if no page title is available and address with a short description of the site.
3. Save links to a database (Not done)
4. Output the HTML from a site or save it to an HTML file. (Not done)
5. Save the link tree as a JSON file.
6. Crawl custom domains
7. Check if the link is live
8. Built-in Updater
9. Build a visual tree of link relationships that can be quickly viewed or saved to a file

...(will be updated)

### Dependencies
- Tor (Optional)
- Python ^3.9
- Poetry (Optional)

### Python Dependencies

(see pyproject.toml or requirements.txt for more details)

## Installation

### TorBot

#### Using `venv`
* If using Python ^3.4,
```sh
python -m venv torbot_venv
source torbot_venv/bin/activate
pip install -r requirements.txt
pip install -e .
./main.py --help
```

#### Using `docker`
```sh
docker build -t {image_name} .

# Running without Tor
docker run {image_name} poetry run python torbot -u https://example.com --depth 2 --visualize tree --save json --disable-socks5

# Running with Tor
docker run --network="host" {image_name} poetry run python torbot -u https://example.com --depth 2 --visualize tree --save json --disable-socks5
```

### Options
<pre>
usage: Gather and analyze data from Tor sites.

optional arguments:
  -u URL, --url URL     Specify a website link to crawl
  --depth DEPTH         Specify max depth of crawler (default 1)
  -h, --help            Show this help message and exit
  --host                Set IP address for SOCKS5 proxy (defaults to 127.0.0.1)
  --port                Set port for SOCKS5 proxy (defaults to 9050)
  -v                    Displays DEBUG level logging, default is INFO
  --version             Show the current version of TorBot.
  --update              Update TorBot to the latest stable version
  -q, --quiet           Prevents display of header and IP address
  --save FORMAT         Save results in a file. (tree, JSON)
  --visualize FORMAT    Visualizes tree of data gathered. (tree, JSON, table)
  -i, --info            Info displays basic info of the scanned site
  --disable-socks5      Executes HTTP requests without using SOCKS5 proxy</pre>

* NOTE: -u is a mandatory for crawling

Read more about torrc here : [Torrc](https://github.com/DedSecInside/TorBoT/blob/master/Tor.md)

## Curated Features
- [x] Visualization Module Revamp
- [x] Implement BFS Search for webcrawler
- [x] Improve stability (Handle errors gracefully, expand test coverage, etc.)
- [x] Increase test coverage
- [ ] Save the most recent search results to a database
- [ ] Randomize Tor Connection (Random Header and Identity)
- [ ] Keyword/Phrase Search
- [ ] Social Media Integration
- [ ] Increase anonymity
- [ ] Screenshot capture


## Contribution Guidelines

### Found an issue?

If you face any issues in the project, please let us know by creating a new issue [here](https://github.com/DedSecInside/TorBot/issues/new/choose).

### Developer Guidelines

We welcome contributions to this project! Here are a few guidelines to follow:

1. Fork the repository and create a new branch for your contribution.
2. Make sure your code passes all tests by running `pytest` before submitting a pull request to `dev` branch.
3. Follow the [PEP8](https://www.python.org/dev/peps/pep-0008/) style guide for Python code.
4. Make sure to add appropriate documentation for any new features or changes.
5. When submitting a pull request, please provide a detailed description of the changes made.

## References

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


## Maintainers

- [X] [PS Narayanan](https://github.com/PSNAppz) - Co-owner
- [X] [KingAkeem](https://github.com/KingAkeem) - Co-owner

## All Thanks to Our Contributors

<a href="https://github.com/DedSecInside/TorBot/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=DedSecInside/TorBot" />
</a>

## License
[GNU Public License](https://github.com/DedSecInside/TorBot/blob/dev/LICENSE.md)
