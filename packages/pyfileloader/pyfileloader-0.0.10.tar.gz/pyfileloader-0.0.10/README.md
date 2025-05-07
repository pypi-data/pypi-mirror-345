# fileloader

`fileloader` are functions for quickly loading files into lists. Supported types
are `txt`, `jsonl/ndjson`, and `csv`. JSON loading is there too, if needed(it returns a standard json.load(), so it's an object rather than a list of objects)

### Building

`pip3 install build && python3 -m build`

### Installing

`pip3 install pyfileloader`

### Usage

```
>>> from fileloader import load_jsonl
>>> items = load_jsonl('test-10.jsonl')
>>> len(items)
10
>>> comp_items = load_jsonl('compress-10.jsonl.gz')
>>> len(comp_items)
10
```
