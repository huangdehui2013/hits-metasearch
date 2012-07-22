# HITS for Metasearch

*A metasearch algorithm which evaluates system performance using HITS.*

This program is part of a research project I'm doing with [Javed Aslam](http://www.ccs.neu.edu/home/jaa/) at Northeastern University. It works with TREC-formatted ranked document lists. Use `compress.py` to convert a directory of TREC data to numpy data files. Use `hitsmetasearch.py` to run the algorithm on the numpy data files. Currently it just outputs the top documents and systems.

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

### versions.py

Print out your python and NumPy persions.

## Requirements

Requires Python 2.7, Numpy 1.7

    NumPy 1.7.0.dev-a0d1a96
    Python 2.7.3 (v2.7.3:70274d53c1dd, Apr  9 2012, 20:52:43) 