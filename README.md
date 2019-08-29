## Python wrapper for [Coda.io](https://coda.io) API

[![CodaAPI](https://img.shields.io/badge/Coda_API_version-0.1.1--beta1-orange)](https://coda.io/developers/apis/v1beta1)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI](https://img.shields.io/pypi/v/codaio)](https://pypi.org/project/codaio/)
[![Documentation Status](https://readthedocs.org/projects/codaio/badge/?version=latest)](https://codaio.readthedocs.io/en/latest/?badge=latest)


### Installation
```shell script
pip install codaio
```

### Config via environment variables
The following variables will be called from environment where applicable:

* `CODA_API_ENDPOINT` (default value `https://coda.io/apis/v1beta1`)
* `CODA_API_KEY` - your API key to use when initializing document from environment

### Quickstart
You can initialize a document by providing API_KEY and document_id directly, or by storing your API key in environment under `CODA_API_KEY`

```python
from codaio import Document


# Directly
doc = Document('YOUR_DOC_ID', 'YOUR_API_KEY')

# From environment
>>> doc = Document.from_environment('YOUR_DOC_ID')
>>> print(doc)
Document(id='YOUR_DOC_ID', name='Document Name', owner='owner@example.com', browser_link='https://coda.io/d/URL')

>>> doc.all_tables()
[Table(name='Table1'), Table(name='table2')]

>>> doc.get_table('Table1')
Table(name='Table1')

>>> table.columns
[Column(name='First Column', calculated=False)]

>>> table.rows
[Row(name='Some row', index=1)]

# Find row by column name and value:
>> table.find_row_by_column_name_and_value('COLUMN_NAME', 'VALUE')
Row(name='Some row', index=1)

# Find row by column id and value
>>> table.find_row_by_column_id_and_value('COLUMN_ID', 'VALUE')
Row(name='Some row', index=1)

# To get cell value for a column use getitem:
>>> row['Column 1']
Cell(column=Column 1, row=Some row, value=Some Value)
```

#### Using raw API

`codaio` implements all methods of raw api in a convenient python manner. So API's `listDocs` becomes in `codaio` `Coda.list_docs()`. Get requests return a dictionary. Put, delete and post return a requests Response object.

### Coda
```python
Coda(self, api_key: 'str', href: 'str' = 'https://coda.io/apis/v1beta1') -> None
```

Raw API client. It is used in `codaio` objects like Document to access the raw API endpoints. Can also be used by itself to access Raw API.

###### from_environment
```python
Coda.from_environment() -> 'Coda'
```

Initializes a Coda instance using API key store in environment variables under `CODA_API_KEY`

:return:

###### get
```python
Coda.get(self, endpoint: 'str', data: 'Dict' = None, limit=None, offset=None) -> 'Dict'
```

Make a GET request to API endpoint.

:param endpoint: API endpoint to request

:param data: dictionary of optional query params

:param limit: Maximum number of results to return in this query.

:param offset: An opaque token used to fetch the next page of results.

:return:

###### post
```python
Coda.post(self, endpoint: 'str', data: 'Dict') -> 'Response'
```

Make a POST request to the API endpoint.

:param endpoint: API endpoint to request

:param data: data dict to be sent as body json

:return:

###### put
```python
Coda.put(self, endpoint: 'str', data: 'Dict') -> 'Response'
```

Make a PUT request to the API endpoint.

:param endpoint: API endpoint to request

:param data: data dict to be sent as body json

:return:

###### delete
```python
Coda.delete(self, endpoint: 'str') -> 'Response'
```

Make a DELETE request to the API endpoint.

:param endpoint: API endpoint to request

:return:

###### list_docs
```python
Coda.list_docs(self, is_owner: 'bool' = False, query: 'str' = None, source_doc_id: 'str' = None, limit: 'int' = 100, offset: 'int' = 0)
```

Returns a list of Coda docs accessible by the user. These are returned in the same order as on the docs page: reverse
chronological by the latest event relevant to the user (last viewed, edited, or shared).

Docs: https://coda.io/developers/apis/v1beta1###operation/listDocs

:param is_owner: Show only docs owned by the user.

:param query: Search term used to filter down results.

:param source_doc_id: Show only docs copied from the specified doc ID.

:param limit: Maximum number of results to return in this query.

:param offset: An opaque token used to fetch the next page of results.

:return:

###### create_doc
```python
Coda.create_doc(self, title: 'str', source_doc: 'str' = None, tz: 'str' = None) -> 'Response'
```

Creates a new Coda doc, optionally copying an existing doc.

Docs: https://coda.io/developers/apis/v1beta1###operation/createDoc

:param title: Title of the new doc.

:param source_doc: An optional doc ID from which to create a copy.

:param tz: The timezone to use for the newly created doc.

:return:

###### get_doc
```python
Coda.get_doc(self, doc_id: 'str')
```

Returns metadata for the specified doc.

Docs: https://coda.io/developers/apis/v1beta1###operation/getDoc

:param doc_id: ID of the doc. Example: "AbCDeFGH"

:return:

###### delete_doc
```python
Coda.delete_doc(self, doc_id: 'str') -> 'Response'
```

Deletes a doc.

Docs: https://coda.io/developers/apis/v1beta1###operation/deleteDoc

:param doc_id: ID of the doc. Example: "AbCDeFGH"

:return:

###### list_sections
```python
Coda.list_sections(self, doc_id: 'str')
```

Returns a list of sections in a Coda doc.

Docs: https://coda.io/developers/apis/v1beta1###operation/listSections

:param doc_id: ID of the doc. Example: "AbCDeFGH"

:return:

###### get_section
```python
Coda.get_section(self, doc_id: 'str', section_id_or_name: 'str')
```

Returns details about a section.

Docs: https://coda.io/developers/apis/v1beta1###operation/getSection

:param doc_id: ID of the doc. Example: "AbCDeFGH"

:param section_id_or_name: ID or name of the section. Names are discouraged because they're easily prone to being changed by users.
    If you're using a name, be sure to URI-encode it. Example: "canvas-IjkLmnO"

:return:

###### list_folders
```python
Coda.list_folders(self, doc_id: 'str')
```

Returns a list of folders in a Coda doc.

Docs: https://coda.io/developers/apis/v1beta1###operation/listFolders

:param doc_id: ID of the doc. Example: "AbCDeFGH"

:return:

###### get_folder
```python
Coda.get_folder(self, doc_id: 'str', folder_id_or_name: 'str')
```

Returns details about a folder.

Docs: https://coda.io/developers/apis/v1beta1###operation/getFolder

:param doc_id: ID of the doc. Example: "AbCDeFGH"

:param folder_id_or_name: ID or name of the folder. Names are discouraged because they're easily prone to being
    changed by users. If you're using a name, be sure to URI-encode it. Example: "section-IjkLmnO"

:return:

###### list_tables
```python
Coda.list_tables(self, doc_id: 'str')
```

Returns a list of tables in a Coda doc.

Docs: https://coda.io/developers/apis/v1beta1###operation/listTables

:param doc_id: ID of the doc. Example: "AbCDeFGH"

:return:

###### get_table
```python
Coda.get_table(self, doc_id: 'str', table_id_or_name: 'str')
```

Returns details about a specific table.

Docs: https://coda.io/developers/apis/v1beta1###operation/getTable

:param doc_id: ID of the doc. Example: "AbCDeFGH"

:param table_id_or_name: ID or name of the table. Names are discouraged because they're easily prone to being changed by users.
    If you're using a name, be sure to URI-encode it. Example: "grid-pqRst-U"

:return:

###### list_views
```python
Coda.list_views(self, doc_id: 'str')
```

Returns a list of views in a Coda doc.

Docs: https://coda.io/developers/apis/v1beta1###operation/listViews

:param doc_id: ID of the doc. Example: "AbCDeFGH"

:return:

###### get_view
```python
Coda.get_view(self, doc_id: 'str', view_id_or_name: 'str')
```

Returns details about a specific view.

Docs: https://coda.io/developers/apis/v1beta1###operation/getView

:param doc_id: ID of the doc. Example: "AbCDeFGH"

:param view_id_or_name: ID or name of the view. Names are discouraged because they're easily prone to being changed by users.
    If you're using a name, be sure to URI-encode it. Example: "table-pqRst-U"

:return:

###### list_columns
```python
Coda.list_columns(self, doc_id: 'str', table_id_or_name: 'str')
```

Returns a list of columns in a table.

:param doc_id: ID of the doc. Example: "AbCDeFGH"

:param table_id_or_name: ID or name of the table. Names are discouraged because they're easily prone to being changed by users.
    If you're using a name, be sure to URI-encode it. Example: "grid-pqRst-U"

:return:

###### get_column
```python
Coda.get_column(self, doc_id: 'str', table_id_or_name: 'str', column_id_or_name: 'str')
```

Returns details about a column in a table.

Docs: https://coda.io/developers/apis/v1beta1###operation/getColumn

:param doc_id:  ID of the doc. Example: "AbCDeFGH"

:param table_id_or_name: ID or name of the table. Names are discouraged because they're easily prone to being changed by users.
    If you're using a name, be sure to URI-encode it. Example: "grid-pqRst-U"

:param column_id_or_name: ID or name of the column. Names are discouraged because they're easily prone to being changed by users.
    If you're using a name, be sure to URI-encode it. Example: "c-tuVwxYz"

:return:

###### list_rows
```python
Coda.list_rows(self, doc_id: 'str', table_id_or_name: 'str')
```

Returns a list of rows in a table.

Docs: https://coda.io/developers/apis/v1beta1###tag/Rows

:param doc_id:  ID of the doc. Example: "AbCDeFGH"

:param table_id_or_name: ID or name of the table. Names are discouraged because they're easily prone to being changed by users. If you're using a name, be sure to URI-encode it. Example: "grid-pqRst-U"

:return:

###### upsert_row
```python
Coda.upsert_row(self, doc_id: 'str', table_id_or_name: 'str', data: 'Dict')
```

Inserts rows into a table, optionally updating existing rows if any upsert key columns are provided. This endpoint will always return a 202,
so long as the doc and table exist and are accessible (and the update is structurally valid). Row inserts/upserts are generally
processed within several seconds. When upserting, if multiple rows match the specified key column(s), they will all be updated with the specified value.

Docs: https://coda.io/developers/apis/v1beta1###operation/upsertRows

:param doc_id:  ID of the doc. Example: "AbCDeFGH"

:param table_id_or_name: ID or name of the table. Names are discouraged because they're easily prone to being changed by users.
If you're using a name, be sure to URI-encode it. Example: "grid-pqRst-U"

:param data: {"rows": [{"cells": [{"column": "c-tuVwxYz", "value": "$12.34"}]}], "keyColumns": ["c-bCdeFgh"]}

:return:

###### get_row
```python
Coda.get_row(self, doc_id: 'str', table_id_or_name: 'str', row_id_or_name: 'str')
```

Returns details about a row in a table.

Docs: https://coda.io/developers/apis/v1beta1###operation/getRow

:param doc_id:  ID of the doc. Example: "AbCDeFGH"

:param table_id_or_name: ID or name of the table. Names are discouraged because they're easily prone to being changed by users.
    If you're using a name, be sure to URI-encode it. Example: "grid-pqRst-U"

:param row_id_or_name: ID or name of the row. Names are discouraged because they're easily prone to being changed by users.
    If you're using a name, be sure to URI-encode it. If there are multiple rows with the same value in the identifying column,
    an arbitrary one will be selected.

:return:

###### update_row
```python
Coda.update_row(self, doc_id: 'str', table_id_or_name: 'str', row_id_or_name: 'str', data: 'Dict')
```

Updates the specified row in the table. This endpoint will always return a 202, so long as the row exists and is
accessible (and the update is structurally valid). Row updates are generally processed within several seconds.
When updating using a name as opposed to an ID, an arbitrary row will be affected.

Docs: https://coda.io/developers/apis/v1beta1###operation/updateRow

:param doc_id:  ID of the doc. Example: "AbCDeFGH"

:param table_id_or_name: ID or name of the table. Names are discouraged because they're easily prone to being changed by users.
If you're using a name, be sure to URI-encode it. Example: "grid-pqRst-U"

:param row_id_or_name: ID or name of the row. Names are discouraged because they're easily prone to being changed by users.
If you're using a name, be sure to URI-encode it. If there are multiple rows with the same value in the identifying column,
an arbitrary one will be selected.

:param data: Example: {"row": {"cells": [{"column": "c-tuVwxYz", "value": "$12.34"}]}}

:return: Response

###### delete_row
```python
Coda.delete_row_by_id(self, doc_id, table_id_or_name: 'str', row_id_or_name: 'str')
```

Deletes the specified row from the table. This endpoint will always return a 202, so long as the row exists and is accessible
(and the update is structurally valid). Row deletions are generally processed within several seconds.
When deleting using a name as opposed to an ID, an arbitrary row will be removed.

Docs: https://coda.io/developers/apis/v1beta1###operation/deleteRow

:param doc_id:  ID of the doc. Example: "AbCDeFGH"

:param table_id_or_name: ID or name of the table. Names are discouraged because they're easily prone to being changed by users.
If you're using a name, be sure to URI-encode it. Example: "grid-pqRst-U"

:param row_id_or_name: ID or name of the row. Names are discouraged because they're easily prone to being changed by users.
If you're using a name, be sure to URI-encode it. If there are multiple rows with the same value in the identifying column,
an arbitrary one will be selected.
:return:

###### list_formulas
```python
Coda.list_formulas(self, doc_id: 'str')
```

Returns a list of named formulas in a Coda doc.

Docs: https://coda.io/developers/apis/v1beta1###operation/listFormulas

:param doc_id:  ID of the doc. Example: "AbCDeFGH"

:return:

###### get_formula
```python
Coda.get_formula(self, doc_id: 'str', formula_id_or_name: 'str')
```

Returns info on a formula.

Docs: https://coda.io/developers/apis/v1beta1###operation/getFormula

:param doc_id:  ID of the doc. Example: "AbCDeFGH"

:param formula_id_or_name: ID or name of the formula. Names are discouraged because they're easily prone to being changed by users.
If you're using a name, be sure to URI-encode it. Example: "f-fgHijkLm"

:return:

###### list_controls
```python
Coda.list_controls(self, doc_id: 'str')
```

Controls provide a user-friendly way to input a value that can affect other parts of the doc. This API lets you list controls
and get their current values.

Docs: https://coda.io/developers/apis/v1beta1###tag/Controls

:param doc_id:  ID of the doc. Example: "AbCDeFGH"

:return:

###### get_control
```python
Coda.get_control(self, doc_id: 'str', control_id_or_name: 'str')
```

Returns info on a control.

Docs: https://coda.io/developers/apis/v1beta1###operation/getControl

:param doc_id:  ID of the doc. Example: "AbCDeFGH"
:param control_id_or_name: ID or name of the control. Names are discouraged because they're easily prone to being changed by users.
If you're using a name, be sure to URI-encode it. Example: "ctrl-cDefGhij"

:return:

###### account
```python
Coda.account(self)
```

At this time, the API exposes some limited information about your account. However, /whoami is a good endpoint to hit to verify
that you're hitting the API correctly and that your token is working as expected.

Docs: https://coda.io/developers/apis/v1beta1###tag/Account

:return:

###### resolve_browser_link
```python
Coda.resolve_browser_link(self, url: 'str', degrade_gracefully: 'bool' = False)
```

Given a browser link to a Coda object, attempts to find it and return metadata that can be used to get more info on it.
Returns a 400 if the URL does not appear to be a Coda URL or a 404 if the resource cannot be located with the current credentials.

Docs: https://coda.io/developers/apis/v1beta1###operation/resolveBrowserLink

:param url: The browser link to try to resolve. Example: "https://coda.io/d/_dAbCDeFGH/Launch-Status_sumnO"

:param degrade_gracefully: By default, attempting to resolve the Coda URL of a deleted object will result in an error.
If this flag is set, the next-available object, all the way up to the doc itself, will be resolved.

:return:




### Contributing
All contributions, issues and PRs very welcome!
