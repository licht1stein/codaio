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

#### Documentation

`codaio` documentation lives at [readthedocs.io](https://codaio.readthedocs.io/en/latest/index.html)

#### Using raw API

`codaio` implements all methods of raw api in a convenient python manner. So API's `listDocs` becomes in `codaio` `Coda.list_docs()`. Get requests return a dictionary. Put, delete and post return a requests Response object.

All methods of Coda class are describe in the [documentation](https://codaio.readthedocs.io/en/latest/index.html#codaio.Coda).
