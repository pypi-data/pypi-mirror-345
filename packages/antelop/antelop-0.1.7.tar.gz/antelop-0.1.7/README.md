# Antelop
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Antelop is a complete data processing and management tool for systems neuroscientists.

It allows you to easily adopt modern data engineering infrastructures and efficient data preprocessing pipelines in a simple graphical application. It also provides a host of visualisation tools and a standard library of common analysis functions, as well as a framework for you to write your own fully reproducable analysis functions.

At present, Antelop supports electrophysiology, calcium imaging, and behavioural data.

To learn more about Antelop, please read our [documentation](https://antelop.readthedocs.io/en/latest/).

## Installation

The terminal interface of Antelop can be installed via pip. Note that Antelop requires python 3.9:

```python
pip install antelop
```

To minimise installation time, a number of features are offered as optional dependencies.

```python
pip install antelop[gui] # For our graphical user interface

pip install antelop[gui, phy] # For electrophysiology manual curation

pip install antelop[gui, dlc] # For deeplabcut subject pose estimation

pip install antelop[full] # For everything (longer installation time)
```

Conda users can get started as follows:

```python
conda create -n antelop python=3.9
conda activate antelop
pip install antelop
```

## Usage

To run the gui:

```python
antelop
```

![Antelop UI](src/antelop/resources/spiketrain.png)

*Antelop user interface*

You will be prompted for your database login credentials.

To run the IPython console interface:

```python
antelop-python
```

To use Antelop in a script, set the `$DB_USER` and `$DB_PASS` environment variables, then import all the tables and analysis functions as follows:

```python
from antelop.load_connection import *
```

## Authors

Developed by [Rory Bedford](https://www.github.com/rory-bedford/) in the [Tripodi Lab](https://www.github.com/marcotripodi/).

## License

MIT License

Copyright (c) 2024 Rory Bedford

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.