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

### Quickstart using raw API
Coda class provides a wrapper for all API methods.

```python
from codaio import Coda

coda = Coda('YOUR_API_KEY')

coda.list_docs()
coda.create_doc('My document')
```
For full API reference for Coda class see [documentation](https://codaio.readthedocs.io/en/latest/index.html#codaio.Coda)

### Quickstart using codaio objects

`codaio` implements convenient classes to work with Coda documents: `Document`, `Table`, `Row`, `Column` and `Cell`.

```python
from codaio import Coda, Document, Table

coda = Coda('YOUR_API_KEY')

doc = Document('YOUR_DOC_ID', coda=coda)
doc.list_tables()

table: Table = doc.get_table('TABLE_ID')
```

For full API reference for Document class see [documentation](https://codaio.readthedocs.io/en/latest/index.html#codaio.Document)

#### Documentation

`codaio` documentation lives at [readthedocs.io](https://codaio.readthedocs.io/en/latest/index.html)

#### Using raw API

`codaio` implements all methods of raw api in a convenient python manner. So API's `listDocs` becomes in `codaio` `Coda.list_docs()`. Get requests return a dictionary. Put, delete and post return a requests Response object.

All methods of Coda class are describe in the [documentation](https://codaio.readthedocs.io/en/latest/index.html#codaio.Coda).
