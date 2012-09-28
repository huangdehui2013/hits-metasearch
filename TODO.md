# Notes / To-Do

[Old Notes [Google docs]](https://docs.google.com/document/d/1jS7W8ScsRFPnczzXhOrFC18mULkno4JeCefQvoDtgH0/edit)

## Project work

* Write routines to perform the analysis below automatically

## Results analysis

* discover the best configuration among hits-for-metasearch trials
** graph these lines...
*** best underlying system
*** hits-metasearch {0, 10, and 100 iterations} dot {const, linear, and negexp edgedecay}
** ...with these axes
*** x=DOC-CUTOFF, y=HITS-MAP
*** x=HITS-ITERATION, y=HITS-MAP

* final authority scores are like 'document relevance judgements'
** these scores order the metasearch ranked document list
** compare P-R graph of metasearch list with that of the best-underlying-system and some of combMNZ, borda, or hedge

* final hub scores are like 'system evaluations'
** compare these scores with the actual system evaluations given by trec (the mean-average-precision given by trec_eval.pl)
*** scatterplot of x=TREC-MAP, y=HITS-HUB
*** scatterplot of x=rank(TREC-MAP), y=rank(HITS-HUB)
