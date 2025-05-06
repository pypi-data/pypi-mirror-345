"""Load the JIRA instance."""

import argparse
import datetime as dti
import json
import logging
import pathlib
from typing import Dict, Union, no_type_check

import lippu.ticket_system_actions as actions
from lippu import (
    APP_ALIAS,
    APP_ENV,
    BASE_URL,
    ENCODING,
    IDENTITY,
    IS_CLOUD,
    NODE_INDICATOR,
    PROJECT,
    STORE,
    TOKEN,
    TS_FORMAT_PAYLOADS,
    USER,
    __version__ as version,
    log,
)
from lippu.store import Store

Context = Dict[str, Union[str, dti.datetime]]
COMMA = ','
NL = '\n'
SPACE = ' '

@no_type_check
def setup_twenty_seven(options: argparse.Namespace) -> object:
    """Set up the scenario adn return the parameters as members of an object."""

    class Setup:
        pass

    setup = Setup()

    setup.user = options.user if options.user else USER
    setup.token = options.token if options.token else TOKEN
    setup.target_url = options.target_url if options.target_url else BASE_URL
    setup.is_cloud = options.is_cloud if options.is_cloud else IS_CLOUD
    setup.target_project = options.target_project if options.target_project else PROJECT
    setup.scenario = options.scenario if options.scenario else 'unknown'
    setup.identity = options.identity if options.identity else IDENTITY
    setup.storage_path = options.out_path if options.out_path else STORE

    setup.kind = options.kind if options.kind else 'Task'
    summary = options.summary if options.summary else 'unknown summary'
    setup.summary = summary[:254]

    desc = options.description if options.description else 'unknown description'
    description = desc
    if pathlib.Path(desc).is_file():
        log.info(f'- Note: Reading description from file at {desc}')
        with open(desc, 'rt', encoding=ENCODING) as handle:
            description = handle.read()
    setup.description = description.rstrip()[:32767]

    labels = options.labels.strip() if options.labels else ''
    setup.labels = [v for v in labels.replace(SPACE, COMMA).split(COMMA) if v.strip()]

    comm = options.comment if options.comment else ''
    comment = comm
    if pathlib.Path(comm).is_file():
        log.info(f'- Note: Reading comment from file at {comm}')
        with open(comm, 'rt', encoding=ENCODING) as handle:
            comment = handle.read()
    setup.comment = comment.rstrip()[:32767]

    setup.estimate = options.estimate if options.estimate else ''
    setup.cut = options.cut

    log.info(f'- Setup <00> Kind ({setup.kind})')
    log.info(f'- Setup <00> Summary ({setup.summary})')

    description = setup.description if len(setup.description) < 100 else f'{setup.description[:100]} ...'
    description = description.replace(NL, '$NL')
    log.info(f'- Setup <00> Description ({description})')

    if setup.labels:
        log.info(f'- Setup <00> Labels ({setup.labels})')
    else:
        log.info(f'- Setup <00> No Labels')

    if setup.comment:
        comment = setup.comment if len(setup.comment) < 50 else f'{setup.comment[:50]} ...'
        comment = comment.replace(NL, '$NL')
        log.info(f'- Setup <00> Comment ({comment})')
    else:
        log.info(f'- Setup <00> No Comment')

    if setup.estimate:
        log.info(f'- Setup <00> Estimate ({setup.estimate})')
    else:
        log.info(f'- Setup <00> No Estimate')

    log.info('=' * 84)
    log.info(f'Generator {APP_ALIAS} version {version}')

    setup.node_indicator = NODE_INDICATOR
    log.info(f'- Setup <00> Node indicator ({setup.node_indicator})')

    log.info(
        f'- Setup <00> Connect will be to upstream ({"cloud" if setup.is_cloud else "on-site"})'
        f' service ({setup.target_url}) per login ({setup.user})'
    )
    log.info(f'- Setup <00> Cut (limit) longer text in logs ({setup.cut})')
    log.info('-' * 84)

    return setup


