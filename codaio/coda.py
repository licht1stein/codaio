from __future__ import annotations

import json
from functools import lru_cache
from envparse import env

import datetime as dt
from typing import Dict, Any, List, Union, Optional, Tuple

import attr
import inflection
import requests
from dateutil.parser import parse
from requests import Response

from codaio import err


@attr.s(hash=True)
class Coda:
    api_key: str = attr.ib(repr=False)
    authorization: Dict = attr.ib(init=False, repr=False)
    href: str = attr.ib(
        repr=False,
        default=env(
            "CODA_API_ENDPOINT", cast=str, default="https://coda.io/apis/v1beta1"
        ),
    )

    @classmethod
    def from_environment(cls) -> Coda:
        """
        Initializes a Coda instance using API key store in environment variables under `CODA_API_KEY`

        :return:
        """
        api_key = env("CODA_API_KEY", cast=str)
        return cls(api_key=api_key)

    def __attrs_post_init__(self):
        self.authorization = {"Authorization": f"Bearer {self.api_key}"}

    def get(self, endpoint: str, data: Dict = None, limit=None, offset=None) -> Dict:
        """
        Make a GET request to API endpoint.

        :param endpoint: API endpoint to request

        :param data: dictionary of optional query params

        :param limit: Maximum number of results to return in this query.

        :param offset: An opaque token used to fetch the next page of results.

        :return:
        """
        if not data:
            data = {}
        if limit:
            data["limit"] = limit
        if offset:
            data["pageToken"] = offset
        r = requests.get(self.href + endpoint, params=data, headers=self.authorization)
        if not r.json().get("items"):
            return r.json()
        res = r.json()
        if limit:
            return res
        while r.json().get("nextPageLink"):
            next_page = r.json()["nextPageLink"]
            r = requests.get(next_page, headers=self.authorization)
            res["items"].extend(r.json()["items"])
            if res.get("nextPageLink"):
                res.pop("nextPageLink")
                res.pop("nextPageToken")
        return res

    def post(self, endpoint: str, data: Dict) -> Response:
        """
        Make a POST request to the API endpoint.

        :param endpoint: API endpoint to request

        :param data: data dict to be sent as body json

        :return:
        """
        return requests.post(
            self.href + endpoint,
            json=data,
            headers={**self.authorization, "Content-Type": "application/json"},
        )

    def put(self, endpoint: str, data: Dict) -> Response:
        """
        Make a PUT request to the API endpoint.

        :param endpoint: API endpoint to request

        :param data: data dict to be sent as body json

        :return:
        """
        return requests.put(self.href + endpoint, json=data, headers=self.authorization)

    def delete(self, endpoint: str) -> Response:
        """
        Make a DELETE request to the API endpoint.

        :param endpoint: API endpoint to request

        :return:
        """
        return requests.delete(self.href + endpoint, headers=self.authorization)

    def list_docs(
        self,
        is_owner: bool = False,
        query: str = None,
        source_doc_id: str = None,
        limit: int = 100,
        offset: int = 0,
    ):
        """
        Returns a list of Coda docs accessible by the user. These are returned in the same order as on the docs page: reverse
        chronological by the latest event relevant to the user (last viewed, edited, or shared).

        Docs: https://coda.io/developers/apis/v1beta1#operation/listDocs

        :param is_owner: Show only docs owned by the user.

        :param query: Search term used to filter down results.

        :param source_doc_id: Show only docs copied from the specified doc ID.

        :param limit: Maximum number of results to return in this query.

        :param offset: An opaque token used to fetch the next page of results.

        :return:
        """
        return self.get(
            "/docs",
            data={"isOwner": is_owner, "query": query, "sourceDoc": source_doc_id},
            limit=limit,
            offset=offset,
        )

    def create_doc(
        self, title: str, source_doc: str = None, tz: str = None
    ) -> Response:
        """
        Creates a new Coda doc, optionally copying an existing doc.

        Docs: https://coda.io/developers/apis/v1beta1#operation/createDoc

        :param title: Title of the new doc.

        :param source_doc: An optional doc ID from which to create a copy.

        :param tz: The timezone to use for the newly created doc.

        :return:
        """
        data = {"title": title}
        if source_doc:
            data["sourceDoc"] = source_doc
        if tz:
            data["timezone"] = tz

        return self.post("/docs", data)

    def get_doc(self, doc_id: str):
        """
        Returns metadata for the specified doc.

        Docs: https://coda.io/developers/apis/v1beta1#operation/getDoc

        :param doc_id: ID of the doc. Example: "AbCDeFGH"

        :return:
        """
        return self.get("/docs/" + doc_id)

    def delete_doc(self, doc_id: str) -> Response:
        """
        Deletes a doc.

        Docs: https://coda.io/developers/apis/v1beta1#operation/deleteDoc

        :param doc_id: ID of the doc. Example: "AbCDeFGH"

        :return:
        """
        return self.delete("/docs/" + doc_id)

    def list_sections(self, doc_id: str):
        """
        Returns a list of sections in a Coda doc.

        Docs: https://coda.io/developers/apis/v1beta1#operation/listSections

        :param doc_id: ID of the doc. Example: "AbCDeFGH"

        :return:
        """
        return self.get(f"/docs/{doc_id}/sections")

    def get_section(self, doc_id: str, section_id_or_name: str):
        """
        Returns details about a section.

        Docs: https://coda.io/developers/apis/v1beta1#operation/getSection

        :param doc_id: ID of the doc. Example: "AbCDeFGH"

        :param section_id_or_name: ID or name of the section. Names are discouraged because they're easily prone to being changed by users.
            If you're using a name, be sure to URI-encode it. Example: "canvas-IjkLmnO"

        :return:
        """
        return self.get(f"/docs/{doc_id}/sections/{section_id_or_name}")

    def list_folders(self, doc_id: str):
        """
        Returns a list of folders in a Coda doc.

        Docs: https://coda.io/developers/apis/v1beta1#operation/listFolders

        :param doc_id: ID of the doc. Example: "AbCDeFGH"

        :return:
        """
        return self.get(f"/docs/{doc_id}/folders")

    def get_folder(self, doc_id: str, folder_id_or_name: str):
        """
        Returns details about a folder.

        Docs: https://coda.io/developers/apis/v1beta1#operation/getFolder

        :param doc_id: ID of the doc. Example: "AbCDeFGH"

        :param folder_id_or_name: ID or name of the folder. Names are discouraged because they're easily prone to being
            changed by users. If you're using a name, be sure to URI-encode it. Example: "section-IjkLmnO"

        :return:
        """
        return self.get(f"/docs/{doc_id}/folders/{folder_id_or_name}")

    def list_tables(self, doc_id: str):
        """
        Returns a list of tables in a Coda doc.

        Docs: https://coda.io/developers/apis/v1beta1#operation/listTables

        :param doc_id: ID of the doc. Example: "AbCDeFGH"

        :return:
        """
        return self.get(f"/docs/{doc_id}/tables")

    def get_table(self, doc_id: str, table_id_or_name: str):
        """
        Returns details about a specific table.

        Docs: https://coda.io/developers/apis/v1beta1#operation/getTable

        :param doc_id: ID of the doc. Example: "AbCDeFGH"

        :param table_id_or_name: ID or name of the table. Names are discouraged because they're easily prone to being changed by users.
            If you're using a name, be sure to URI-encode it. Example: "grid-pqRst-U"

        :return:
        """
        return self.get(f"/docs/{doc_id}/tables/{table_id_or_name}")

    def list_views(self, doc_id: str):
        """
        Returns a list of views in a Coda doc.

        Docs: https://coda.io/developers/apis/v1beta1#operation/listViews

        :param doc_id: ID of the doc. Example: "AbCDeFGH"

        :return:
        """
        return self.get(f"/docs/{doc_id}/views")

    def get_view(self, doc_id: str, view_id_or_name: str):
        """
        Returns details about a specific view.

        Docs: https://coda.io/developers/apis/v1beta1#operation/getView

        :param doc_id: ID of the doc. Example: "AbCDeFGH"

        :param view_id_or_name: ID or name of the view. Names are discouraged because they're easily prone to being changed by users.
            If you're using a name, be sure to URI-encode it. Example: "table-pqRst-U"

        :return:
        """
        return self.get(f"/docs/{doc_id}/views/{view_id_or_name}")

    def list_columns(self, doc_id: str, table_id_or_name: str):
        """
        Returns a list of columns in a table.

        :param doc_id: ID of the doc. Example: "AbCDeFGH"

        :param table_id_or_name: ID or name of the table. Names are discouraged because they're easily prone to being changed by users.
            If you're using a name, be sure to URI-encode it. Example: "grid-pqRst-U"

        :return:
        """
        return self.get(f"/docs/{doc_id}/tables/{table_id_or_name}/columns")

    def get_column(self, doc_id: str, table_id_or_name: str, column_id_or_name: str):
        """
        Returns details about a column in a table.

        Docs: https://coda.io/developers/apis/v1beta1#operation/getColumn

        :param doc_id:  ID of the doc. Example: "AbCDeFGH"

        :param table_id_or_name: ID or name of the table. Names are discouraged because they're easily prone to being changed by users.
            If you're using a name, be sure to URI-encode it. Example: "grid-pqRst-U"

        :param column_id_or_name: ID or name of the column. Names are discouraged because they're easily prone to being changed by users.
            If you're using a name, be sure to URI-encode it. Example: "c-tuVwxYz"

        :return:
        """
        return self.get(
            f"/docs/{doc_id}/tables/{table_id_or_name}/columns/{column_id_or_name}"
        )

    def list_rows(self, doc_id: str, table_id_or_name: str):
        """
        Returns a list of rows in a table.

        Docs: https://coda.io/developers/apis/v1beta1#tag/Rows

        :param doc_id:  ID of the doc. Example: "AbCDeFGH"

        :param table_id_or_name: ID or name of the table. Names are discouraged because they're easily prone to being changed by users. If you're using a name, be sure to URI-encode it. Example: "grid-pqRst-U"

        :return:
        """
        return self.get(f"/docs/{doc_id}/tables/{table_id_or_name}/rows")

    def upsert_row(self, doc_id: str, table_id_or_name: str, data: Dict):
        """
        Inserts rows into a table, optionally updating existing rows if any upsert key columns are provided. This endpoint will always return a 202,
        so long as the doc and table exist and are accessible (and the update is structurally valid). Row inserts/upserts are generally
        processed within several seconds. When upserting, if multiple rows match the specified key column(s), they will all be updated with the specified value.

        Docs: https://coda.io/developers/apis/v1beta1#operation/upsertRows

        :param doc_id:  ID of the doc. Example: "AbCDeFGH"

        :param table_id_or_name: ID or name of the table. Names are discouraged because they're easily prone to being changed by users.
        If you're using a name, be sure to URI-encode it. Example: "grid-pqRst-U"

        :param data: {"rows": [{"cells": [{"column": "c-tuVwxYz", "value": "$12.34"}]}], "keyColumns": ["c-bCdeFgh"]}

        :return:
        """
        return self.post(f"/docs/{doc_id}/tables/{table_id_or_name}/rows", data)

    def get_row(self, doc_id: str, table_id_or_name: str, row_id_or_name: str):
        """
        Returns details about a row in a table.

        Docs: https://coda.io/developers/apis/v1beta1#operation/getRow

        :param doc_id:  ID of the doc. Example: "AbCDeFGH"

        :param table_id_or_name: ID or name of the table. Names are discouraged because they're easily prone to being changed by users.
            If you're using a name, be sure to URI-encode it. Example: "grid-pqRst-U"

        :param row_id_or_name: ID or name of the row. Names are discouraged because they're easily prone to being changed by users.
            If you're using a name, be sure to URI-encode it. If there are multiple rows with the same value in the identifying column,
            an arbitrary one will be selected.

        :return:
        """
        return self.get(
            f"/docs/{doc_id}/tables/{table_id_or_name}/rows/{row_id_or_name}"
        )

    def update_row(
        self, doc_id: str, table_id_or_name: str, row_id_or_name: str, data: Dict
    ):
        """
        Updates the specified row in the table. This endpoint will always return a 202, so long as the row exists and is
        accessible (and the update is structurally valid). Row updates are generally processed within several seconds.
        When updating using a name as opposed to an ID, an arbitrary row will be affected.

        Docs: https://coda.io/developers/apis/v1beta1#operation/updateRow

        :param doc_id:  ID of the doc. Example: "AbCDeFGH"

        :param table_id_or_name: ID or name of the table. Names are discouraged because they're easily prone to being changed by users.
        If you're using a name, be sure to URI-encode it. Example: "grid-pqRst-U"

        :param row_id_or_name: ID or name of the row. Names are discouraged because they're easily prone to being changed by users.
        If you're using a name, be sure to URI-encode it. If there are multiple rows with the same value in the identifying column,
        an arbitrary one will be selected.

        :param data: Example: {"row": {"cells": [{"column": "c-tuVwxYz", "value": "$12.34"}]}}

        :return: Response
        """
        return self.put(
            f"/docs/{doc_id}/tables/{table_id_or_name}/rows/{row_id_or_name}", data
        )

    def delete_row(self, doc_id, table_id_or_name: str, row_id_or_name: str):
        """
        Deletes the specified row from the table. This endpoint will always return a 202, so long as the row exists and is accessible
        (and the update is structurally valid). Row deletions are generally processed within several seconds.
        When deleting using a name as opposed to an ID, an arbitrary row will be removed.

        Docs: https://coda.io/developers/apis/v1beta1#operation/deleteRow

        :param doc_id:  ID of the doc. Example: "AbCDeFGH"

        :param table_id_or_name: ID or name of the table. Names are discouraged because they're easily prone to being changed by users.
        If you're using a name, be sure to URI-encode it. Example: "grid-pqRst-U"

        :param row_id_or_name: ID or name of the row. Names are discouraged because they're easily prone to being changed by users.
        If you're using a name, be sure to URI-encode it. If there are multiple rows with the same value in the identifying column,
        an arbitrary one will be selected.
        :return:
        """
        return self.delete(
            f"/docs/{doc_id}/tables/{table_id_or_name}/rows/{row_id_or_name}"
        )

    def list_formulas(self, doc_id: str):
        """
        Returns a list of named formulas in a Coda doc.

        Docs: https://coda.io/developers/apis/v1beta1#operation/listFormulas

        :param doc_id:  ID of the doc. Example: "AbCDeFGH"

        :return:
        """
        return self.get(f"/docs/{doc_id}/formulas")

    def get_formula(self, doc_id: str, formula_id_or_name: str):
        """
        Returns info on a formula.

        Docs: https://coda.io/developers/apis/v1beta1#operation/getFormula

        :param doc_id:  ID of the doc. Example: "AbCDeFGH"

        :param formula_id_or_name: ID or name of the formula. Names are discouraged because they're easily prone to being changed by users.
        If you're using a name, be sure to URI-encode it. Example: "f-fgHijkLm"

        :return:
        """
        return self.get(f"/docs/{doc_id}/formulas/{formula_id_or_name}")

    def list_controls(self, doc_id: str):
        """
        Controls provide a user-friendly way to input a value that can affect other parts of the doc. This API lets you list controls
        and get their current values.

        Docs: https://coda.io/developers/apis/v1beta1#tag/Controls

        :param doc_id:  ID of the doc. Example: "AbCDeFGH"

        :return:
        """
        return self.get(f"/docs/{doc_id}/controls")

    def get_control(self, doc_id: str, control_id_or_name: str):
        """
        Returns info on a control.

        Docs: https://coda.io/developers/apis/v1beta1#operation/getControl

        :param doc_id:  ID of the doc. Example: "AbCDeFGH"
        :param control_id_or_name: ID or name of the control. Names are discouraged because they're easily prone to being changed by users.
        If you're using a name, be sure to URI-encode it. Example: "ctrl-cDefGhij"

        :return:
        """
        return self.get(f"/docs/{doc_id}/controls/{control_id_or_name}")

    def account(self):
        """
        At this time, the API exposes some limited information about your account. However, /whoami is a good endpoint to hit to verify
        that you're hitting the API correctly and that your token is working as expected.

        Docs: https://coda.io/developers/apis/v1beta1#tag/Account

        :return:
        """
        return self.get("/whoami")

    def resolve_browser_link(self, url: str, degrade_gracefully: bool = False):
        """
        Given a browser link to a Coda object, attempts to find it and return metadata that can be used to get more info on it.
        Returns a 400 if the URL does not appear to be a Coda URL or a 404 if the resource cannot be located with the current credentials.

        Docs: https://coda.io/developers/apis/v1beta1#operation/resolveBrowserLink

        :param url: The browser link to try to resolve. Example: "https://coda.io/d/_dAbCDeFGH/Launch-Status_sumnO"

        :param degrade_gracefully: By default, attempting to resolve the Coda URL of a deleted object will result in an error.
        If this flag is set, the next-available object, all the way up to the doc itself, will be resolved.

        :return:
        """
        return self.get(
            "/resolveBrowserLink",
            data={"url": url, "degradeGracefully": degrade_gracefully},
        )


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
    coda: Coda = attr.ib(repr=False)

    @classmethod
    def from_environment(cls, doc_id: str):
        return cls(id=doc_id, coda=Coda.from_environment())

    def __attrs_post_init__(self):
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
