## Python wrapper for [Coda.io](https://coda.io) API

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/codaio)
[![CodaAPI](https://img.shields.io/badge/Coda_API_version-0.1.1--beta1-orange)](https://coda.io/developers/apis/v1beta1)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI](https://img.shields.io/pypi/v/codaio)](https://pypi.org/project/codaio/)


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

>>> doc.tables()
[Table(name='Table1'), Table(name='table2')]

>>> doc.find_table('Table1')
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

You can issue [raw API requests](https://coda.io/developers/apis/v1beta1#tag/Docs) directly using Document methods `get` and `post`. You can skip entire url up to `/docs/{docId}`, this is handled by the wrapper. So for request to `https://coda.io/apis/v1beta1/docs/{docId}/tables` just use endpoint value of `/tables`:

```python
from codaio import Document

doc = Document.from_environment('YOUR_DOC_ID')

tables = doc.get(endpoint='/tables')
```

You can also use `offset` and `limit` to get a portion of results. If limit is not set, all the data will be automatically fetched. Pagination is handled for you by the wrapper.

### Contributing
All contributions, issues and PRs very welcome!
