"""Utilities to track and record file system."""

import os
import uuid
import shutil
import json
import re

TFSTUDIO_EXPERIMENT = 'TFSTUDIO_EXPERIMENT'


def get_experiment_key():
    if TFSTUDIO_EXPERIMENT not in os.environ.keys():
        key = str(uuid.uuid4())
        setup_experiment(os.environ, key)
    return os.environ[TFSTUDIO_EXPERIMENT]


def setup_experiment(env, experiment, clean=True):
    env[TFSTUDIO_EXPERIMENT] = experiment.key

    _setup_model_directory(experiment.key, clean)

    amapping = {}
    for tag, art in experiment.artifacts.iteritems():
        if art.get('local') is not None:
            amapping[tag] = art['local']

        with open(_get_artifact_mapping_path(experiment.key), 'w') as f:
            json.dump(amapping, f)


def get_artifact(tag):
    with open(_get_artifact_mapping_path(), 'r') as f:
        a_mapping = json.load(f)

    return a_mapping[tag]


def get_model_directory(experiment_name=None):
    return get_artifact_cache('modeldir', experiment_name)


def get_artifact_cache(tag, experiment_name=None):
    assert tag is not None

    if tag.startswith('experiments/'):
        experiment_name = re.sub(
            '\Aexperiments/',
            '',
            re.sub(
                '/[^/]*\Z',
                '',
                tag))
        tag = re.sub('.tgz\Z', '', re.sub('.*/', '', tag))

    if tag.startswith('blobstore/'):
        return get_blob_cache(tag)

    experiment_name = experiment_name if experiment_name else \
        os.environ[TFSTUDIO_EXPERIMENT]
    retval = os.path.join(
        os.path.expanduser('~'),
        '.tfstudio/experiments',
        experiment_name,
        tag
    )

    # if not os.path.exists(retval):
    #    os.makedirs(retval)
    return retval


def get_blob_cache(blobkey):
    blobkey = re.sub('.tgz\Z','', blobkey)
    if blobkey.startswith('blobstore/'):
        blobkey = re.sub('.*/', '', blobkey)

    return os.path.join(
        os.path.expanduser('~'),
        '.tfstudio/blobcache',
        blobkey
    )


def _get_artifact_mapping_path(experiment_name=None):
    experiment_name = experiment_name if experiment_name else \
        os.environ[TFSTUDIO_EXPERIMENT]

    basepath = os.path.join(
        os.path.expanduser('~'),
        '.tfstudio/artifact_mappings/',
        experiment_name
    )
    if not os.path.exists(basepath):
        os.makedirs(basepath)

    return os.path.join(basepath, 'artifacts.json')


def _setup_model_directory(experiment_name, clean=False):
    path = get_model_directory(experiment_name)
    if clean and os.path.exists(path):
        shutil.rmtree(path)

    if not os.path.exists(path):
        os.makedirs(path)


def get_queue_directory():
    queue_dir = os.path.join(os.path.expanduser('~'),
                             '.tfstudio/queue')
    if not os.path.exists(queue_dir):
        os.makedirs(queue_dir)

    return queue_dir


def get_tensorboard_dir(experiment_name=None):
    return get_artifact_cache('tb', experiment_name)
