# Copyright 2021-2024 Henix, henix.fr
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

"""opentf-ctl workflow handling part"""

from typing import (
    Any,
    Dict,
    Iterable,
    List,
    NamedTuple,
    NoReturn,
    Optional,
    Set,
    TextIO,
)

import json
import os
import re
import sys

from collections import defaultdict
from io import StringIO
from time import sleep

import yaml

from opentf.tools.ctlcommons import (
    _make_params_from_selectors,
    _ensure_either_uuids_or_selectors,
    _ensure_options,
    _file_not_found,
    _is_command,
    _get_arg,
    _get_args,
    generate_output,
    _ensure_uuid,
    _error,
    _fatal,
    _warning,
    UUID_REGEX,
)
from opentf.tools.ctlconfig import read_configuration, CONFIG
from opentf.tools.ctlnetworking import (
    _observer,
    _receptionist,
    _killswitch,
    _get,
    _get_workflows,
    _delete,
    _post,
)

from opentf.tools.ctlqualitygate import get_qualitygate


########################################################################

# pylint: disable=broad-except

DEFAULT_COLUMNS = (
    'WORKFLOW_ID:.metadata.workflow_id',
    'STATUS:.status.phase',
    'NAME:.metadata.name',
)
WIDE_COLUMNS = (
    'WORKFLOW_ID:.metadata.workflow_id',
    'STATUS:.status.phase',
    'FIRST_SEEN_TIMESTAMP:.metadata.creationTimestamp',
    'NAME:.metadata.name',
)


WATCHED_EVENTS = (
    'ExecutionCommand',
    'ExecutionResult',
    'ExecutionError',
    'ProviderCommand',
    'GeneratorCommand',
    'Notification',
    'WorkflowResult',
)

AUTOVARIABLES_PREFIX = 'OPENTF_RUN_'

MAX_COMMAND_LENGTH = 15
DEFAULT_OUTPUTPREFIX_TEMPLATE = '[{timestamp}] [Job {job_id}]'

TIMESTAMP_PATTERN = re.compile(r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}\] ')

OS_TAGS = {'windows', 'linux', 'macos'}
ATTACHMENT_PREFIX_LENGTH = len('/tmp/')
ALLURE_PREFIX_LENGTH = len('allureReporting/')
UUID_LENGTH = 36

OUTPUTCONTEXT_PARAMETERS = {
    'output-format': None,
    'step-depth': 1,
    'job-depth': 1,
    'max-command-length': MAX_COMMAND_LENGTH,
    'output-prefix': None,
}

########################################################################
# Help messages

GETWORKFLOWS_COMMAND = 'get workflows'
GETWORKFLOW_COMMAND = 'get workflow _'
RUNWORKFLOW_COMMAND = 'run workflow _'
KILLWORKFLOW_COMMAND = 'kill workflow *'
DELETEWORKFLOW_COMMAND = 'delete workflow *'

QUALITYGATE_OPTIONS = (('--mode', '-m'), ('--using', '-u'), ('--output', '-o'))
QUALITYGATE_PLUGIN_OPTION = '--plugin'

REPORT_EXTENSIONS_TYPES = ('.html', '.txt', '.xml')

RUN_WORKFLOW_HELP = '''Start a workflow

Examples:
  # Start the workflow defined in my_workflow.yaml
  opentf-ctl run workflow my_workflow.yaml

  # Start the workflow and wait until it completes
  opentf-ctl run workflow my_workflow.yaml --wait

  # Start the workflow and define an environment variable
  opentf-ctl run workflow my_workflow.yaml -e TARGET=example.com

  # Start a workflow and provide environment variables defined in a file
  opentf-ctl run workflow my_workflow.yaml -e variables

  # Start a workflow and provide a localy-defined environment variable
  export OPENTF_RUN_MYVAR=my_value
  opentf-ctl run workflow my_workflow.yaml  # variable 'MYVAR' will be defined

  # Start the wokflow and provide a local file
  opentf-ctl run workflow my_workflow.yaml -f key=./access_key.pem

  # Start the wokflow and apply a quality gate after completion
  opentf-ctl run workflow my_workflow.yaml --mode=my.quality.gate

  # Start the workflow and download an execution report after completion
  opentf-ctl run workflow my_workflow.yaml --report=executionreport.html:path/to/report_01.html

Environment Variables:
  Environment variables with an 'OPENTF_RUN_' prefix will be defined without the prefix in the workflow and while running commands in execution environment.

Options:
  -e var=value: 'var' will be defined in the workflow and while running commands in execution environment.
  -e path/to/file: variables defined in file will be defined in the workflow and while running commands in execution environment.  'file' must contain one variable definition per line, of the form 'var=value'.
  -f name=path/to/file: the specified local file will be available for use by the workflow.  'name' is the file name specified in the `resources.files` part of the workflow.
  -i input=value: 'input' will be defined in the workflow.
  -i path/to/file: inputs defined in file will be defined in the workflow .  'file' must contain one input definition per line, of the form 'input=value'.
  --namespace=default or -n=default: the workflow will run on the specified namespace.
  --tags=tag[,tag]: the specified tags will be added to existing 'runs-on' execution environment requests.
  --dry-run: simulate workflow run without starting it.
  --wait or --watch or -w: wait for workflow completion.
  --mode=my.quality.gate|strict|passing|... or -m=...: apply the specified quality gate from the definition file or one of the default quality gates (strict with 100% threshold and passing with 0% threshold). `run workflow` command also supports all the remaining `get qualitygate` command options.
    (more at: https://opentestfactory.org/tools/opentf-ctl/qualitygate.html)
  --report=report_name.ext[:report/path/name.ext]: download an execution report after workflow completion. Report name should end with the file extension (.html, .txt or .xml). Report path is a complete path including file name. If the path does not exist, it will be created.
  --step-depth=1 or -s=1: show nested steps to the given depth (only used with --wait).
  --job-depth=1 or -j=1: show nested jobs to the given depth (only used with --wait).
  --max-command-length=15 or -c=15: show the first n characters of running commands (only used with --wait).
  --show-notifications or -a: show notifications.
  --verbose or -v: enable verbose mode (when used with --show-notifications, show all notification, can be noisy).
  --show-attachments: show produced attachments in the workflow output.
  --output=format or -o format: show information in specified format (json or yaml).
    (more at: https://opentestfactory.org/tools/running-commands#output-formats)
  --selector=s or -l=s: selector (label query) to filter on, supports '=', '==', and '!='.  (e.g. -l key1=value1,key2=value2) (only used with --wait).
  --field-selector=s: selector (field query) to filter on, supports '=', '==', and '!='. (e.g. --field-selector key1=value1,key2=value2) (only used with --wait).
    (more at: https://opentestfactory.org/tools/running-commands#label-and-field-selectors)

Usage:
  opentf-ctl run workflow NAME [-e var=value]... [-e path/to/file] [-f name=path/to/file]... [--namespace=value] [--wait] [--job_depth=value] [--step_depth=value] [--mode=quality.gate.name] [--report=report_name][options]

Use "opentf-ctl options" for a list of global command-line options (applies to all commands).
'''

