import hashlib
import os
import shutil
import json

from collections import namedtuple
from contextlib import contextmanager


# Will be initialized in cli.main()
GIT_DIR = None


@contextmanager
def change_git_dir (new_dir):
    global GIT_DIR
    old_dir = GIT_DIR
    GIT_DIR = f'{new_dir}/.ugit'
    yield
    GIT_DIR = old_dir
    
def init ():
    if os.path.exists(GIT_DIR):
        print(f"ugit repository already exists in {GIT_DIR}")
        return
    os.makedirs (GIT_DIR)
    os.makedirs (f'{GIT_DIR}/objects')


RefValue = namedtuple ('RefValue', ['symbolic', 'value'])


def update_ref (ref, value, deref=True):
    # assert not value.symbolic
    ref = _get_ref_internal (ref, deref)[0]
    assert value.value
    if value.symbolic:
        value = f'ref: {value.value}'
    else:
        value = value.value
    ref_path = f'{GIT_DIR}/{ref}'
    os.makedirs (os.path.dirname (ref_path), exist_ok=True)
    with open (ref_path, 'w') as f:
        f.write (value)



def get_ref (ref, deref=True):
    return _get_ref_internal (ref, deref)[1]

def delete_ref (ref, deref=True):
    ref = _get_ref_internal (ref, deref)[0]
    os.remove (f'{GIT_DIR}/{ref}')

def _get_ref_internal (ref,deref):
    ref_path = f'{GIT_DIR}/{ref}'
    value = None
    if os.path.isfile (ref_path):
        with open (ref_path) as f:
            value = f.read ().strip ()
    if not value:
        # If the file is empty, return None instead of recursing
        return ref, RefValue(symbolic=False, value=None)
    symbolic = bool (value) and value.startswith ('ref:')
    if symbolic:
        target = value.split(':', 1)[1].strip()
        if deref:
            if target == ref:
                return ref, RefValue(symbolic=True, value=target)
            return _get_ref_internal(target, deref=True)
        return ref, RefValue(symbolic=True, value=target)
    return ref, RefValue (symbolic=symbolic, value=value)


def iter_refs (prefix='', deref=True):
    refs = ['HEAD', 'MERGE_HEAD']
    for root, _, filenames in os.walk (f'{GIT_DIR}/refs/'):
        root = os.path.relpath (root, GIT_DIR)
        refs.extend (f'{root}/{name}' for name in filenames)

    for refname in refs:
        if not refname.startswith (prefix):
            continue
        ref = get_ref (refname, deref=deref)
        if ref.value:
            yield refname, ref

@contextmanager
def get_index ():
    index = {}
    if os.path.isfile (f'{GIT_DIR}/index'):
        with open (f'{GIT_DIR}/index') as f:
            index = json.load (f)

    yield index

    with open (f'{GIT_DIR}/index', 'w') as f:
        json.dump (index, f)

def hash_object (data, type_='blob'):
    obj = type_.encode () + b'\x00' + data
    oid = hashlib.sha1 (obj).hexdigest ()
    with open (f'{GIT_DIR}/objects/{oid}', 'wb') as out:
        out.write (obj)
    return oid


def get_object (oid, expected='blob'):
    with open (f'{GIT_DIR}/objects/{oid}', 'rb') as f:
        obj = f.read ()

    type_, _, content = obj.partition (b'\x00')
    type_ = type_.decode ()

    if expected is not None:
        assert type_ == expected, f'Expected {expected}, got {type_}'
    return content

def object_exists (oid):
    return os.path.isfile (f'{GIT_DIR}/objects/{oid}')


def fetch_object_if_missing (oid, remote_git_dir):
    if object_exists (oid):
        return
    # remote_git_dir += '/.ugit'
    shutil.copy (f'{remote_git_dir}/objects/{oid}',
                 f'{GIT_DIR}/objects/{oid}')
    
def push_object (oid, remote_git_dir):
    # remote_git_dir += '/.ugit'
    shutil.copy (f'{GIT_DIR}/objects/{oid}',
                 f'{remote_git_dir}/objects/{oid}')