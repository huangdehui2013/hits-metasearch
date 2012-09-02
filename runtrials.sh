#!/bin/sh

./hitsmetasearch.py data-trec8/comp/ 0   > hm0xones
./hitsmetasearch.py data-trec8/comp/ 10  > hm10xones
./hitsmetasearch.py data-trec8/comp/ 100 > hm100xones

# linear func...?

# nonlinear func??
