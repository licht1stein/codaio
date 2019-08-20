from os import environ as env

import datetime as dt
from typing import Dict


import attr
import requests
from dateutil.parser import parse
from codaio import err

CODA_API_ENDPOINT = env.get("CODA_API_ENDPOINT", "https://coda.io/apis/v1beta1")
CODA_API_KEY = env.get("CODA_API_KEY")


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

    @property
    def headers(self) -> Dict:
        return {"Authorization": f"Bearer {CODA_API_KEY}"}

    @classmethod
    def from_environment(cls, doc_id: str):
        if not CODA_API_KEY:
            raise err.NoApiKey(f"No CODA_API_KEY in environment variables")
        return cls(id=doc_id, api_key=CODA_API_KEY)

    def __attrs_post_init__(self):
        self.href = CODA_API_ENDPOINT + f"/docs/{self.id}"
        data = self.get("/")
        if not data:
            raise err.DocumentNotFound(f"No document with id {self.id}")
        self.name = data["name"]
        self.owner = data["owner"]
        self.created_at = parse(data["createdAt"])
        self.updated_at = parse(data["updatedAt"])
        self.type = data["type"]
        self.browser_link = data["browserLink"]

    def get(self, endpoint: str, data: Dict = None, limit=None, offset=None) -> Dict:
        if not data:
            data = {}
        if limit:
            data["limit"] = limit
        if offset:
            data["pageToken"] = offset
        r = requests.get(self.href + endpoint, params=data, headers=self.headers)
        if not r.json().get("items"):
            return r.json()
        res = r.json()
        if limit:
            return res
        while r.json().get("nextPageLink"):
            next_page = r.json()["nextPageLink"]
            r = requests.get(next_page, params=data, headers=self.headers)
            res["items"].extend(r.json()["items"])
            res.pop("nextPageLink")
            res.pop("nextPageToken")
        return res

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
        self,
        table_id_or_name: str,
        filt: Dict = None,
        limit: int = None,
        offset: int = None,
        use_names: bool = False,
    ) -> Dict:
        """
        Get table rows.

        :param table_id_or_name: name or id of Coda table
        :param filt: a filter dictionary if you want to filter by column value. Accepts either dict(column_name='foo', value='bar') or dict(column_id='COLUMN_ID', value='bar')
        :param limit: int for limiting number of rows to return
        :param offset: int for offsetting the first row
        :param use_names: boolean for returning column names instead of ids
        :return:
        """
        data = {}
        if filt:
            data.update(self._parse_filter(filt))
        if use_names:
            data.update({"useNames": use_names})
        r = self.get(
            f"/tables/{table_id_or_name}/rows", data=data, limit=limit, offset=offset
        )
        return r

    @staticmethod
    def _parse_filter(filt: Dict) -> Dict:
        if (
            all(("column_id" not in filt, "column_name" not in filt))
            or "value" not in filt
        ):
            raise err.InvalidFilter(
                'Filter must be a dict of either {"column_id": "YOUR_COLUMN_ID", "value": "FILTER_VALUE"} or {"column_name": "YOUR_COLUMN_NAME", "value": "FILTER_VALUE"}'
            )
        if "column_id" in filt:
            return {"query": f'{filt["column_id"]}:"{filt["value"]}"'}
        else:
            return {"query": f'"{filt["column_name"]}":"{filt["value"]}"'}

    def get_table_columns(self, table_id_or_name: str):
        return self.get(f"/tables/{table_id_or_name}/columns")
