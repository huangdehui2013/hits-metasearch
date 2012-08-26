'''Implement HITS in a general way using callbacks.'''


# future
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from codecs import open
# stdlib
import unittest
# 3rd party
import numpy


def hits_update(a_old, h_old, a_inlinks, h_outlinks, data=None):
    '''Update authority and hub scores.

    1darr<num> 1darr<num> 2darr<bool> 2darr<bool> any --> 1darr<num> 1darr<num>

    '''
    assert len(h_old) == h_outlinks.shape[0]
    assert len(a_old) == h_outlinks.shape[1]
    # an auth score is the sum of the scores of the hubs which point to it
    # a hub score is the sum of the scores of the auths to which it points
    a = numpy.fromiter((h_old[m].sum() for m in a_inlinks),
        dtype=a_old.dtype, count=a_old.shape[0])
    h = numpy.fromiter((a_old[m].sum() for m in h_outlinks),
        dtype=h_old.dtype, count=h_old.shape[0])
    return a, h


def hits(h_outlinks, stopping_fn, update_fn=hits_update, sqrnorm=False,
        data=None):
    '''Calculate hub and authority scores; end when stopping_fn returns true.

    h_outlinks:
        2darr<bool>
        An adjacency matrix indexed [hub][auth] with True for edges.
    stopping_fn:
        [int 1darr<num> 1darr<num> --> bool]
        [iteration_number cur_auths cur_hubs --> continue?]
        The algorithm will continue while this function returns False.
    update_fn:
        [1darr<num> 1darr<num> 2darr<bool> data --> (1darr<num>, 1darr<num>)]
        [old_auths old_hubs hub_outlinks data --> (cur_auths, cur_hubs)]
        Executed each iteration to update hub and authority scores.
    sqrnorm:
        bool
        Should we normalize the square of the weights after each update?
        (We normalize the raw weights when this is False.)
    data:
        Auxiliary data passed directly into update_fn.

    return:
        (1darr<num>, 1darr<num>)
        (final_auths, final_hubs)

    '''
    a_inlinks = h_outlinks.transpose()
    # initialize scores to 1
    a = numpy.ones(h_outlinks.shape[1], dtype=numpy.float64)
    h = numpy.ones(h_outlinks.shape[0], dtype=numpy.float64)
    # iteratively update scores
    i = 1
    while not stopping_fn(i, a, h):
        print('Iteration', i)
        # update
        a, h = update_fn(a, h, a_inlinks, h_outlinks, data)
        # normalize
        if sqrnorm:
            a **= 2
            h **= 2
        a /= a.sum()
        h /= h.sum()
        # count
        i += 1
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
