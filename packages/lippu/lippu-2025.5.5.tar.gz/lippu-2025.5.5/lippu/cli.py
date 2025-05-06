"""CLI operations for ticket (Finnish: lippo) creator."""

import argparse
import sys
from typing import List, Union

import lippu.api as api
from lippu import APP_ALIAS, APP_ENV, BASE_URL, DEBUG, IDENTITY, IS_CLOUD, PROJECT, STORE, TOKEN, USER


def parse_request(argv: List[str]) -> argparse.Namespace:
    """DRY."""
    parser = argparse.ArgumentParser(description=APP_ALIAS)
    parser.add_argument(
        '--user',
        '-u',
        dest='user',
        default=USER,
        help=f'user (default: {USER if USER else f"None, set {APP_ENV}_USER for default"})',
    )
    parser.add_argument(
        '--token',
        '-T',
        dest='token',
        default=TOKEN,
        help='token (default: ' ' set {APP_ENV}_TOKEN for default)',
    )
    parser.add_argument(
        '--target',
        '-t',
        dest='target_url',
        default=BASE_URL,
        help=f'target URL (default: {BASE_URL if BASE_URL else f"None, set {APP_ENV}_BASE_URL for default"})',
    )
    parser.add_argument(
        '--is-cloud',
        action='store_true',
        dest='is_cloud',
        default=IS_CLOUD,
        help=(
            'target is cloud instance (default: '
            f'{"True" if IS_CLOUD else f"False, set {APP_ENV}_IS_CLOUD for a different default"})'
        ),
    )
    parser.add_argument(
        '--project',
        '-p',
        dest='target_project',
        default=PROJECT,
        help=f'target project (default: {PROJECT if PROJECT else f"None, set {APP_ENV}_PROJECT for default"})',
    )
    parser.add_argument(
        '--scenario',
        '-s',
        dest='scenario',
        default='unknown',
        help='scenario for recording (default: unknown)',
    )
    parser.add_argument(
        '--identity',
        '-i',
        dest='identity',
        default=IDENTITY if IDENTITY else 'adhoc',
        help=(
            'identity of take for recording'
            f' (default: {IDENTITY if IDENTITY else f"adhoc, set {APP_ENV}_IDENTITY for default"})'
        ),
    )
    parser.add_argument(
        '--out-path',
        '-o',
        dest='out_path',
        default=STORE if STORE else 'store',
        help=(
            'output folder path for recording'
            f' (default: {STORE if STORE else f"store, set {APP_ENV}_STORE for default"})'
        ),
    )
    parser.add_argument(
        '--kind',
        '-K',
        dest='kind',
        default='Task',
        help='kind of ticket (type of Task, Artifact, Bug, ...)',
    )
    parser.add_argument(
        '--summary',
        '-S',
        dest='summary',
        default='Needing a title ...',
        help='summary for ticket (maximal length 254 chars)',
    )
    parser.add_argument(
        '--description',
        '-D',
        dest='description',
        default='Needing a description ...',
        help='description for ticket (maximal length 32767 chars)',
    )
    parser.add_argument(
        '--labels',
        '-L',
        dest='labels',
        default='',
        help='labels for ticket (as comma or space separated values string)',
    )
    parser.add_argument(
        '--comment',
        '-C',
        dest='comment',
        default='',
        help='comment for ticket',
    )
    parser.add_argument(
        '--estimate',
        '-E',
        dest='estimate',
        default='',
        help='original estimate for ticket',
    )
    parser.add_argument(
        '--cut',
        '-c',
        action='store_true',
        dest='cut',
        default=False,
        help='cut (limit) text info in logs (default: "False")',
    )
    parser.add_argument(
        '--debug',
        '-d',
        action='store_true',
        dest='debug',
        default=DEBUG,
        help=(
            'emit debug level information (default: '
            f'{"True" if DEBUG else f"False, set {APP_ENV}_DEBUG for a different default"})'
        ),
    )
    parser.add_argument(
        '--trace',
        action='store_true',
        dest='trace',
        default=False,
        help='hand down debug level request to imported modules (default: "False")',
    )
    return parser.parse_args(argv)


# pylint: disable=expression-not-assigned
def main(argv: Union[List[str], None] = None) -> int:
    """Delegate processing to functional module."""
    argv = sys.argv[1:] if argv is None else argv

    return api.main(parse_request(argv))