# Not documenting --show-attachments-only: show workflow attachments list

GET_WORKFLOW_HELP = '''Get a workflow status

Examples:
  # Get the current status of a workflow
  opentf-ctl get workflow 9ea3be45-ee90-4135-b47f-e66e4f793383

  # Get the status of a workflow and wait until its completion
  opentf-ctl get workflow 9ea3be45-ee90-4135-b47f-e66e4f793383 --watch

  # Get the status of a workflow, showing first-level nested steps
  opentf-ctl get workflow 9ea3be45-ee90-4135-b47f-e66e4f793383 --step_depth=2

Options:
  --step-depth=1 or -s=1: show nested steps to the given depth.
  --job-depth=1 or -j=1: show nested jobs to the given depth.
  --max-command-length=15 or -c=15: show the first n characters of running commands.
  --watch or -w: wait until workflow completion or cancellation, displaying status updates as they occur.
  --show-notifications or -a: show notifications.
  --verbose or -v: enable verbose mode (when used with --show-notifications, show all notification, can be noisy).
  --show-attachments: show produced attachments in the workflow output.
  --output=format or -o format: show information in specified format (json or yaml).
    (more at: https://opentestfactory.org/tools/running-commands#output-formats)
  --output-prefix=prefix: prefix to display before each output line.
  --selector=s or -l=s: selector (label query) to filter on, supports '=', '==', and '!='.  (e.g. -l key1=value1,key2=value2).
  --field-selector=s: selector (field query) to filter on, supports '=', '==', and '!='. (e.g. --field-selector key1=value1,key2=value2).
    (more at: https://opentestfactory.org/tools/running-commands#label-and-field-selectors)

Usage:
  opentf-ctl get workflow WORKFLOW_ID [--step_depth=value] [--job_depth=value] [--watch] [options]

Use "opentf-ctl options" for a list of global command-line options (applies to all commands).
'''

GET_WORKFLOWS_HELP = '''List active and recent workflows

Examples:
  # List the IDs of active and recent workflows
  opentf-ctl get workflows

  # Get the status of active and recent workflows
  opentf-ctl get workflows --output=wide

  # Get just the workflow IDs of active and recent workflows
  opentf-ctl get workflows --output=custom-columns=ID:.metadata.workflow_id

  # Get the workflow(s) that have a job with a specific ID
  opentf-ctl get workflows --having=metadata.job_id=9ea3be45-ee90-4135-b47f-e66e4f793383

Options:
  --output={yaml,json} or -o {yaml,json}: show information as YAML or JSON.
  --output=wide or -o wide: show additional information.
  --output=custom-columns= or -o custom-columns=: show specified information.
    (more at: https://opentestfactory.org/tools/running-commands#output-formats)
  --selector=s or -l=s: selector (label query) to filter on, supports '=', '==', and '!='.  (e.g. -l key1=value1,key2=value2).
  --field-selector=s: selector (field query) to filter on, supports '=', '==', and '!='. (e.g. --field-selector key1=value1,key2=value2).
  --having=s: associated events selector (field query) to filter on, supports '=', '==', and '!='. (e.g. --having key1=value1,key2=value2).
    (more at: https://opentestfactory.org/tools/running-commands#label-and-field-selectors)

Usage:
  opentf-ctl get workflows [--output=wide] [options]

Use "opentf-ctl options" for a list of global command-line options (applies to all commands).
'''

KILL_WORKFLOW_HELP = '''Kill a running or pending workflow

Example:
  # Kill all workflows in namespace foo
  opentf-ctl kill workflow --field-selector=metadata.namespace==foo

  # Kill all running and pending workflows
  opentf-ctl kill workflow --all

  # Kill the specified workflow
  opentf-ctl kill workflow 9ea3be45-ee90-4135-b47f-e66e4f793383

  # Kill the specified workflow, providing a reason
  opentf-ctl kill workflow 1f76e165-d005-47d4-b742-9eb39f4bef46 --reason 'This workflow is no longer needed'

Options:
  --reason=reason: reason for killing the workflow.
  --source=source: source of the kill request.
  --dry-run: simulate workflow kill without killing it.
  --all: kill all running and pending workflows.
  --selector=s or -l=s: selector (label query) to filter on, supports '=', '==', and '!='.  (e.g. -l key1=value1,key2=value2).
  --field-selector=s: selector (field query) to filter on, supports '=', '==', and '!='. (e.g. --field-selector key1=value1,key2=value2).
    (more at: https://opentestfactory.org/tools/running-commands#label-and-field-selectors)

Usage:
  opentf-ctl kill|delete workflow (WORKFLOW_ID... | --selector label | --all) [options]

Use "opentf-ctl options" for a list of global command-line options (applies to all commands).
'''


