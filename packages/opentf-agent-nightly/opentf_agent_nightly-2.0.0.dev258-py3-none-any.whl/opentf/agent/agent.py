# Copyright (c) 2022 Henix, Henix.fr
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""OpenTestFactory Agent"""

from typing import Any, Dict, List, Optional, Union

import argparse
import asyncio
import logging
import platform
import subprocess
import sys
import os
import re

try:
    from importlib.metadata import version

    VERSION = version('opentf-agent')
except ModuleNotFoundError:
    try:
        import pkg_resources

        VERSION = pkg_resources.get_distribution('opentf-agent').version
    except:
        VERSION = '2.0.0'

from time import sleep, time
from urllib.parse import urlparse

import requests


REGISTRATION = {
    'apiVersion': 'opentestfactory.org/v1alpha1',
    'kind': 'AgentRegistration',
    'metadata': {'name': 'test agent', 'namespaces': 'default', 'version': VERSION},
    'spec': {
        'tags': [],
        'encoding': 'utf-8',
        'script_path': '',
    },
}

DEFAULT_POLLING_DELAY = 5
DEFAULT_PORT = 24368
DEFAULT_RETRY = 5

NOTIFY_OUTPUT = 5  # async logs posting interval (s)

REGISTRATION_URL_TEMPLATE = '{server}/agents'
ENDPOINT_TEMPLATE = '{server}/agents/{agent_id}'
FILE_URL_TEMPLATE = '{server}/agents/{agent_id}/files/{file_id}'

STATUS_REGISTRATION_FAILED = 2
STATUS_KEYBOARD_INTERRUPT = 0
STATUS_EXCEPTION = 1

BAD_OSTAG_TEMPLATE = 'You can only use the "%s" tag if you are launching the agent on a %s platform (the current platform is %s).'

DOMAINNAME_PATTERN = r'^[a-zA-Z]+([0-9A-Za-z-]*[0-9a-zA-Z])?$'  # rfc 1035

########################################################################
# Helpers


def download_file(
    url: str,
    local_filename: str,
    root,
    headers: Optional[Dict[str, str]],
    verify: Union[bool, str],
):
    """Download file to local_filename."""
    response = requests.get(url, stream=True, headers=headers, verify=verify)
    if root:
        base = REGISTRATION['spec']['workspace_dir']
    else:
        base = REGISTRATION['spec']['script_path']
    with open(os.path.join(base, local_filename), 'wb') as file:
        for chunk in response.iter_content(chunk_size=128):
            file.write(chunk)


def post(
    endpoint: str,
    json: Dict[str, Any],
    headers: Optional[Dict[str, str]],
    retry: int,
    delay: int,
    verify: Union[bool, str],
):
    """Query endpoint, retrying if connection failed.

    If `retry` is `0`, retry forever.
    """
    count = retry
    raised = None
    while True:
        try:
            return requests.post(endpoint, json=json, headers=headers, verify=verify)
        except Exception as err:
            raised = err
            if count <= 0 and retry != 0:
                break
        logging.info('Could not reach %s, retrying.', endpoint)
        if isinstance(raised, requests.exceptions.ProxyError):
            logging.debug('(A proxy error occurred: %s.)', str(raised))
        elif isinstance(raised, requests.exceptions.SSLError):
            logging.debug('(A SSL error occurred: %s.)', str(raised))
        elif isinstance(raised, requests.exceptions.ConnectionError):
            logging.debug('(A connection error occurred: %s.)', str(raised))
        count -= 1
        sleep(delay)

    raise raised or Exception(f'Could not reach {endpoint}, aborting.')


def abort(*args):
    """Log a message with severity ERROR and exit with code 2."""
    logging.error(*args)
    sys.exit(2)


########################################################################
# Handlers


def _handle_registration_error(err: Exception, registration_url: str) -> int:
    if isinstance(err, requests.exceptions.ProxyError):
        logging.error('A proxy error occurred: %s.', str(err))
        logging.error(
            '(You can use the HTTP_PROXY or the HTTPS_PROXY environment variables to set a proxy.)'
        )
    elif isinstance(err, requests.exceptions.SSLError):
        logging.error('A SSL error occurred: %s.', str(err))
        logging.error(
            '(You can use the "--verify false|path_to_pem_file" command line option to adjust SSL handling.)'
        )
    elif isinstance(err, requests.exceptions.ConnectionError):
        logging.error(
            'Could not reach the orchestrator (%s).  Is the orchestrator running?',
            str(err),
        )
        logging.error('(Attempting to reach %s)', registration_url)
    else:
        logging.error('Failed to register to server: %s.', err)
    return STATUS_REGISTRATION_FAILED


def register_and_handle(
    args, headers: Optional[Dict[str, str]], verify: Union[bool, str]
) -> int:
    """Register to host and process commands.

    Returns 0 if interrupted by keyboard interrupt, 2 if registration
    failed and 1 if something else occurred.
    """
    stripped_prefix = args.path_prefix.strip('/')
    server = f'{args.host.rstrip("/")}:{args.port}/{stripped_prefix}'.strip('/')
    registration_url = REGISTRATION_URL_TEMPLATE.format(server=server)
    logging.info('Registering agent on %s.', registration_url)
    try:
        if 'workspace_dir' in REGISTRATION['spec']:
            del REGISTRATION['spec']['workspace_dir']
        response = post(
            registration_url,
            json=REGISTRATION,
            headers=headers,
            retry=args.retry,
            delay=args.polling_delay,
            verify=verify,
        )
        if response.status_code in (401, 403):
            logging.error(response.json()['message'])
            return STATUS_REGISTRATION_FAILED
    except Exception as err:
        return _handle_registration_error(err, registration_url)

    try:
        REGISTRATION['spec']['workspace_dir'] = (
            args.workspace_dir.rstrip(os.sep) + os.sep
        )
        details = response.json()['details']
        uuid = details['uuid']
        if 'version' in details:
            logging.info('OpenTestFactory Orchestrator version %s.', details['version'])
        logging.info('Agent ready, will poll every %d seconds.', args.polling_delay)
    except Exception as err:
        logging.info('Registration cancelled.')
        logging.debug('Exception: %s.', str(err))
        logging.debug('Server response: %s.', response.text)
        return STATUS_REGISTRATION_FAILED

    endpoint = ENDPOINT_TEMPLATE.format(server=server, agent_id=uuid)
    try:
        while True:
            try:
                response = requests.get(endpoint, headers=headers, verify=verify)
            except requests.ConnectionError as err:
                logging.error(
                    'An exception occurred while polling: %s.  Retrying.', err
                )
                sleep(args.polling_delay)
                continue

            if response.status_code == 204:
                sleep(args.polling_delay)
                continue

            try:
                body = response.json()
            except Exception as err:
                logging.error('Command is not JSON: %s.', err)
                logging.debug('Command:\n%s.', str(response.text))
                continue

            if 'details' not in body:
                logging.error('Invalid command, .details not found.')
                logging.debug('Command:\n%s', str(body))
                continue
            kind = body['details'].get('kind')
            if kind not in KINDS_HANDLERS:
                logging.error('Unexpected command kind %s, ignoring.', kind)
                logging.debug('Command:\n%s', str(body))
                continue

            KINDS_HANDLERS[kind](uuid, body['details'], server, headers, verify)
    except Exception as err:
        logging.error('An exception occurred: %s.', err)
        return STATUS_EXCEPTION
    except KeyboardInterrupt:
        logging.info('^C')
        return STATUS_KEYBOARD_INTERRUPT
    finally:
        _deregister_if_possible(endpoint, headers, verify)


def _deregister_if_possible(
    endpoint: str, headers: Optional[Dict[str, Any]], verify: Union[bool, str]
):
    try:
        requests.delete(endpoint, headers=headers, verify=verify)
        logging.info('Agent successfully de-registered.')
    except Exception as err:
        logging.error('Could not de-register agent: %s.', err)


def process_run(
    agent_id: str,
    command: Dict[str, Any],
    server: str,
    headers: Optional[Dict[str, str]],
    verify: Union[bool, str],
) -> None:
    """Process run command."""
    with open(
        os.path.join(REGISTRATION['spec']['script_path'], command['filename']), 'wb'
    ) as file:
        file.write(command['content'].encode())
    KINDS_HANDLERS['exec'](agent_id, command, server, headers, verify)


def _get_opentf_variables(command: Dict[str, Any]) -> Optional[List[str]]:
    variables = None
    if (var_path := command.get('variables_path')) and '_-2.' not in command['command']:
        try:
            with open(var_path, 'r') as vf:
                variables = vf.read().splitlines()
        except FileNotFoundError as err:
            logging.warning(str(err))
    return variables


def process_exec(
    agent_id: str,
    command: Dict[str, Any],
    server: str,
    headers: Optional[Dict[str, str]],
    verify: Union[bool, str],
):
    """Process exec command."""
    try:
        instruction = command['command']
        logging.debug('Will run %s', instruction)
        process = subprocess.run(
            command['command'],
            cwd=REGISTRATION['spec']['workspace_dir'],
            shell=True,
            capture_output=True,
            check=False,
        )
        sent = False
        while not sent:
            try:
                result = requests.post(
                    ENDPOINT_TEMPLATE.format(agent_id=agent_id, server=server),
                    json={
                        'stdout': str(
                            process.stdout,
                            encoding=REGISTRATION['spec']['encoding'],
                            errors='backslashreplace',
                        ).splitlines(),
                        'stderr': str(
                            process.stderr,
                            encoding=REGISTRATION['spec']['encoding'],
                            errors='backslashreplace',
                        ).splitlines(),
                        'variables': _get_opentf_variables(command),
                        'exit_status': process.returncode,
                    },
                    headers=headers,
                    verify=verify,
                )
                sent = True
                if result.status_code != 200:
                    logging.error(
                        'Failed to push command result: %d.', result.status_code
                    )
            except Exception as err:
                logging.error('Failed to push command result: %s.  Retrying.', err)
    except Exception as err:
        logging.error('Failed to run command: %s.', err)


async def async_process_exec(
    agent_id: str,
    command: Dict[str, Any],
    server: str,
    headers: Optional[Dict[str, str]],
    verify: Union[bool, str],
):
    """Asynchronous process exec command with cancel support."""
    try:
        instruction = command['command']
        logging.debug('Will run %s', instruction)

        process = await asyncio.create_subprocess_shell(
            instruction,
            cwd=REGISTRATION['spec']['workspace_dir'],
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout_lines = []
        stderr_lines = []

        async def read_stream(stream, stream_name: str, line_collector: List[str]):
            start = time()
            while True:
                line = await stream.readline()
                if not line:
                    break
                decoded_line = line.decode().strip()
                line_collector.append(decoded_line)
                logging.info(f"[{stream_name}] {decoded_line}")
                if time() - start >= NOTIFY_OUTPUT:
                    try:
                        logging.debug('Sending command logs to the agentchannel.')
                        result = requests.post(
                            ENDPOINT_TEMPLATE.format(agent_id=agent_id, server=server),
                            json={stream_name.lower(): line_collector},
                            headers=headers,
                            verify=verify,
                        )
                        if result.status_code != 200:
                            logging.error(
                                'Failed to push command logs: (%d) %s. Retrying.',
                                result.status_code,
                                result.text,
                            )
                        else:
                            line_collector.clear()
                            start = time()
                    except Exception as err:
                        logging.error(
                            'Error while retrieving command logs: %s.', str(err)
                        )

        async def check_for_cancel():
            """Periodically query the server to check for a cancel command."""
            while True:
                await asyncio.sleep(1)
                try:
                    response = requests.get(
                        ENDPOINT_TEMPLATE.format(agent_id=agent_id, server=server),
                        headers=headers,
                        verify=verify,
                    )
                    if (
                        response.status_code == 200
                        and response.json().get('details', {}).get('kind') == 'cancel'
                    ):
                        process.terminate()
                        logging.info("Execution cancelled by server.")
                        break
                except Exception as err:
                    logging.error('Error while checking for cancel command: %s', err)

        stdout_task = asyncio.create_task(
            read_stream(process.stdout, "STDOUT", stdout_lines)
        )
        stderr_task = asyncio.create_task(
            read_stream(process.stderr, "STDERR", stderr_lines)
        )
        cancel_task = asyncio.create_task(check_for_cancel())

        await asyncio.wait(
            [stdout_task, stderr_task, cancel_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        if process.returncode is None:
            await process.wait()

        returncode = process.returncode

        result_payload = {
            'stdout': stdout_lines,
            'stderr': stderr_lines,
            'exit_status': returncode,
        }

        sent = False
        while not sent:
            try:
                result = requests.post(
                    ENDPOINT_TEMPLATE.format(agent_id=agent_id, server=server),
                    json=result_payload,
                    headers=headers,
                    verify=verify,
                )
                sent = True
                if result.status_code != 200:
                    logging.error(
                        'Failed to push command result: %d.', result.status_code
                    )
            except Exception as err:
                logging.error('Failed to push command result: %s.  Retrying.', err)
    except Exception as err:
        logging.error('Failed to run command: %s.', err)


def process_put(
    agent_id: str,
    command: Dict[str, Any],
    server: str,
    headers: Optional[Dict[str, str]],
    verify: Union[bool, str],
):
    """Process put command.

    From orchestrator to execution environment.

    `command` format:

    - file_id: a string
    - path: a non-empty string
    - root: a possibly empty string

    If `root` is empty, copy to script directory.  If not empty,
    relative to the workspace directory.

    If the copy does not succeed, POST an error message.
    """
    if 'path' not in command:
        logging.error('No path specified in command.')
        return
    if 'file_id' not in command:
        logging.error('No file_id specified in command.')
        return
    try:
        download_file(
            FILE_URL_TEMPLATE.format(
                agent_id=agent_id, file_id=command['file_id'], server=server
            ),
            command['path'],
            command.get('root'),
            headers,
            verify=verify,
        )
        logging.debug('File successfully downloaded to %s.', command['path'])
    except Exception as err:
        result = requests.post(
            ENDPOINT_TEMPLATE.format(agent_id=agent_id, server=server),
            json={
                'details': {
                    'error': f'Failed to download file {command["file_id"]} to {command["path"]}: {err}.'
                }
            },
            headers=headers,
            verify=verify,
        )
        logging.error('An error occurred while downloading file: %s.', err)
        if result.status_code != 200:
            logging.debug(
                '(Failed to notify the orchestrator.  Got a %d status code.)',
                result.status_code,
            )


def process_get(
    agent_id: str,
    command: Dict[str, Any],
    server: str,
    headers: Optional[Dict[str, str]],
    verify: Union[bool, str],
):
    """Process get command.

    From execution environment to orchestrator.

    `command` format:

    - file_id: a string
    - path: a string

    If the copy does not succeed, POST an error message.
    """
    if 'path' not in command:
        logging.error('No path specified in command.')
        return
    if 'file_id' not in command:
        logging.error('No file_id specified in command.')
        return

    try:
        with open(command['path'], 'rb') as file:
            requests.post(
                FILE_URL_TEMPLATE.format(
                    agent_id=agent_id, file_id=command['file_id'], server=server
                ),
                data=file,
                headers=headers,
                verify=verify,
            )
    except OSError as err:
        file_path = command['path']
        result = requests.post(
            ENDPOINT_TEMPLATE.format(agent_id=agent_id, server=server),
            json={'details': {'error': f'Failed to fetch file {file_path}: {err}.'}},
            headers=headers,
            verify=verify,
        )
        if result.status_code != 200:
            logging.error('Failed to push command result: %d.', result.status_code)


KINDS_HANDLERS = {
    'exec': process_exec,
    'put': process_put,
    'get': process_get,
    'run': process_run,
}


########################################################################
# Main


def _parse_args():
    parser = argparse.ArgumentParser(description='OpenTestFactory Agent')
    parser.add_argument(
        '--version',
        action='version',
        version=f'OpenTestFactory Agent version {VERSION}.',
    )
    parser.add_argument(
        '--tags',
        help='a comma-separated list of tags (e.g., windows,robotframework)',
        required=True,
    )
    parser.add_argument(
        '--host',
        help='target host with protocol (e.g., https://example.local)',
        required=True,
    )
    parser.add_argument(
        '--port',
        help=f'target port (defaults to {DEFAULT_PORT})',
        default=DEFAULT_PORT,
        type=int,
    )
    parser.add_argument(
        '--path_prefix',
        help='target context path (defaults to no context path)',
        default='',
    )
    parser.add_argument('--token', help='token')
    parser.add_argument(
        '--encoding',
        help='encoding on the console side (defaults to utf-8)',
        default='utf-8',
    )
    parser.add_argument(
        '--script_path',
        help='where to put generated script (defaults to current directory)',
        default=os.getcwd(),
    )
    parser.add_argument(
        '--workspace_dir',
        help='where to put workspaces (defaults to current directory)',
        default='.',
    )
    parser.add_argument(
        '--name',
        help='agent name (defaults to "test agent")',
    )
    parser.add_argument(
        '--namespaces',
        '--namespace',
        help='namespace(s) this agent is accessible from (defaults to "default")',
        default='default',
    )
    parser.add_argument(
        '--polling_delay',
        help=f'polling delay in seconds (defaults to {DEFAULT_POLLING_DELAY})',
        default=DEFAULT_POLLING_DELAY,
        type=int,
    )
    parser.add_argument(
        '--liveness_probe',
        help='liveness probe in seconds (defaults to 300 seconds)',
        type=int,
    )
    parser.add_argument(
        '--retry',
        help=f'how many times to try joining host (defaults to {DEFAULT_RETRY}, 0 = try forever)',
        default=DEFAULT_RETRY,
        type=int,
    )
    parser.add_argument(
        '--verify',
        help='whether to verify the SSL connection (defaults to true, true = enabled, false = disabled, file.pem = server certificate plus all intermediate certificates)',
        default='true',
    )
    parser.add_argument(
        '--async',
        help='whether to run commands asynchronously.',
        action='store_true',
        dest='use_async',
    )
    parser.add_argument(
        '--debug', help='whether to log debug information.', action='store_true'
    )

    return parser.parse_args()


def _read_sslconfiguration(args):
    """Check SSL verification option.

    Exits with error code 2 if the verification option (--verify) is not
    valid.

    It must be `true`, `false`, or an existing file path.

    # Returned value

    The verify option (a boolean of a file path).
    """
    if args.verify:
        if args.verify.upper() == 'TRUE':
            verify = True
        elif args.verify.upper() == 'FALSE':
            verify = False
        else:
            if not os.path.isfile(args.verify):
                abort(
                    'The certificates file %s does not exist or is not readable.  '
                    'Use "--verify false" if you want to disable certificates checks.  '
                    'Use "--verify certificates.pem" to use a specific verification chain '
                    '(it must include the server certificate and all intermediate '
                    'certificates too).',
                    args.verify,
                )
            verify = args.verify
    else:
        verify = True

    logging.debug(
        'Default certificate bundle is %s.', requests.utils.DEFAULT_CA_BUNDLE_PATH
    )

    if verify is False:
        logging.debug('Certificate validation is disabled.')
    elif verify is True:
        logging.debug('Certificate validation is enabled.')
    else:
        logging.debug(
            'Certificate validation is enabled using certificates in %s.', verify
        )

    for var in ('http_proxy', 'https_proxy', 'no_proxy', 'CURL_CA_BUNDLE'):
        val = os.environ.get(var, os.environ.get(var.upper()))
        if val is not None:
            logging.debug('Environment variable %s is "%s".', var, val)
        else:
            logging.debug('Environment variable %s is not set.', var)

    return verify


def _ensure_tags_valid(tags: List[str]):
    """Check tags."""
    if len(set(tags) & {'linux', 'windows', 'macos'}) != 1:
        abort('tags must include one and only one of "linux", "windows", "macos".')
    if 'inception' in tags:
        abort('"inception" cannot be used as a tag name.')
    system = platform.system()
    if 'linux' in tags and system != 'Linux':
        abort(BAD_OSTAG_TEMPLATE, 'linux', 'Linux', system)
    if 'windows' in tags and system != 'Windows':
        abort(BAD_OSTAG_TEMPLATE, 'windows', 'Windows', system)
    if 'macos' in tags and system != 'Darwin':
        abort(BAD_OSTAG_TEMPLATE, 'macos', 'MacOS (Darwin)', system)


def _ensure_namespaces_valid(namespaces: str):
    namespaces = namespaces.strip()
    if not namespaces:
        abort('Namespaces cannot be empty.')
    if namespaces == '*':
        return
    if '*' in namespaces:
        abort('Namespaces is either "*" or a comma-separated list of namespaces.')
    for namespace in namespaces.split(','):
        if not re.match(DOMAINNAME_PATTERN, namespace):
            logging.error(
                'A namespace name must start with a letter and end with a letter or a digit.  It may contain hypens.'
            )
            abort('The specified namespace "%s" is not a valid name.', namespace)


def _prepare_registration(args):
    """Fill REGISTRATION manifest.

    Exits with error code 2 if specified tags are invalid.
    """
    if args.tags:
        tags = args.tags.split(',')
        _ensure_tags_valid(tags)
        REGISTRATION['spec']['tags'] = args.tags.split(',')
    if args.encoding:
        REGISTRATION['spec']['encoding'] = args.encoding
    if args.encoding == 'utf-8':
        if 'windows' in REGISTRATION['spec']['tags']:
            from ctypes import windll

            if windll.kernel32.GetConsoleOutputCP() != 65001:
                logging.warning(
                    'No encoding specified but console encoding is not 65001 (utf-8).'
                )
        else:
            if not os.environ.get('LANG', '').lower().endswith('utf-8'):
                logging.warning(
                    'No encoding specified but LANG does not ends with ".UTF-8".'
                )
    if args.script_path:
        REGISTRATION['spec']['script_path'] = args.script_path.rstrip(os.sep)
    if args.name:
        REGISTRATION['metadata']['name'] = args.name
    if args.namespaces:
        _ensure_namespaces_valid(args.namespaces)
        REGISTRATION['metadata']['namespaces'] = args.namespaces
    if args.liveness_probe:
        REGISTRATION['spec']['liveness_probe'] = args.liveness_probe


def main():
    """Start agent."""
    args = _parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    host = urlparse(args.host)
    if not host.scheme:
        abort('--host must specify a scheme ("https:" or "http:", typically).')
    if not host.netloc:
        abort('--host must specify a hostname or IP address.')

    logging.info('OpenTestFactory Agent version %s.', VERSION)
    if args.debug:
        logging.info('Running on Python %s.', sys.version)

    verify = _read_sslconfiguration(args)

    _prepare_registration(args)

    if args.token:
        headers = {'Authorization': f'Bearer {args.token}'}
    else:
        headers = None

    if args.use_async:
        logging.info('Using async mode.')
        KINDS_HANDLERS['exec'] = lambda *args: asyncio.run(async_process_exec(*args))

    while True:
        status = register_and_handle(args, headers, verify)
        if status in (STATUS_KEYBOARD_INTERRUPT, STATUS_REGISTRATION_FAILED):
            sys.exit(status)


if __name__ == '__main__':
    main()
