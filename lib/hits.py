'''Implement HITS in a general way using callbacks.'''

# stdlib
import unittest
import itertools
# 3rd party
import numpy


def hits_update(a_old, h_old, h_outlinks, data):
    # auths [x <- I()]
    # hubs  [y <- O()]
    # an auth score is the sum of the scores of the hubs which point to it
    # a hub score is the sum of the scores of the auths to which it points
    assert len(h_old) == h_outlinks.shape[0]
    assert len(a_old) == h_outlinks.shape[1]
    a = numpy.fromiter((h_old[m].sum() for m in h_outlinks.transpose()),
        dtype=a_old.dtype, count=a_old.shape[0])
    h = numpy.fromiter((a_old[m].sum() for m in h_outlinks),
        dtype=h_old.dtype, count=h_old.shape[1])
    return a, h


def hits(a_inlinks, h_outlinks, update_fn, stopping_fn, data):
    '''Calculate hub and authority scores; end when stopping_fn returns true.

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
    # report sizes
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
        self.oldauths = assoc([('a',3), ('b',1), ('c',4), ('d',3), ('e',5)])
        self.oldhubs  = assoc([('h1',3), ('h2',7)])
        self.newauths = assoc([('a',10), ('b',3), ('c',10), ('d',3), ('e',7)])
        self.newhubs  = assoc([('h1',11), ('h2',13)])
    def test__hits_update(self):
        a, h = hits_update(self.graph, self.oldauths, self.oldhubs)
        self.assertEqual(a, self.newauths)
        self.assertEqual(h, self.newhubs)


if __name__ == '__main__':
    unittest.main()


# eof