#!/usr/bin/python
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ansible.module_utils.basic import *

import os

from dciclient.v1.api import context as dci_context
from dciclient.v1.api import job as dci_job
from dciclient.v1.api import file as dci_file
from dciclient.v1.api import component as dci_component

try:
    import requests
except ImportError:
    requests_found = False
else:
    requests_found = True


DOCUMENTATION = '''
---
module: dci_component
short_description: An ansible module to schedule a new job with DCI
version_added: 2.2
options:
  login:
    required: false
    description: User's DCI login
  password:
    required: false
    description: User's DCI password
  url:
    required: false
    description: DCI Control Server URL
  component_id:
    required: true
    description: ID of the component to retrieve
  dest:
    required: true
    description: Path where to drop the retrieved component
'''

EXAMPLES = '''
- name: retrieve component
  dci_component:
    dest: /srv/dci/components/{{ component_id }}
    component_id: {{ component_id }}
'''

# TODO
RETURN = '''
'''


def get_details(module):
    """Method that retrieves the appropriate credentials. """

    login_list = [module.params['login'], os.getenv('DCI_LOGIN')]
    login = next((item for item in login_list if item is not None), None)

    password_list = [module.params['password'], os.getenv('DCI_PASSWORD')]
    password = next((item for item in password_list if item is not None), None)

    url_list = [module.params['url'], os.getenv('DCI_CS_URL')]
    url = next((item for item in url_list if item is not None), 'https://api.distributed-ci.io')

    return login, password, url


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'absent'], type='str'),
            login=dict(required=False, type='str'),
            password=dict(required=False, type='str'),
            component_id=dict(type='str'),
            dest=dict(type='str'),
            url=dict(required=False, type='str'),
        ),
    )

    if not requests_found:
        module.fail_json(msg='The python requests module is required')

    login, password, url = get_details(module)
    if not login or not password:
        module.fail_json(msg='login and/or password have not been specified')

    ctx = dci_context.build_dci_context(url, login, password, 'ansible')

    component_file = dci_component.file_list(ctx, module.params['component_id']).json()['component_files'][0]
    dci_component.file_download(ctx, module.params['component_id'], component_file['id'], module.params['dest'])

    module.exit_json(changed=True)


if __name__ == '__main__':
    main()