def main(options: argparse.Namespace) -> int:
    """Drive the transactions."""

    if not options.token and not TOKEN:
        log.error(f'No secret token or pass phrase given, please set {APP_ENV}_TOKEN accordingly')
        return 2

    if options.trace:
        logging.getLogger().setLevel(logging.DEBUG)
    elif options.debug:
        log.setLevel(logging.DEBUG)
    cfg = setup_twenty_seven(options=options)

    # Belt and braces:
    has_failures = False

    # Here we start the timer for the session:
    start_time = dti.datetime.now(tz=dti.timezone.utc)
    start_ts = start_time.strftime(TS_FORMAT_PAYLOADS)
    context: Context = {
        'target': cfg.target_url,
        'mode': f'{"cloud" if cfg.is_cloud else "on-site"}',
        'project': cfg.target_project,
        'scenario': cfg.scenario,
        'identity': cfg.identity,
        'start_time': start_time,
    }
    store = Store(context=context, setup=cfg, folder_path=cfg.storage_path)
    log.info(f'# Starting ticket creation at ({start_ts})')
    log.info('- Step <01> LOGIN')
    clk, service = actions.login(cfg.target_url, cfg.user, password=cfg.token, is_cloud=cfg.is_cloud)
    log.info(f'^ Connected to upstream service; CLK={clk}')
    store.add('LOGIN', True, clk)

    log.info('- Step <02> SERVER_INFO')
    try:
        clk, server_info = actions.get_server_info(service)
        log.info(f'^ Retrieved upstream server info cf. [SRV]; CLK={clk}')
        store.add('SERVER_INFO', True, clk, str(server_info))
    except Exception as e:  # noqa
        log.error(f'^ Failed to retrieve upstream server info cf. [SRV]')

    log.info('- Step <03> PROJECTS')
    clk, projects = actions.get_all_projects(service)
    log.info(f'^ Retrieved {len(projects)} unarchived projects; CLK={clk}')
    store.add('PROJECTS', True, clk, f'count({len(projects)})')

    proj_env_ok = False
    if cfg.target_project:
        proj_env_ok = any((cfg.target_project == project['key'] for project in projects))

    if not proj_env_ok:
        log.error('Belt and braces - verify project selection:')
        log.info(json.dumps(sorted([project['key'] for project in projects]), indent=2))
        return 1

    first_proj_key = cfg.target_project if proj_env_ok else projects[0]['key']
    log.info(
        f'Verified target project from request ({cfg.target_project}) to be'
        f' {"" if proj_env_ok else "not "}present and set target project to ({first_proj_key})'
    )

    log.info('- Step <04> CREATE_ISSUE')
    clk, c_key = actions.create_issue_annotated(
        service, first_proj_key, kind=cfg.kind, summary=cfg.summary, description=cfg.description
    )
    log.info(f'^ Created ticket ({c_key}); CLK={clk}')
    store.add('CREATE_ISSUE', True, clk, 'original')

    log.info('- Step <05> ISSUE_EXISTS')
    clk, c_e = actions.issue_exists(service, c_key)
    log.info(f'^ Existence of ticket ({c_key}) verified with result ({c_e}); CLK={clk}')
    store.add('ISSUE_EXISTS', bool(c_e), clk, 'original')

    query = f'issue = {c_key}'
    log.info('- Step <06> EXECUTE_JQL')
    clk, c_q = actions.execute_jql(service=service, query=query)
    log.info(f'^ Executed JQL({query}); CLK={clk}')
    store.add('EXECUTE_JQL', True, clk, f'query({query.replace(c_key, "original-key")})')

    log.info('- Step <07> ADD_COMMENT')
    if cfg.comment:
        clk, _ = actions.add_comment(service=service, issue_key=c_key, comment=cfg.comment)
        comment = cfg.comment if len(cfg.comment) < 50 else f'{cfg.comment[:50]} ...'
        comment = comment.replace(NL, '$NL')
        log.info(f'^ Added comment ({comment}) to ticket {c_key}; CLK={clk}')
        store.add('ADD_COMMENT', True, clk, 'original')
    else:
        log.info(f'^ Skipped commenting to ticket {c_key}; CLK={clk}')

    log.info('- Step <08> UPDATE_ISSUE_FIELD')
    if cfg.labels:
        clk = actions.update_issue_field(service, c_key, labels=cfg.labels)
        log.info(f'^ Updated original {c_key} issue field of labels to ({cfg.labels}); CLK={clk}')
        store.add('UPDATE_ISSUE_FIELD', True, clk, 'original')
    else:
        log.info(f'^ Skipped labeling of ticket {c_key}; CLK={clk}')

    log.info('- Step <09> GET_ISSUE_STATUS')
    clk, c_iss_state = actions.get_issue_status(service, c_key)
    c_is_todo = c_iss_state.lower() == "To Do"
    log.info(
        f'^ Retrieved status of the ticket {c_key} as ({c_iss_state})'
        f' with result (is_todo == {c_is_todo}); CLK={clk}'
    )
    store.add('GET_ISSUE_STATUS', c_is_todo, clk, f'duplicate({c_iss_state})')

    log.info('- Step <10> SET_ORIGINAL_ESTIMATE')
    if cfg.estimate:
        clk, ok = actions.set_original_estimate_string(service, c_key, dur=cfg.estimate)
        log.info(
            f'^ Added ({cfg.estimate}) duration as original estimate to ticket {c_key} with result ({ok}); CLK={clk}'
        )
        store.add('SET_ORIGINAL_ESTIMATE', ok, clk, 'original')
    else:
        log.info(f'^ Skipped estimation of ticket {c_key}; CLK={clk}')

    log.info('- Step <11> LOAD_ISSUE')
    clk, x_iss = actions.load_issue(service, c_key)
    log.info(f'^ Loaded issue {c_key}; CLK={clk}')
    log.debug(json.dumps(x_iss, indent=2))
    store.add('LOAD_ISSUE', True, clk, 'original')

    # Here we stop the timer for the session:
    end_time = dti.datetime.now(tz=dti.timezone.utc)
    end_ts = end_time.strftime(TS_FORMAT_PAYLOADS)
    log.info(f'# Ended creation of ticket at ({end_ts})')
    log.info(f'Creation of ticket took {(end_time - start_time)} h:mm:ss.uuuuuu')
    log.info('-' * 84)

    log.info('# References:')
    log.info(f'[SRV]          Server info is ({server_info})')
    log.info('-' * 84)

    log.info('Dumping records to store...')
    store.dump(end_time=end_time, has_failures=has_failures)
    log.info('-' * 84)

    log.info('OK')
    log.info('=' * 84)

    return 0
