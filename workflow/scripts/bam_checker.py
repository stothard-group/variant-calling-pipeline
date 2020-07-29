#!/usr/bin/env python3

### This program compares original and merged bam files based on their name and
### associated read group information to make sure that the merged file
### contains the same number of reads that are in all the original files. It
### was created specifically to work with the Snakemake ReadMapping.sm workflow.


import pysam
import sys
import os
import glob
import snakemake

#sample_file_path = snakemake.input[0]

#bam_dir = snakemake.params[1]
sample_file_path = "results/alignment/DG15B032179-1.m.md.bam"
bam_file_dir = "results/alignment/"
all_bam_files = os.listdir(bam_file_dir)


header_info = pysam.view("-H", sample_file_path)
header_list = header_info.split("\n")
RG_info = []
# Get read group information
for line in header_list:
    if line.startswith("@RG"):
        RG_info.append(line)

# Find corresponding original files
original_file_list = []
for readgroup in RG_info:
    rg_line = readgroup.split("\t")
    id_line = rg_line[1]
    id_short = id_line.replace("ID:", "")
    sample = rg_line[4]
    sample_short = sample.replace("SM:", "")
    for file in all_bam_files:
        pattern1 = "HI." + id_short + "."
        pattern2 = "." + sample_short + ".m.bam"
        if file.startswith(pattern1) and file.endswith(pattern2):
            original_file_path = os.path.join(bam_file_dir, file)
            original_file_list.append(original_file_path)
        else:
            pass

# Count the number of mapped reads and compare
merged_read_number = int(pysam.view("-c", sample_file_path))
original_read_count = 0
original_read_values = {}
for original_file in original_file_list:
    original_file_count = int(pysam.view("-c", original_file))
    original_read_values.update({original_file: original_file_count})
    original_read_count = original_read_count + original_file_count

# Write output file
good_filename = sample_name + "_correct.txt"
good_output_path = os.path.join(bam_file_dir, good_filename)
bad_filename = sample_name + "_incorrect.txt"
bad_output_path = os.path.join(bam_file_dir, bad_filename)
if merged_read_number == original_read_count:
    output_path = good_output_path
else:
    output_path = bad_output_path
with open(output_path, "w") as out:
    out.write("Merged read count: " + str(merged_read_number) + "\nOriginal read counts:\n")
    for key in original_read_values:
        out.write(key + ": " + str(original_read_values[key]) + "\n")
    out.write("Sum: " + str(original_read_count))
out.close()
