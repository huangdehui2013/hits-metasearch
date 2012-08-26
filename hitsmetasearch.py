#!ENV/bin/python


# future
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from codecs import open
# stdlib
import sys
import glob
import os.path
import unittest
import itertools
import collections
# 3rd party
import numpy
# local
import lib.trec
import lib.hits
import lib.end


##############################################################################
## Utilities


def mk_nodes(allruns):
    '''Return (set, set) of (sysids, docids).'''
    docfield = lib.trec.DOC
    docs = set()
    for arr in allruns.itervalues():
        docs |= set(arr[docfield])
    return set(allruns.keys()), docs


def mk_edges(allruns, sysarr, docarr):
    '''Return an adjacency matrix with the edges from systems to documents.

    Return a numpy.array shaped (# sys, # docs) containing booleans.

    '''
    docfield = lib.trec.DOC
    edges = numpy.zeros([len(sysarr),len(docarr)], dtype=numpy.bool)
    docindexes = {docid:i for i, docid in enumerate(docarr)}
    for sys_i, sysid in enumerate(sysarr):
            sysdocs = allruns[sysid][docfield]
            for docid in sysdocs:
                doc_i = docindexes[docid]
                edges[sys_i][doc_i] = True
            sysdocs = None
    del docindexes
    return edges


class RatioIsOne(object):
    '''True if the ratio of vectors prev:cur are within epsilon of 1.'''
    def __init__(self, epsilon, msg=None):
        self.eps, = numpy.array([abs(epsilon)], dtype=lib.trec.SCR_SCALAR)
        self.msg = msg
        self.prev = None
    def __call__(self, vector):
        '''1darr<float> -> bool'''
        if self.prev is None:
            self.prev = vector
            return False
        else:
            eq = (abs(self.prev / vector - 1) < self.eps).all()
            self.prev = vector
            if self.msg:
                print(self.msg)
            return eq


class TestMainUtils(unittest.TestCase):
    def assoc(self, iterable):
        return numpy.fromiter(
            iterable,
            dtype=numpy.dtype([
                (lib.trec.DOC, lib.trec.DOC_SCALAR),
                (lib.trec.SCR, lib.trec.SCR_SCALAR),
            ])
        )
    def setUp(self):
        self.runs = {
            'h1':self.assoc(zip('abcd', itertools.repeat(0))),
            'h2':self.assoc(zip('ace', itertools.repeat(0))),
        }
        self.sl = ['h1', 'h2']
        self.dl = list('abcde')
        self.e = numpy.array([[1, 1, 1, 1, 0],
                              [1, 0, 1, 0, 1]], dtype=numpy.bool_)
    def test__mk_nodes(self):
        sys, docs = mk_nodes(self.runs)
        self.assertEquals(sorted(sys), self.sl)
        self.assertEquals(sorted(docs), self.dl)
    def test__mk_edges(self):
        e = mk_edges(self.runs, numpy.array(self.sl), numpy.array(self.dl))
        self.assertTrue((e == self.e).all())


##############################################################################
## Main


if __name__ == '__main__':
    # run tests
    if '-t' in sys.argv or '--test' in sys.argv:
        '-t' in sys.argv and sys.argv.remove('-t')
        '--test' in sys.argv and sys.argv.remove('--test')
        unittest.main()
        exit()
    # parse args
    try:
        npzpath = sys.argv[1]
        queryno = int(sys.argv[2])
        assert os.path.isdir(npzpath)
    except:
        print('USAGE: python {} PATH INT'.format(__file__))
        print()
        print('PATH - directory with *.npz files produced by compress.py')
        print('INT  - query number')
        exit()
    # load run data
    runs = lib.trec.load_comp_system_dir(npzpath, queryno)
    if not runs:
        print('No runs were loaded.')
        exit()
    # make graph nodes
    sysset, docset = mk_nodes(runs)
    sysarr = numpy.array(sorted(sysset))
    docarr = numpy.array(sorted(docset))
    del sysset, docset
    print(len(sysarr), 'Systems;', len(docarr), 'Documents')
    # make graph edges
    sys_outlinks = mk_edges(runs, sysarr, docarr)
    print(sys_outlinks.nbytes, 'bytes used by adjacency matrix')
    # perform hits analysis
    a_rio = RatioIsOne(0.001, msg="\tAuths satisfy")
    h_rio = RatioIsOne(0.1, msg="\tHubs satisfy")
    docscr, sysscr = lib.hits.hits(
        sys_outlinks,
        lib.end.ConditionStreak(lambda i,a,h: a_rio(a) and h_rio(h), 3)
    )
    # report
    order = numpy.argsort(sysscr)[::-1]
    print('\n'.join('{:< 20} {}'.format(*x) for x in zip(sysscr[order][:10], sysarr[order])))
    print()
    order = numpy.argsort(docscr)[::-1]
    print('\n'.join('{:< 20} {}'.format(*x) for x in zip(docscr[order][:10], docarr[order])))


##############################################################################
# eof
