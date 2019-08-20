from os import environ as env

import datetime as dt
from typing import Dict


import attr
import requests
from dateutil.parser import parse

CODA_API_ENDPOINT = env.get("CODA_API_ENDPOINT", "https://coda.io/apis/v1beta1")
CODA_API_KEY = env.get("CODA_API_KEY")


class CodaError(Exception):
    pass


class NoApiKey(CodaError):
    pass


class DocumentNotFound(CodaError):
    pass


@attr.s
class Document:
    id: str = attr.ib()
    name: str = attr.ib(init=False)
    owner: str = attr.ib(init=False)
    created_at: dt.datetime = attr.ib(init=False, repr=False)
    updated_at: dt.datetime = attr.ib(init=False, repr=False)
    type: str = attr.ib(init=False, repr=False)
    browser_link: str = attr.ib(init=False)
    href: str = attr.ib(init=False, repr=False)
    api_key: str = attr.ib(repr=False)
    headers: Dict = {"Authorization": f"Bearer {CODA_API_KEY}"}

    @classmethod
    def from_environment(cls, doc_id: str):
        if not CODA_API_KEY:
            raise NoApiKey(f"No CODA_API_KEY in environment variables")
        return cls(id=doc_id, api_key=CODA_API_KEY)

    def __attrs_post_init__(self):
        self.href = CODA_API_ENDPOINT + f"/docs/{self.id}"
        data = self.get("/")
        if not data:
            raise DocumentNotFound(f"No document with id {self.id}")
        self.name = data["name"]
        self.owner = data["owner"]
        self.created_at = parse(data["createdAt"])
        self.updated_at = parse(data["updatedAt"])
        self.type = data["type"]
        self.browser_link = data["browserLink"]

    def get(self, endpoint: str, data: Dict = None):
        r = requests.get(self.href + endpoint, params=data, headers=self.headers)
        return r.json()

    def post(self, endpoint: str, data: Dict):
        return requests.post(self.href + endpoint, data, headers=self.headers).json()

    def sections(self):
        return self.get("/sections")

    def get_section(self, section_id_or_name: str):
        endpoint = f"/sections/{section_id_or_name}"
        return self.get(endpoint)

    def tables(self):
        return self.get("/tables")

    def get_table(self, table_id_or_name: str):
        return self.get(f"/tables/{table_id_or_name}")

    def get_table_rows(
        self, table_id_or_name: str, query: Dict = None, use_names: bool = False
    ):
        if not query:
            query = {}
        r = self.get(
            f"/tables/{table_id_or_name}/rows",
            data=query.update({"use_names": use_names}),
        )
        return r

    def get_table_columns(self, table_id_or_name: str):
        return self.get(f"/tables/{table_id_or_name}/columns")
