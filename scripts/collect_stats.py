#!/usr/bin/env python3

# This script collects stats from the parsed multiqc output, the bam alignment
# stats, and the sample depth summary stats and reports them in a single file
# for all samples in the final results directory


import os
import sys
import pandas as pd
import functools as ft


def collect_stats(multiqc, stats_dir, outpath):
    """
    Main function
    :param multiqc: path to parsed multiqc results
    :param stats_dir: path to stats directory
    :return:
    """
    multiqc_df = pd.read_csv(multiqc, sep='\t')
    statsfiles = os.listdir(stats_dir)
    bamfile_df_list = []
    summary_df_list = []
    for f in statsfiles:
        if f.endswith(".bam.stats.txt"):
            fpath = os.path.join(stats_dir, f)
            with open(fpath, 'r') as bamstats:
                for i, line in enumerate(bamstats):
                    splitline = line.split()
                    if i == 4:
                        pc_mapped = splitline[4]
                        pc_mapped = pc_mapped.replace("(", "")
                        pc_mapped = pc_mapped.replace("%", "")
                    elif i == 8:
                        pc_paired = splitline[5]
                        pc_paired = pc_paired.replace("(", "")
                        pc_paired = pc_paired.replace("%", "")
                    else:
                        pass
                sample = f.replace(".m.md.recal.bam.stats.txt", "")
                partial_bam_df = pd.DataFrame({"Sample": sample, "Mapped Reads (%)": pc_mapped, "Paired Mapped Reads (%)": pc_paired}, index=[0])
                bamfile_df_list.append(partial_bam_df)
            bamstats.close()
        elif f.endswith(".bam.depth.sample_summary"):
            s_path = os.path.join(stats_dir, f)
            s_df = pd.read_csv(s_path, sep='\t')
            s_df_small = s_df[['sample_id', 'mean']].head(1)
            s_df_small.rename(columns={'sample_id': 'Sample', 'mean': 'Average Coverage'}, inplace=True)
            summary_df_list.append(s_df_small)
    bamfile_df = pd.concat(bamfile_df_list, ignore_index=True)
    summary_df = pd.concat(summary_df_list, ignore_index=True)
    all_dfs = [multiqc_df, bamfile_df, summary_df]
    merged_df = ft.reduce(lambda left, right: pd.merge(left, right, on='Sample'), all_dfs)
    merged_df.to_csv(outpath, sep='\t', index=False)
    return True


if __name__ == "__main__":
    output = collect_stats(sys.argv[1], sys.argv[2], sys.argv[3])
