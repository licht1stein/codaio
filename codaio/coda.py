from __future__ import annotations

from functools import lru_cache
from os import environ as env

import datetime as dt
from typing import Dict, Any, List, Union

import attr
import inflection
import requests
from dateutil.parser import parse
from codaio import err

CODA_API_ENDPOINT = env.get("CODA_API_ENDPOINT", "https://coda.io/apis/v1beta1")
CODA_API_KEY = env.get("CODA_API_KEY")


@attr.s(hash=True)
class CodaObject:
    id: str = attr.ib(repr=False)
    type: str = attr.ib(repr=False)
    href: str = attr.ib(repr=False)

    document: Document = attr.ib(repr=False)

    @classmethod
    def from_json(cls, js: Dict, *, document: Document):
        js = {inflection.underscore(k): v for k, v in js.items()}
        return cls(**js, document=document)


@attr.s(hash=True)
class Document:
    id: str = attr.ib(repr=False)
    type: str = attr.ib(init=False, repr=False)
    href: str = attr.ib(init=False, repr=False)
    name: str = attr.ib(init=False)
    owner: str = attr.ib(init=False)
    created_at: dt.datetime = attr.ib(init=False, repr=False)
    updated_at: dt.datetime = attr.ib(init=False, repr=False)
    browser_link: str = attr.ib(init=False)
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

    @property
    def sections(self) -> List[Section]:
        return [
            Section.from_json(i, document=self) for i in self.get_sections()["items"]
        ]

    @property
    def tables(self) -> List[Table]:
        return [Table.from_json(i, document=self) for i in self.get_tables()["items"]]

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

    def get_sections(self):
        r = self.get("/sections")
        return r

    def get_section(self, section_id_or_name: str):
        endpoint = f"/sections/{section_id_or_name}"
        return self.get(endpoint)

    def get_tables(self):
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


@attr.s(auto_attribs=True, hash=True)
class Folder(CodaObject):
    pass


@attr.s(auto_attribs=True, hash=True)
class Section(CodaObject):
    name: str
    browser_link: str = attr.ib(repr=False)
    document: Document = attr.ib(repr=False)


@attr.s(auto_attribs=True, hash=True)
class Table(CodaObject):
    name: str
    document: Document = attr.ib(repr=False)
    display_column: Dict = attr.ib(default=None, repr=False)
    browser_link: str = attr.ib(default=None, repr=False)

    def get_all_rows(self):
        return self.document.get_table_rows(self.id)

    def get_columns(self):
        return self.document.get_table_columns(self.id)

    @property
    @lru_cache(maxsize=1)
    def columns(self) -> List[Column]:
        return [
            Column.from_json(i, document=self.document)
            for i in self.get_columns()["items"]
        ]

    @property
    def rows(self) -> List[Row]:
        return [
            Row.from_json({"table": self, **i}, document=self.document)
            for i in self.get_all_rows()["items"]
        ]

    @lru_cache(maxsize=128)
    def find_column_by_id(self, column_id) -> Union[Column, None]:
        try:
            return next(filter(lambda x: x.id == column_id, self.columns))
        except StopIteration:
            return None


@attr.s(auto_attribs=True, hash=True)
class Column(CodaObject):
    name: str
    display: bool = attr.ib(default=None, repr=False)
    calculated: bool = attr.ib(default=False)


@attr.s(auto_attribs=True, hash=True)
class Row(CodaObject):
    name: str
    browser_link: str = attr.ib(repr=False)
    created_at: dt.datetime = attr.ib(convert=lambda x: parse(x), repr=False)
    index: int
    updated_at: dt.datetime = attr.ib(convert=lambda x: parse(x), repr=False)
    values: Dict = attr.ib(repr=False)
    table: Table = attr.ib(repr=False)

    @property
    def columns(self):
        return self.table.columns

    @property
    def column_values(self) -> List[ColumnValue]:
        return [
            ColumnValue(column=self.table.find_column_by_id(k), value=v, row=self)
            for k, v in self.values.items()
        ]


@attr.s(auto_attribs=True, hash=True, repr=False)
class ColumnValue:
    column: Column
    value: Any
    row: Row = attr.ib(repr=False)

    @property
    def name(self):
        return self.column.name

    @property
    def table(self):
        return self.row.table

    @property
    def document(self):
        return self.table.document

    def __repr__(self):
        return f"ColumnValue(column={self.column.name}, value={self.value})"
