from helpers.file import File
from helpers.image import Image
from natsort import natsorted
from pathlib import Path

import argparse
import os
import re
import yaml

SUPPORTED_K8S_TYPES='Deployment|DaemonSet|StatefulSet'

def run(args):
    path = Path(args.path)
    path = path.resolve()

    if args.configcsv:
        configcsv = Path(args.configcsv)
        configcsv = configcsv.resolve()
    else:
        configcsv = path / 'imageupdater.csv'

    if args.exclude:
        all_yaml_files = get_all_yaml_files(path, args.exclude)
    else:
        all_yaml_files = get_all_yaml_files(path)

    image_regex_matches = get_image_tag_regexes_from_csv(configcsv)

    supported_yaml_files = filter_for_supported_yaml_files(all_yaml_files)
    get_images_of_supported_yaml_files(supported_yaml_files, image_regex_matches)

    if args.write_newest:
        write_yaml_files_with_newest_tag(supported_yaml_files)
    

def get_all_yaml_files(path, exclude=''):
    all_yaml_files = []

    for file in list(path.rglob('*.yaml')) + list(path.rglob('*.yml')):
        file = file.resolve()
        if exclude:
            if not re.match(exclude, str(file)):
                all_yaml_files.append(Path(file))
        else:
            all_yaml_files.append(Path(file))

    return all_yaml_files


def get_image_tag_regexes_from_csv(csv_file):
    image_regex_matches = {}

    if not csv_file.exists():
        print(f'WARNING: File {csv_file} does not exist. No image regexes will be used.')
        return image_regex_matches
    
    with open(csv_file, 'r') as open_csv_file:
        for line in open_csv_file:
            image = line.strip().split(';')
            if len(image) == 2:
                image_regex_matches[image[0]] = image[1]

    return image_regex_matches


def filter_for_supported_yaml_files(yaml_files):
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


def get_images_of_supported_yaml_files(supported_yaml_files, image_regex_matches):
    for supported_yaml_file in supported_yaml_files:
        with open(supported_yaml_file.path, 'r') as open_supported_yaml_file:
            all_yamls = yaml.safe_load_all(open_supported_yaml_file)
            for yaml_data in all_yamls:
                    try: 
                        containers = yaml_data['spec']['template']['spec']['containers']
                        for container in containers:
                            image = Image((container['image']))
                            image.setNewestTag(get_newest_tag_of_image(image, image_regex_matches))
                            supported_yaml_file.addImage(image)
                    except (KeyError, TypeError):
                        pass

        print(f'Path: {supported_yaml_file.path}')
        supported_yaml_file.printImages()


def get_newest_tag_of_image(image, image_regex_matches):
    tags = os.popen(f'regctl tag ls {image.registry}/{image.imagename}').read().split('\n')

    if tags and tags[-1] == '':
        tags.pop()

    if f'{image.registry}/{image.imagename}' in image_regex_matches:
        image_regex = re.compile(image_regex_matches[f'{image.registry}/{image.imagename}'])
        tags = [tag for tag in tags if image_regex.match(tag)]
        
    tags = natsorted(tags)
    return tags[-1]


def write_yaml_files_with_newest_tag(supported_yaml_files):
    for supported_yaml_file in supported_yaml_files:
        with open(supported_yaml_file.path, 'r') as open_supported_yaml_file:
            all_yamls = list(yaml.safe_load_all(open_supported_yaml_file))
        
        for yaml_data in all_yamls:
            try:
                containers = yaml_data['spec']['template']['spec']['containers']
                for container in containers:
                    for image in supported_yaml_file.images:
                        if container['image'] == f'{image.registry}/{image.imagename}:{image.tag}':
                            container['image'] = f'{image.registry}/{image.imagename}:{image.newesttag}'
            except (KeyError, TypeError):
                pass
    
        with open(supported_yaml_file.path, 'w') as open_supported_yaml_file:
            yaml.safe_dump_all(all_yamls, open_supported_yaml_file, sort_keys=False, default_flow_style=False)


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', nargs='?', default=Path.cwd(), help='path to search for YAML files')
    parser.add_argument('-c', '--configcsv', action='store', help='provide CSV file with image names and their regex the tag has to match')
    parser.add_argument('-e', '--exclude', action='store', help='provide regex pattern to exclude while searching for YAML files')
    parser.add_argument('-w', '--write-newest', action='store_true', help='enable writing the newest tag into the YAML files')
    return parser


def main(args=None):
    parsed = get_parser().parse_args(args)
    run(parsed)


if __name__ == '__main__':
    main()