"""
Helper script that manages several aspects of the project.
Each topic is put into a separate action.
"""

from argparse import ArgumentParser
from build import ProjectBuilder
from datetime import datetime
from os import getcwd
from pathlib import Path
from subprocess import PIPE, Popen

from util.logging import Ansi, get_logger, LogLevel
from version import MAJOR, MINOR, PATCH, BRANCH, HASH

SOURCE_DIR = Path(__file__).parent
ROOT_DIR = SOURCE_DIR.parent.parent
VERSION_TEMPLATE = str(
    'MAJOR: int = {MAJOR:d}\n'  # Number of releases
    'MINOR: int = {MINOR:d}\n'  # Number of features (MRs or PRs)
    'PATCH: int = {PATCH:d}\n'  # Number of commits since HASH
    'HASH: str = \'{HASH:s}\'\n'
    'DATE: str = \'{DATE:s}\'\n'
    'BRANCH: str = \'{BRANCH:s}\'\n'
    'NUMBER: tuple[int, int, int] = ({MAJOR}, {MINOR:d}, {PATCH:d})\n'
    'STRING: str = \'{MAJOR:02d}.{MINOR:02d}.{PATCH:06d}_{HASH:s}_{BRANCH:s}_{DATE:s}\'\n'
)

logger = get_logger('make', ansi_style=True)


def run(args, cwd: Path = Path(getcwd())):
    # yapf: disable
    proc = Popen(
        args,
        cwd=str(cwd),
        stdout=PIPE,
        stderr=PIPE,
        text=True,
        bufsize=1
    )
    # yapf: enable

    logger.info(f'Run {Ansi.bold(" ".join(args))}')

    stdout = ''
    for line in proc.stdout:
        line = line.strip()
        if line:
            logger.info(line)
            stdout += line

    stderr = ''
    for line in proc.stderr:
        line = line.strip()
        if line:
            logger.error(line)
            stderr += line

    proc.wait()

    return proc.returncode, stdout, stderr


class Git:

    def __init__(self, path: Path = Path(getcwd())):
        self.args = []
        self.cwd = path

    def _run(self, *args):
        _, stdout, _ = run(['git'] + list(args), cwd=self.cwd)
        return stdout.strip()

    def add(self, *files: str) -> str:
        return self._run('add', ' '.join(files))

    def branch(self) -> str:
        return self._run('rev-parse', '--abbrev-ref', 'HEAD')

    def commits(self, source: str, target: str) -> int:
        return int(self._run('rev-list', '--count', f'{source}..{target}'))

    def commit(self, msg: str) -> str:
        return self._run('commit', '-m', msg)

    def hash(self, short: bool = True) -> str:
        return self._run('rev-parse', '--short' if short else '', 'HEAD')

    def push(self, remote: str) -> str:
        return self._run('push', remote)

    def tag(self, tag: str, remote: str) -> tuple[str, str]:
        tag_msg = self._run('tag', tag)
        push_msg = self._run('push', remote, tag)
        return tag_msg, push_msg


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-l', '--log-level', default=LogLevel.Info, choices=list(LogLevel))

    actions = parser.add_subparsers(dest='action')

    build_action = actions.add_parser('build')
    build_action.add_argument('-d', '--deploy', action='store_true', default=False)

    docs_action = actions.add_parser('docs')
    docs_action.add_argument('-a', '--autogen', action='store_true', default=False)
    docs_action.add_argument('-b', '--build', action='store_true', default=False)

    format_action = actions.add_parser('format')
    format_action.add_argument('-c', '--code', type=Path, default=Path(getcwd()))

    git_action = actions.add_parser('git')
    git_action.add_argument('-a', '--add', type=str, nargs='+')
    git_action.add_argument('-c', '--commit', type=str)
    git_action.add_argument('-p', '--push', action='store_true', default=False)
    git_action.add_argument('-t', '--tag', action='store_true', default=False)

    version_action = actions.add_parser('version')
    version_action.add_argument('-i', '--increment', type=str, choices=['major', 'minor'])

    args = parser.parse_args()

    logger.setLevel(args.log_level.upper())
    for key, arg in args.__dict__.items():
        logger.debug(f'{key:15s} {Ansi.bold(str(arg))}')

    git = Git()

    if args.action == 'build':
        ProjectBuilder(ROOT_DIR).build('wheel', output_directory='build')

        if args.deploy:
            run(
                ['python', '-m', 'twine', 'upload', '--repository', 'pypi', 'build/*'],
                cwd=ROOT_DIR,
            )

    if args.action == 'docs':
        if args.autogen:
            run(
                ['sphinx-apidoc', '-o', 'docs/source', 'source/pymunge'],
                cwd=ROOT_DIR,
            )

        if args.build:
            run(
                ['sphinx-build', '-b', 'html', '-E', 'docs/source', 'docs/build'],
                cwd=ROOT_DIR,
            )

    if args.action == 'format':
        location = str(args.code)
        run(
            ['yapf', '--style', '.style.yapf', '--in-place', '--recursive', location],
            cwd=ROOT_DIR,
        )

    if args.action == 'git':
        if args.add:
            git.add(args.add)
        if args.commit:
            git.commit(args.commit)
        if args.push:
            git.push('origin')
        if args.tag:
            git.tag(f'v{MAJOR}.{MINOR}', 'origin')

    if args.action == 'version':
        if args.increment:
            if args.increment == 'major':
                MAJOR += 1
            elif args.increment == 'minor':
                MINOR += 1

        PATCH += git.commits(HASH, git.hash())
        BRANCH = git.branch()
        HASH = git.hash(short=True)
        DATE = datetime.now().strftime('%Y-%m-%d-%H-%M%z')

        with open(SOURCE_DIR / 'version.py', 'w+') as version_file:
            version_file.write(
                VERSION_TEMPLATE.format(
                    MAJOR=MAJOR,
                    MINOR=MINOR,
                    PATCH=PATCH,
                    HASH=HASH,
                    DATE=DATE,
                    BRANCH=BRANCH,
                )
            )

        new_version = f'{MAJOR:02d}.{MINOR:02d}.{PATCH:06d}_{HASH:s}_{BRANCH:s}_{DATE:s}'
        logger.info(f'Sync version: {Ansi.bold(new_version)}')
