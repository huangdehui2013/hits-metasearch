'''Load and process whole directories of TREC-formatted retrieval runs.'''


# future
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from codecs import open
# stdlib
import os
import sys
import glob
import itertools
import collections
# 3rd party
import numpy


QRY = b'queryno'
DOC = b'docid'
SCR = b'score'


QRY_SCALAR = '<i2' # numpy.int16
DOC_SCALAR = 'S32' # (numpy.str_, 32)
SCR_SCALAR = '<f8' # numpy.float64


def load_system(path):
    '''str --> str, ndarray

    Load the system stored at the path.

    '''
    # let
    name = os.path.splitext(path)[1][1:]
    # error
    if not name:
        raise ValueError('no name after dot in "{}"'.format(path))
    # let -- read the file
    raw = numpy.genfromtxt(
        path,
        usecols=(0, 2, 4),
        dtype=numpy.dtype([
            (QRY, QRY_SCALAR),
            (DOC, DOC_SCALAR),
            (SCR, SCR_SCALAR),
        ])
    )
    # let -- accumulate data for each query
    data = {}
    for qno in set(raw[QRY]):
        # filter to only this query's data
        qraw = raw[raw[QRY] == qno]
        # put data in a new container
        qdat = numpy.fromiter(
            itertools.izip(numpy.char.upper(qraw[DOC]), qraw[SCR]),
            dtype=numpy.dtype([
                (DOC, DOC_SCALAR),
                (SCR, SCR_SCALAR),
            ])
        )
        # sort by docid, then reverse
        ordering = numpy.argsort(qdat[DOC])[::-1]
        qdat = qdat[ordering]
        # stable sort by score, then reverse
        ordering = numpy.lexsort(  (qdat[SCR],)  )[::-1]
        qdat = qdat[ordering]
        # accum
        data['query{}'.format(qno)] = qdat
    del raw
    return name, data


def gen_system_dir(dirpath):
    '''Yield all systems in a directory.'''
    # let
    names = set()
    # loop
    for path in glob.iglob(os.path.join(dirpath, 'input.*')):
        name, data = load_system(path)
        if name in names:
            raise ValueError('duplicate systems with name "{}"'.format(name))
        else:
            names.add(name)
            yield name, data
    if not names:
        raise ValueError('no systems in "{}"'.format(dirpath))


def comp_system_dir(dirpath, outpath, printto=None):
    '''str str optional<file-like> --> None
    
    Convert a directory of TREC run files to numpy npz files.

    '''
    outpath = os.path.normpath(outpath)
    os.makedirs(outpath)
    printto and print('Compressing systems...', file=printto)
    for i, (name, data) in enumerate(gen_system_dir(dirpath)):
        outname = os.path.join(outpath, '{}.npz'.format(name))
        numpy.savez_compressed(outname, **data)
        printto and print('\r', (i + 1), end='', file=printto)
        printto and printto.flush()
    printto and print('\rCompressed', (i + 1), file=printto)


def load_comp_system_dir(dirpath, queries=None, printto=None):
    '''str [int] --> {int:      {str  : 1darr<str  ,float>, ...}, ...}
                     {querynum: {sysid: 1darr<docid,score>, ...}, ...}

    Load ranked document lists from npz files in the directory into a
    dictionary indexed:
        d[querynum][sysid] --> 1darr<docid,score>

    '''
    # npz files don't allow numerical keys..
    n2k = lambda n: 'query{:d}'.format(n)
    k2n = lambda k: int(k.replace('query', ''))
    def loadnpz(path):
        sysid, _ = os.path.splitext(os.path.basename(path))
        return sysid, numpy.load(p)
    def iterdata(sysid, npzdata):
        if queries is None:
            for k, v in npzdata.iteritems():
                yield k2n(k), v
        else:
            for n in queries:
                try:
                    yield n, npzdata[n2k(n)]
                except KeyError:
                    printto and print('No run for query #{} in system "{}"'.
                        format(n, sysid), file=printto)
    # -- inner --
    data = collections.defaultdict(dict)
    for p in glob.iglob(os.path.join(dirpath, '*.npz')):
        sysid, runs = loadnpz(p)
        for qno, run in iterdata(sysid, runs):
            data[qno][sysid] = run
    data.default_factory = None
    return data


# eof
