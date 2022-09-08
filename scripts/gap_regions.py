#!/usr/bin/env python3
"""
Adapted from solution in https://www.biostars.org/p/133742/
Parallelized by fasta record.
"""
import sys
import gzip
from Bio import SeqIO
from joblib import Parallel, delayed

### Find gap regions in a single fasta record (ie contig)
# This function simply iterates over each character in a fasta record
# and keeps track of the position as it goes.  Once a 'N' is encountered,
# we will keep track of how long the run of N's is in order to get the
# start/end coordinates
def get_gap_regions(record):
    regions = []
    start_pos = 0
    counter = 0
    gap = False
    gap_length = 0
    for char in record.seq:
        if char == "N":
            if gap_length == 0:
                start_pos = counter
                gap_length = 1
                gap = True
            else:
                gap_length += 1
        else:
            if gap:
                regions.append([record.id, str(start_pos),
                                str(start_pos + gap_length)])
                gap_length = 0
                gap = False
        counter += 1
    return regions

if __name__ == "__main__":
    # reference genome path
    fasta = sys.argv[1]

    # number of processes to parallelize with
    processes = int(sys.argv[2])

    # I'm using a library called joblib to parallelize the task by fasta record.
    # parallelizing by fasta record is usefull for reference genomes with lots of
    # small contigs, like the one we're working with here.
    # Fun fact: joblib is used extensively by scikit-learn for parallelization
    # and data pipline caching.
    with gzip.open(fasta, mode="rt") as fasta_handle:
        gap_regions = Parallel(n_jobs=processes)(delayed(get_gap_regions)(record)
            for record in SeqIO.parse(fasta_handle, "fasta"))
        for regions in gap_regions:
            for r in regions:
                print('\t'.join(r))
