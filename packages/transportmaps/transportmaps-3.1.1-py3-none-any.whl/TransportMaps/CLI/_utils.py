import functools
import logging
import pickle
from pathlib import Path
from typing import Tuple, Union

import click
import fasteners
import h5py
from TransportMaps import DataStorageObject, cmdinput
from TransportMaps.Distributions import Distribution


class CLIException(BaseException):
    pass


def logged(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        logging.basicConfig()
        logging.getLogger().setLevel(kwargs['log'])
        return f(*args, **kwargs)
    return wrapper


def _lambda_str_to_list_argument(t):
    return lambda s: [s] if isinstance(s, t) else [t(ss) for ss in s.split(',')]


_GENERAL_OPTIONS = [
    click.option(
        '--input', 'path_input', required=True, type=Path,
        help='path to the file containing the target distribution '
             'the base distribution and the transport map pushing forward '
             'the base to the target.'
    ),
    click.option(
        '--overwrite', is_flag=True,
        help='whether to overwrite output if exists'
    ),
    click.option(
        '--nprocs', type=int, default=1,
        help='number of processes used for the evaluations'
    ),
    click.option(
        '--log', type=int, default=20,
        help='Log level (see logging)'
    )
]


def _general_options(f):
    return functools.reduce(lambda x, opt: opt(x), _GENERAL_OPTIONS, f)


def _ask_overwrite():
    resp = ''
    while resp.lower() not in ['y', 'n']:
        resp = cmdinput(
            'Data is already available for the required postprocess procedure. '
            'Do you want to overwrite? [y/n] '
        )
    return resp == 'y'


def _load_input(
        path_input: Path
) -> DataStorageObject:
    with open(path_input, 'rb') as in_stream:
        stg = pickle.load(in_stream)
    return stg


class H5(object):
    def __init__(
            self,
            fname: Path,
            method: str
    ):
        self.h5_lock = fasteners.InterProcessLock(str(fname) + '.lock')
        if not self.h5_lock.acquire(blocking=False):
            raise IOError(
                "ERROR: the hdf5 file is locked. " +
                "Lock: " + str(self.h5_lock)
            )
        self.h5_file = h5py.File(str(fname), method)

    def __enter__(self):
        return self.h5_file

    def __exit__(self, type, value, traceback):
        self.h5_file.close()
        self.h5_lock.release()


def _select_dist(
        stg,
        dist: str
) -> Distribution:
    if dist == 'exact-target':
        return stg.target_distribution
    elif dist == 'approx-target':
        return stg.approx_target_distribution
    elif dist == 'exact-base':
        return stg.base_distribution
    elif dist == 'approx-base':
        return stg.approx_base_distribution


def _select_dist_tuple(
        stg,
        dist: str
) -> Tuple[Distribution, Distribution]:
    if dist == 'exact-target':
        d1 = stg.target_distribution
        d2 = stg.approx_target_distribution
    elif dist == 'approx-target':
        d1 = stg.approx_target_distribution
        d2 = stg.target_distribution
    elif dist == 'exact-base':
        d1 = stg.base_distribution
        d2 = stg.approx_base_distribution
    elif dist == 'approx-base':
        d1 = stg.approx_base_distribution
        d2 = stg.base_distribution
    else:
        raise ValueError(
            f'Distribution option {dist} not recognized'
        )
    return d1, d2

