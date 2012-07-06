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
import treclib


def mk_nodes():
    #
    authset = set()
    for authdat in graph.itervalues():
        authset |= set(authdat['k'])
    authtup = tuple(sorted(authset))
    del authset
    hubtup = tuple(sorted(graph.keys()))


def mk_edges():
    #
    a_inlink = np.zeros([len(auttup),len(hubtup)], dtype=numpy.bool)
    authindexes = {authid:i for i, authid in enumerate(authtup)}
    for hubi, hubid in enumerate(hubtup):
            hublinks = graph[hubid]['k']
            for authid in links:
                authi = authindexes[authid]
                a_inlink[authi][hubi] = True
            hublinks = None
    del authindexes
    h_outlink = a_inlink.transpose()


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
    # open npz files
    # perform analysis
    print len(authtup), 'authorities;', len(hubtup), 'hubs'
    k=[3]
    print hits(runs, hits_update,
        lambda *_, **__: k.append(k.pop()-1) or k[0]>=0)
    # close npz files


##############################################################################
# eof
