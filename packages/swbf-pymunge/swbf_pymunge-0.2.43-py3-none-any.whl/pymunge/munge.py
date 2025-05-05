from argparse import ArgumentParser, Namespace
from os import getcwd
from pathlib import Path
from sys import exit

from app.munger import Munger
from util.logging import LogLevel, get_logger
from version import STRING as VERSION_STRING

BASE_DIR = Path(__file__).parent
CONFIG = Namespace(kwargs={''})


def MungePath(arg: str) -> Path:
    path = Path(arg)
    if not path.exists():
        path.mkdir()  # TODO: should parents be created and existing folders overwritten?
    return path.resolve()


def main():
    parser = ArgumentParser('pymunge')
    parser.add_argument('-a', '--ansi-style', action='store_true', default=False)
    parser.add_argument('-b', '--binary-dir', type=MungePath, default=Path(getcwd()))
    parser.add_argument('-c', '--config', type=Path, default=Path(getcwd()))
    parser.add_argument('-d', '--dry-run', action='store_true', default=False)
    parser.add_argument('-i', '--interactive', action='store_true', default=False)
    parser.add_argument('-l', '--log-level', type=str, default=LogLevel.Info, choices=list(LogLevel))
    parser.add_argument('-m', '--munge-mode', type=str, default=Munger.Mode.Full, choices=list(Munger.Mode))
    parser.add_argument('-n', '--no-gui', action='store_true', default=False)
    parser.add_argument('-p', '--platform', type=str, default=Munger.Platform.PC, choices=list(Munger.Platform))
    parser.add_argument('-r', '--resolve-dependencies', action='store_true', default=True)
    parser.add_argument('-s', '--source', type=MungePath, default=Path(getcwd()))
    parser.add_argument('-t', '--target', type=MungePath)
    parser.add_argument('-v', '--version', action='store_true', default=False)

    subparsers = parser.add_subparsers(dest='tool')

    odfmunge = subparsers.add_parser(Munger.Tool.OdfMunge)

    scriptmunge = subparsers.add_parser(Munger.Tool.ScriptMunge)

    args = parser.parse_args()

    if args.version:
        print(VERSION_STRING)
        return 0

    logger = get_logger('pymunge', path=Path(getcwd()), level=args.log_level, ansi_style=args.ansi_style)

    logger.info(f'Munger config:')
    with logger:
        for key, arg in args.__dict__.items():
            logger.info(f'{key:20s} {arg}')

    munger = Munger(args, logger)
    #munger.run()
    munger.munge()


if __name__ == '__main__':
    exit(main())
