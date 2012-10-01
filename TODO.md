# Notes / To-Do

[Old Notes [Google docs]](https://docs.google.com/document/d/1jS7W8ScsRFPnczzXhOrFC18mULkno4JeCefQvoDtgH0/edit)

## Project work

* Write routines to perform the analysis below automatically

## Results analysis

* discover the best configuration among hitsm trials
    * graph these lines...
        * best underlying system
        * hitsm {0, 10, and 100 iterations} dot {const, linear, and negexp edgedecay}
    * ...on these plots
        * x=DOC-CUTOFF, y=HITS-MAP
        * x=HITS-ITERATION, y=HITS-MAP
* final authority scores are like *document relevance judgements*
    * these scores order the metasearch ranked document list
    * compare P-R graph of metasearch list with that of the best-underlying-system and some of combMNZ, borda, or hedge
* final hub scores are like *system evaluations*
    * compare these scores with the actual system evaluations given by trec (the mean-average-precision given by trec_eval.pl)
        * scatterplot of x=TREC-MAP, y=HITS-HUB
        * scatterplot of x=rank(TREC-MAP), y=rank(HITS-HUB)

## 1 Oct 2012

* look for email of metasearch evals to compare with hitsm evals
    * eval.mnz is combmnz
    * eval.sum is combsum
    * eval.jaa_rand_ties is some kind of condorcet
* get aquanted with decay functions (discount functions) in descending order of severity; try looking at them un-inverted; try some with hitsm which exhibit non-exponential decay
    * mangled negative exponential (in the current code)
    * negative exponential with varying values for lambda
        * what is weight at rank 1
            * should be 1, but _if you scale negexp by a constant, it should not change hitsm mathematically_ 
        * how far do you have to scan the list before the weight drops by half? another half? (what is the half-life?)
        * what about adjusting lamda on a per-query basis?
    * inverse linear
        * 1 / rank
    * inverse logarithmic
    * w(r) = ln(z/r) [/ ln(z)]
    * ndcg classic 
        * 1 / ln(r+1)
        * ndcg IR evaluation methods have spawned a huge variety of discount functions
* show javed graph of mangled negexp function and data to determine half life
