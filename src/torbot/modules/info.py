"""
Module that contains methods for collecting all relevant data from links,
and saving data to file.
"""
import re
import httpx
import logging

from urllib.parse import urlsplit
from bs4 import BeautifulSoup
from termcolor import cprint


keys = set()  # high entropy strings, prolly secret keys
files = set()  # pdf, css, png etc.
intel = set()  # emails, website accounts, aws buckets etc.
robots = set()  # entries of robots.txt
custom = set()  # string extracted by custom regex pattern
failed = set()  # urls that photon failed to crawl
scripts = set()  # javascript files
external = set()  # urls that don't belong to the target i.e. out-of-scope
fuzzable = set()  # urls that have get params in them e.g. example.com/page.php?id=2
endpoints = set()  # urls found from javascript files
processed = set()  # urls that have been crawled

everything = []
bad_intel = set()  # unclean intel urls
bad_scripts = set()  # unclean javascript file urls
datasets = [
    files,
    intel,
    robots,
    custom,
    failed,
    scripts,
    external,
    fuzzable,
    endpoints,
    keys,
]
dataset_names = [
    "files",
    "intel",
    "robots",
    "custom",
    "failed",
    "scripts",
    "external",
    "fuzzable",
    "endpoints",
    "keys",
]


def execute_all(
    client: httpx.Client, link: str, *, display_status: bool = False
) -> None:
    """Initialise datasets and functions to retrieve data, and execute
    each for a given link.

    Args:
        link (str): Link to be interogated.
        display_status (bool, optional): Whether to print connection
            attempts to terminal.
    """

    resp = client.get(url=link)
    soup = BeautifulSoup(resp.text, "html.parser")
    validation_functions = [
        get_robots_txt,
        get_dot_git,
        get_dot_svn,
        get_dot_git,
        get_intel,
        get_dot_htaccess,
        get_bitcoin_address,
    ]
    for validate_func in validation_functions:
        try:
            validate_func(client, link, resp)
        except Exception as e:
            logging.debug(e)
            cprint("Error", "red")

    display_webpage_description(soup)
    # display_headers(response)


def display_headers(response):
    """Print all headers in response object.

    Args:
        response (object): Response object.
    """
    print(
        """
          RESPONSE HEADERS
          __________________
          """
    )
    for key, val in response.headers.items():
        print("*", key, ":", val)


def get_robots_txt(client: httpx.Client, target: str, response: str) -> None:
    """Check link for Robot.txt, and if found, add link to robots dataset.

    Args:
        target (str): URL to be checked.
        response (object): Response object containing data to check.
    """
    cprint("[*]Checking for Robots.txt", "yellow")
    url = target
    target = "{0.scheme}://{0.netloc}/".format(urlsplit(url))
    client.get(target + "robots.txt")
    print(target + "robots.txt")
    matches = re.findall(r"Allow: (.*)|Disallow: (.*)", response)
    for match in matches:
        match = "".join(match)
        if "*" not in match:
            url = target + match
            robots.add(url)
        cprint("Robots.txt found", "blue")
        print(robots)


def get_intel(client: httpx.Client, url: str, response: str) -> None:
    """Check link for intel, and if found, add link to intel dataset,
    including but not limited to website accounts and AWS buckets.

    Args:
        target (str): URL to be checked.
        response (object): Response object containing data to check.
    """
    intel = set()
    regex = r"""([\w\.-]+s[\w\.-]+\.amazonaws\.com)|([\w\.-]+@[\w\.-]+\.[\.\w]+)"""
    matches = re.findall(regex, response)
    print("Intel\n--------\n\n")
    for match in matches:
        intel.add(match)


def get_dot_git(client: httpx.Client, target: str, response: str) -> None:
    """Check link for .git folders exposed on public domain.

    Args:
        target (str): URL to be checked.
        response (object): Response object containing data to check.
    """
    cprint("[*]Checking for .git folder", "yellow")
    url = target
    target = "{0.scheme}://{0.netloc}/".format(urlsplit(url))
    resp = client.get(target + "/.git/config")
    if not resp.text.__contains__("404"):
        cprint("Alert!", "red")
        cprint(".git folder exposed publicly", "red")
    else:
        cprint("NO .git folder found", "blue")


def get_bitcoin_address(client: httpx.Client, target: str, response: str) -> None:
    """Check link for Bitcoin addresses, and if found, print.

    Args:
        target (str): URL to be checked.
        response (object): Response object containing data to check.
    """
    bitcoins = re.findall(r"^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$", response)
    print("BTC FOUND: ", len(bitcoins))
    for bitcoin in bitcoins:
        print("BTC: ", bitcoin)


def get_dot_svn(client: httpx.Client, target: str, response: str) -> None:
    """Check link for .svn folders exposed on public domain=.

    Args:
        target (str): URL to be checked.
        response (object): Response object containing data to check.
    """
    cprint("[*]Checking for .svn folder", "yellow")
    url = target
    target = "{0.scheme}://{0.netloc}/".format(urlsplit(url))
    resp = httpx.get(target + "/.svn/entries", proxies="socks5://127.0.0.1:9050")
    if not resp.text.__contains__("404"):
        cprint("Alert!", "red")
        cprint(".SVN folder exposed publicly", "red")
    else:
        cprint("NO .SVN folder found", "blue")


def get_dot_htaccess(client: httpx.Client, target: str, response: str) -> None:
    """Check link for .htaccess files on public domain.

    Args:
        target (str): URL to be checked.
        response (object): Response object containing data to check.
    """
    cprint("[*]Checking for .htaccess", "yellow")
    url = target
    target = "{0.scheme}://{0.netloc}/".format(urlsplit(url))
    resp = httpx.get(target + "/.htaccess", proxies="socks5://127.0.0.1:9050")
    if resp.text.__contains__("403"):
        cprint("403 Forbidden", "blue")
    elif not resp.text.__contains__("404") or resp.text.__contains__("500"):
        cprint("Alert!!", "blue")
        cprint(".htaccess file found!", "blue")
    else:
        cprint("Response", "blue")
        cprint(resp, "blue")


def display_webpage_description(soup: BeautifulSoup) -> None:
    """Print all meta tags found in page.

    Args:
        soup (object): Processed HTML object.
    """
    cprint("[*]Checking for meta tag", "yellow")
    metatags = soup.find_all("meta")
    for meta in metatags:
        print("Meta : ", meta)


def writer(datasets, dataset_names, output_dir):
    """Write content of all datasets to file.

    Args:
        datasets (list): List of datasets containing relevant content.
        dataset_names (list): Identifiers for each dataset.
        output_dir (str): Path where data file should be saved.
    """
    for dataset, dataset_name in zip(datasets, dataset_names):
        if dataset:
            filepath = output_dir + "/" + dataset_name + ".txt"

            with open(filepath, "w+", encoding="utf8") as f:
                f.write(str("\n".join(dataset)))
                f.write("\n")
            # else:
            #     with open(filepath, 'w+') as f:
            #         joined = '\n'.join(dataset)
            #         f.write(str(joined.encode('utf-8')))
            #         f.write('\n')
