# Contributing guide

Scanpy provides extensive [developer documentation][scanpy developer guide], most of which applies to this repo, too.
This document will not reproduce the entire content from there. Instead, it aims at summarizing the most important
information to get you started on contributing.

We assume that you are already familiar with git and with making pull requests on GitHub. If not, please refer
to the [scanpy developer guide][].

## Writing tests

```{note}
Remember to first install the package with `pip install '-e[dev,test]'`
```

This package uses the [pytest][] for automated testing. Please [write tests][scanpy-test-docs] for every function added
to the package.

Most IDEs integrate with pytest and provide a GUI to run tests. Alternatively, you can run all tests from the
command line by executing

```bash
pytest
```

in the root of the repository. Continuous integration will automatically run the tests on all pull requests.

[scanpy-test-docs]: https://scanpy.readthedocs.io/en/latest/dev/testing.html#writing-tests

## Publishing a release

### Updating the version number

Before making a release, you need to update the version number. Please adhere to [Semantic Versioning][semver], in brief

> Given a version number MAJOR.MINOR.PATCH, increment the:
>
> 1.  MAJOR version when you make incompatible API changes,
> 2.  MINOR version when you add functionality in a backwards compatible manner, and
> 3.  PATCH version when you make backwards compatible bug fixes.
>
> Additional labels for pre-release and build metadata are available as extensions to the MAJOR.MINOR.PATCH format.

We use [bump2version][] to automatically update the version number in all places and automatically create a git tag.
Run one of the following commands in the root of the repository

```bash
bump2version patch
bump2version minor
bump2version major
```

Once you are done, run

```
git push --tags
```

to publish the created tag on GitHub.

[bump2version]: https://github.com/c4urself/bump2version

## Writing documentation

Please write documentation for new or changed features and use-cases. This project uses [sphinx][] with the following features:

-   the [myst][] extension allows to write documentation in markdown/Markedly Structured Text
-   [Numpy-style docstrings][numpydoc] (through the [napoloen][numpydoc-napoleon] extension).
-   Jupyter notebooks as tutorials through [myst-nb][] (See [Tutorials with myst-nb](#tutorials-with-myst-nb-and-jupyter-notebooks))
-   [Sphinx autodoc typehints][], to automatically reference annotated input and output types

See the [scanpy developer docs](https://scanpy.readthedocs.io/en/latest/dev/documentation.html) for more information
on how to write documentation.

### Tutorials with myst-nb and jupyter notebooks

The documentation is set-up to render jupyter notebooks stored in the `docs/notebooks` directory using [myst-nb][].
Currently, only notebooks in `.ipynb` format are supported that will be included with both their input and output cells.
It is your reponsibility to update and re-run the notebook whenever necessary.

If you are interested in automatically running notebooks as part of the continuous integration, please check
out [this feature request](https://github.com/scverse/cookiecutter-scverse/issues/40) in the `cookiecutter-scverse`
repository.

#### Hints

-   If you refer to objects from other packages, please add an entry to `intersphinx_mapping` in `docs/conf.py`. Only
    if you do so can sphinx automatically create a link to the external documentation.
-   If building the documentation fails because of a missing link that is outside your control, you can add an entry to
    the `nitpick_ignore` list in `docs/conf.py`

#### Building the docs locally

```bash
cd docs
make html
open _build/html/index.html
```

<!-- Links -->

[scanpy developer guide]: https://scanpy.readthedocs.io/en/latest/dev/index.html
[cookiecutter-scverse-instance]: https://cookiecutter-scverse-instance.readthedocs.io/en/latest/template_usage.html
[github quickstart guide]: https://docs.github.com/en/get-started/quickstart/create-a-repo?tool=webui
[codecov]: https://about.codecov.io/sign-up/
[codecov docs]: https://docs.codecov.com/docs
[codecov bot]: https://docs.codecov.com/docs/team-bot
[codecov app]: https://github.com/apps/codecov
[pre-commit.ci]: https://pre-commit.ci/
[readthedocs.org]: https://readthedocs.org/
[myst-nb]: https://myst-nb.readthedocs.io/en/latest/
[jupytext]: https://jupytext.readthedocs.io/en/latest/
[pre-commit]: https://pre-commit.com/
[anndata]: https://github.com/scverse/anndata
[mudata]: https://github.com/scverse/mudata
[pytest]: https://docs.pytest.org/
[semver]: https://semver.org/
[sphinx]: https://www.sphinx-doc.org/en/master/
[myst]: https://myst-parser.readthedocs.io/en/latest/intro.html
[numpydoc-napoleon]: https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
[numpydoc]: https://numpydoc.readthedocs.io/en/latest/format.html
[sphinx autodoc typehints]: https://github.com/tox-dev/sphinx-autodoc-typehints
[pypi]: https://pypi.org/
