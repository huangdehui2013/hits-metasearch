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


##############################################################################
## HITS algorithm


def hits_update(oldauths, oldhubs, authinlinks, huboutlinks, auxdata):
    # auths [x <- I()]
    # hubs  [y <- O()]
    # an auth score is the sum of the scores of the hubs which point to it
    # a hub score is the sum of the scores of the auths to which it points
    auths = oldauths.copy()
    for authi, inlinks in enumerate(authinlinks):
        auths[authi] = 
    hubs = oldhubs.copy()
    return auths, hubs


def hits(graph, update_fn, stopping_fn):
    '''Calculate hub and authority scores; end when stopping_fn returns true.

    graph:
        {str: 1darr<2>, ...}
        {hubid: <authid,?>, ...}
    update_fn:
        [1darr 1darr 2darr 2darr graph --> (assoc, assoc)]
        [old_auths old_hubs auth_inlinks hub_outlinks --> (cur_auths, cur_hubs)]
    stopping_fn:
            True when the algorithm should stop, false otherwise
        [int 1darr 1darr --> bool]
        [iteration_number cur_auths cur_hubs --> converged]

    return:
        (1darr, 1darr)
        (final_auths, final_hubs)

    '''
    def get_authset(g):
        s = set()
        for authdat in graph.itervalues():
            authset |= set(authdat['k'])
        authtup = tuple(sorted(authset))
    del authset
    hubtup = tuple(sorted(graph.keys()))
    # report sizes
    print len(authtup), 'authorities;', len(hubtup), 'hubs'
    # characterize the graph
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
    # initialize scores to 1
    a = numpy.ones(len(auttup), dtype=numpy.float64)
    h = numpy.ones(len(hubtup), dtype=numpy.float64)
    # iteratively update scores
    for i in itertools.count(1):
        print 'Iteration', i
        # update i-1 to i
        a, h = update_fn(a, h, a_inlinks, h_outlinks, graph)
        # normalize
        # a **= 2
        # h **= 2
        a /= a.sum()
        h /= h.sum()
        # check stopping condition
        if stopping_fn(i_math, a, h):
            break
    return a, h


class TestHITS(unittest.TestCase):
    def setUp(self):
        self.graph = {
            'h1':assoc(zip('abcd', itertools.repeat(0))),
            'h2':assoc(zip('ace', itertools.repeat(0))),
        }
        self.oldauths = assoc([('a',3), ('b',1), ('c',4), ('d',3), ('e',5)])
        self.oldhubs  = assoc([('h1',3), ('h2',7)])
        self.newauths = assoc([('a',10), ('b',3), ('c',10), ('d',3), ('e',7)])
        self.newhubs  = assoc([('h1',11), ('h2',13)])
    def test__hits_update(self):
        a, h = hits_update(self.graph, self.oldauths, self.oldhubs)
        self.assertEqual(a, self.newauths)
        self.assertEqual(h, self.newhubs)


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
    npz = []
    run = {}
    for p in glob.iglob(os.path.join(npzpath, '*.npz')):
        npzfile = numpy.load(p)
        npz.append(npzfile)
        sysid = os.path.splitext(os.path.basename(p))[0]
        try:
            # extract a run for the specified query
            run[sysid] = npzfile['query' + str(queryno)]
        except KeyError:
            print 'No run for query #{} in system "{}"'.format(
                queryno, sysid)
    if run:
        print '{} runs loaded for query #{}'.format(len(run), queryno)
    else:
        print 'No runs were loaded'
        exit()
    # analysis
    k=[3]
    print hits(run, hits_update,
        lambda *_, **__: k.append(k.pop()-1) or k[0]>=0)
    # close npz files
    [f.close() for f in npz]


##############################################################################
# eof
