#!/usr/bin/python

# Author: Kathy Lam
# Date original: 2016-11-12
# Purpose: Use BioPython and Lucy to trim Sanger sequencing reads of vector sequence
# Required arguments:   (1) directory of ab1 files
#                       (2) vector sequence file
#                       (3) splice site sequence file
# Output:	(1) directory of fasta/qual file pairs for each ab1 file
# 		(2) directory of lucy output fasta/qual pairs
# 		(3) directory of fasta files manually trimmed using lucy info


from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq
import sys
import os
import subprocess
import re


# get input dir of ab1 files; get vector/splice site seqs
ab1_dir = sys.argv[1]
vector_file = sys.argv[2]
splice_site_file = sys.argv[3]

# make new dirs for output files
converted_dir = "output_fasta-qual"
os.mkdir(converted_dir)
lucy_dir = "output_lucy"
os.mkdir(lucy_dir)
trimmed_dir = "output_trimmed"
os.mkdir(trimmed_dir)

# process each file in dir of ab1 files
ab1_files = os.listdir(ab1_dir)
ab1_files.sort()
for ab1 in ab1_files:
    
    print("Processing: " + ab1 + "...")
    
    # get the file basename; clean it of shell-disliked characters
    ab1_basename = os.path.splitext(ab1)[0]
    clean_basename = re.sub("[^a-zA-Z\_\-\d]", "", ab1_basename)
    
    # STEP 1: convert ab1 file to fasta/qual file pair required by lucy; save in converted_dir
    
    input_path = ab1_dir + "/" + ab1
    SeqIO.convert(input_path, "abi", converted_dir + "/" + clean_basename + ".fasta", "fasta")
    SeqIO.convert(input_path, "abi", converted_dir + "/" + clean_basename + ".qual", "qual")

    # STEP 2: run lucy on fasta/qual file pair, to trim vector seq; save in lucy_dir
    
    lucy_command = ("lucy -vector " + vector_file + " " + splice_site_file + " "    #vector/splice site
                    + " -output "
                    + lucy_dir + "/" + clean_basename + "_lucy.fasta "                #output fasta
                    + lucy_dir + "/" + clean_basename + "_lucy.qual "                 #output qual
                    + converted_dir + "/" + clean_basename + ".fasta "                #input fasta
                    + converted_dir + "/" + clean_basename + ".qual")                 #input qual
    
    check = subprocess.call(lucy_command, shell = "True")                                                                     
    if check == 0:
        print("Done running Lucy.")
    else:
        print("Whoops, something went wrong with Lucy!")

    # STEP 3: lucy provides coordinates - manually trim; save in trimmed_dir
    
    trimmed_filename = trimmed_dir + "/" + clean_basename + "_trimmed.fasta"
    lucy_output = lucy_dir + "/" + clean_basename + "_lucy.fasta"
    for record in SeqIO.parse(lucy_output, "fasta"):
        
        # note: start/end coords are the last two integers of the seq id; account for off-by-one DNA to python index
        insert_end = int(record.description.split(" ")[-1]) - 1
        insert_start = int(record.description.split(" ")[-2]) - 1
        
        # substring whole seq to get insert seq only
        insert_seq = str(record.seq[insert_start:insert_end])
        insert_id = record.id + "-trimmed"
        descr = str(insert_start) + "-" + str(insert_end) + " " + str(len(insert_seq))
        new_record = SeqRecord(Seq(insert_seq), id=insert_id, description=descr)
        
        # write to new file
        SeqIO.write(new_record, trimmed_filename, "fasta")
        
    print("Done trimming.")
    
    print("***********************************************")
    
