#!/usr/bin/env python3
"""
We're using pandas to read the mosdepth output
and output the high coverage regions.  In this
case we've chosen 4x stddev above the mean for
our threshold.
"""
import pandas as pd
import sys


input = sys.argv[1] # mosdepth coverage at each region)
output = sys.argv[2] # high coverage regions leftover

mosdepth_bed = pd.read_csv(
    input, compression='gzip', sep='\t',
    names=['chrom', 'start', 'end', 'depth'])

mean_depth = mosdepth_bed.depth.mean()
std_depth = mosdepth_bed.depth.std()
high_cov_bed = mosdepth_bed.loc[
    mosdepth_bed.depth > (mean_depth + 4*std_depth)]
high_cov_bed.to_csv(output, sep='\t', header=False, index=False)

