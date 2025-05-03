import os
import configparser
from io import BytesIO
from itertools import chain
from collections import OrderedDict
from ..file import read_text, remove_path, iglob, normal_path
from ..shell import shell_wrapper, shell_output


def git_parse_modules(s):
    cp = configparser.ConfigParser()
    if isinstance(s, str):
        cp.read_string(s)
    else:
        if isinstance(s, bytes):
            s = BytesIO(s)
        cp.read_file(s)
    result = OrderedDict()
    for section in cp.sections():
        submodule = section.split(' ', 1)[-1][1:-1]
        options = result[submodule] = OrderedDict()
        for k in cp.options(section):
            v = cp.get(section, k)
            options[k] = v
    return result


def git_clean_dir(path, dfx=True, git=True, root=True, verbose=1):
    modules = read_text(os.path.join(path, '.gitmodules'), default=None)
    if modules:
        subs = (os.path.join(path, v['path']) for v in git_parse_modules(modules).values())
    else:
        subs = range(0)
    for p in chain(iter([path] if root else []), iter(subs)):
        path_git = os.path.join(p, '.git')
        if os.path.exists(path_git):
            if dfx:
                shell_wrapper(f'git -C "{p}" clean -dfX')
            if git:
                remove_path(path_git)
            if verbose >= 2:
                print(f'Clean git: `{normal_path(p)}`', flush=True)
        else:
            if verbose >= 1:
                print(f'Clean git: `{normal_path(p)}` is skipped as it is not a git folder', flush=True)


def git_fetch_min(url, tag, path):
    shell_wrapper(f'git -C "{path}" clone --depth 1 --branch {tag} {url} .')
    shell_wrapper(f'git -C "{path}" submodule update --depth 1 --init --recursive')


def git_remove_tag(tag, path=None, remote=None):
    if not path:
        path = os.getcwd()
    shell_wrapper(f'git -C "{path}" tag -d {tag}')
    if remote is None:
        remote = git_list_remotes(path)
    elif isinstance(remote, str):
        remote = [remote]
    for r in remote:
        shell_wrapper(f'git -C "{path}" push {r} :refs/tags/{tag}')


def git_list_remotes(path=None):
    if not path:
        path = os.getcwd()
    command = f'git -C "{path}" remote show'
    output = shell_output(command, check=True)
    return [x for x in output.splitlines() if x]


def git_apply(src, target, status=False, ignore=True):
    if os.path.isfile(src):
        stat = '--stat' if status else ''
        ig = '--ignore-space-change --ignore-whitespace' if ignore else ''
        shell_wrapper(f'git -C "{target}" apply {ig} {stat} "{src}"')
    elif os.path.isdir(src):
        for p in iglob('*.patch', src, True):
            git_apply(p, target, status)


def git_head(head=None, path=None):
    if not path:
        path = os.getcwd()
    if head is None:
        return shell_output(f'git -C "{path}" rev-parse HEAD').strip()
    else:
        shell_wrapper(f'git -C "{path}" checkout {head}')
