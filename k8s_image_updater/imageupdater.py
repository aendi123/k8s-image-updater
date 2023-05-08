import json
from pathlib import Path

import requests
from helpers.image import Image
from helpers.file import File
from helpers.registrylogin import RegistryLogin

import argparse
import re
import yaml

SUPPORTED_K8S_TYPES='Deployment|DaemonSet|StatefulSet'

def run(args):
    path = Path(args.path)
    path = path.resolve()

    registrylogins = []
    if args.dockerconfigjson:
        dockerconfigjson = Path(args.dockerconfigjson)
        dockerconfigjson = dockerconfigjson.resolve()
        with open(dockerconfigjson, 'r') as dockerconfigjson:
            content = json.loads(dockerconfigjson.read())
            for registry in content['auths']:
                registrylogins.append(RegistryLogin(registry, content['auths'][registry]['auth']))

    if args.exclude:
        all_yaml_files = list_all_yaml_files(path, args.exclude)
    else:
        all_yaml_files = list_all_yaml_files(path)

    supported_yaml_files = list_supported_yaml_files(all_yaml_files)
    get_images_of_supported_yaml_files(supported_yaml_files)

    get_newest_images(supported_yaml_files)


def list_all_yaml_files(path, exclude=''):
    all_yaml_files = []

    for file in path.rglob('*.yaml'):
        file = file.resolve()
        if not exclude == '':
            if not re.match(exclude, str(file)):
                all_yaml_files.append(Path(file))
        else:
            all_yaml_files.append(Path(file))
    for file in path.rglob('*.yml'):
        file = file.resolve()
        if not exclude == '':
            if not re.match(exclude, str(file)):
                all_yaml_files.append(Path(file))
        else:
            all_yaml_files.append(Path(file))

    return all_yaml_files


def list_supported_yaml_files(yaml_files):
    supported_yaml_files = []

    for yaml_file in yaml_files:
        with open(yaml_file, 'r') as yaml_file:
            all_yamls = yaml.safe_load_all(yaml_file)
            for yaml_data in all_yamls:
                try: 
                    if re.match(SUPPORTED_K8S_TYPES, yaml_data['kind']):
                        supported_yaml_files.append(File(Path(yaml_file.name)))
                except (KeyError, TypeError):
                    pass
    
    return supported_yaml_files


def get_images_of_supported_yaml_files(supported_yaml_files):
    for supported_yaml_file in supported_yaml_files:
        with open(supported_yaml_file.path, 'r') as open_supported_yaml_file:
            all_yamls = yaml.safe_load_all(open_supported_yaml_file)
            for yaml_data in all_yamls:
                    try: 
                        if re.match(SUPPORTED_K8S_TYPES, yaml_data['kind']):
                            containers = yaml_data['spec']['template']['spec']['containers']
                            for container in containers:
                                supported_yaml_file.addImage(Image((container['image'])))
                    except (KeyError, TypeError):
                        pass


def get_newest_images(supported_yaml_files):
    for file in supported_yaml_files:
        print(f'Path: {file.path}')
        file.printImages()
        for image in file.images:
            if (image.registry == "docker.io"):
                registry = "hub.docker.com"
            else:
                registry = image.registry
            tags = requests.get(f"https://{registry}/v2/repositories/{image.imagename}/tags/?page_size=1000")
            tags.raise_for_status()
            tags.encoding = tags.apparent_encoding
            tags = tags.json()
            print(tags)
        print()


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', nargs='?', default=Path.cwd(), help='path to search for YAML files')
    parser.add_argument('-e', '--exclude', action='store', help='provide regex pattern to exclude while searching for YAML files')
    parser.add_argument('-c', '--dockerconfigjson', action='store', help='file containing docker config to login into private registries')
    return parser


def main(args=None):
    parsed = get_parser().parse_args(args)
    run(parsed)


if __name__ == '__main__':
    main()