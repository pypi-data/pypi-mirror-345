# simple-state-tracker

A minimal, file-backed, type-safe state tracker using Pydantic models — ideal for scripts, scrapers, ETL pipelines, and resumable workflows.


![PyPI](https://img.shields.io/pypi/v/simple-state-tracker)
![Python](https://img.shields.io/pypi/pyversions/simple-state-tracker)
![License](https://img.shields.io/github/license/yourname/simple-state-tracker)


## Features

- 🧠 Strong typing with `pydantic` models
- 💾 Transparent JSON persistence
- 🧰 Simple `.get()`, `.set()`, `.edit()` API
- ✅ Schema validation and strict key control
- 🪶 Lightweight — no databases, no DAGs, no dependencies beyond `pydantic`


## Installation

```bash
pip install simple-state-tracker
```

---

### Example

```markdown
## Quick Start

```python
from simple_state_tracker import SimpleStateTracker, KeyModel, DataModel

class ScrapeKey(KeyModel):
    county: str
    municipality: str
    year: int

class ScrapeState(DataModel):
    scraped: bool = False
    scrape_error: str | None = None
    processed: bool = False
    process_error: str | None = None

tracker = SimpleStateTracker(ScrapeKey, ScrapeState, path="tracker.json")

key = ScrapeKey(county="DAUPHIN", municipality="HARRISBURG", year=2022)

with tracker.edit(key) as state:
    state.scraped = True
    state.scrape_error = None

tracker.save()

```


---

### Use Cases

- Track which URLs, files, or locations have been processed
- Resume scraping jobs or ETL pipelines
- Store structured state across CLI or batch job invocations
- Replace ad-hoc JSON or YAML logs with something type-safe and self-validating

## API Overview

### `SimpleStateTracker(key_model, data_model, path)`
Creates a new tracker instance.

- `get(key)` → returns the data model (or `None`)
- `set(key, value)` → manually sets a value
- `edit(key)` → yields a context-managed editable state
- `save()` → writes the cache to disk
- `load()` → reads from disk
- `all()` → returns a shallow copy of all state


