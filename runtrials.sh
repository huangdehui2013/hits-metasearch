#!/bin/sh

mkdir trials 2> /dev/null

./hitsmetasearch.py data-trec8/comp/ negexp > trials/hm-negexp 2> logs/hm-negexp.log
./hitsmetasearch.py data-trec8/comp/ linear > trials/hm-linear 2> logs/hm-linear.log
./hitsmetasearch.py data-trec8/comp/ const  > trials/hm-const  2> logs/hm-const.log

./hitsmetasearch.py data-trec8/comp/ negexp -s > trials/hm-negexp-s 2> logs/hm-negexp-s.log
./hitsmetasearch.py data-trec8/comp/ linear -s > trials/hm-linear-s 2> logs/hm-linear-s.log
./hitsmetasearch.py data-trec8/comp/ const  -s > trials/hm-const-s  2> logs/hm-const-s.log

./eval.py