########################################################################
# Helpers


class OutputContext(NamedTuple):
    """An output context (aka. options for output)."""

    output_format: Optional[str]
    step_depth: int
    job_depth: int
    max_command_length: Optional[int]
    output_prefix: Optional[str]
    file: TextIO = sys.stdout
    color: Dict[str, str] = defaultdict(str)


def _read_kv_file(file: str, dest: Dict[str, str]) -> None:
    """Read file and add items.

    Abort with an error code 2 if the file does not exist or contains
    invalid content.
    """
    try:
        with open(file, 'r', encoding='utf-8') as varfile:
            for line in varfile:
                if '=' not in line:
                    _fatal(
                        'Invalid format in file "%s", was expecting var=value.',
                        file,
                    )
                var, _, value = line.strip().partition('=')
                dest[var] = value
    except FileNotFoundError as err:
        _file_not_found(file, err)


def _add_kv(args: List[str], dest: Dict[str, str], key: str) -> None:
    process = False
    for option in args:
        if option == key:
            process = True
            continue
        if option.startswith(f'{key}='):
            process = True
            option = option[3:]
        if process:
            process = False
            if '=' in option:
                var, _, value = option.partition('=')
                dest[var] = value
            else:
                _read_kv_file(option, dest)


def _add_files(args: List[str], files: Dict[str, Any]) -> None:
    """Handling -f file command-line options."""
    process = False
    for option in args:
        if option == '-f':
            process = True
            continue
        if option.startswith('-f='):
            process = True
            option = option[3:]
        if process:
            process = False
            name, path = option.split('=')
            try:
                files[name] = open(path, 'rb')
            except FileNotFoundError as err:
                _file_not_found(path, err)


def _add_inputs(args: List[str], files: Dict[str, Any]) -> None:
    """Handling -i file and -i input=value command-line options."""
    inputs = {}
    _add_kv(args, inputs, '-i')
    if inputs:
        files['inputs'] = '\n'.join(f'{k}={v}' for k, v in inputs.items())


def _add_variables(args: List[str], files: Dict[str, Any]) -> None:
    """Handling -e file and -e var=value command-line options."""
    # OPENTF_CONFIG and OPENTF_TOKEN are explicitly excluded to prevent
    # unexpected leak
    variables = {
        key[len(AUTOVARIABLES_PREFIX) :]: value
        for key, value in os.environ.items()
        if key.startswith(AUTOVARIABLES_PREFIX)
        and key not in ('OPENTF_CONFIG', 'OPENTF_TOKEN')
    }
    _add_kv(args, variables, '-e')
    if variables:
        files['variables'] = '\n'.join(f'{k}={v}' for k, v in variables.items())


def _add_tags(_: List[str], files: Dict[str, Any]) -> None:
    """Handling -t tag command-line options."""
    if not (tags := _get_arg('--tags=')):
        return
    tags = tags.split(',')
    if not all(re.match(r'^[a-zA-Z][a-zA-Z0-9-]*$', tag) for tag in tags):
        _fatal(
            'Invalid tag name(s): "%s".  Must start with a letter and only contains alphanumeric or "-" symbols.',
            ', '.join(tags),
        )
    ostag = set(tags) & OS_TAGS
    if len(ostag) > 1:
        _fatal('At most one tag among "windows", "linux" and "macos" is allowed.')
    workflow = yaml.safe_load(files['workflow'])
    for job in workflow['jobs'].values():
        if 'runs-on' in job:
            runs_on = job['runs-on']
            if isinstance(runs_on, str):
                runs_on = [runs_on]
            if ostag:
                job['runs-on'] = list(set(runs_on) - OS_TAGS | set(tags))
            else:
                job['runs-on'] = list(set(runs_on) | set(tags))
    files['workflow'] = StringIO(yaml.dump(workflow))


