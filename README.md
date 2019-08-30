## Python wrapper for [Coda.io](https://coda.io) API

[![CodaAPI](https://img.shields.io/badge/Coda_API_version-0.1.1--beta1-orange)](https://coda.io/developers/apis/v1beta1)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI](https://img.shields.io/pypi/v/codaio)](https://pypi.org/project/codaio/)
[![Documentation Status](https://readthedocs.org/projects/codaio/badge/?version=latest)](https://codaio.readthedocs.io/en/latest/?badge=latest)

`codaio` is in active development stage. Issues and PRs very welcome!

### Installation
```shell script
pip install codaio
```

### Config via environment variables
The following variables will be called from environment where applicable:

* `CODA_API_ENDPOINT` (default value `https://coda.io/apis/v1beta1`)
* `CODA_API_KEY` - your API key to use when initializing document from environment

### Quickstart using raw API
Coda class provides a wrapper for all API methods. If API response included a JSON it will be returned as a dictionary from all methods. If it didn't a dictionary `{"status": response.status_code}` will be returned.
If request wasn't successful a `CodaError` will be raised with details of the API error.

```python
from codaio import Coda

coda = Coda('YOUR_API_KEY')

>>> coda.create_doc('My document')
{'id': 'NEW_DOC_ID', 'type': 'doc', 'href': 'https://coda.io/apis/v1beta1/docs/LINK', 'browserLink': 'https://coda.io/d/LINK', 'name': 'My Document', 'owner': 'your@email', 'createdAt': '2019-08-29T11:36:45.120Z', 'updatedAt': '2019-08-29T11:36:45.272Z'}
```
For full API reference for Coda class see [documentation](https://codaio.readthedocs.io/en/latest/index.html#codaio.Coda)

### Quickstart using codaio objects

`codaio` implements convenient classes to work with Coda documents: `Document`, `Table`, `Row`, `Column` and `Cell`.

```python
from codaio import Coda, Document

# Initialize by providing a coda object directly
coda = Coda('YOUR_API_KEY')

doc = Document('YOUR_DOC_ID', coda=coda)

# Or initialiaze from environment by storing your API key in environment variable `CODA_API_KEY`
doc = Document.from_environment('YOUR_DOC_ID')

doc.list_tables()

table = doc.get_table('TABLE_ID')

# You can fetch a row by ID
row  = table['ROW_ID']

# Or fetch a cell by ROW_ID and COLUMN_ID
cell = table['ROW_ID']['COLUMN_ID'] 

# This is equivalent to getting item from a row
cell = row['COLUMN_ID']

# To set a cell value 
cell.value = 'foo'

# Please mind that this takes a while in the current API, so you'll need to manually check when the value returns correct
# You can manually refresh row cells by calling:
row.refresh()
```

For full API reference for Document class see [documentation](https://codaio.readthedocs.io/en/latest/index.html#codaio.Document)

#### Documentation

`codaio` documentation lives at [readthedocs.io](https://codaio.readthedocs.io/en/latest/index.html)


#### Testing

All tests are in 
