## Python wrapper for [Coda.io](https://coda.io) API

[![CodaAPI](https://img.shields.io/badge/Coda_API_-V1-green)](https://coda.io/developers/apis/v1beta1)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/codaio)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation Status](https://readthedocs.org/projects/codaio/badge/?version=latest)](https://codaio.readthedocs.io/en/latest/?badge=latest)
[![PyPI](https://img.shields.io/pypi/v/codaio)](https://pypi.org/project/codaio/)
![PyPI - Downloads](https://img.shields.io/pypi/dw/codaio)
[![](https://img.shields.io/badge/Support-Buy_coffee!-Orange)](https://www.buymeacoffee.com/licht1stein)

`codaio` is in active development stage. Issues and PRs very welcome! 


### Installation
```shell script
pip install codaio
```

### Config via environment variables
The following variables will be called from environment where applicable:

* `CODA_API_ENDPOINT` (default value `https://coda.io/apis/v1`)
* `CODA_API_KEY` - your API key to use when initializing document from environment

### Quickstart using raw API
Coda class provides a wrapper for all API methods. If API response included a JSON it will be returned as a dictionary from all methods. If it didn't a dictionary `{"status": response.status_code}` will be returned.
If request wasn't successful a `CodaError` will be raised with details of the API error.

```python
from codaio import Coda

coda = Coda('YOUR_API_KEY')

>>> coda.create_doc('My Document')
{'id': 'NEW_DOC_ID', 'type': 'doc', 'href': 'https://coda.io/apis/v1/docs/NEW_DOC_ID', 'browserLink': 'https://coda.io/d/_dNEW_DOC_ID', 'name': 'My Document', 'owner': 'your@email', 'ownerName': 'Your Name', 'createdAt': '2020-09-28T19:32:20.866Z', 'updatedAt': '2020-09-28T19:32:20.924Z'}
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
```
#### Fetching a Row
```python
# You can fetch a row by ID
row  = table['ROW_ID']
```

#### Using with Pandas
If you want to load a codaio Table or Row into pandas, you can use the `Table.to_dict()` or `Row.to_dict()` methods:
```python
import pandas as pd

df = pd.DataFrame(table.to_dict())
```

#### Fetching a Cell
```python
# Or fetch a cell by ROW_ID and COLUMN_ID
cell = table['ROW_ID']['COLUMN_ID']  

# This is equivalent to getting item from a row
cell = row['COLUMN_ID']
# or 
cell = row['COLUMN_NAME']  # This should work fine if COLUMN_NAME is unique, otherwise it will raise AmbiguousColumn error
# or use a Column instance
cell = row[column]
```

#### Changing Cell value

```python
row['COLUMN_ID'] = 'foo'
# or
row['Column Name'] = 'foo'
```

#### Iterating over rows
```
# Iterate over rows using IDs -> delete rows that match a condition
for row in table.rows():
    if row['COLUMN_ID'] == 'foo':
        row.delete()

# Iterate over rows using names -> edit cells in rows that match a condition
for row in table.rows():
    if row['Name'] == 'bar':
        row['Value'] = 'spam'
```

#### Upserting new row
To upsert a new row you can pass a list of cells to `table.upsert_row()`
```python
name_cell = Cell(column='COLUMN_ID', value_storage='new_name')
value_cell = Cell(column='COLUMN_ID', value_storage='new_value')

table.upsert_row([name_cell, value_cell])
```

#### Upserting multiple new rows
Works like upserting one row, except you pass a list of lists to `table.upsert_rows()` (rows, not row)
```python
name_cell_a = Cell(column='COLUMN_ID', value_storage='new_name')
value_cell_a = Cell(column='COLUMN_ID', value_storage='new_value')

name_cell_b = Cell(column='COLUMN_ID', value_storage='new_name')
value_cell_b = Cell(column='COLUMN_ID', value_storage='new_value')

table.upsert_rows([[name_cell_a, value_cell_a], [name_cell_b, value_cell_b]])
```

#### Updating a row
To update a row use `table.update_row(row, cells)`
```python
row = table['ROW_ID']

name_cell_a = Cell(column='COLUMN_ID', value_storage='new_name')
value_cell_a = Cell(column='COLUMN_ID', value_storage='new_value')

table.update_row(row, [name_cell_a, value_cell_a])
```

### Documentation

`codaio` documentation lives at [readthedocs.io](https://codaio.readthedocs.io/en/latest/index.html)

### Running the tests

The recommended way of running the test suite is to use [nox](https://nox.thea.codes/en/stable/tutorial.html).

Once `nox`: is installed, just run the following command:
```shell script
nox
```

The nox session will run the test suite against python 3.8 and 3.7. It will also look for linting errors with `flake8`.

You can still invoke `pytest` directly with:
```shell script
poetry run pytest --cov
```

Check out the fixtures if you want to improve the testing process.


#### Contributing

If you are willing to contribute please go ahead, we can use some help!

##### Using CI to deploy to PyPi

When a PR is merged to master the CI will try to deploy to pypi.org using poetry. It will succeed only if the 
version number changed in pyproject.toml. 

To do so use poetry's [version command](https://python-poetry.org/docs/cli/#version). For example:

Bump 0.4.11 to 0.4.12:
```bash
poetry version patch
```

Bump 0.4.11 to 0.5.0:
```bash
poetry version minor
```

Bump 0.4.11 to 1.0.0:
```bash
poetry version major
```
