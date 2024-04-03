"""
Module is used for analyzing link relationships
"""
import http.client
import os
import json
import httpx
import validators
import logging
import phonenumbers

from urllib import parse
from tabulate import tabulate
from treelib import Tree, exceptions, Node
from bs4 import BeautifulSoup

from .color import color
from .config import project_root_directory
from .nlp.main import classify


class LinkNode(Node):
    def __init__(
        self,
        title: str,
        url: str,
        status: int,
        classification: str,
        accuracy: float,
        numbers: list[str],
        emails: list[str],
    ):
        super().__init__()
        self.identifier = url
        self.tag = title
        self.status = status
        self.classification = classification
        self.accuracy = accuracy
        self.numbers = numbers
        self.emails = emails


class LinkTree(Tree):
    def __init__(self, url: str, depth: int, client: httpx.Client) -> None:
        super().__init__()
        self._url = url
        self._depth = depth
        self._client = client

    def load(self) -> None:
        self._append_node(id=self._url, parent_id=None)
        self._build_tree(url=self._url, depth=self._depth)

    def _append_node(self, id: str, parent_id: str or None) -> None:
        """
        Creates a node for a tree using the given ID which corresponds to a URL.
        If the parent_id is None, this will be considered a root node.
        """
        resp = self._client.get(id)
        soup = BeautifulSoup(resp.text, "html.parser")
        title = (
            soup.title.text.strip() if soup.title is not None else parse_hostname(id)
        )
        try:
            [classification, accuracy] = classify(resp.text)
            numbers = parse_phone_numbers(soup)
            emails = parse_emails(soup)
            data = LinkNode(
                title, id, resp.status_code, classification, accuracy, numbers, emails
            )
            self.create_node(title, identifier=id, parent=parent_id, data=data)
        except exceptions.DuplicatedNodeIdError:
            logging.debug(f"found a duplicate URL {id}")

    def _build_tree(self, url: str, depth: int) -> None:
        """
        Builds a tree from the root to the given depth.
        """
        if depth > 0:
            depth -= 1
            resp = self._client.get(url)
            children = parse_links(resp.text)
            for child in children:
                self._append_node(id=child, parent_id=url)
                self._build_tree(url=child, depth=depth)

    def _get_tree_file_name(self) -> str:
        root_id = self.root
        root_node = self.get_node(root_id)
        if root_node is None:
            raise Exception("no root node can be found.")

        return os.path.join(
            project_root_directory, f"{root_node.tag} - Depth {self._depth}"
        )

    def save(self) -> None:
        """
        Saves the tree to the current working directory under the given file name.
        """
        file_name = self._get_tree_file_name()
        self.save2file(f"{file_name}.txt")

    def saveJSON(self) -> None:
        """
        Saves the tree to the current working directory under the given file name in JSON.
        """
        json_data = self._to_json()
        file_name = self._get_tree_file_name()
        with open(f"{file_name}.json", "w+") as f:
            f.write(json_data)

    def _to_json(self) -> str:
        json_data = self.to_json()
        return json.dumps(json.loads(json_data), indent=2)

    def showJSON(self) -> None:
        """
        Prints tree to console as JSON
        """
        print(self._to_json())

    def showTable(self) -> None:
        """
        Prints the status of a link based on it's connection status
        """
        nodes = self.all_nodes_itr()
        table_data = []

        def insert(node, color_code):
            status = str(node.data.status)
            code = http.client.responses[node.data.status]
            status_message = f"{status} {code}"
            table_data.append(
                [
                    node.tag,
                    node.identifier,
                    color(status_message, color_code),
                    node.data.numbers,
                    node.data.emails,
                    node.data.classification,
                ]
            )

        for node in nodes:
            status_code = node.data.status
            if 200 <= status_code < 300:
                insert(node, "green")
            elif 300 <= status_code < 400:
                insert(node, "yellow")
            else:
                insert(node, "red")

        headers = ["Title", "URL", "Status", "Phone Numbers", "Emails", "Category"]
        table = tabulate(table_data, headers=headers)
        print(table)


def parse_hostname(url: str) -> str:
    hostname = parse.urlsplit(url).hostname
    if hostname is not None:
        return hostname

    raise Exception("unable to parse hostname from URL")


def parse_links(html: str) -> list[str]:
    """
    Finds all anchor tags and parses the href attribute.
    """
    soup = BeautifulSoup(html, "html.parser")
    tags = soup.find_all("a")
    return [
        tag["href"]
        for tag in tags
        if tag.has_attr("href") and validators.url(tag["href"])
    ]


def parse_emails(soup: BeautifulSoup) -> list[str]:
    """
    Finds all anchor tags and parses the email href attributes.
    example attribute: `mailto:example@example.com`
    """
    tags = soup.find_all("a")

    emails = set()
    for tag in tags:
        if tag.has_attr("href") and "mailto:" in tag["href"]:
            email = tag["href"].split("mailto:", 1)[1]
            if validators.email(email):
                emails.add(email)

    return list(emails)


def parse_phone_numbers(soup: BeautifulSoup) -> list[str]:
    """
    Finds all anchor tags and parses the href attribute.
    example attribute: `tel:+45651112331` or possiby the href attribute itself.
    """
    tags = soup.find_all("a")
    numbers = set()

    def validate_phone_number(phone_number: str) -> bool:
        try:
            possible_number = phonenumbers.parse(phone_number)
            return phonenumbers.is_possible_number(possible_number)
        except phonenumbers.NumberParseException:
            return False

    for tag in tags:
        if tag.has_attr("href") and "tel:" in tag["href"]:
            number = tag["href"].split("tel:", 1)[1]
            if validate_phone_number(number):
                numbers.add(number)

    return list(numbers)
