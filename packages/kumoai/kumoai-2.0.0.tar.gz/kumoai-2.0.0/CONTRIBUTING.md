## Development

To develop the Kumo SDK, clone this repository and run

```
pip install -e .
```

to install in editable mode. This will allow you to make changes to the SDK and test them
without re-running installation.

## Documentation

The latest version of the SDK documentation is located [here](https://kumo-ai.github.io/kumo-sdk/docs/#).

Documentation is built via Sphinx. To build locally, within the `docs` directory, run

```
make clean; make html SPHINXOPTS="-W --keep-going" ; cd build/html ; python3 -m http.server ; cd -
```
