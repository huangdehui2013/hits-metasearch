'''Implement HITS in a general way using callbacks.'''


# future
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from codecs import open
# stdlib
import time
import unittest
import itertools
# 3rd party
import numpy


def hits_update(a_old, h_old, a_inlinks, h_outlinks, a_inweights=None):
    '''Update authority and hub scores.

    1darr<num> 1darr<num> 2darr<bool> 2darr<bool> (2darr<float>  ) --> (1darr<num>, 1darr<num>)
    old_auths  old_hubs   auths_in    hub_out     (auth_inweights) --> (cur_auths,  cur_hubs  )

    '''
    assert a_old.shape[0], h_old.shape[0] == a_inlinks.shape
    assert a_inlinks.shape == tuple(reversed(h_outlinks.shape))
    if a_inweights is not None:
        assert a_inlinks.shape == a_inweights.shape
    # a hub score is the sum of the scores of the auths to which it points
    h = numpy.fromiter(
        [a_old[m].sum() for m in h_outlinks],
        dtype=h_old.dtype, count=h_old.shape[0])
    #
    if a_inweights is None:
        # an auth score is the sum of the scores of the hubs which point to it
        a = numpy.fromiter(
            [h_old[m].sum() for m in a_inlinks],
            dtype=a_old.dtype, count=a_old.shape[0])
    else:
        # an auth score is the linear combination of the hub scores which
        # point to it and the weight on the edge from each hub to the auth
        a_in = itertools.izip(a_inlinks, a_inweights)
        a = numpy.fromiter(
            [numpy.vdot(h_old[m], w[m]) for m, w in a_in],
            dtype=a_old.dtype, count=a_old.shape[0])
    #
    return a, h


def hits(h_out, stopping_fn, update_fn=hits_update, sqrnorm=False,
    printto=None):
    '''Calculate hub and authority scores; end when stopping_fn returns true.

    h_out
        2darr<bool or float>
        An adjacency matrix indexed [hub][auth] where edges are indicated by
        True or a value greater than 0.0.

    stopping_fn
        [int              1darr<num> 1darr<num> --> bool     ]
        [iteration_number cur_auths  cur_hubs   --> continue?]
        The algorithm will continue while this function returns False.

    (update_fn)
        [1darr<num> 1darr<num> 2darr<bool> 2darr<bool> (2darr<float>  ) --> (1darr<num>, 1darr<num>)]
        [old_auths  old_hubs   auths_in    hub_out     (auth_inweights) --> (cur_auths,  cur_hubs  )]
        Executed each iteration to update hub and authority scores.

    (sqrnorm)
        bool
        Should we normalize the square of the weights after each update?
        (We normalize the raw weights when this is False.)

    (a_inweights)
        2darr<float>
        Weights from systems to documents.

    (printto)
        File-object to which messages are printed.

    Return value:
        (1darr<num>, 1darr<num>)
        (final_auths, final_hubs)

    '''
    start = time.time()
    printto and print('INFO: Start {}'.format(start), file=printto)
    # make adjacency matrices
    if h_out.dtype is numpy.dtype(bool):
        printto and print('INFO: hits - boolean graph', file=printto)
        h_outlinks = h_out
        a_inweights = None
    else:
        printto and print('INFO: hits - weighted graph', file=printto)
        h_outlinks = numpy.array(h_out, dtype=bool)
        a_inweights = h_out.transpose()
    a_inlinks = h_outlinks.transpose()
    del h_out

    # initialize scores to 1
    a = numpy.ones(a_inlinks.shape[0], dtype=numpy.float64)
    h = numpy.ones(a_inlinks.shape[1], dtype=numpy.float64)

    # iteratively update scores
    i = 1
    while not stopping_fn(i, a, h):
        printto and print('INFO: Iteration', i, file=printto)
        # update
        a, h = update_fn(a, h, a_inlinks, h_outlinks, a_inweights)
        # normalize
        if sqrnorm:
            a **= 2
            h **= 2
        a /= a.sum()
        h /= h.sum()
        # count
        i += 1
    printto and print('INFO: HITS Converged; elapsed {}'.format(time.time() - start), file=printto)
    return a, h


class TestHITS(unittest.TestCase):
    def setUp(self):
        self.a_old = numpy.array([3, 1, 4, 3, 5])
        self.h_old = numpy.array([3, 7])
        self.h_links = numpy.array([[1, 1, 1, 1, 0],
                                    [1, 0, 1, 0, 1]], dtype=numpy.bool_)
        self.a_new = numpy.array([10, 3, 10, 3, 7])
        self.h_new = numpy.array([11, 12])
    def test__hits_update(self):
        a, h = hits_update(self.a_old, self.h_old,
            self.h_links.transpose(), self.h_links)
        self.assertTrue((a == self.a_new).all())
        self.assertTrue((h == self.h_new).all())


if __name__ == '__main__':
    unittest.main()


# eof
