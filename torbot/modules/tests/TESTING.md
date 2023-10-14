# Testing Documentation

We are currently using [`pytest`](https://docs.pytest.org/en/latest/) as our testing framework so if you want to run the test suite. Run `pytest` from the base directory of TorBot or from the `tests` directory.
If you would like to see `print` statements show up in the console, use `pytest -s`.

### Relevant Frameworks
- [`yattag`](https://www.yattag.org/) is used to generate HTML documents.
- [`unittest.mock`](https://docs.python.org/3/library/unittest.mock.html) is used to patch the httpx Client.
