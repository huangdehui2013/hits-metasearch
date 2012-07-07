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


def mk_nodes(allruns):
    '''Return (set, set) of (sysids, docids).'''
    doc_field = lib.trec.DOC
    docs = set()
    for arr in allruns.itervalues():
        docs |= set(arr[doc_field])
    return set(graph.keys()), docs


def mk_edges(allruns, systup, doctup):
    '''Return an adjacency matrix with the edges from systems to documents.

    Return a numpy.array shaped (# sys, # docs) containing booleans.

    '''
    doc_field = lib.trec.DOC
    edges = numpy.zeros([len(systup),len(doctup)], dtype=numpy.bool)
    docindexes = {docid:i for i, docid in enumerate(doctup)}
    for sys_i, sysid in enumerate(systup):
            sysdocs = allruns[sisid][doc_field]
            for docid in sysdocs:
                doc_i = docindexes[docid]
                edges[sys_i][doc_i] = True
            sysdocs = None
    del docindexes
    return edges


##############################################################################
## Main


if __name__ == '__main__':
    unittest.main()
    # args
    try:
        queryno = int(sys.argv[1])
        npzpath = sys.argv[2]
        assert os.path.isdir(npzpath)
    except:
        print 'USAGE: python {} INT PATH'.format(__file__)
        print
        print 'INT  - query number'
        print 'PATH - directory with *.npz files produced by compress.py'
        exit()
    # data
    runs = lib.trec.load_comp_system_dir(npzpath, queryno)
    if not runs:
        print 'No runs were loaded.'
        exit()
    # graph nodes
    sysset, docset = mk_nodes(runs)
    systup = tuple(sorted(syss))
    doctup = tuple(sorted(docs))
    del sysset
    del docset
    # graph edges
    sys_outlinks = mk_edges(runs, systup, doctup)
    doc_inlinks = sys_outlinks.transpose()
    # perform analysis
    print len(authtup), 'authorities;', len(hubtup), 'hubs'
    k=[3]
    print hits(runs, hits_update,
        lambda *_, **__: k.append(k.pop()-1) or k[0]>=0)
    # close npz files


##############################################################################
# eof
