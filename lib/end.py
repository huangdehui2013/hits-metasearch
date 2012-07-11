'''Convergence detection utilities. Call them once per iteration.

Callables in this module return True or False indicating whether convergence
has been detected. True means convergence is detected and iteration may stop.

'''

# stdlib
import unittest
# 3rd party
import numpy


class Countdown(object):
    '''int -> Countdown

    Converge after n calls.

    '''
    def __init__(self, n):
        self.n = n
    def __call__(self, *a, **k):
        self.n -= 1
        return self.n < 0


class TestCountdown(unittest.TestCase):
    def seqtest(self, n, expected_binstr):
        c = Countdown(n)
        binstr = ''.join([str(int(c())) for _ in
            xrange(len(expected_binstr))])
        self.assertEquals(binstr, expected_binstr)
    def test_three(self):
        self.seqtest(3, '000111')
    def test_one(self):
        self.seqtest(1, '011111')
    def test_zero(self):
        self.seqtest(0, '111111')


class ConditionCount(object):
    '''[*a **k -> bool] int -> ConditionCount

    Converge when the condition callback has returned True n times.

    '''
    def __init__(self, stop_fn, n):
        self.f = stop_fn
        self.n = n
    def __call__(self, *a, **k):
        if self.f(*a, **k):
            self.n -= 1
        return self.n <= 0


class TestConditionCount(unittest.TestCase):
    @staticmethod
    def runseqtest(condition_binstr, n, expected_binstr, tc, cls):
        cc = cls(lambda x: x.pop(0), n)
        data = [bool(int(n)) for n in condition_binstr]
        binstr = ''.join([str(int(cc(data))) for _ in
            xrange(len(expected_binstr))])
        tc.assertEquals(len(binstr), len(expected_binstr))
        tc.assertEquals(binstr, expected_binstr)
    def seqtest(self, *a, **k):
        a = list(a) + [self, ConditionCount]
        TestConditionCount.runseqtest(*a, **k)
    def test_immediate(self):
        self.seqtest('1110000110000', 3, '0011111111111')
    def test_fast(self):
        self.seqtest('0000111001000', 3, '0000001111111')
    def test_delayed(self):
        self.seqtest('0000010110000', 3, '0000000011111')
    def test_late(self):
        self.seqtest('0010010000100', 3, '0000000000111')
    def test_not(self):
        self.seqtest('0010010000000', 3, '0000000000000')


class ConditionStreak(object):
    '''[*a **k -> bool] int -> ConditionStreak

    Converge when the condition callback returns True n consecutive times.

    '''
    def __init__(self, stop_fn, n):
        self.f = stop_fn
        self._n = n
        self.n = n
    def __call__(self, *a, **k):
        # if condition
        #   decrement
        # else
        #   reset
        if self.f(*a, **k):
            self.n -= 1
        else:
            self.n = self._n
        # check whether it's done (if so, stay done)
        if self.n <= 0:
            self._n = 0
            return True
        return False


class TestConditionStreak(unittest.TestCase):
    def seqtest(self, *a, **k):
        a = list(a) + [self, ConditionStreak]
        TestConditionCount.runseqtest(*a, **k)
    def test_immediate(self):
        self.seqtest('1110000110000', 3, '0011111111111')
    def test_fast(self):
        self.seqtest('0000111001000', 3, '0000001111111')
    def test_delayed(self):
        self.seqtest('0000010110000', 3, '0000000000000')
    def test_late(self):
        self.seqtest('0010010000100', 3, '0000000000000')
    def test_not(self):
        self.seqtest('0010010000000', 3, '0000000000000')
    def test_touchngo(self):
        self.seqtest('0110110110111', 3, '0000000000001')


if __name__ == '__main__':
    unittest.main()


# eof