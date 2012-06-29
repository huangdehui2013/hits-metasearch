#!ENV/bin/python


import sys
import glob
import os.path
import itertools
# 3rd party
import numpy
# local
import treclib


##############################################################################
## HITS algorithm


def normalized(assoc):
    '''Return a copy of the assoc with the values normalized to 1.'''
    a = assoc.copy()
    a['v'] /= a['v'].sum()
    return a


def hits_update(g, oldauts, oldhubs):
    # an aut score is the sum of the scores of the hubs which point to it
    # a hub score is the sum of the scores of the auts to which it points
    return oldauts, oldhubs


def hits(graph, update_fn, stopping_fn):
    '''Calculate hub and authority scores; end when stopping_fn returns true.

    A ScrA is a <assoc:str,float>.

    graph:
        {str: <assoc:str,?>, ...}
        {hubid: <assoc:authid,?>, ...}
    update_fn:
        [graph ScrA ScrA --> (ScrA, ScrA)]
        [graph old_auts old_hubs --> (cur_auts, cur_hubs)]
    stopping_fn:
        [int ScrA ScrA --> bool]
        [iteration_number cur_auts cur_hubs --> converged]

    return:
        (ScrA, ScrA)
        (final_auts, final_hubs)

    '''
    # get aut and hub sets
    auttup = set()
    for autdat in graph.itervalues():
        auttup |= set(autdat['k'])
    auttup = tuple(sorted(auttup))
    hubtup = tuple(sorted(graph.keys()))
    # report sizes
    print len(auttup), 'authorities;', len(hubtup), 'hubs'
    # initialize ScrAssoc(s) to 1
    a = treclib.assoc((s, 1) for s in auttup)
    h = treclib.assoc((s, 1) for s in hubtup)
    # iterate
    for cs_i in itertools.count():
        math_i = cs_i + 1
        print 'Iteration', math_i
        # auts [x <- I()]
        # hubs [y <- O()]
        a, h = update_fn(graph, a, h) # i-1 becomes i
        # normalize
        # a['k'] **= 2
        # h['k'] **= 2
        a = normalized(a)
        h = normalized(h)
        # check stopping condition
        if stopping_fn(math_i, a, h):
            break
    return a, h


##############################################################################
## Main functions


if __name__ == '__main__':
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
