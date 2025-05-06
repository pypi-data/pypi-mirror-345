---
# hello-NOO Python Package

This is an example repository for a python package, for my own reference.


---
PyPI:

[![PyPi Version](https://img.shields.io/pypi/v/hello-NOO.svg)](https://pypi.org/project/hello-NOO/)
[![PyPi Version](https://img.shields.io/pypi/dm/hello-NOO.svg)](https://pypi.org/project/hello-NOO/)

GitHub: 

[![GitHub Tag](https://img.shields.io/github/v/tag/NeonOrangeOrange/hello-NOO)](https://github.com/NeonOrangeOrange/hello-NOO)
[![GitHub Downloads](https://img.shields.io/github/downloads/NeonOrangeOrange/hello-NOO/total)](https://neonorangeorange.github.io/hello-NOO/)
[![GitHub License](https://img.shields.io/github/license/NeonOrangeOrange/hello-NOO)](https://github.com/NeonOrangeOrange/hello-NOO/blob/main/LICENSE)
[![GitHub Pages Website](https://img.shields.io/website?url=http%3A//neonorangeorange.github.io/hello-NOO/)](https://neonorangeorange.github.io/hello-NOO/)

---
## Install

Not that you would want to, but you can install with 

```
pip install hello-NOO
```

Developer install

1. Clone this repository and `cd` into it.
2. Create a virtual environment: `python3 -m venv .venv`
3. Activate the virtual environment: (linux) `source .venv/bin/activate`
4. Install the package locally: (linux) `pip install -e ./[dev,docs]`


---
## Building

```bash
# Build a source distribution (stored in dist/)
python -m build --sdist

# Build a wheel (stored in dist/)
python -m build --wheel

# Run a test to check all the builds in dist
twine check dist/*
```



---
## Upload to PyPi

Once your account is set up, run

```text
twine upload --verbose --repository pypi dist/*
```



---
## Other Notes

To reset the installation

```
pip freeze --exlucde hello-NOO | xargs pip uninstall -y
pip uninstall hello-NOO
```


---
## Resources

<https://pypi.org/classifiers/>

<https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#classifiers>


