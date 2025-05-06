# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['redcap', 'redcap.methods']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.20,<3.0', 'semantic-version>=2.8.5,<3.0.0']

extras_require = \
{'data-science': ['pandas>=2.0.0,<3.0.0']}

setup_kwargs = {
    'name': 'pycap',
    'version': '2.7.0',
    'description': 'PyCap: Python interface to REDCap',
    'long_description': '# PyCap\n\n[![CI](https://github.com/redcap-tools/PyCap/actions/workflows/ci.yml/badge.svg)](https://github.com/redcap-tools/PyCap/actions/workflows/ci.yml)\n[![Codecov](https://codecov.io/gh/redcap-tools/PyCap/branch/master/graph/badge.svg?token=IRgcPzANxU)](https://codecov.io/gh/redcap-tools/PyCap)\n[![PyPI version](https://badge.fury.io/py/pycap.svg)](https://badge.fury.io/py/pycap)\n[![black](https://img.shields.io/badge/code%20style-black-black)](https://pypi.org/project/black/)\n\n## Intro\n\n`PyCap` is a python module exposing the REDCap API through some helpful abstractions. Information about the REDCap project can be found at https://project-redcap.org/.\n\nAvailable under the MIT license.\n\n## Installation\n\nInstall the latest version with [`pip`](https://pypi.python.org/pypi/pip)\n\n```sh\n$ pip install PyCap\n```\n\nIf you want to load REDCap data into [`pandas`](https://pandas.pydata.org/) dataframes, this will make sure you have `pandas` installed\n\n```sh\n$ pip install PyCap[all]\n```\n\nTo install the bleeding edge version from the github repo, use the following\n\n```sh\n$ pip install -e git+https://github.com/redcap-tools/PyCap.git#egg=PyCap\n```\n\n## Documentation\n\nCanonical documentation and usage examples can be found [here](https://redcap-tools.github.io/PyCap/).\n\n## Features\n\nCurrently, these API calls are available:\n\n### Export\n\n* Arms\n* Data Access Groups\n* Events\n* Field names\n* Instruments\n* Instrument-event mapping\n* File\n* File Repository\n* Logging\n* Metadata\n* Project Info\n* PDF of instruments\n* Records\n* Repeating instruments and events\n* Report\n* Surveys\n* Users\n* User-DAG assignment\n* User Roles\n* User-Role assignment\n* Version\n\n### Import\n\n* Arms\n* Data Access Groups\n* Events\n* File\n* File Repository\n* Instrument-event mapping\n* Metadata\n* Records\n* Repeating instruments and events\n* Users\n* User-DAG assignment\n* User Roles\n* User-Role assignment\n\n### Delete\n\n* Arms\n* Data Access Groups\n* Events\n* File\n* File Repository\n* Records\n* Users\n* User Roles\n\n### Other\n\n* Generate next record name\n* Switch data access group\n\n## Citing\n\nIf you use PyCap in your research, please consider citing the software:\n\n>    Burns, S. S., Browne, A., Davis, G. N., Rimrodt, S. L., & Cutting, L. E. PyCap (Version 1.0) [Computer Software].\n>    Nashville, TN: Vanderbilt University and Philadelphia, PA: Childrens Hospital of Philadelphia.\n>    Available from https://github.com/redcap-tools/PyCap. doi:10.5281/zenodo.9917\n',
    'author': 'Scott Burns',
    'author_email': 'scott.s.burns@gmail.com',
    'maintainer': 'Paul Wildenhain',
    'maintainer_email': 'pwildenhain@gmail.com',
    'url': 'https://github.com/redcap-tools/PyCap',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
