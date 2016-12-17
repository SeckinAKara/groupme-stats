# groupme-stats
This repository contains code to generate a printout and graphs of statistics of a GroupMe chat.

The entire history of a single GroupMe chat should be saved within the groupme_logs.txt file. The format of the txt file could be recreated by hand, but the easiest way to get a working log file is to use groupme-tools https://github.com/cdzombak/groupme-tools. 

The bulk of the work is done by analyze_groupme.py, which not only generates the analysis printout but also creates groupme_logs.csv. This file is needed to run groupme_graphs.R.

groupme_graphs.R contains a function graph_word, which, given a string, creates a graph of the 10 users who have said that word the most.
