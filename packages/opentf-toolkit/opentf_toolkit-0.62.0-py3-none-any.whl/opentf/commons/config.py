# Copyright (c) 2023 Henix, Henix.fr
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

"""Helpers for the OpenTestFactory config."""

from typing import Any, Dict, List, Optional, Tuple

import argparse
import inspect
import os

from logging.config import dictConfig

import yaml

from .exceptions import ConfigError
from .schemas import read_and_validate, SERVICECONFIG


########################################################################

NOTIFICATION_LOGGER_EXCLUSIONS = 'eventbus'

DEFAULT_CONTEXT: Dict[str, Any] = {
    'host': '127.0.0.1',
    'port': 443,
    'ssl_context': 'adhoc',
    'eventbus': {'endpoint': 'https://127.0.0.1:38368', 'token': 'invalid-token'},
}

DEBUG_LEVELS = {'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'}


########################################################################


def make_argparser(description: str, configfile: str) -> argparse.ArgumentParser:
    """Make an argument parser.

    The configured argument parser includes definitions for all commons
    command-line parameters.  It can be extended with additional
    parameters.

    # Required parameters

    - description: a string, the parser description
    - configfile: a string, the default configuration file name

    # Returned value

    An argument parser, configured.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--descriptor', help='alternate descriptor file')
    parser.add_argument(
        '--config', help=f'alternate config file (default to {configfile})'
    )
    parser.add_argument('--context', help='alternative context')
    parser.add_argument('--host', help='alternative host')
    parser.add_argument('--port', help='alternative port')
    parser.add_argument(
        '--ssl_context', '--ssl-context', help='alternative ssl context'
    )
    parser.add_argument(
        '--trusted_authorities',
        '--trusted-authorities',
        help='alternative trusted authorities',
    )
    parser.add_argument(
        '--enable_insecure_login',
        '--enable-insecure-login',
        action='store_true',
        help='enable insecure login (disabled by default)',
    )
    parser.add_argument(
        '--insecure_bind_address',
        '--insecure-bind-address',
        help='insecure bind address (127.0.0.1 by default)',
        default='127.0.0.1',
    )
    parser.add_argument(
        '--authorization_mode',
        '--authorization-mode',
        help='authorization mode, JWT without RBAC if unspecified',
    )
    parser.add_argument(
        '--authorization_policy_file',
        '--authorization-policy-file',
        help='authorization policies for ABAC',
    )
    parser.add_argument(
        '--token_auth_file',
        '--token-auth-file',
        help='authenticated users for ABAC and RBAC',
    )
    parser.add_argument(
        '--trustedkeys_auth_file',
        '--trustedkeys-auth-file',
        help='authenticated trusted keys for ABAC and RBAC',
    )
    parser.add_argument(
        '--enable-insecure-healthcheck-endpoint',
        '--enable_insecure_healthcheck_endpoint',
        action='store_true',
        help='enable insecure healthcheck endpoint (disabled by default)',
    )
    return parser


def configure_logging(name: str, debug_level: str) -> None:
    """Configure logging.

    The logging configuration is driven by the `debug_level` parameter.

    A `wsgi` handler is defined, that will log messages to the WSGI
    stream.

    You can use the `OPENTF_LOGGING_REDIRECT` environment variable to
    redirect the logs to a specific stream.

    If `name` is not in `NOTIFICATION_LOGGER_EXCLUSIONS`, an `eventbus`
    handler is added.  It will post log messages to the event bus as
    `Notification` events.

    The configured format is:

    `[%(asctime)s] %(levelname)s in {name}: %(message)s`

    # Required parameters

    - name: a string, the service name
    - debug_level: a string, the log level

    # Returned value

    None.
    """
    logging_conf: Dict[str, Any] = {
        'version': 1,
        'formatters': {
            'default': {
                'format': f'[%(asctime)s] %(levelname)s in {name}: %(message)s',
            }
        },
        'handlers': {
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': f'ext://{os.environ.get("OPENTF_LOGGING_REDIRECT", "flask.logging.wsgi_errors_stream")}',
                'formatter': 'default',
            },
        },
        'root': {
            'level': debug_level,
            'handlers': ['wsgi'],
        },
    }
    if name not in NOTIFICATION_LOGGER_EXCLUSIONS:
        logging_conf['handlers']['eventbus'] = {
            'class': 'opentf.commons.EventbusLogger',
            'formatter': 'default',
        }
        logging_conf['root']['handlers'] += ['eventbus']
    dictConfig(logging_conf)


def read_config(
    altconfig: Optional[str],
    altcontext: Optional[str],
    configfile: str,
    defaultcontext: Optional[Dict[str, Any]],
    schema: Optional[str],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Read service configuration.

    If not None, the `alt` parameters are used to override the default
    ones.

    # Required parameters

    - altconfig: a string (the configuration file location) or None
    - altcontext: a string (the context name) or None
    - configfile: a string, the configuration file name
    - defaultcontext: a dictionary (the default context) or None
    - schema: a string (the schema that validates the configuration)
      or None

    If `altcontext` is None, returns the current context as specified
    in the service configuration.

    If `schema` is None, uses SERVICECONFIG as the default schema.

    # Returned value

    A pair of dictionaries.  The first item is the context, the second
    item is the complete configuration.

    # Raised exceptions

    A _ConfigError_ exception is raised if the configuration file cannot
    be read or if the configuration file is invalid.
    """
    if altconfig is None and not os.path.isfile(configfile):
        if altcontext:
            raise ConfigError(
                'Cannot specify a context when using default configuration.'
            )
        context = defaultcontext or DEFAULT_CONTEXT
        config = {}
    else:
        configfile = altconfig or configfile
        try:
            config = read_and_validate(schema or SERVICECONFIG, configfile)
        except (ValueError, OSError) as err:
            raise ConfigError(f'Could not read configfile "{configfile}": {err}.')

        context_name = altcontext or config['current-context']
        try:
            context = get_named(config['contexts'], context_name)['context']
        except ValueError as err:
            raise ConfigError(f'Could not find context "{context_name}": {err}.')
    return context, config


