urlscraper
----------

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run

```
fastapi dev app/main.py
```

Testing

```
cd app
pip install pytest requests-mock httpx difflib
pytest
```

with watch

```
cd app
pip install pytest-watch
ptw
```
