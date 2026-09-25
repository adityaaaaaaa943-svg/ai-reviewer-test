# ai-reviewer-test

Sandbox repository used to evaluate third-party pull request review tools for
codzee.io.

> **This code is intentionally defective.** It contains planted logic bugs and
> security vulnerabilities so that automated reviewers have something to find.
> Do not deploy it, copy from it, or point it at a real database.

## Layout

| Path | What it holds |
| --- | --- |
| `codzee/config.py` | Runtime configuration and credentials |
| `codzee/db.py` | SQLite access layer |
| `codzee/auth.py` | Password hashing, JWT issuing, role checks |
| `codzee/billing.py` | Invoice, proration and overage math |
| `codzee/utils.py` | Pagination, retry, caching, rate limiting |
| `codzee/api.py` | Flask HTTP surface |
| `web/webhook-handler.js` | Express webhook receiver and admin endpoints |
| `tests/` | Unit tests |

## Running

```
pip install -r requirements.txt
python -m codzee.api
pytest -q
```

The test suite passes as written. That is part of the exercise: several tests
encode the wrong expectation.