def _get_workflow_manifest(what: Iterable[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Return workflow manifest.

    # Required parameters

    - what: a collection of messages.

    # Returned value

    If manifest is not found in `what`, returns `None`.
    """
    for manifest in what:
        if manifest.get('kind') == 'Workflow':
            return manifest
    return None


def _get_manifests(workflows_ids) -> Iterable[Dict[str, Any]]:
    for workflow_id in workflows_ids:
        response = _get_first_page(workflow_id)
        if response.status_code == 200:
            wf = _get_workflow_manifest(response.json()['details']['items'])
            if wf:
                wf['status'] = {'phase': response.json()['details']['status']}
            else:
                wf = {'metadata': {'workflow_id': workflow_id}}
            yield wf
        else:
            print(workflow_id, 'got response code', response.status_code)


def _filter_workflows(workflows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter workflows."""
    having = _get_arg('--having=')
    if not having:
        return workflows
    return [
        wf
        for wf in workflows
        if _get_first_page(
            wf['metadata']['workflow_id'], params={'fieldSelector': having}
        )
        .json()
        .get('details', {})
        .get('items')
    ]


def list_workflows() -> None:
    """List active and recent workflows."""
    params = _make_params_from_selectors()
    params['expand'] = 'manifest'
    workflows = _get_workflows(params)
    if isinstance(workflows, dict):
        workflows = list(
            sorted(
                workflows.values(),
                key=lambda x: x.get('metadata', {}).get('creationTimestamp', ''),
            )
        )
    else:
        workflows = list(_get_manifests(workflows))
    if _get_arg('--having='):
        workflows = _filter_workflows(workflows)
    generate_output(workflows, DEFAULT_COLUMNS, WIDE_COLUMNS)


def _handle_maybe_details(response) -> NoReturn:
    _error(response.json()['message'])
    if response.json().get('details'):
        _error(response.json()['details'].get('error'))
    sys.exit(1)


def _apply_qualitygate(workflow_id: str, workflow_done: bool) -> None:
    if not workflow_done:
        print('Waiting for workflow completion to apply qualitygate...')
    while not workflow_done:
        status = _get_first_page(workflow_id).json()
        if status['details']['status'] in ('RUNNING', 'PENDING'):
            sleep(CONFIG['orchestrator']['polling-delay'])
        elif status['details']['status'] == 'DONE':
            workflow_done = True
        elif status['details']['status'] == 'FAILED':
            _error(
                'Workflow %s failed, quality gate not applied.',
                workflow_id,
            )
            sys.exit(1)
    get_qualitygate(
        workflow_id,
        _get_arg('--mode=') or _get_arg('-m=') or 'strict',
        False,
        _get_arg('--using=') or _get_arg('-u='),
    )


def _get_reports(args: List[str]) -> Dict[str, Set[str]]:
    reports = defaultdict(set)
    for arg in args:
        report, _, path = arg.partition(':')
        if not report.endswith(REPORT_EXTENSIONS_TYPES):
            _warning(
                'Unexpected report name %s, was expecting one of extensions %s.',
                report,
                ', '.join(REPORT_EXTENSIONS_TYPES),
            )
            continue
        reports[report].add(path or '.')
    return reports


def _download_execution_reports(
    workflow_id: str, workflow_done: bool, args: List[str]
) -> None:
    from opentf.tools.ctlattachments import download_workflow_reports

    if not workflow_done:
        print('Waiting for workflow completion to download reports...')
    while not workflow_done:
        status = _get_first_page(workflow_id).json()
        if status['details']['status'] in ('RUNNING', 'PENDING'):
            sleep(CONFIG['orchestrator']['polling-delay'])
        else:
            workflow_done = True
    download_workflow_reports(workflow_id, _get_reports(args))


def _is_sys_argv(args: List[str]) -> bool:
    return any(arg in sys.argv for arg in args)


def run_workflow(workflow_name: str) -> None:
    """Run a workflow.

    # Required parameters

    - workflow_name: a file name

    # Returned value

    Returns the workflow ID if everything was OK.

    # Raised exceptions

    Abort with an error code of 1 if the workflow was not properly
    received by the orchestrator.

    Abort with an error code of 2 if a parameter was invalid (file not
    found or invalid format).
    """
    try:
        files = {'workflow': open(workflow_name, 'r', encoding='utf-8')}
        _add_files(sys.argv[1:], files)
        _add_variables(sys.argv[1:], files)
        _add_tags(sys.argv[1:], files)
        _add_inputs(sys.argv[1:], files)

        params = {}
        ns = _get_arg('--namespace=') or _get_arg('-n=') or CONFIG.get('namespace')
        if ns is not None:
            params['namespace'] = ns
        if _is_sys_argv(['--dry-run']):
            params['dryRun'] = ''
        result = _post(
            _receptionist(),
            '/workflows',
            files=files,
            statuses=(201,),
            params=params or None,
            handler=_handle_maybe_details,
        )
        if not isinstance(result, dict):
            _fatal(
                'Internal error: was expecting a dictionary, got a %s while querying /workflows.',
                result.__class__,
            )
        if not (_get_arg('--output=') or _get_arg('-o=')):
            print('Workflow', result['details']['workflow_id'], 'is running.')
    except FileNotFoundError as err:
        _file_not_found(workflow_name, err)
    except Exception as err:
        _fatal('Could not start workflow: %s.', err)

    workflow_done = False
    watch_args = ['--wait', '--watch', '-w']
    qualitygate_arg = _get_arg('--mode=') or _get_arg('-m=')
    report_args = _get_args('--report=')
    if _is_sys_argv(watch_args) or qualitygate_arg or report_args:
        url = (
            _observer()
            + f'/workflows/{result["details"]["workflow_id"]}/status?per_page=1'
        )
        params = _make_params_from_selectors()
        sleep(CONFIG['orchestrator']['warmup-delay'])
        try:
            while (
                _get(url, params=params, handler=lambda _: False, raw=True).status_code
                != 200
            ):
                sleep(CONFIG['orchestrator']['polling-delay'])
            workflow_id = result['details']['workflow_id']
            if _is_sys_argv(watch_args):
                get_workflow(result['details']['workflow_id'], watch=True)
                workflow_done = True
            if report_args:
                _download_execution_reports(workflow_id, workflow_done, report_args)
            if qualitygate_arg:
                _apply_qualitygate(result['details']['workflow_id'], workflow_done)
        except Exception as err:
            _fatal('Could not show workflow execution result: %s.', err)


def _emit_prefix(event: Dict[str, Any], context: OutputContext) -> None:
    cts = event['metadata'].get('creationTimestamp', ' ' * 19)[:19]
    job_id = event['metadata'].get('job_id', '')
    tmpl = (
        DEFAULT_OUTPUTPREFIX_TEMPLATE
        if context.output_prefix is None
        else context.output_prefix
    )
    try:
        prefix = tmpl.format(timestamp=cts, job_id=job_id).strip().replace('[Job ]', '')
        if prefix:
            prefix = _color(context, 'pre', prefix)
    except (ValueError, KeyError) as err:
        prefix = _color(context, 'inv', f'{{invalid prefix: {err}}}'.strip())
    print((prefix.strip() + ' ') if prefix else '', end='', file=context.file)


def _emit_command(
    event: Dict[str, Any],
    context: OutputContext,
    silent: bool,
    namespace: Optional[str] = None,
    job_cache: Optional[Dict[str, Any]] = None,
) -> None:
    if event['metadata']['step_sequence_id'] == -1:
        if job_cache is not None:
            if event['metadata'].get('job_id') in job_cache:
                return
            job_cache[event['metadata']['job_id']] = True
        _emit_prefix(event, context)
        if tags := event['runs-on']:
            what = 'execution environment providing "' + '", "'.join(tags) + '"'
        else:
            what = 'any execution environment'
        print_color(
            context,
            'req',
            'Requesting',
            what,
            'for job' if namespace is None else f'in namespace "{namespace}" for job',
            f'"{event["metadata"]["name"]}"',
        )
    elif event['metadata']['step_sequence_id'] == -2:
        _emit_prefix(event, context)
        print_color(
            context,
            'rel',
            'Releasing execution environment for job',
            f'"{event["metadata"]["name"]}"',
        )
    elif not silent:
        _emit_prefix(event, context)
        print_color(
            context,
            'idx',
            ' ' * (len(event['metadata'].get('step_origin', []))),
            end='',
        )
        if len(event['scripts']):
            command = event['scripts'][0]
            if context.max_command_length and len(command) > context.max_command_length:
                command = command[: context.max_command_length] + '...'
        else:
            command = 'None'
        print_color(context, 'run', 'Running command:', command)


def _emit_notification(
    event: Dict[str, Any], context: OutputContext, silent: bool
) -> None:
    if 'spec' not in event or 'logs' not in event['spec']:
        return
    always = event['metadata']['name'] == 'group notification'
    if '--show-notifications' not in sys.argv and '-a' not in sys.argv and not always:
        return
    verbosity = ('-v' in sys.argv) or ('--verbose' in sys.argv)
    for log in event['spec']['logs']:
        if TIMESTAMP_PATTERN.match(log):
            log = log[26:]
        if (
            any(
                log.startswith((x, f'[{x}]')) or f'] {x} in' in log
                for x in ('DEBUG', 'TRACE')
            )
            or '127.0.0.1 - - "POST' in log
        ):
            if silent or not verbosity:
                continue
        _emit_prefix(event, context)
        if always or event['metadata']['name'] == 'log notification':
            msg = _color(context, 'grp', log) if always else log
        else:
            msg = _color(context, 'ntf', f'[{event["metadata"]["name"]}] {log}')
        print(msg, file=context.file)


def _emit_attachment_info(
    event: Dict[str, Any],
    context: OutputContext,
    silent: bool,
    name: str,
    uuid: str,
) -> None:
    if re.match(UUID_REGEX, name[:UUID_LENGTH]) and name[UUID_LENGTH:] in (
        '-attachment.html',
        '-result.json',
    ):
        return
    _emit_prefix(event, context)
    if not silent:
        print_color(
            context,
            'att',
            ' ' * (len(event['metadata'].get('step_origin', []))),
            end='',
        )
    else:
        print_color(context, 'att', ' ', end='')
    print_color(context, 'att', f'Produced attachment {uuid} ({name}).')


def _maybe_emit_attachment(
    event: Dict[str, Any], context: OutputContext, silent: bool
) -> None:
    if 'Errno 2' in ''.join(event.get('logs', [])):
        return
    for attachment in event['attachments']:
        if 'allure' in attachment:
            uuid = event['metadata']['workflow_id']
            name = attachment[
                ATTACHMENT_PREFIX_LENGTH + ALLURE_PREFIX_LENGTH + UUID_LENGTH + 1 :
            ]
        else:
            name = attachment[ATTACHMENT_PREFIX_LENGTH:].split('_', maxsplit=2)[2]
            uuid = event['metadata']['attachments'][attachment].get('uuid')
        _emit_attachment_info(event, context, silent, name, uuid)


def _maybe_emit_testcase_name(event: Dict[str, Any]) -> str:
    if event.get('step', {}).get('with', {}).get('test'):
        return f" for test reference `{event['step']['with']['test']}`:"
    return ''


def _emit_result(event: Dict[str, Any], context: OutputContext, silent: bool) -> None:
    for item in event.get('logs', []):
        _emit_prefix(event, context)
        print_color(context, 'out', item.rstrip())
    if event.get('attachments') and any(
        x in sys.argv for x in ['--show-attachments', '--show-attachments-only']
    ):
        _maybe_emit_attachment(event, context, silent)
    if event.get('status') == 0 or silent:
        return
    if event.get('status'):
        _emit_prefix(event, context)
        print_color(context, 'ret', 'Status code was:', event['status'])


def _emit_executionerror(event: Dict[str, Any], context: OutputContext) -> None:
    _emit_prefix(event, context)
    if details := event.get('details'):
        if 'error' in details:
            print_color(context, 'err', 'ERROR:', details['error'], flush=True)
        else:
            print_color(
                context, 'err', 'ERROR: An ExecutionError occurred:', flush=True
            )
            for key, val in details.items():
                print_color(context, 'err', f'{key}: {val}', flush=True)
    else:
        print_color(context, 'err', f'An ExecutionError occurred: {event}', flush=True)


def emit_event(
    kind: str,
    event: Dict[str, Any],
    context: OutputContext,
    first: bool,
    namespace: Optional[str],
    job_cache: Optional[Dict[str, Any]] = None,
) -> None:
    """Emit event.

    # Required parameters

    - kind: a string, the event kind (`Workflow`, ...)
    - event: a dictionary
    - context: an OutputContext
    - first: a boolean
    - namespace: a string or None

    # Optional parameters

    - job_cache: a dictionary or None (None by default)
    """
    if context.output_format == 'json':
        print('    ' if first else ',\n    ', end='', file=context.file)
        print(
            '    '.join(json.dumps(event, indent=2).splitlines(keepends=True)),
            end='',
            file=context.file,
        )
        return
    if context.output_format == 'yaml':
        print('- ', end='', file=context.file)
        print(
            '  '.join(yaml.safe_dump(event).splitlines(keepends=True)),
            end='',
            file=context.file,
        )
        return

    if kind == 'Workflow':
        print_color(context, 'ttl', 'Workflow ', event['metadata']['name'], flush=True)
        if namespace is not None:
            print_color(context, 'ns', f'(running in namespace "{namespace}")')
        return
    if kind not in WATCHED_EVENTS:
        return
    if kind == 'ExecutionError':
        _emit_executionerror(event, context)
        return

    silent = False
    if (
        context.job_depth
        and len(event['metadata'].get('job_origin', [])) >= context.job_depth
    ):
        silent = True
    elif (
        context.step_depth
        and len(event['metadata'].get('step_origin', [])) >= context.step_depth
    ):
        silent = True

    if kind in ('ExecutionResult', 'WorkflowResult'):
        _emit_result(event, context, silent)
    elif kind == 'ExecutionCommand':
        _emit_command(event, context, silent, namespace, job_cache)
    elif kind == 'Notification':
        _emit_notification(event, context, silent)
    elif not silent:
        if '--show-attachments-only' in sys.argv:
            testcase_name = _maybe_emit_testcase_name(event)
        else:
            testcase_name = ''
        _emit_prefix(event, context)
        print_color(
            context,
            'idx',
            ' ' * (len(event['metadata'].get('step_origin', []))),
            end='',
        )
        print_color(
            context,
            'fun',
            'Running',
            'function:' if 'step_id' in event['metadata'] else 'job bundle:',
            f'"{event["metadata"]["name"]}"',
            testcase_name,
            flush=True,
        )


def _get_first_page(workflow_id: str, params=None):
    """Return a requests.Response, to get following pages if needed."""

    def _handler_unknown_workflowid(response):
        if response.status_code == 404:
            _error(
                'Could not find workflow %s.  The ID is incorrect or too recent or too old.',
                workflow_id,
            )
            sys.exit(1)
        _error(
            'Could not get workflow %s.  Got status code %d (%s).',
            workflow_id,
            response.status_code,
            response.text,
        )
        sys.exit(1)

    return _get(
        _observer(),
        f'/workflows/{workflow_id}/status',
        params=params,
        handler=_handler_unknown_workflowid,
        raw=True,
    )


def _get_outputformat(allowed: Iterable[str]) -> Optional[str]:
    """Ensure the specified format, if any, is in the allowed set."""
    output_format = _get_arg('--output=') or _get_arg('-o=')
    if '-o' in sys.argv and not output_format:
        _fatal('Missing value for option "-o" (was expecting %s).', ', '.join(allowed))
    if output_format is not None and output_format not in allowed:
        _fatal(
            'Unexpected output format specified: "%s" (was expecting %s).',
            output_format,
            ', '.join(allowed),
        )
    return output_format


def _get_workflow_events(workflow_id: str, watch: bool) -> Iterable[Dict[str, Any]]:
    """Yield events.

    If `watch` is True, yields events as they come, til the workflow
    completes.  Otherwise, yields events from the currently available
    page(s).
    """
    current_item = 0
    response = _get_first_page(workflow_id, _make_params_from_selectors())
    current_page = _observer() + f'/workflows/{workflow_id}/status'
    params = _make_params_from_selectors()

    while True:
        status = response.json()
        for event in status['details']['items'][current_item:]:
            yield event

        if 'next' in response.links:
            current_item = 0
            if (
                CONFIG['orchestrator']
                .get('services', {})
                .get('observer', {})
                .get('force-base-url', False)
            ):
                current_page = (
                    _observer()
                    + f'/workflows/{workflow_id}/status?'
                    + response.links['next']['url'].partition('?')[2]
                )
            else:
                current_page = response.links['next']['url']
            response = _get(current_page, raw=True)
            continue

        if not watch:
            break
        if response.json()['details']['status'] not in ('RUNNING', 'PENDING'):
            break

        current_item = len(status['details']['items'])
        while len(status['details']['items']) <= current_item:
            sleep(CONFIG['orchestrator']['polling-delay'])
            response = _get(current_page, params=params, raw=True)
            status = response.json()
            if len(status['details']['items']) != current_item:
                break
            if 'next' in response.links:
                break
            if current_item == 0 and len(status['details']['items']) == 0:
                _warning(f'Could not find items matching selectors: {params}')
                break


def _is_useful_attachments(attachments: List[str]) -> bool:
    if not attachments:
        return False
    names = [
        attachment[ATTACHMENT_PREFIX_LENGTH:].split('_', maxsplit=2)[2]
        for attachment in attachments
    ]
    return not all(
        re.match(UUID_REGEX, name[:UUID_LENGTH])
        and name[UUID_LENGTH:] in ('-attachment.html', '-result.json')
        for name in names
    )


def _get_workflow_attachments_events(
    workflow_id: str, verbose: bool = False
) -> List[Dict[str, Any]]:
    """Get attachments-related events from a workflow."""
    events = list(_get_workflow_events(workflow_id, watch=False))
    if verbose:
        execution_results = [
            event
            for event in events
            if event.get('kind') == 'ExecutionResult' and event.get('attachments')
        ]
    else:
        execution_results = [
            event
            for event in events
            if event.get('kind') == 'ExecutionResult'
            and _is_useful_attachments(event.get('attachments', []))
        ]

    provider_commands = [
        event
        for event in events
        if event.get('kind') == 'ProviderCommand'
        and event.get('step', {}).get('id')
        in [
            origin
            for result in execution_results
            for origin in result['metadata']['step_origin']
        ]
    ]
    execution_commands = [
        event
        for event in events
        if event.get('kind') == 'ExecutionCommand'
        and (
            event.get('metadata', {}).get('step_id')
            in [result['metadata']['step_id'] for result in execution_results]
            or event.get('metadata', {}).get('step_sequence_id') in (-1, -2)
        )
    ]

    to_keep = execution_results + provider_commands + execution_commands
    return [
        event
        for event in events
        if event.get('kind')
        not in ('ExecutionResult', 'ProviderCommand', 'ExecutionCommand')
        or event in to_keep
    ]


def _get_events(workflow_id, watch, show_attachments):
    if show_attachments:
        return _get_workflow_attachments_events(workflow_id)
    return _get_workflow_events(workflow_id, watch)


def _color(context: OutputContext, key: str, *msg: str) -> str:
    return context.color[key] + ' '.join(str(m) for m in msg) + context.color['rs']


def print_color(context: OutputContext, key, *msg: str, **kwargs) -> None:
    print(_color(context, key, *msg), file=context.file, **kwargs)


def _make_outputcontext() -> OutputContext:
    """Read output details options.

    If the details options are invalid, abort with an error code 2.

    Command lines parameters win over configuration file.  If neither
    are provided, defaults to 1 for job depth and step depth, and
    MAX_COMMAND_LENGTH for max command lenght.

    # Returned value

    An _OutputContext_ named tuple.
    """
    job_depth = _get_arg('--job-depth=') or _get_arg('-j=') or CONFIG.get('job-depth')
    if job_depth is None:
        job_depth = 1
    try:
        job_depth = int(job_depth)
    except ValueError:
        _fatal(f'--job-depth must be an integer.  Got: {job_depth}.')

    step_depth = (
        _get_arg('--step-depth=') or _get_arg('-s=') or CONFIG.get('step-depth')
    )
    if step_depth is None:
        step_depth = 1
    try:
        step_depth = int(step_depth)
    except ValueError:
        _fatal(f'--step-depth must be an integer.  Got: {step_depth}.')

    max_command_length = (
        _get_arg('--max-command-length=')
        or _get_arg('-c=')
        or CONFIG.get('max-command-length')
    )
    if max_command_length is None:
        max_command_length = MAX_COMMAND_LENGTH
    try:
        max_command_length = int(max_command_length)
    except ValueError:
        _fatal(f'--max-command-length must be an integer.  Got: {max_command_length}.')

    output_prefix = _get_arg('--output-prefix=') or CONFIG.get('output-prefix')

    # OPENTF_COLORS > NO_COLOR > FORCE_COLOR
    yes = ('1', 'on', 'true', 'yes')
    try:
        use_color = os.isatty(sys.stdout.fileno())
    except:
        use_color = False
    if use_color and 'TERM' in os.environ and os.environ['TERM'] == 'dumb':
        use_color = False
    if 'OPENTF_COLORS' in os.environ:
        use_color = os.environ['OPENTF_COLORS'].lower().strip() in yes
    elif 'NO_COLOR' in os.environ:
        use_color = os.environ['NO_COLOR'].lower().strip() not in yes
    elif 'FORCE_COLOR' in os.environ:
        use_color = os.environ['FORCE_COLOR'].lower().strip() in yes
    colors = defaultdict(str)
    if use_color:
        for color in CONFIG.get('colors', '').split(':'):
            key, _, val = color.partition('=')
            colors[key.strip()] = f'\033[{val}m'

    return OutputContext(
        output_format=_get_outputformat(allowed=('yaml', 'json')),
        job_depth=job_depth,
        step_depth=step_depth,
        max_command_length=max_command_length,
        output_prefix=output_prefix,
        file=sys.stdout,
        color=colors,
    )


def get_workflow(workflow_id: str, watch=False) -> None:
    """Get a workflow.

    # Required parameters

    - workflow_id: a string

    # Optional parameters

    - watch: a boolean (False by default)

    # Returned value

    None.

    # Raised exceptions

    Abort with an error code 1 if the workflow could not be found on the
    orchestrator.

    Abort with an error code 2 if another error occurred.
    """
    workflow_id = _ensure_uuid(workflow_id, _get_workflows)

    context = _make_outputcontext()

    if context.output_format == 'json':
        print('{\n  "items": [')
    elif context.output_format == 'yaml':
        print('items:')

    verbose = ('-v' in sys.argv) or ('--verbose' in sys.argv)

    first = True
    namespace = None
    cancelation_event = None
    job_cache = None if verbose else {}
    try:
        for event in _get_events(
            workflow_id, watch, '--show-attachments-only' in sys.argv
        ):
            kind = event.get('kind', 'None')
            if kind == 'WorkflowCanceled':
                cancelation_event = event
            if kind == 'Workflow':
                namespace = event['metadata'].get('namespace')
            emit_event(
                kind,
                event,
                context=context,
                first=first,
                namespace=namespace,
                job_cache=job_cache,
            )
            first = False
    except KeyboardInterrupt:
        print('^C')
        sys.exit(1)
    except BrokenPipeError:
        _error('BrokenPipeError: [Errno 32] Broken pipe')
        sys.exit(1)

    status = _get_first_page(workflow_id, _make_params_from_selectors()).json()

    if context.output_format == 'json':
        print('\n  ],\n  "status":', json.dumps(status['details']['status']))
        print('}')
        return
    if context.output_format == 'yaml':
        yaml.safe_dump({'status': status['details']['status']}, sys.stdout)
        return

    workflow_status = status['details']['status']
    if workflow_status == 'DONE':
        print_color(context, 'sta', 'Workflow completed successfully.')
    elif workflow_status == 'RUNNING':
        print_color(context, 'sta', 'Workflow is running.')
    elif workflow_status == 'PENDING':
        print_color(context, 'sta', 'Workflow is pending.')
    elif workflow_status == 'FAILED':
        if cancelation_event and (
            reason := cancelation_event.get('details', {}).get('reason')
        ):
            print_color(context, 'rsn', reason)
        if (
            cancelation_event
            and cancelation_event.get('details', {}).get('status') == 'cancelled'
        ):
            print_color(context, 'sta', 'Workflow cancelled.')
        else:
            print_color(context, 'sta', 'Workflow failed.')
    else:
        _warning(
            'Unexpected workflow sta: %s (was expecting DONE, RUNNING, PENDING, or FAILED).',
            workflow_status,
        )


def delete_workflow(workflow_ids: List[str]) -> None:
    """Kill workflow.

    # Required parameter

    - workflow_ids: a possibly empty list of strings (UUIDs)

    # Raised exceptions

    Abort with an error code 1 if the orchestrator replied with an
    unexpected status code (!= 200).

    Abort with an error code 2 if an error occurred while contacting the
    orchestrator.
    """

    def _notknown(response):
        if response.status_code == 404:
            _error(f'Workflow {workflow_id} is not known.')
        else:
            _error(f'Could not check if workflow {workflow_id} exists.')
        _error('Could not kill workflow.')
        sys.exit(1)

    params = {}
    if _is_sys_argv(['--dry-run']):
        params['dryRun'] = ''
    if reason := _get_arg('--reason='):
        params['reason'] = reason
    if source := _get_arg('--source='):
        params['source'] = source
    workflow_ids = _ensure_either_uuids_or_selectors(
        workflow_ids,
        _get_workflows,
        {'fieldSelector': 'status.phase in (RUNNING, PENDING)'},
    )
    for workflow_id in workflow_ids:
        workflow_id = _ensure_uuid(workflow_id, _get_workflows)

        _ = _get(_observer(), f'/workflows/{workflow_id}/status', handler=_notknown)
        _ = _delete(_killswitch(), f'/workflows/{workflow_id}', params=params)
        print(f'Killing workflow {workflow_id}.')


########################################################################
# Helpers


def print_workflow_help(args: List[str]):
    """Display help."""
    if _is_command('run workflow', args):
        print(RUN_WORKFLOW_HELP)
    elif _is_command(GETWORKFLOWS_COMMAND, args):
        print(GET_WORKFLOWS_HELP)
    elif _is_command('get workflow', args):
        print(GET_WORKFLOW_HELP)
    elif _is_command('kill workflow', args) or _is_command('delete workflow', args):
        print(KILL_WORKFLOW_HELP)
    else:
        _error('Unknown command.  Use "--help" to list known commands.')
        sys.exit(1)


def workflow_cmd():
    """Interact with workflows."""
    if _is_command(GETWORKFLOWS_COMMAND, sys.argv):
        _ensure_options(
            GETWORKFLOWS_COMMAND,
            sys.argv[1:],
            extra=[
                ('--output', '-o'),
                ('--selector', '-l'),
                ('--field-selector',),
                ('--having',),
            ],
        )
        read_configuration()
        list_workflows()
    elif _is_command(RUNWORKFLOW_COMMAND, sys.argv):
        workflow = _ensure_options(
            RUNWORKFLOW_COMMAND,
            sys.argv[1:],
            extra=[
                ('--namespace', '-n'),
                ('--tags',),
                ('--step-depth', '-s'),
                ('--job-depth', '-j'),
                ('--max-command-length', '-c'),
                ('--output', '-o'),
                ('--selector', '-l'),
                ('--field-selector',),
                *QUALITYGATE_OPTIONS,
            ],
            multi=[
                ('-e',),
                ('-f',),
                ('-i',),
                (QUALITYGATE_PLUGIN_OPTION,),
                ('--report',),
            ],
            flags=[
                ('--wait', '--watch', '-w'),
                ('--show-notifications', '-a'),
                ('--verbose', '-v'),
                ('--show-attachments',),
                ('--dry-run',),
            ],
        )
        read_configuration()
        run_workflow(workflow)
    elif _is_command(GETWORKFLOW_COMMAND, sys.argv):
        workflow_id = _ensure_options(
            GETWORKFLOW_COMMAND,
            sys.argv[1:],
            extra=[
                ('--step-depth', '-s'),
                ('--job-depth', '-j'),
                ('--max-command-length', '-c'),
                ('--output-prefix',),
                ('--output', '-o'),
                ('--selector', '-l'),
                ('--field-selector',),
            ],
            flags=[
                ('--watch', '-w'),
                ('--show-notifications', '-a'),
                ('--verbose', '-v'),
                ('--show-attachments',),
                ('--show-attachments-only',),
            ],
        )
        read_configuration()
        get_workflow(workflow_id, '--watch' in sys.argv or '-w' in sys.argv)
    elif _is_command(KILLWORKFLOW_COMMAND, sys.argv):
        workflow_ids = _ensure_options(
            KILLWORKFLOW_COMMAND,
            sys.argv[1:],
            extra=[
                ('--selector', '-l'),
                ('--field-selector',),
                ('--reason',),
                ('--source',),
            ],
            flags=[
                ('--all',),
                ('--dry-run',),
            ],
        )
        read_configuration()
        delete_workflow(workflow_ids)
    elif _is_command(DELETEWORKFLOW_COMMAND, sys.argv):
        workflow_ids = _ensure_options(
            DELETEWORKFLOW_COMMAND,
            sys.argv[1:],
            extra=[
                ('--selector', '-l'),
                ('--field-selector',),
                ('--reason',),
                ('--source',),
            ],
            flags=[
                ('--all',),
                ('--dry-run',),
            ],
        )
        read_configuration()
        delete_workflow(workflow_ids)
    else:
        _error('Unknown command.  Use "--help" to list known commands.')
        sys.exit(1)
