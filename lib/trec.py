#!ENV/bin/python


# stdlib
import os
import sys
import glob
import itertools
# 3rd party
import numpy


QRY = 'queryno'
DOC = 'docid'
SCR = 'score'


QRY_SCALAR = '<i2' # numpy.int16
DOC_SCALAR = 'S32' # (numpy.str_, 32)
SCR_SCALAR = '<f8' # numpy.float64


def assoc(yields_twotups):
    '''Create a numpy record array with a string and a float field.'''
    return numpy.fromiter(
        yields_twotups,
        dtype=numpy.dtype([
            ('k', DOC_SCALAR),
            ('v', SCR_SCALAR),
        ])
    )


def nplist(yields_floats):
    return numpy.fromiter(
        yields_floats,
        dtype=numpy.dtype(SCR_SCALAR)
    )


def __gen_system_paths(p):
    return glob.iglob(os.path.join(p, 'input.*'))


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
        qdat = assoc(itertools.izip(numpy.char.upper(qraw[DOC]), qraw[SCR]))
        # sort by docid, then reverse
        ordering = numpy.argsort(qdat['k'])[::-1]
        qdat = qdat[ordering]
        # stable sort by score, then reverse
        ordering = numpy.lexsort(  (qdat['v'],)  )[::-1]
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
    for path in __gen_system_paths(dirpath):
        name, data = load_system(path)
        if name in names:
            raise ValueError('duplicate systems with name "{}"'.format(name))
        else:
            names.add(name)
            yield name, data
    if not names:
        raise ValueError('no systems in "{}"'.format(dirpath))


def comp_system_dir(dirpath, outpath):
    outpath = os.path.normpath(outpath)
    os.makedirs(outpath)
    print 'Compressing systems...'
    for i, (name, data) in enumerate(gen_system_dir(dirpath)):
        outname = os.path.join(outpath, '{}.npz'.format(name))
        numpy.savez_compressed(outname, **data)
        print '\r', (i + 1),
        sys.stdout.flush()
    print '\rCompressed', (i + 1)


# eof