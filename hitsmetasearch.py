#!ENV/bin/python


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


##############################################################################
## Utilities


def mk_nodes(allruns):
    '''Return (set, set) of (sysids, docids).'''
    docfield = lib.trec.DOC
    docs = set()
    for arr in allruns.itervalues():
        docs |= set(arr[docfield])
    return set(allruns.keys()), docs


def mk_edges(allruns, systup, doctup):
    '''Return an adjacency matrix with the edges from systems to documents.

    Return a numpy.array shaped (# sys, # docs) containing booleans.

    '''
    docfield = lib.trec.DOC
    edges = numpy.zeros([len(systup),len(doctup)], dtype=numpy.bool)
    docindexes = {docid:i for i, docid in enumerate(doctup)}
    for sys_i, sysid in enumerate(systup):
            sysdocs = allruns[sysid][docfield]
            for docid in sysdocs:
                doc_i = docindexes[docid]
                edges[sys_i][doc_i] = True
            sysdocs = None
    del docindexes
    return edges


class TestHITS(unittest.TestCase):
    def setUp(self):
        self.graph = {
            'h1':assoc(zip('abcd', itertools.repeat(0))),
            'h2':assoc(zip('ace', itertools.repeat(0))),
        }


##############################################################################
## Main


if __name__ == '__main__':
    unittest.main()
    # args
    try:
        npzpath = sys.argv[1]
        queryno = int(sys.argv[2])
        assert os.path.isdir(npzpath)
    except:
        print 'USAGE: python {} PATH INT'.format(__file__)
        print
        print 'PATH - directory with *.npz files produced by compress.py'
        print 'INT  - query number'
        exit()
    # data
    runs = lib.trec.load_comp_system_dir(npzpath, queryno)
    if not runs:
        print 'No runs were loaded.'
        exit()
    # graph nodes
    systup, doctup = (tuple(sorted(s)) for s in mk_nodes(runs))
    # graph edges
    sys_outlinks = mk_edges(runs, systup, doctup)
    x = doc_inlinks
    print x.dtype, x.shape

    exit()
    # perform analysis
    print len(authtup), 'authorities;', len(hubtup), 'hubs'
    k=[3]
    print hits(runs, hits_update,
        lambda *_, **__: k.append(k.pop()-1) or k[0]>=0)
    # close npz files


##############################################################################
# eof
