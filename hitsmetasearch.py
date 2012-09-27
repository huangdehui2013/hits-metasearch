#!ENV/bin/python


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
import argparse
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


def __edgemode_negexp():
    zerotofive = lambda r, ct: (r / ct) * 5 # Dr=0..ct; Dct=..; R=0..5
    lam = 1
    negexp = lambda x: lam * (math.e ** (-x * lam)) # Dx=0..5; R=1..0
    return lambda r, ct: negexp(zerotofive(r, ct)) # Dr=0..ct; Dct=..; R=1..0


EDGEMODE = {
    'const': None, # lambda _*: 1, # Dr=..; Dct=..; R=1
    'linear': lambda r, ct: 1 - (r / ct), # Dr=0..ct; Dct=..; R=1..0
    'negexp': __edgemode_negexp(),
}


def mk_nodes(allruns):
    '''{sysid: 1darr<docid,score>, ...} --> (sysids, docids)
       {str  : 1darr<str  ,float>, ...} --> ({str} , {str} )

    allruns is a map from sysid to the ranked list of one system and query

    '''
    docfield = lib.trec.DOC
    docs = set()
    for arr in allruns.itervalues():
        docs |= set(arr[docfield])
    return set(allruns.keys()), docs


def mk_edgeweights(allruns, sysarr, docarr, edgeweight=None):
    '''{sysid: 1darr<docid,score>, ...} 1darr<sysid> 1darr<docid> [num num --> num   ]
       {str  : 1darr<str  ,float>, ...} 1darr<str  > 1darr<str  > [rank ct --> weight]
    -->
        2darr[sysid][docid]<num    OR bool>
        2darr[str  ][str  ]<weight OR edge>

    allruns is a map from sysid to the ranked list of one system and query

    Return an adjacency matrix with the edge weights from systems to
    documents, or boolean values if no edge weight function is given.

    '''
    # let
    docfield = lib.trec.DOC
    if edgeweight is None:
        dt = numpy.bool_
        edgeweight = lambda *_: True
    else:
        dt = lib.trec.SCR_SCALAR
    # let
    edges = numpy.zeros([len(sysarr), len(docarr)], dtype=dt)
    docindexes = {docid:i for i, docid in enumerate(docarr)}
    # for
    for sys_i, sysid in enumerate(sysarr):
            sysdocs = allruns[sysid][docfield] # in ranked order
            rankct = len(sysdocs)
            for rank, docid in enumerate(sysdocs):
                doc_i = docindexes[docid]
                edges[sys_i][doc_i] = edgeweight(rank, rankct)
            sysdocs = None
    # ret
    return edges


class RatioIsOne(object):
    '''True if the ratio of vectors prev:cur are within epsilon of 1.'''
    def __init__(self, epsilon, msg=None, printto=None):
        self.eps, = numpy.array([abs(epsilon)], dtype=lib.trec.SCR_SCALAR)
        self.msg = msg
        self.prev = None
        self.printto = printto
    def __call__(self, vector):
        '''1darr<float> -> bool'''
        if self.prev is None:
            self.prev = vector
            return False
        else:
            eq = (abs(self.prev / vector - 1) < self.eps).all()
            self.prev = vector
            if self.msg:
                self.printto and print('INFO:', self.msg, file=printto)
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
                              [1, 0, 1, 0, 1]],
                              dtype=numpy.bool_)
        self.w = numpy.array([[1.0, 0.75, 0.5,                0.25, 0.0                ],
                              [1.0, 0.0,  0.6666666666666667, 0.0,  0.33333333333333337]],
                              dtype=numpy.float64)
    def test__mk_nodes(self):
        sys, docs = mk_nodes(self.runs)
        self.assertEquals(sorted(sys), self.sl)
        self.assertEquals(sorted(docs), self.dl)
    def test__mk_edges(self):
        e = mk_edgeweights(self.runs, numpy.array(self.sl), numpy.array(self.dl))
        numpy.testing.assert_equal(e, self.e)
    def test__mk_edgeweights(self):
        w = mk_edgeweights(self.runs, numpy.array(self.sl), numpy.array(self.dl),
            lambda r, ct: 1 - (r / ct))
        numpy.testing.assert_allclose(w, self.w)


