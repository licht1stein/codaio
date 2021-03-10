from __future__ import annotations

import datetime as dt
import json
import time
from typing import Any, Dict, List, Tuple, Union

import attr
import inflection
from dateutil.parser import parse
from decorator import decorator
from envparse import env

from codaio import err

# Trying to make it compatible with eventlet
USE_HTTPX = env("USE_HTTPX", cast=bool, default=False)
if not USE_HTTPX:
    import requests
else:
    try:
        import httpx as requests
    except ImportError:
        import requests


MAX_GET_LIMIT = 200


@decorator
def handle_response(func, *args, **kwargs) -> Dict:
    response = func(*args, **kwargs)

    if isinstance(response, List):
        res = {}
        items = []
        for r in response:
            if r.json().get("items"):
                items.extend(r.json().pop("items"))

            res.update(r.json())
        if items:
            res["items"] = items
        return res

    if 200 <= response.status_code <= 299:
        if not response.json():
            return {"status": response.status_code}
        return response.json()

    error_dict = {404: err.NotFound}

    if response.status_code in error_dict:
        raise error_dict[response.status_code](
            f'Status code: {response.status_code}. Message: {response.json()["message"]}'
        )

    raise err.CodaError(
        f'Status code: {response.status_code}. Message: {response.json()["message"]}'
    )


