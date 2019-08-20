## Python wrapper for [Coda.io](https://coda.io) API

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

### Installation
```shell script
pip install codaio
```


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

#### Using raw API

You can issue [raw API requests](https://coda.io/developers/apis/v1beta1#tag/Docs) directly using Document methods `get` and `post`. You can skip entire url up to `/docs/{docId}`, this is handled by the wrapper. So for request to `/docs/{docId}/tables` just use endpoint value of `/tables`:

```python
from codaio import Document

doc = Document.from_environment('YOUR_DOC_ID')

tables = doc.get(endpoint='/tables')
```
