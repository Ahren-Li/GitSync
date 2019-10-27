#!/usr/bin/env python3

from __future__ import print_function
import os
import sys

if os.path.dirname(__file__):
    os.chdir(os.path.dirname(__file__))

from git import Repo
from git import RemoteProgress


class MyProgressPrinter(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        send = '\r'
        if op_code & RemoteProgress.END:
            send = ',' + RemoteProgress.DONE_TOKEN + '\n'

        op_code = op_code & RemoteProgress.OP_MASK
        if op_code == RemoteProgress.COUNTING:
            print('Counting objects: %d %s' % (cur_count, str(message)), end=send)
        elif op_code == RemoteProgress.COMPRESSING:
            print('Compressing objects: %d%% (%d/%d) %s' % ((cur_count/max_count) * 100, cur_count,
                                                            max_count, str(message)), end=send)
        elif op_code == RemoteProgress.WRITING:
            print('Writing objects: %d%% (%d/%d) %s' % ((cur_count/max_count) * 100, cur_count,
                                                        max_count, str(message)), end=send)
        elif op_code == RemoteProgress.RESOLVING:
            print('remote: Resolving deltas: %d%% (%d/%d) %s' % ((cur_count/max_count) * 100, cur_count,
                                                                 max_count, str(message)), end=send)


def do_git(path, url):
    name = url.split('/')[-1]
    if ".git" not in name:
        name = name + ".git"
    git_path = path + "/" + name
    print("do " + url)
    if not os.path.exists(git_path):
        bare_repo = Repo.init(os.path.join(path, name), bare=True)
    else:
        bare_repo = Repo(git_path)

    try:
        remote = bare_repo.remote('backup')
        if url not in remote.urls:
            remote.add_url(url)
    except ValueError:
        remote = bare_repo.create_remote('backup', url)
    finally:
        pass
    remote.fetch(refspec='refs/heads/*:refs/heads/*', progress=MyProgressPrinter())


def do_backup(path):
    git_list = open(path + "/git-project")
    while 1:
        line = git_list.readline()
        if not line:
            break
        line = line.replace('\n', '')
        line_split = line.split(' ')
        if len(line_split) > 1 and line_split[1]:
            path = path + "/" + line_split[1]
            if not os.path.exists(path):
                os.makedirs(path, 0o664)
        do_git(path, line_split[0])
    git_list.close()


def check_backup(path):
    if os.path.exists(path + "/git-project"):
        return 1
    return 0


def _main(argv):
    for s in os.listdir("."):
        if os.path.isdir(s) & check_backup(s):
            do_backup(s)


if __name__ == '__main__':
    _main(sys.argv[1:])

