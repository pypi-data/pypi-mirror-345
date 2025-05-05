[![License](https://img.shields.io/pypi/l/QuanTables?color=blue)](https://codeberg.org/Cs137/QuanTables/src/branch/main/LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/QuanTables.svg)](https://pypi.org/project/QuanTables/)
[![PyPI Downloads](https://static.pepy.tech/badge/quantables)](https://pepy.tech/projects/quantables)


# QuanTables

A Python package for managing unit-aware quantities with uncertainties, tailored
for PySide6/Qt GUIs. It provides a collection of modules with reusable components
for retrieving and displaying `pint.Quantity`, `pint.Measurement,` or `pandas`
objects containing such quantities. The modules are designed to be used as a
toolkit rather than stand-alone components, but provide ready-to-use components,
like this *CSV Importer*:

![Example of a data import from a CSV file.](https://codeberg.org/Cs137/QuanTables/raw/branch/main/images/csv_importer.png)

__Consult the [`demo.md` file](https://codeberg.org/Cs137/QuanTables/src/branch/main/demo.md)
to learn about the components provided by this package.__

```{warning}
The project is currently under development and changes in its behaviour might be introduced.
```


## Installation

Install the latest release of QuanTables from [PyPI](https://pypi.org/project/quantables/)
via `pip`:

```sh
$ pip install quantables
```

The development version can be installed from
[the Git repository](https://codeberg.org/Cs137/QuanTables) using `pip`:

```sh
# Via https
pip install git+https://codeberg.org/Cs137/QuanTables.git

# Via ssh
pip install git+ssh://git@codeberg.org:Cs137/QuanTables.git
```


## Usage

__Examples demonstrating several use cases can be found in the
[`demo.md` file](https://codeberg.org/Cs137/QuanTables/src/branch/main/demo.md),
the corresponding modules are located in the
[examples](https://codeberg.org/Cs137/QuanTables/src/branch/main/examples)
directory of this repository.__


## Changes

All notable changes to this project are documented in the file
[`CHANGELOG.md`](https://codeberg.org/Cs137/QuanTables/src/branch/main/CHANGELOG.md).


## Contributing

Contributions to the `QuanTables` package are very welcomed. Feel free to submit a
pull request, if you would like to contribute to the project. In case you are
unfamiliar with the process, consult the
[forgejo documentation](https://forgejo.org/docs/latest/user/pull-requests-and-git-flow/)
and follow the steps using this repository instead of the `example` repository.

Create your [pull request (PR)](https://codeberg.org/Cs137/QuanTables/pulls) to
inform that you start working on a contribution. Provide a clear description
of your envisaged changes and the motivation behind them, prefix the PR's title
with ``WIP: `` until your changes are finalised.

All kind of contributions are appreciated, whether they are
bug fixes, new features, or improvements to the documentation.


## License

QuanTables is open source software released under the MIT License.
See [LICENSE](https://codeberg.org/Cs137/QuanTables/src/branch/main/LICENSE) file for details.

---

This package was created and is maintained by Christian Schreinemachers, (C) 2025.