def read_descriptor(
    altdescriptor: Optional[str], descriptor: Optional[str]
) -> Tuple[str, List[Dict[str, Any]]]:
    """Read service descriptor.

    If `altdescriptor` is None, the descriptor is read from the module
    where the function is called.  If `descriptor` is None, the default
    descriptor name is `service.yaml`.

    # Required parameter

    - altdescriptor: a string, the descriptor file location or None
    - descriptor: a string, the descriptor file name or None

    # Returned value

    A pair (filename, manifests) where filename is the descriptor file
    name and manifests is a list of dictionaries.

    # Raised exceptions

    A _ConfigError_ exception is raised if the descriptor file cannot
    be read.
    """
    try:
        if altdescriptor:
            filename = altdescriptor
        else:
            for frame in inspect.stack():
                if frame.frame.f_code.co_name == '<module>':
                    break
            else:
                raise ConfigError('Could not get module location, aborting.')
            filename = os.path.join(
                os.path.dirname(frame.filename),
                descriptor or 'service.yaml',
            )
        with open(filename, 'r', encoding='utf-8') as definition:
            manifests = list(yaml.safe_load_all(definition))
        return filename, manifests
    except ConfigError:
        raise
    except Exception as err:
        raise ConfigError(f'Could not get descriptor "{filename}", aborting: {err}.')


def get_named(entries: List[Dict[str, Any]], name: str) -> Dict[str, Any]:
    """Get an entry from a list of dictionaries.

    Matching entries are those with a 'name' entry equal to the
    requested name.

    # Required parameters

    - entries: a list of dictionaries
    - name: a string, the entry 'name'

    # Returned value

    A dictionary, the entry with the 'name' `name`.

    # Raised exceptions

    A _ValueError_ exception is raised if no entry is found or if more
    than one entry is found.
    """
    items = [entry for entry in entries if entry.get('name') == name]
    if not items:
        raise ValueError(f'Found no entry with name "{name}"')
    if len(items) > 1:
        raise ValueError(f'Found more than one entry with name "{name}"')
    return items.pop()


def get_debug_level(name: str) -> str:
    """Get service log level.

    Driven by environment variables.  If `{name}_DEBUG_LEVEL` is
    defined, this value is used.  If not, if `DEBUG_LEVEL` is set, then
    it is used.  Otherwise, returns `INFO`.

    Value must be one of `CRITICAL`, `ERROR`, `WARNING`, `INFO`,
    `DEBUG`, `TRACE`, or `NOTSET`.

    # Required parameter

    - name: a string, the service name

    # Returned value

    The requested log level if in the allowed values, `INFO` otherwise.
    """
    level = os.environ.get(
        f'{name.upper()}_DEBUG_LEVEL', os.environ.get('DEBUG_LEVEL', 'INFO')
    )
    if level == 'TRACE':
        level = 'NOTSET'
    return level if level in DEBUG_LEVELS else 'INFO'
