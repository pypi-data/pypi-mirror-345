from . import base, data, diff, remote

import argparse
import os
import subprocess
import sys
import textwrap

from . import base
from . import data
from . import diff
from . import remote

__version__ = "1.4"  # ✅ Make sure this matches your setup.py

def main():
    with data.change_git_dir('.'):
        args = parse_args()
        args.func(args)


# Forward declarations for parser
def init(args): pass
def hash_object(args): pass
def cat_file(args): pass
def write_tree(args): pass
def read_tree(args): pass
def commit(args): pass
def log(args): pass
def show(args): pass
def _diff(args): pass
def checkout(args): pass
def tag(args): pass
def branch(args): pass
def k(args): pass
def status(args): pass
def reset(args): pass
def merge(args): pass
def merge_base(args): pass
def fetch(args): pass
def push(args): pass
def add(args): pass


def parse_args():
    parser = argparse.ArgumentParser()

    # ✅ Add version flag
    parser.add_argument('--version', action='version', version=f"ugit {__version__}")

    commands = parser.add_subparsers(dest='command')
    commands.required = True

    oid = base.get_oid

    init_parser = commands.add_parser('init')
    init_parser.set_defaults(func=init)

    hash_object_parser = commands.add_parser('hash-object')
    hash_object_parser.set_defaults(func=hash_object)
    hash_object_parser.add_argument('file')

    cat_file_parser = commands.add_parser('cat-file')
    cat_file_parser.set_defaults(func=cat_file)
    cat_file_parser.add_argument('object', type=oid)

    write_tree_parser = commands.add_parser('write-tree')
    write_tree_parser.set_defaults(func=write_tree)

    read_tree_parser = commands.add_parser('read-tree')
    read_tree_parser.set_defaults(func=read_tree)
    read_tree_parser.add_argument('tree', type=oid)

    commit_parser = commands.add_parser('commit')
    commit_parser.set_defaults(func=commit)
    commit_parser.add_argument('-m', '--message', required=True)

    log_parser = commands.add_parser('log')
    log_parser.set_defaults(func=log)
    log_parser.add_argument('oid', default='@', type=oid, nargs='?')

    show_parser = commands.add_parser('show')
    show_parser.set_defaults(func=show)
    show_parser.add_argument('oid', default='@', type=oid, nargs='?')

    diff_parser = commands.add_parser('diff')
    diff_parser.set_defaults(func=_diff)
    diff_parser.add_argument('--cached', action='store_true')
    diff_parser.add_argument('commit', nargs='?')

    checkout_parser = commands.add_parser('checkout')
    checkout_parser.set_defaults(func=checkout)
    checkout_parser.add_argument('commit')

    tag_parser = commands.add_parser('tag')
    tag_parser.set_defaults(func=tag)
    tag_parser.add_argument('name')
    tag_parser.add_argument('oid', default='@', type=oid, nargs='?')

    branch_parser = commands.add_parser('branch')
    branch_parser.set_defaults(func=branch)
    branch_parser.add_argument('name', nargs='?')
    branch_parser.add_argument('start_point', default='@', type=oid, nargs='?')

    k_parser = commands.add_parser('k')
    k_parser.set_defaults(func=k)

    status_parser = commands.add_parser('status')
    status_parser.set_defaults(func=status)

    reset_parser = commands.add_parser('reset')
    reset_parser.set_defaults(func=reset)
    reset_parser.add_argument('commit', type=oid)

    merge_parser = commands.add_parser('merge')
    merge_parser.set_defaults(func=merge)
    merge_parser.add_argument('commit', type=oid)

    merge_base_parser = commands.add_parser('merge-base')
    merge_base_parser.set_defaults(func=merge_base)
    merge_base_parser.add_argument('commit1', type=oid)
    merge_base_parser.add_argument('commit2', type=oid)

    fetch_parser = commands.add_parser('fetch')
    fetch_parser.set_defaults(func=fetch)
    fetch_parser.add_argument('remote')

    push_parser = commands.add_parser('push')
    push_parser.set_defaults(func=push)
    push_parser.add_argument('remote')
    push_parser.add_argument('branch')

    add_parser = commands.add_parser('add')
    add_parser.set_defaults(func=add)
    add_parser.add_argument('files', nargs='+')

    return parser.parse_args()
