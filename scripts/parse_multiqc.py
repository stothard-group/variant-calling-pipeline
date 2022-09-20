#!/usr/bin/env python3


# This script parses the outputs of multiqc run on raw and trimmed reads.
# Inputs are the paths to the raw and trimmed results, where trimmed results
# are split into n-chunks defined in the config file.

import pandas as pd
import numpy
import os
import sys


def parse_multiqc(raw_path, trimmed_path, outpath):
    """
    Main function
    :param raw_path: Path to multiqc file containing raw fastqc results
    :param trimmed_path: Path to multiqc file containing trimmed fastq results
    :return:
    """
    raw_df = pd.read_csv(raw_path, sep='\t')
    raw_df_small = raw_df[["Sample", "Total Sequences"]].copy()
    trimmed_df = pd.read_csv(trimmed_path, sep='\t')
    trimmed_df_small = trimmed_df[["Sample", "Total Sequences"]].copy()
    # Combine parts
    df_list = []
    raw_samples = raw_df_small.Sample.to_list()
    for s in raw_samples:
        sample_trimmed = trimmed_df_small[trimmed_df_small['Sample'].str.contains(s)]
        total_seqs = sample_trimmed['Total Sequences'].sum()
        part_df = pd.DataFrame({"Sample": s, "Post-QC Sequences": total_seqs}, index=[0])
        df_list.append(part_df)
    trimmed_sums = pd.concat(df_list, ignore_index=True)
    merged_df = pd.merge(left=raw_df_small, right=trimmed_sums, how='outer', on=['Sample'])
    merged_df.rename(columns={'Total Sequences': 'Raw Sequences'}, inplace=True)
    merged_df.to_csv(outpath, sep='\t', index=False)
    return True


if __name__ == "__main__":
    output = parse_multiqc(sys.argv[1], sys.argv[2], sys.argv[3])
