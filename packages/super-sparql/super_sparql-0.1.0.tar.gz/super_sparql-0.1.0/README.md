# 🧠 super_sparql

**super_sparql** is a lightweight Python package for parsing and analyzing SPARQL queries in a structured, programmable way. It extracts components like prefixes, triple patterns, filters, limits, and even infers types from the query structure.

## 🚀 Features

- Parses SPARQL SELECT, CONSTRUCT, ASK, DESCRIBE queries
- Extracts:
  - Prefixes
  - Triple patterns
  - SELECT variables
  - Filters
  - LIMIT / OFFSET / ORDER BY
- Infers variable roles and types
- Returns a structured dataclass representation of the query
- Handles partial or loosely formatted SPARQL

## 📦 Installation

```bash
pip install super_sparql
```

Or if you're using it locally (after building your wheel):

```bash
pip install dist/super_sparql-0.1.0-py3-none-any.whl
```

## ✨ Quick Start

```python
from super_sparql import parse_my_SPARQL

query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dcm: <http://example.org/ns/dcm#>

SELECT ?x ?label
WHERE {
  ?x rdf:type dcm:Image .
  ?x dcm:label ?label .
  FILTER(lang(?label) = "en")
}
ORDER BY ?label
LIMIT 10
OFFSET 5
"""

parser = parse_my_SPARQL(query)
parsed = parser.parse()
print(parsed)
```

Output:

```
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dcm: <http://example.org/ns/dcm#>

SELECT ?x ?label
WHERE {
  ?x rdf:type dcm:Image.
  ?x dcm:label ?label.
  FILTER(lang(?label) = "en")
}
ORDER BY ?label
LIMIT 10
OFFSET 5
```

## 🔍 Use Cases

1. Get SELECT Variables

```python
parser.get_select_variables()
# ➞ ['?x', '?label']
```

2. Extract Triple Patterns

```python
for triple in parser.get_triple_patterns():
    print(triple)
# ➞ ?x rdf:type dcm:Image
# ➞ ?x dcm:label ?label
```

3. Get Variable Types

```python
parser.get_select_variable_types()
# ➞ {'?x': ['dcm:Image'], '?label': ['Range of dcm:label']}
```

4. Full Query Analysis

```python
analysis = parser.analyze_query()
print(analysis)
```

Sample Output:

```json
{
  "query_type": "SELECT",
  "select_variables": ["?x", "?label"],
  "variable_types": {
    "?x": ["dcm:Image"],
    "?label": ["Range of dcm:label"]
  },
  "variables_details": {
    "?x": {
      "in_select": true,
      "occurrences": {
        "as_subject": [{"triple_index": 0, "triple": "?x rdf:type dcm:Image"}, {"triple_index": 1, "triple": "?x dcm:label ?label"}],
        "as_predicate": [],
        "as_object": []
      }
    },
    ...
  },
  "triple_count": 2,
  "filter_count": 1,
  "has_order_by": true,
  "has_limit": true,
  "has_offset": true
}
```

## 📚 Supported SPARQL Clauses

| Clause | Supported | Notes |
|--------|-----------|-------|
| `PREFIX` | ✅ | Auto-completes common prefixes |
| `SELECT` | ✅ | Supports variables and wildcard `*` |
| `WHERE` | ✅ | Parses triple patterns and filters |
| `FILTER` | ✅ | Basic extraction supported |
| `ORDER BY` | ✅ | Supports `ASC`/`DESC` |
| `LIMIT` | ✅ | Extracts integer limit |
| `OFFSET` | ✅ | Extracts integer offset |
| `CONSTRUCT` | ⚠️ | Detected, parsed like SELECT |
| `ASK`, `DESCRIBE` | ⚠️ | Detected, parsed like SELECT |

## 📝 License

MIT License — see `LICENSE` for full text.

## 🙌 Acknowledgements

Built with sarcasm and care to make SPARQL parsing easier, faster, and less soul-crushing.

## 🧪 Example Query Playground

Try with queries like:

```sparql
SELECT * 
WHERE {
  ?book rdf:type dcm:Book .
  ?book dcm:title ?title .
  FILTER regex(?title, "SPARQL", "i")
}
ORDER BY DESC(?title)
LIMIT 5
```
