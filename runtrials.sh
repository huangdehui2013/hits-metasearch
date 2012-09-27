#!/bin/sh

mkdir trials 2> /dev/null

# edges equal to 1
./hitsmetasearch.py data-trec8/comp/ 0   const > trials/hm0xconst
./hitsmetasearch.py data-trec8/comp/ 10  const > trials/hm10xconst
./hitsmetasearch.py data-trec8/comp/ 100 const > trials/hm100xconst

# linear edge decay
./hitsmetasearch.py data-trec8/comp/ 0   linear > trials/hm0xlinear
./hitsmetasearch.py data-trec8/comp/ 10  linear > trials/hm10xlinear
./hitsmetasearch.py data-trec8/comp/ 100 linear > trials/hm100xlinear

# nonlinear edge decay
./hitsmetasearch.py data-trec8/comp/ 0   negexp > trials/hm0xnegexp
./hitsmetasearch.py data-trec8/comp/ 10  negexp > trials/hm10xnegexp
./hitsmetasearch.py data-trec8/comp/ 100 negexp > trials/hm100xnegexp