@attr.s(hash=True)
class Coda:
    """
    Raw API client.

    It is used in `codaio` objects like Document to access the raw API endpoints.
    Can also be used by itself to access Raw API.
    """

    api_key: str = attr.ib(repr=False)
    authorization: Dict = attr.ib(init=False, repr=False)
    href: str = attr.ib(
        repr=False,
        default=env("CODA_API_ENDPOINT", cast=str, default="https://coda.io/apis/v1"),
    )

    @classmethod
    def from_environment(cls) -> Coda:
        """
        Instantiates Coda using the API key stored in the `CODA_API_KEY` environment variable.

        :return:
        """
        api_key = env("CODA_API_KEY", cast=str)
        return cls(api_key=api_key)

    def __attrs_post_init__(self):
        self.authorization = {"Authorization": f"Bearer {self.api_key}"}

    @handle_response
    def get(self, endpoint: str, data: Dict = None, limit=None, offset=None) -> Dict:
        """
        Makes a GET request to API endpoint.

        :param endpoint: API endpoint to request

        :param data: dictionary of optional query params

        :param limit: Maximum number of results to return in this query.

        :param offset: An opaque token used to fetch the next page of results.

        :return:
        """
        if not data:
            data = {}
        if limit:
            if limit > MAX_GET_LIMIT:
                limit = MAX_GET_LIMIT
            data["limit"] = limit

        if offset:
            data["pageToken"] = offset
        r = requests.get(self.href + endpoint, params=data, headers=self.authorization)
        if limit or not r.json().get("nextPageLink"):
            return r

        res = [r]
        while r.json().get("nextPageLink"):
            next_page = r.json()["nextPageLink"]
            r = requests.get(next_page, headers=self.authorization)
            res.append(r)
        return res

    # noinspection PyTypeChecker
    @handle_response
    def post(self, endpoint: str, data: Dict) -> Dict:
        """
        Makes a POST request to the API endpoint.

        :param endpoint: API endpoint to request

        :param data: data dict to be sent as body json

        :return:
        """
        return requests.post(
            self.href + endpoint,
            json=data,
            headers={**self.authorization, "Content-Type": "application/json"},
        )

    # noinspection PyTypeChecker
    @handle_response
    def put(self, endpoint: str, data: Dict) -> Dict:
        """
        Makes a PUT request to the API endpoint.

        :param endpoint: API endpoint to request

        :param data: data dict to be sent as body json

        :return:
        """
        return requests.put(self.href + endpoint, json=data, headers=self.authorization)

    # noinspection PyTypeChecker
    @handle_response
    def delete(self, endpoint: str, data: Dict = None) -> Dict:
        """
        Makes a DELETE request to the API endpoint.

        :param endpoint: API endpoint to request

        :param data: data dict to be sent as body json

        :return:
        """
        if data is not None:
            return requests.delete(
                self.href + endpoint, json=data, headers=self.authorization
            )

        return requests.delete(self.href + endpoint, headers=self.authorization)

    def list_docs(
        self,
        is_owner: bool = False,
        query: str = None,
        source_doc_id: str = None,
        limit: int = None,
        offset: int = None,
    ) -> Dict:
        """
        Returns a list of Coda documents accessible by the user.

        These are returned in the same order as on the docs page: reverse
        chronological by the latest event relevant to the user (last viewed, edited, or shared).

        Docs: https://coda.io/developers/apis/v1/#operation/listDocs

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

    def create_doc(self, title: str, source_doc: str = None, tz: str = None) -> Dict:
        """
        Creates a new Coda doc, optionally copying an existing doc.

        Docs: https://coda.io/developers/apis/v1/#operation/createDoc

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

    def get_doc(self, doc_id: str) -> Dict:
        """
        Returns metadata for the specified doc.

        Docs: https://coda.io/developers/apis/v1/#operation/getDoc

        :param doc_id: ID of the doc. Example: "AbCDeFGH"

        :return:
        """
        return self.get("/docs/" + doc_id)

    def delete_doc(self, doc_id: str) -> Dict:
        """
        Deletes a doc.

        Docs: https://coda.io/developers/apis/v1/#operation/deleteDoc

        :param doc_id: ID of the doc. Example: "AbCDeFGH"

        :return:
        """
        return self.delete("/docs/" + doc_id)

    def list_sections(self, doc_id: str, offset: int = None, limit: int = None) -> Dict:
        """
        Returns a list of sections in a Coda doc.

        Docs: https://coda.io/developers/apis/v1/#operation/listSections

        :param doc_id: ID of the doc. Example: "AbCDeFGH"

        :param limit: Maximum number of results to return in this query.

        :param offset: An opaque token used to fetch the next page of results.

        :return:
        """
        return self.get(f"/docs/{doc_id}/pages", offset=offset, limit=limit)

    def get_section(self, doc_id: str, section_id_or_name: str) -> Dict:
        """
        Returns details about a section.

        Docs: https://coda.io/developers/apis/v1/#operation/getSection

        :param doc_id: ID of the doc. Example: "AbCDeFGH"

        :param section_id_or_name: ID or name of the section.
            Names are discouraged because they're easily prone to being changed by users.
            If you're using a name, be sure to URI-encode it. Example: "canvas-IjkLmnO"

        :return:
        """
        return self.get(f"/docs/{doc_id}/pages/{section_id_or_name}")

    def list_folders(self, doc_id: str, offset: int = None, limit: int = None) -> Dict:
        """
        Returns a list of folders in a Coda doc.

        Docs: https://coda.io/developers/apis/v1/#operation/listFolders

        :param doc_id: ID of the doc. Example: "AbCDeFGH"

        :param limit: Maximum number of results to return in this query.

        :param offset: An opaque token used to fetch the next page of results.

        :return:
        """
        return self.get(f"/docs/{doc_id}/folders", offset=offset, limit=limit)

    def get_folder(self, doc_id: str, folder_id_or_name: str) -> Dict:
        """
        Returns details about a folder.

        Docs: https://coda.io/developers/apis/v1/#operation/getFolder

        :param doc_id: ID of the doc. Example: "AbCDeFGH"

        :param folder_id_or_name: ID or name of the folder.
            Names are discouraged because they're easily prone to being
            changed by users. If you're using a name, be sure to URI-encode it.
            Example: "section-IjkLmnO"

        :return:
        """
        return self.get(f"/docs/{doc_id}/folders/{folder_id_or_name}")

    def list_tables(self, doc_id: str, offset: int = None, limit: int = None) -> Dict:
        """
        Returns a list of tables in a Coda doc.

        Docs: https://coda.io/developers/apis/v1/#operation/listTables

        :param doc_id: ID of the doc. Example: "AbCDeFGH"

        :param limit: Maximum number of results to return in this query.

        :param offset: An opaque token used to fetch the next page of results.

        :return:
        """
        return self.get(f"/docs/{doc_id}/tables", offset=offset, limit=limit)

    def get_table(self, doc_id: str, table_id_or_name: str) -> Dict:
        """
        Returns details about a specific table.

        Docs: https://coda.io/developers/apis/v1/#operation/getTable

        :param doc_id: ID of the doc. Example: "AbCDeFGH"

        :param table_id_or_name: ID or name of the table.
            Names are discouraged because they're easily prone to being changed by users.
            If you're using a name, be sure to URI-encode it. Example: "grid-pqRst-U"

        :return:
        """
        return self.get(f"/docs/{doc_id}/tables/{table_id_or_name}")

    def list_views(self, doc_id: str, offset: int = None, limit: int = None) -> Dict:
        """
        Returns a list of views in a Coda doc.

        Docs: https://coda.io/developers/apis/v1/#operation/listViews

        :param doc_id: ID of the doc. Example: "AbCDeFGH"

        :param limit: Maximum number of results to return in this query.

        :param offset: An opaque token used to fetch the next page of results.

        :return:
        """
        return self.get(
            f"/docs/{doc_id}/tables?tableTypes=view", offset=offset, limit=limit
        )

    def get_view(self, doc_id: str, view_id_or_name: str) -> Dict:
        """
        Returns details about a specific view.

        Docs: https://coda.io/developers/apis/v1/#operation/getView

        :param doc_id: ID of the doc. Example: "AbCDeFGH"

        :param view_id_or_name: ID or name of the view.
            Names are discouraged because they're easily prone to being changed by users.
            If you're using a name, be sure to URI-encode it. Example: "table-pqRst-U"

        :return:
        """
        return self.get(f"/docs/{doc_id}/tables/{view_id_or_name}")

    def list_columns(
        self, doc_id: str, table_id_or_name: str, offset: int = None, limit: int = None
    ) -> Dict:
        """
        Returns a list of columns in a table.

        :param doc_id: ID of the doc. Example: "AbCDeFGH"

        :param table_id_or_name: ID or name of the table.
            Names are discouraged because they're easily prone to being changed by users.
            If you're using a name, be sure to URI-encode it. Example: "grid-pqRst-U"

        :param limit: Maximum number of results to return in this query.

        :param offset: An opaque token used to fetch the next page of results.

        :return:
        """
        return self.get(
            f"/docs/{doc_id}/tables/{table_id_or_name}/columns",
            offset=offset,
            limit=limit,
        )

    def get_column(
        self, doc_id: str, table_id_or_name: str, column_id_or_name: str
    ) -> Dict:
        """
        Returns details about a column in a table.

        Docs: https://coda.io/developers/apis/v1/#operation/getColumn

        :param doc_id:  ID of the doc. Example: "AbCDeFGH"

        :param table_id_or_name: ID or name of the table.
            Names are discouraged because they're easily prone to being changed by users.
            If you're using a name, be sure to URI-encode it. Example: "grid-pqRst-U"

        :param column_id_or_name: ID or name of the column.
            Names are discouraged because they're easily prone to being changed by users.
            If you're using a name, be sure to URI-encode it. Example: "c-tuVwxYz"

        :return:
        """
        return self.get(
            f"/docs/{doc_id}/tables/{table_id_or_name}/columns/{column_id_or_name}"
        )

    def list_rows(
        self,
        doc_id: str,
        table_id_or_name: str,
        query: str = None,
        use_column_names: bool = False,
        limit: int = None,
        offset: int = None,
    ) -> Dict:
        """
        Returns a list of rows in a table.

        Docs: https://coda.io/developers/apis/v1/#tag/Rows

        :param doc_id:  ID of the doc. Example: "AbCDeFGH"

        :param table_id_or_name: ID or name of the table.
            Names are discouraged because they're easily prone to being changed by users.
            If you're using a name, be sure to URI-encode it. Example: "grid-pqRst-U"

        :param query: filter returned rows, specified as `<column_id_or_name>:<value>`.
            If you'd like to use a column name instead of an ID,
            you must quote it (e.g., `"My Column":123`).
            Also note that `value` is a JSON value; if you'd like to use a string,
            you must surround it in quotes (e.g., `"groceries"`).

        :param use_column_names: Use column names instead of column IDs in the returned output.
            This is generally discouraged as it is fragile.
            If columns are renamed, code using original names may throw errors.

        :param limit: Maximum number of results to return in this query.

        :param offset: An opaque token used to fetch the next page of results.
        """
        data = {"useColumnNames": use_column_names}
        if query:
            data["query"] = query

        return self.get(
            f"/docs/{doc_id}/tables/{table_id_or_name}/rows",
            data=data,
            limit=limit,
            offset=offset,
        )

    def upsert_row(self, doc_id: str, table_id_or_name: str, data: Dict) -> Dict:
        """
        Inserts rows into a table, optionally updating existing rows if key columns are provided.

        This endpoint will always return a 202, so long as the doc and table exist and
        are accessible (and the update is structurally valid). Row inserts/upserts are generally
        processed within several seconds.
        When upserting, if multiple rows match the specified key column(s),
        they will all be updated with the specified value.

        Docs: https://coda.io/developers/apis/v1/#operation/upsertRows

        :param doc_id:  ID of the doc. Example: "AbCDeFGH"

        :param table_id_or_name: ID or name of the table.
            Names are discouraged because they're easily prone to being changed by users.
            If you're using a name, be sure to URI-encode it. Example: "grid-pqRst-U"

        :param data:
            {
                "rows": [{"cells": [{"column": "c-tuVwxYz", "value": "$12.34"}]}],
                "keyColumns": ["c-bCdeFgh"]
            }
        """
        return self.post(f"/docs/{doc_id}/tables/{table_id_or_name}/rows", data)

    def get_row(self, doc_id: str, table_id_or_name: str, row_id_or_name: str) -> Dict:
        """
        Returns details about a row in a table.

        Docs: https://coda.io/developers/apis/v1/#operation/getRow

        :param doc_id:  ID of the doc. Example: "AbCDeFGH"

        :param table_id_or_name: ID or name of the table.
            Names are discouraged because they're easily prone to being changed by users.
            If you're using a name, be sure to URI-encode it. Example: "grid-pqRst-U"

        :param row_id_or_name: ID or name of the row.
            Names are discouraged because they're easily prone to being changed by users.
            If you're using a name, be sure to URI-encode it.
            If there are multiple rows with the same value in the identifying column,
            an arbitrary one will be selected.
        """
        return self.get(
            f"/docs/{doc_id}/tables/{table_id_or_name}/rows/{row_id_or_name}"
        )

    def update_row(
        self, doc_id: str, table_id_or_name: str, row_id_or_name: str, data: Dict
    ) -> Dict:
        """
        Updates the specified row in the table.

        This endpoint will always return a 202, so long as the doc and table exist and
        are accessible (and the update is structurally valid). Row updates are generally
        processed within several seconds.
        When updating using a name as opposed to an ID, an arbitrary row will be affected.

        Docs: https://coda.io/developers/apis/v1/#operation/updateRow

        :param doc_id:  ID of the doc. Example: "AbCDeFGH"

        :param table_id_or_name: ID or name of the table.
            Names are discouraged because they're easily prone to being changed by users.
            If you're using a name, be sure to URI-encode it. Example: "grid-pqRst-U"

        :param row_id_or_name: ID or name of the row.
            Names are discouraged because they're easily prone to being changed by users.
            If you're using a name, be sure to URI-encode it.
            If there are multiple rows with the same value in the identifying column,
            an arbitrary one will be selected.

        :param data: Example: {"row": {"cells": [{"column": "c-tuVwxYz", "value": "$12.34"}]}}
        """
        return self.put(
            f"/docs/{doc_id}/tables/{table_id_or_name}/rows/{row_id_or_name}", data
        )

    def delete_row(self, doc_id, table_id_or_name: str, row_id_or_name: str) -> Dict:
        """
        Deletes the specified row from the table.

        This endpoint will always return a 202, so long as the row exists and
        is accessible (and the update is structurally valid).
        Row deletions are generally processed within several seconds.
        When deleting using a name as opposed to an ID, an arbitrary row will be removed.

        Docs: https://coda.io/developers/apis/v1/#operation/deleteRow

        :param doc_id:  ID of the doc. Example: "AbCDeFGH"

        :param table_id_or_name: ID or name of the table.
            Names are discouraged because they're easily prone to being changed by users.
        If you're using a name, be sure to URI-encode it. Example: "grid-pqRst-U"

        :param row_id_or_name: ID or name of the row.
            Names are discouraged because they're easily prone to being changed by users.
            If you're using a name, be sure to URI-encode it.
            If there are multiple rows with the same value in the identifying column,
            an arbitrary one will be selected.
        """
        return self.delete(
            f"/docs/{doc_id}/tables/{table_id_or_name}/rows/{row_id_or_name}"
        )

    def list_formulas(self, doc_id: str, offset: int = None, limit: int = None) -> Dict:
        """
        Returns a list of named formulas in a Coda doc.

        Docs: https://coda.io/developers/apis/v1/#operation/listFormulas

        :param doc_id:  ID of the doc. Example: "AbCDeFGH"

        :param limit: Maximum number of results to return in this query.

        :param offset: An opaque token used to fetch the next page of results.
        """
        return self.get(f"/docs/{doc_id}/formulas", offset=offset, limit=limit)

    def get_formula(self, doc_id: str, formula_id_or_name: str) -> Dict:
        """
        Returns info on a formula.

        Docs: https://coda.io/developers/apis/v1/#operation/getFormula

        :param doc_id:  ID of the doc. Example: "AbCDeFGH"

        :param formula_id_or_name: ID or name of the formula.
            Names are discouraged because they're easily prone to being changed by users.
            If you're using a name, be sure to URI-encode it. Example: "f-fgHijkLm".
        """
        return self.get(f"/docs/{doc_id}/formulas/{formula_id_or_name}")

    def list_controls(self, doc_id: str, offset: int = None, limit: int = None) -> Dict:
        """
        Lists controls and get their current values.

        Controls provide a user-friendly way to input a value
        that can affect other parts of the doc.

        Docs: https://coda.io/developers/apis/v1/#tag/Controls

        :param doc_id:  ID of the doc. Example: "AbCDeFGH"

        :param limit: Maximum number of results to return in this query.

        :param offset: An opaque token used to fetch the next page of results.

        :return:
        """
        return self.get(f"/docs/{doc_id}/controls", offset=offset, limit=limit)

    def get_control(self, doc_id: str, control_id_or_name: str) -> Dict:
        """
        Returns info on a control.

        Docs: https://coda.io/developers/apis/v1/#operation/getControl

        :param doc_id:  ID of the doc. Example: "AbCDeFGH"
        :param control_id_or_name: ID or name of the control.
            Names are discouraged because they're easily prone to being changed by users.
            If you're using a name, be sure to URI-encode it. Example: "ctrl-cDefGhij".
        """
        return self.get(f"/docs/{doc_id}/controls/{control_id_or_name}")

    def account(self) -> Dict:
        """
        Retrieves logged-in account information.

        At this time, the API exposes some limited information about your account.
        However, /whoami is a good endpoint to hit to verify that
        you're hitting the API correctly and that your token is working as expected.

        Docs: https://coda.io/developers/apis/v1/#tag/Account
        """
        return self.get("/whoami")

    def resolve_browser_link(self, url: str, degrade_gracefully: bool = False) -> Dict:
        """
        Retrieves the metadata of a Coda object for an URL.

        Given a browser link to a Coda object, attempts to find it and
        return metadata that can be used to get more info on it.
        Returns a 400 if the URL does not appear to be a Coda URL or a
        404 if the resource cannot be located with the current credentials.

        Docs: https://coda.io/developers/apis/v1/#operation/resolveBrowserLink

        :param url: The browser link to try to resolve.
            Example: "https://coda.io/d/_dAbCDeFGH/Launch-Status_sumnO"

        :param degrade_gracefully: By default, attempting to resolve the Coda URL
            of a deleted object will result in an error. If this flag is set,
            the next-available object, all the way up to the doc itself, will be resolved.
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
        for key in ["parent", "format"]:
            if key in js:
                js.pop(key)
        return cls(**js, document=document)


@attr.s(hash=True)
class Document:
    """Main class for interacting with coda.io API using `codaio` objects."""

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
        """
        Instantiates a `Document` with the API key in the `CODA_API_KEY` environment variable.

        :param doc_id: ID of the doc. Example: "AbCDeFGH"

        :return:
        """
        return cls(id=doc_id, coda=Coda.from_environment())

    def __attrs_post_init__(self):
        self.href = f"/docs/{self.id}"
        data = self.coda.get(self.href + "/")
        if not data:
            raise err.DocumentNotFound(f"No document with id {self.id}")
        self.name = data["name"]
        self.owner = data["owner"]
        self.created_at = parse(data["createdAt"])
        self.updated_at = parse(data["updatedAt"])
        self.type = data["type"]
        self.browser_link = data["browserLink"]

    def list_sections(self, offset: int = None, limit: int = None) -> List[Section]:
        """
        Returns a list of `Section` objects for each section in the document.

        :param limit: Maximum number of results to return in this query.

        :param offset: An opaque token used to fetch the next page of results.

        :return:
        """
        return [
            Section.from_json(i, document=self)
            for i in self.coda.list_sections(self.id, offset=offset, limit=limit)[
                "items"
            ]
        ]

    def list_tables(self, offset: int = None, limit: int = None) -> List[Table]:
        """
        Returns a list of `Table` objects for each table in the document.

        :param limit: Maximum number of results to return in this query.

        :param offset: An opaque token used to fetch the next page of results.

        :return:
        """

        return [
            Table.from_json(i, document=self)
            for i in self.coda.list_tables(self.id, offset=offset, limit=limit)["items"]
        ]

    def get_table(self, table_id_or_name: str) -> Table:
        """
        Gets a Table object from table name or ID.

        :param table_id_or_name: ID or name of the table.
            Names are discouraged because they're easily prone to being changed by users.
            If you're using a name, be sure to URI-encode it. Example: "grid-pqRst-U"

        :return:
        """
        table_data = self.coda.get_table(self.id, table_id_or_name)
        if table_data:
            return Table.from_json(table_data, document=self)
        raise err.TableNotFound(f"{table_id_or_name}")


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
    table_type: str = attr.ib(default=None, repr=False)
    created_at: dt.datetime = attr.ib(
        repr=False, converter=lambda x: parse(x) if x else None, default=None
    )
    updated_at: dt.datetime = attr.ib(
        repr=False, converter=lambda x: parse(x) if x else None, default=None
    )
    columns_storage: List[Column] = attr.ib(default=[], repr=False)

    def __getitem__(self, item):
        """
        table[row_id] -> Row with this id
        table[Row] -> Row with id == Row.id

        table[row_id][column_id] -> Cell from this intersection
        table[row_id][Column] -> Cell from this intersection

        :param item:

        :return:
        """
        if isinstance(item, str):
            return self.get_row_by_id(item)
        elif isinstance(item, Row):
            return self.get_row_by_id(item.id)
        raise ValueError("item type must be in [str, Row]")

    def columns(self, offset: int = None, limit: int = None) -> List[Column]:
        """
        Lists Table columns.

        Columns are stored in self.columns_storage for faster access
        as they tend to change less frequently than rows.

        :param limit: Maximum number of results to return in this query.

        :param offset: An opaque token used to fetch the next page of results.

        :return:
        """
        if not self.columns_storage:
            self.columns_storage = [
                Column.from_json({**i, "table": self}, document=self.document)
                for i in self.document.coda.list_columns(
                    self.document.id, self.id, offset=offset, limit=limit
                )["items"]
            ]
        return self.columns_storage

    def rows(self, offset: int = None, limit: int = None) -> List[Row]:
        """
        Returns list of Table rows.

        :param limit: Maximum number of results to return in this query.

        :param offset: An opaque token used to fetch the next page of results.

        :return:
        """
        return [
            Row.from_json({"table": self, **i}, document=self.document)
            for i in self.document.coda.list_rows(
                self.document.id, self.id, offset=offset, limit=limit
            )["items"]
        ]

    def get_row_by_id(self, row_id: str) -> Row:
        row_js = self.document.coda.get_row(self.document.id, self.id, row_id)
        row = Row.from_json({**row_js, "table": self}, document=self.document)
        return row

    def get_column_by_id(self, column_id) -> Column:
        """
        Gets a Column by id.

        :param column_id: ID of the column. Example: "c-tuVwxYz"

        :return:
        """
        try:
            return next(filter(lambda x: x.id == column_id, self.columns()))
        except StopIteration:
            raise err.ColumnNotFound(f"No column with id {column_id}")

    def get_column_by_name(self, column_name) -> Column:
        """
        Gets a Column by id.

        :param column_name: Name of the column. Discouraged in case using column_id is possible.
            Example: "Column 1"

        :return:
        """
        res = list(filter(lambda x: x.name == column_name, self.columns()))
        if not res:
            raise err.ColumnNotFound(f"No column with name: {column_name}")
        if len(res) > 1:
            raise err.AmbiguousName(
                "More than 1 column found. Try using ID instead of Name"
            )
        return res[0]

    def find_row_by_column_name_and_value(
        self, column_name: str, value: Any
    ) -> List[Row]:
        """
        Finds rows by a value in column specified by name (discouraged).

        :param column_name:  Name of the column.

        :param value: Search value.

        :return:
        """
        r = self.document.coda.list_rows(
            self.document.id, self.id, query=f'"{column_name}":{json.dumps(value)}'
        )
        if not r.get("items"):
            return []
        return [
            Row.from_json({**i, "table": self}, document=self.document)
            for i in r["items"]
        ]

    def find_row_by_column_id_and_value(self, column_id, value) -> List[Row]:
        """
        Finds rows by a value in column specified by id.

        :param column_id: ID of the column.

        :param value: Search value.

        :return:
        """
        r = self.document.coda.list_rows(
            self.document.id, self.id, query=f"{column_id}:{json.dumps(value)}"
        )
        if not r.get("items"):
            return []
        return [
            Row.from_json({**i, "table": self}, document=self.document)
            for i in r["items"]
        ]

    def upsert_row(
        self, cells: List[Cell], key_columns: List[Union[str, Column]] = None
    ) -> Dict:
        """
        Upsert a Table row using a list of `Cell` objects optionally updating existing rows.

        :param cells: list of `Cell` objects.
        :param key_columns: list of `Column` objects, column IDs, URLs, or names
            specifying columns to be used as upsert keys.
        """

        return self.upsert_rows([cells], key_columns)

    def upsert_rows(
        self,
        rows: List[List[Cell]],
        key_columns: List[Union[str, Column]] = None,
    ) -> Dict:
        """
        Upsert multiple Table rows optionally updating existing rows.

        Works similar to Table.upsert_row() but uses 1 POST request for multiple rows.
        Input is a list of lists of Cells.

        :param rows: list of lists of `Cell` objects, one list for each row.
        :param key_columns: list of `Column` objects, column IDs, URLs, or names
            specifying columns to be used as upsert keys.
        """
        data = {
            "rows": [
                {
                    "cells": [
                        {"column": cell.column_id_or_name, "value": cell.value}
                        for cell in row
                    ]
                }
                for row in rows
            ]
        }

        if key_columns:
            if not isinstance(key_columns, list):
                raise err.ColumnNotFound(
                    f"key_columns parameter '{key_columns}' is not a list."
                )

            data["keyColumns"] = []

            for key_column in key_columns:
                if isinstance(key_column, Column):
                    data["keyColumns"].append(key_column.id)
                elif isinstance(key_column, str):
                    data["keyColumns"].append(key_column)
                else:
                    raise err.ColumnNotFound(
                        f"Invalid parameter: '{key_column}' in key_columns."
                    )

        return self.document.coda.upsert_row(self.document.id, self.id, data)

    def update_row(self, row: Union[str, Row], cells: List[Cell]) -> Dict:
        """
        Updates row with values according to list in cells.

        :param row: a str ROW_ID or an instance of class Row
        :param cells: list of `Cell` objects.
        """
        if isinstance(row, Row):
            row_id = row.id
        elif isinstance(row, str):
            row_id = row
        else:
            raise TypeError("row must be str ROW_ID or an instance of Row")

        data = {
            "row": {
                "cells": [
                    {"column": cell.column_id_or_name, "value": cell.value}
                    for cell in cells
                ]
            }
        }

        return self.document.coda.update_row(self.document.id, self.id, row_id, data)

    def delete_row_by_id(self, row_id: str):
        """
        Deletes row by id.

        :param row_id: ID of the row to delete.
        """
        return self.document.coda.delete_row(self.document.id, self.id, row_id)

    def delete_row(self, row: Row) -> Dict:
        """
        Delete row.

        :param row: a `Row` object to delete.
        """

        return self.delete_row_by_id(row.id)

    def to_dict(self) -> List[Dict]:
        """
        Returns entire table as list of dicts. Intended for use with pandas:

        pd.DataFrame(table.to_dict())
        """
        return [row.to_dict() for row in self.rows()]


@attr.s(auto_attribs=True, hash=True)
class Column(CodaObject):
    name: str
    table: Table = attr.ib(repr=False)
    display: bool = attr.ib(default=None, repr=False)
    calculated: bool = attr.ib(default=False)


@attr.s(auto_attribs=True, hash=True)
class Row(CodaObject):
    name: str
    created_at: dt.datetime = attr.ib(converter=lambda x: parse(x), repr=False)
    index: int
    updated_at: dt.datetime = attr.ib(
        converter=lambda x: parse(x) if x else None, repr=False
    )
    values: Tuple[Tuple] = attr.ib(
        converter=lambda x: tuple([(k, v) for k, v in x.items()]), repr=False
    )
    table: Table = attr.ib(repr=False)
    browser_link: str = attr.ib(default=None, repr=False)

    def columns(self):
        return self.table.columns()

    def refresh(self):
        new_data = self.table.document.coda.get_row(
            self.table.document.id, self.table.id, self.id
        )
        self.values = tuple([(k, v) for k, v in new_data["values"].items()])
        return self

    def cells(self) -> List[Cell]:
        return [
            Cell(column=self.table.get_column_by_id(i[0]), value_storage=i[1], row=self)
            for i in self.values
        ]

    def delete(self):
        """
        Delete row.

        :return:
        """
        return self.table.delete_row(self)

    def get_cell_by_column_id(self, column_id: str) -> Cell:
        try:
            return next(filter(lambda x: x.column.id == column_id, self.cells()))
        except StopIteration:
            raise KeyError("Column not found")

    def __getitem__(self, item) -> Cell:
        if isinstance(item, Column):
            return self.get_cell_by_column_id(item.id)
        elif isinstance(item, str):
            try:
                return self.get_cell_by_column_id(item)
            except KeyError:
                pass
            column = self.table.get_column_by_name(item)
            found_by_name = self.get_cell_by_column_id(column.id)
            if found_by_name:
                return found_by_name

        raise KeyError(f"Invalid column_id: {item}")

    def __setitem__(self, item, value) -> Cell:
        cell = self.__getitem__(item)
        data = {"row": {"cells": [{"column": cell.column.id, "value": value}]}}
        self.document.coda.update_row(
            self.document.id, self.table.id, self.id, data=data
        )
        cell.value_storage = value
        return cell

    def to_dict(self) -> Dict:
        """
        Returns a row as a dictionary.

        :return:
        """
        return {column.name: self[column].value for column in self.columns()}


@attr.s(auto_attribs=True, hash=True, repr=False)
class Cell:
    column: Union[str, Column]
    value_storage: Any
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

    @property
    def value(self):
        return self.value_storage

    @property
    def column_id_or_name(self):
        if isinstance(self.column, Column):
            return self.column.id
        elif isinstance(self.column, str):
            return self.column

    @value.setter
    def value(self, value):
        data = {"row": {"cells": [{"column": self.column.id, "value": value}]}}
        self.document.coda.update_row(
            self.document.id, self.table.id, self.row.id, data=data
        )
        self.value_storage = value

        new_value = None
        while new_value != value:
            self.row.refresh()
            new_value = self.row.get_cell_by_column_id(self.column.id).value
            time.sleep(0.3)
