# HITS for Metasearch

*A metasearch algorithm which evaluates system performance using Jon Kleinberg's HITS algorithm.*

This is a research project I am doing with [Javed Aslam](http://www.ccs.neu.edu/home/jaa/) at Northeastern University. It works with TREC-formatted ranked document lists. Use `compress.py` to convert a directory of TREC data to numpy data files. Use `hitsmetasearch.py` to run the algorithm on the numpy data files.

-- [PLR](http://f06mote.com)

## Scripts

If NumPy is installed system wide you can run the scripts with:

    $ python script

Else, if you are using a virtual environment rooted in `./ENV/` do:

    $ ./script

### compress.py

Load, process, and compress a directory of ascii-formatted TREC runs into corresponding "npz" files. Run without arguments for usage.

### hitsmetasearch.py

Run the hits algorithm as applied to metasearch. Run without arguments for usage.

    Print to stdout a ranked list of documents for the query QNO by running HITS
    for Metasearch for N iterations. TREC systems are the "hubs" and documents are
    the "authorities".

Also supports the weighting of edges based on document rank such that high-ranked documents have a higher edge weight from the systems that point to them than low-ranked documents.

### versions.py

Print out your Python and NumPy versions.

## Requirements

Requires Python 2.7, Numpy 1.8

    NumPy 1.8.0.dev-63cd8f3
    Python 2.7.3 (v2.7.3:70274d53c1dd, Apr  9 2012, 20:52:43)
