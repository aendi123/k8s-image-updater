import argparse
from pathlib import Path
import re

def run(args):
    path = Path(args.path)
    path = path.resolve()

    if args.exclude:
        all_yaml_files = list_all_yaml_files(path, args.exclude)
    else:
        all_yaml_files = list_all_yaml_files(path)
    
    for file in all_yaml_files:
        print(file)


def list_all_yaml_files(path, exclude=''):
    all_yaml_files = []

    for file in path.rglob('*.yaml'):
        file = file.resolve()
        if not exclude == '':
            if not re.match(exclude, str(file)):
                all_yaml_files.append(file)
        else:
            all_yaml_files.append(file)
    for file in path.rglob('*.yml'):
        file = file.resolve()
        if not exclude == '':
            if not re.match(exclude, str(file)):
                all_yaml_files.append(file)
        else:
            all_yaml_files.append(file)

    return all_yaml_files


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', nargs='?', default=Path.cwd(), help='path to search for YAML files')
    parser.add_argument('-e', '--exclude', action='store', help='provide regex pattern to exclude while searching for YAML files')
    return parser


def main(args=None):
    parsed = get_parser().parse_args(args)
    run(parsed)


if __name__ == '__main__':
    main()