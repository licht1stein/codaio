from __future__ import annotations

import json
from functools import lru_cache
from os import environ as env

import datetime as dt
from typing import Dict, Any, List, Union, Optional, Tuple

import attr
import inflection
import requests
from dateutil.parser import parse
from requests import Response

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
        return {"Authorization": f"Bearer {self.api_key}"}

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
            Section.from_json(i, document=self)
            for i in self.get_sections_raw()["items"]
        ]

    @property
    def tables(self) -> List[Table]:
        return [
            Table.from_json(i, document=self) for i in self.get_tables_raw()["items"]
        ]

    def find_table(self, table_name_or_id: str) -> Optional[Table]:
        table_data = self.get_table_raw(table_name_or_id)
        if table_data:
            return Table.from_json(table_data, document=self)

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
            r = requests.get(next_page, headers=self.headers)
            res["items"].extend(r.json()["items"])
            if res.get("nextPageLink"):
                res.pop("nextPageLink")
                res.pop("nextPageToken")
        return res

    def post(self, endpoint: str, data: Dict) -> Response:
        return requests.post(
            self.href + endpoint,
            json=data,
            headers={**self.headers, "Content-Type": "application/json"},
        )

    def put(self, endpoint: str, data: Dict) -> Response:
        return requests.put(self.href + endpoint, json=data, headers=self.headers)

    def delete(self, endpoint: str) -> Response:
        return requests.delete(self.href + endpoint, headers=self.headers)

    def delete_row(self, table_id_or_name: str, row_id: str) -> Response:
        return self.delete(f"/tables/{table_id_or_name}/rows/{row_id}")

    def upsert_row(self, table_id_or_name, cells: List[Dict]):
        js = {"rows": [{"cells": cells}]}
        return self.post(f"/tables/{table_id_or_name}/rows", js)

    def get_sections_raw(self):
        r = self.get("/sections")
        return r

    def get_section(self, section_id_or_name: str):
        endpoint = f"/sections/{section_id_or_name}"
        return self.get(endpoint)

    def get_tables_raw(self):
        return self.get("/tables")

    def get_table_raw(self, table_id_or_name: str):
        return self.get(f"/tables/{table_id_or_name}")

    def get_table_rows_raw(
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

    def get_table_columns_raw(self, table_id_or_name: str):
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
    row_count: int = attr.ib(default=None, repr=False)
    sorts: List = attr.ib(default=[], repr=False)
    layout: str = attr.ib(repr=False, default=None)
    created_at: dt.datetime = attr.ib(
        repr=False, convert=lambda x: parse(x) if x else None, default=None
    )
    updated_at: dt.datetime = attr.ib(
        repr=False, convert=lambda x: parse(x) if x else None, default=None
    )
    columns: List[Column] = attr.ib(init=False, repr=False)

    def __attrs_post_init__(self):
        self.columns = self._make_columns()

    def _get_all_rows(self):
        return self.document.get_table_rows_raw(self.id)

    def _get_columns(self):
        return self.document.get_table_columns_raw(self.id)

    def _make_columns(self) -> List[Column]:
        return [
            Column.from_json({**i, "table": self}, document=self.document)
            for i in self._get_columns()["items"]
        ]

    @property
    def rows(self) -> List[Row]:
        return [
            Row.from_json({"table": self, **i}, document=self.document)
            for i in self._get_all_rows()["items"]
        ]

    # @lru_cache(maxsize=128)
    def find_column_by_id(self, column_id) -> Union[Column, None]:
        try:
            return next(filter(lambda x: x.id == column_id, self.columns))
        except StopIteration:
            return None

    def find_row_by_column_name_and_value(self, column, value) -> List[Row]:
        r = self.document.get_table_rows_raw(
            self.id, filt={"column_name": column, "value": value}
        )
        if not r.get("items"):
            return []
        return [
            Row.from_json({**i, "table": self}, document=self.document)
            for i in r["items"]
        ]

    def find_row_by_column_id_and_value(self, column_id, value) -> List[Row]:
        r = self.document.get_table_rows_raw(
            self.id, filt={"column_id": column_id, "value": value}
        )
        if not r.get("items"):
            return []
        return [
            Row.from_json({**i, "table": self}, document=self.document)
            for i in r["items"]
        ]

    def _upsert_row(self, cells: List[Dict]) -> Response:
        return self.document.upsert_row(self.id, cells)

    def upsert_row(self, cells: List[Cell]):
        cells_js = [{"column": cell.column.id, "value": cell.value} for cell in cells]
        return self._upsert_row(cells_js)

    def delete_row(self, row: Row):
        return self.document.delete_row(self.id, row.id)


@attr.s(auto_attribs=True, hash=True)
class Column(CodaObject):
    name: str
    table: Table = attr.ib(repr=False)
    display: bool = attr.ib(default=None, repr=False)
    calculated: bool = attr.ib(default=False)


@attr.s(auto_attribs=True, hash=True)
class Row(CodaObject):
    name: str
    created_at: dt.datetime = attr.ib(convert=lambda x: parse(x), repr=False)
    index: int
    updated_at: dt.datetime = attr.ib(
        convert=lambda x: parse(x) if x else None, repr=False
    )
    values: Tuple[Tuple] = attr.ib(
        convert=lambda x: tuple([(k, v) for k, v in x.items()]), repr=False
    )
    table: Table = attr.ib(repr=False)
    browser_link: str = attr.ib(default=None, repr=False)

    @property
    def columns(self):
        return self.table.columns

    @property
    def cells(self) -> List[Cell]:
        return [
            Cell(column=self.table.find_column_by_id(i[0]), value=i[1], row=self)
            for i in self.values
        ]

    def delete(self):
        return self.table.delete_row(self)

    def __getitem__(self, item) -> Cell:
        try:
            return next(filter(lambda x: x.column.name == item, self.cells))
        except StopIteration:
            raise KeyError(f"No column named {item}")


@attr.s(auto_attribs=True, hash=True, repr=False)
class Cell:
    column: Column
    value: Any
    row: Row = attr.ib(default=None)

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
        return (
            f"Cell(column={self.column.name}, row={self.row.name}, value={self.value})"
        )
