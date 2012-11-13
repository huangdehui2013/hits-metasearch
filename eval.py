#!ENV/bin/python


# future
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from codecs import open
# stdlib
import os
import glob
import time
import tempfile
import itertools
import subprocess
import multiprocessing
# 3rdparty
import gpw


###############################################################################
# evaluation


def parse_aggregate(output):
    '''Parse stdout from trec_eval run without the -q option.'''
    splitlines = [ln.split() for ln in output.split('\n') if ln.strip()]
    # retrieved, relevant, rel_ret
    d = {k.lower()[:-1] : ('docs', int(v)) for k,v in splitlines[2:5]}
    # interpolated recall - precision averages
    d['r-p'] = ((' '.join(splitlines[5][0:2]).lower(),
                 ' '.join(splitlines[5][3:5]).lower()[:-2]),
                [(float(r), float(p)) for _,r,p in splitlines[6:17]])
    # mean average precision
    d['map'] = (' '.join(splitlines[17]).lower(),
                float(splitlines[18][0]))
    # precision at cutoff
    d['c-p'] = (('document cutoff',
                 splitlines[19][0].lower()[:-1]),
                [(int(c), float(p)) for _,c,_,p in splitlines[20:29]])
    # r-precision
    d['rprec'] = (' '.join(splitlines[29]).lower()[:-1],
                  float(splitlines[30][1]))
    return d


def trec_eval(qrel_file, ranked_list, perl='perl', trec_eval='trec_eval.pl'):
    '''Run trec_eval with a qrel and a ranked-document list.'''
    print('{} {} {} {}'.format(perl, trec_eval, qrel_file, ranked_list))
    output = subprocess.check_output([perl, trec_eval, qrel_file, ranked_list])
    return parse_aggregate(output)


def trec_eval_(x):
    head, rest = x[0], x[1:]
    return head, trec_eval(*rest)


def load_eval(trec_eval_output):
    '''Load a stdout dump from a trec_eval run.'''
    print('Loading {}'.format(trec_eval_output))
    with open(trec_eval_output, 'r', 'utf8') as fd:
        return parse_aggregate(fd.read())


###############################################################################
# evaluation convenience


def eval_all_systems(pool, qrel, paths):
    '''Run a pool of trec_eval(s) to evaluate systems.'''
    args = ((os.path.basename(p).replace('input.', ''), qrel, p) for p in paths)
    evals = pool.imap_unordered(trec_eval_, args)
    return {n:e for n, e in evals}


def load_all_evals(pool, paths):
    '''Run a pool of load_eval(s) to load system evaluations.'''
    names = (os.path.basename(p).replace('eval.', '') for p in paths)
    evals = pool.imap(load_eval, paths)
    return {n:e for n, e in itertools.izip(names, evals)}


###############################################################################
# plotting


def plotscript(**kwargs):
    script = []
    settable = [
        ('title',    "'{}'"),
        ('xlabel',   "'{}'"),
        ('ylabel',   "'{}'"),
        ('xtics',    "{}"),
        ('ytics',    "{}"),
        ('xrange',   "[{}:{}]"),
        ('yrange',   "[{}:{}]"),
        ('size',     "{}"),
        ('terminal', "{}"),
        ('output',   "'{}'"),
        ('key',      "{} {}"),
    ]
    for name, fmt in settable:
        if name in kwargs:
            val = kwargs.pop(name)
            iter = val if hasattr(val, '__iter__') else (val,)
            plugged = fmt.format(*iter)
            script.append('set {} {}'.format(name, plugged))
    if kwargs:
        raise ValueError('Unknown directives', kwargs)
    script.append('plot {lines}')
    return '\n'.join(script)


def _assocdata(assoc):
    fd = tempfile.NamedTemporaryFile()
    fd.write('\n'.join('{}\t{}'.format(x, y) for x, y in assoc))
    fd.flush()
    return fd


def plotline(assoc, line):
    '''

    '{dat}' using 1:2 title 'weight(r,ct)=1' with lines, \
    '{dat}' using 1:3 title 'weight(r,ct)=1-(r/ct)' with lines, \
    '{dat}' using 1:4 title 'f(x) =1*(e^(-x*1)); g(r,ct)=(r/ct)*5; weight(r,ct) = f o g' with lines

    '''
    fd = _assocdata(assoc)
    return "'{}' {}".format(fd.name, line), fd


def plot(script, lines):
    lns, fds = zip(*lines)
    #os.system('cat {}'.format(fds[0].name))
    g = subprocess.Popen('gnuplot', stdin=subprocess.PIPE)
    final = script.format(lines=', \\\n'.join(lns))
    #print(final)
    g.communicate(final)


def compare(sysevals):
    data = []
    for sys, eval in sorted(sysevals.items(),
            key=lambda (k, v): v['map'], reverse=True):
        # make a line
        (xlabel, ylabel), series = eval['r-p']
        _, map = eval['map']
        data.append(plotline(series, "title '{} map{}' with linespoints".format(sys, map)))
    print(eval.keys())
    plot(plotscript(
            output="foo.png",
            terminal='png',
            title='TREC8 & Friends',
            xlabel=xlabel,
            ylabel=ylabel,
            xtics=0.1,
            ytics=0.1,
            size='square',
        ), data)


###############################################################################
# main


if __name__ == '__main__':
    pool = multiprocessing.Pool()

    # load evals
    qrel = 'data-trec8/qrel.trec8'
    trec = eval_all_systems(pool, qrel, glob.glob('data-trec8/raw/input.*'))
    hits = eval_all_systems(pool, qrel, glob.glob('trials/*'))
    aslam = load_all_evals(pool, glob.glob('data-trec8/eval.*'))

    try:
        pool.close()
        pool.join()
        del pool
    except:
        pool.terminate()
        print('Error')
        exit(2)

    # find the best underlying trec systems
    trec_best3 = sorted([(trec[s]['map'][1], s) for s in trec.keys()], reverse=True)[:3]

    # build the comparison set
    assert not (hits.viewkeys() & aslam.viewkeys() & set(trec_best3)), 'names must be disjoint'
    c = {n: trec[n] for _, n in trec_best3}
    c.update(hits)
    c.update(aslam)
    
    compare(c)

# eof
