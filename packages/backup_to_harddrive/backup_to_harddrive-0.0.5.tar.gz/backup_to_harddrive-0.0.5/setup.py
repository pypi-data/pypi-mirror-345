# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['backup_to_harddrive']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML==6.0.2', 'platformdirs>=3.0.0,<4.0.0']

entry_points = \
{'console_scripts': ['backup_to_harddrive = backup_to_harddrive.main:main']}

setup_kwargs = {
    'name': 'backup-to-harddrive',
    'version': '0.0.5',
    'description': 'Backup home files to Harddrive on Linux',
    'long_description': '# backup_to_harddrive\n\n![latest-release](badges/latest-release.svg) ![coverage](badges/coverage.svg) ![python-version](badges/python-version.svg)\n\nThis script can typically be trigger when you want to backup files from your\nhome folder to one or more backup path (e.g harddrives.)\n\n## Installation\n\n- On Ubuntu 22: `pip install backup_to_harddrive`\n- On Ubuntu 24: `pipx install backup_to_harddrive`\n\n## Targeted platform\n\n| Platform       | Implemented | Validation |\n|----------------|--------------------| ----|\n| Linux (Ubuntu 22)         | ✅ | [ci.yaml](../.github/workflows/ci.yaml#L20)|\n| Linux (Ubuntu 24)         | ✅ | [u24-validation.yaml](../.github/workflows/u24-validation.yaml#L20) |\n| Windows        | ❌ | NA |\n| macOS          | ❌ | NA |\n\n## Features included\n\n- Exclude folders by list\n- CLI switch on and off function (useful if you want to quickly reboot\nthe computer without triggering a long backup)\n- CLI retrieval of last date of backup\n- Creation of quick restore shell script. This is useful to quickly restore\npart of a backup (for instance, only document, or music etc.) on another machine.\n\n## Configuration file\n\nCreate a config file in `~/.config/backup_to_harddrive/config.yaml`.\nFollow this example\n\n```yaml\nbackup_configurations:\n  my_backup:\n    source: /home/foo\n    list_of_harddrive:\n      - /media/foo/hd1\n      - /media/foo/hd2\n    list_of_excluded_folders:\n     - .cache\n     - /home/foo/excluded\n  backup_two:\n    source: /home/bar\n    list_of_harddrive:\n      - /mnt/bar\n    list_of_excluded_folders:\n     - .config\n     - .cache\n```\n\n## Use cases\n\nSee [USECASES.md](backup_to_harddrive/USECASES.md)\n\n## Contributing\n\nSee [CONTRIBUTING.md](CONTRIBUTING.md)\n',
    'author': 'Maxime Haselbauer',
    'author_email': 'maxime.haselbauer@googlemail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
}


setup(**setup_kwargs)