def stderr(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


##############################################################################
## Main


def main_query(query, srun, iterct, edgemode):
    '''Run HITS over all systems for one query.'''
    # make graph nodes
    sysarr, docarr = [numpy.array(sorted(s)) for s in mk_nodes(srun)] # only two
    stderr('INFO: {} systems, {} documents'.format(len(sysarr), len(docarr)))
    # make graph edges and edge weights
    if edgemode == 'const':
        sys_outlinks = mk_edgeweights(srun, sysarr, docarr)
        data = dict()
    elif edgemode in {'linear', 'negexp'}:
        sys_outweights = mk_edgeweights(srun, sysarr, docarr, EDGEMODE[edgemode])
        sys_outlinks = numpy.array(sys_out, dtype=numpy.bool_)
        data = {'a_inweights': sys_outweights.transpose()}
        del sys_outweights
    else:
        exit(2)
        stderr('ERROR: unknown edgemode "{}"'.format(edgemode))
    # perform hits analysis
    docscr, sysscr = lib.hits.hits(
        sys_outlinks,
        lib.end.Countdown(iterct),
        data=data,
        printto=sys.stderr)
    # report systems
    order = numpy.argsort(sysscr)[::-1]
    stderr('INFO: Top systems')
    for scr, sysid in itertools.izip(sysscr[order][:3], sysarr[order]):
        stderr('INFO: {:< 20} {}'.format(scr, sysid))
    # report documents
    order = numpy.argsort(docscr)[::-1]
    for i, (scr, docid) in enumerate(
    itertools.izip(docscr[order][:1000], docarr[order])):
        print('{qno:d} Q0 {docid:s} {rank:d} {score:.50f} {sysid:s}'.format(
            qno=query,
            docid=docid,
            rank=(i + 1),
            score=scr,
            sysid='hm{:d}x{}'.format(iterct, edgemode)
        ))


def main(npzpath, querynos, iterct, edgequery):
    # load
    qsrun = lib.trec.load_comp_system_dir(npzpath, querynos, printto=sys.stderr)
    # run algorithm once per query
    for q, srun in qsrun.iteritems():
        if srun:
            stderr('INFO: query {}'.format(q))
            main_query(q, srun, iterct, edgequery)
        else:
            stderr('ERROR: No runs were loaded for query {}.'.format(q))


if __name__ == '__main__':
    # run tests
    if '-t' in sys.argv or '--test' in sys.argv:
        '-t' in sys.argv and sys.argv.remove('-t')
        '--test' in sys.argv and sys.argv.remove('--test')
        unittest.main()
        exit()
    # parse args
    ap = argparse.ArgumentParser(description='''Print to stdout a ranked list
    of documents for the query QNO by running HITS for Metasearch for N
    iterations. TREC systems are the "hubs" and documents are the
    "authorities".''')
    ap.add_argument('dir', metavar='DIR', help='''directory containing npz
        files produced by compress.py''')
    ap.add_argument('iterct', metavar='I', type=int, help='''number of
        iterations to run the algorithm''')
    ap.add_argument('edgetype', metavar='STR', choices=('const', 'linear',
        'negexp'), help='''how edges should decay as document rank
        increases''')
    ap.add_argument('-n', '--queries', metavar='N', nargs='*', type=int,
        help='''query numbers for which to produce a ranked list''')
    ap.add_argument('-t', '--test', action='store_true', help='''run unittests
        and exit; other arguments aren't required''')
    ns = ap.parse_args()
    if not os.path.isdir(ns.dir):
        stderr('ERROR: No such directory "{}".'.format(ns.dir))
        exit(1)
    main(ns.dir, ns.queries, ns.iterct, ns.edgetype)


##############################################################################
# eof
