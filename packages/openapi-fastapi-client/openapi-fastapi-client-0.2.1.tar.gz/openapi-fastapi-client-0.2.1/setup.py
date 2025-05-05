# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['openapi_fastapi_client']

package_data = \
{'': ['*']}

install_requires = \
['black>=24.3.0,<25.0.0',
 'isort>=6.0.1,<7.0.0',
 'pydantic>=2.4.0,<3.0.0',
 'pyyaml>=6.0.2,<7.0.0',
 'typer>=0.15.3,<0.16.0',
 'typing-extensions>=4.13.2,<5.0.0']

entry_points = \
{'console_scripts': ['openapi-fastapi-client = '
                     'openapi_fastapi_client.main:app']}

setup_kwargs = {
    'name': 'openapi-fastapi-client',
    'version': '0.2.1',
    'description': 'A tool to autogenerate FastApi Clients from given openapi.yaml.',
    'long_description': '[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)\n![Python application](https://github.com/FelixTheC/openapi-fastapi-client/workflows/Python%20application/badge.svg)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)\n\n\n# Openapi yaml file to FastApi Client\nA commandline tool to generate Api `functions` and their required `pydantic Model` Schema from an `openapi.yaml` of version 3\n\n## Installation\n```shell\npip install openapi-fastapi-client\n```\n\n## Usage\n```shell\nopenapi-fastapi-client ./openapi.yaml ./my-client\n```\n```shell\nopenapi-fastapi-client ./openapi.yaml ./my-client --async\n```\n- this will generate under the folder `my-client` following files\n  - `__init__.py` if not exists\n  - `api.py` here are all function calls to the external api\n  - `schema.py` here are all pydantic Models\n  \n\n## Arguments\n- `OPENAPI_FILE  [required]`\n- `OUTPUT_PATH   [required]`\n\n## Options\n- `--sync`  All requests to the client are synchronous.  _default_\n- `--async` All requests to the client are asynchronous with __aiohttp__.\n\n## Help\n```shell\nopenapi-fastapi-client --help\n```\n\n![](openapi-fastapi-client_long.gif)\n',
    'author': 'FelixTheC',
    'author_email': 'felixeisenmenger@gmx.net',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/FelixTheC/openapi-fastapi-client',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4',
}


setup(**setup_kwargs)
