"""Prints command to set environment variables from .yaydoc.yml"""
import sys
import os
import argparse
import yaml


def update_dict(base, head):
    """Recursively merge dicts"""
    # https://stackoverflow.com/a/32357112/4127836
    for key, value in head.items():
        if isinstance(base, dict):
            if isinstance(value, dict):
                base[key] = update_dict(base.get(key, {}), value)
            else:
                base[key] = head[key]
        else:
            base = {key: head[key]}
    return base


def _get_default_config(username, reponame):
    conf = {'metadata': {'projectname': reponame,
                         'version': 'development',
                         'author': username,
                        },
            'build': {'markdown_flavour': 'markdown_github',
                      'logo': '',
                      'doctheme': 'fossasia',
                     },
           }
    return conf


def _get_yaml_config():
    try:
        with open('.yaydoc.yml', 'r') as file:
            conf = yaml.safe_load(file)
    except FileNotFoundError:
        return {}
    return conf


def _export_env(commands, dictionary):
    # appends command to export environment variables from dictionary
    # keys are converted to upper case before creating variables
    fmtstr = 'export {key}="{value}"'
    for key, value in dictionary.items():
        envvar = key.upper()
        if envvar not in os.environ:
            commands.append(fmtstr.format(key=envvar, value=str(value)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('username', help='Owner of the repository')
    parser.add_argument('reponame', help='Name of the repository')
    args = parser.parse_args()

    conf = _get_default_config(args.username, args.reponame)
    update_dict(conf, _get_yaml_config())

    metadata = conf.get('metadata', {})
    build = conf.get('build', {})
    ghpages = conf.get('publish', {}).get('ghpages', {})

    commands = []
    _export_env(commands, metadata)
    _export_env(commands, build)
    _export_env(commands, ghpages)

    sys.stdout.write('\n'.join(commands) + '\n')


if __name__ == '__main__':
    main()