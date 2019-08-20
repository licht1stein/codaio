## Python wrapper for [Coda.io](https://coda.io) API

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

### Installation
```shell script
pip install codaio
```

### Config via environment variables
The following variables will be called from environment where applicable:

* `CODA_API_ENDPOINT` (default value `https://coda.io/apis/v1beta1`)
* `CODA_API_KEY` - your API key to use when initializing document from environment

### Usage
You can initialize a document by providing API_KEY and document_id directly, or by storing yoru API key in environment under `CODA_API_KEY`

```python
from codaio import Document

# Directly
doc = Document('YOUR_DOC_ID', 'YOUR_API_KEY')

# From environment
doc = Document.from_environment('YOUR_DOC_ID')

print(doc)
>>> Document(id='YOUR_DOC_ID', name='Document Name', owner='owner@example.com', browser_link='https://coda.io/d/URL')
```

#### Methods

```python
from codaio import Document

doc = Document.from_environment('YOUR_DOC_ID')

doc.tables() # list all tables
doc.get_table_rows(table_id_or_name='YOUR_TABLE')  # get ALL table rows
doc.get_table_rows(table_id_or_name='YOUR_TABLE', query={'query'})
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
