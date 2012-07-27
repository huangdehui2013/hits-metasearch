#!ENV/bin/python


import os
import sys
# 3rd party
import numpy
# local
import lib.trec


if __name__ == '__main__':
    # args
    try:
        srcdir = sys.argv[1]
        dstdir = sys.argv[2]
        assert os.path.isdir(srcdir)
        assert not os.path.exists(dstdir)
    except:
        print 'USAGE: python {} SRC DST'.format(__file__)
        print
        print 'SCR -    data directory containing input.* TREC runs'
        print 'DST -    directory to which *.npz files will be written'
        print '         DST must not exist; it will be created.'
        exit()
    try:
        name = os.path.basename(srcdir.rstrip('/'))
        name = name.strip().strip('./').strip()
        assert name
    except:
        print 'Please provide a path which includes the final basename.'
        print 'Got: "{}"'.format(srcdir)
        exit()
    # compress
    lib.trec.comp_system_dir(srcdir, dstdir)


# eof
