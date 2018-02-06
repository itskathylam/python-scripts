#!/usr/bin/env python2

"""
Created:  Sun Dec 18 2016
Author:   Kathy N. Lam
Purpose:  Use numpy and matplotlib (Python2) to generate plots in PDF format 
          from growth curve data (triplicate samples only) 

Arguments:
(1) data filename (required)
    note: file must be modified from Gen5 output to have:
    - removal of all non-data rows
    - removal of all non-data columns
    - data in tsv format (tab-separated-values)
    - time modified to be in hours, in float format
    - column headers labeled with sample names, which must be without spaces, 
      and with triplicate label following an underscore: "DSM2243_1", "DSM2243_2"...
(2) upper limit for y axis (required)
    - this sets the limit for the y-axis
(3) subgroups file (optional)
    - this creates addtional plots for the specified subgroups
    - note: each subgroup must be specified in a single line in tsv format; see example below

Output:
(1) plot_allsamples.pdf     single plot of mean+stdev for all triplicate samples 
(2) plot_triplicates.pdf    plots of triplicates, as single and mean+stdev
(3) plot_subgroups.pdf      plots of subgroups as specified in subgroups file, as single and mean+stdev

Example data file:
Time	2243_1	2243_2	2243_3 ...
0	0.112	0.114	0.111
0.25	0.112	0.114	0.112
0.5	0.112	0.114	0.112
0.75	0.112	0.114	0.112
1	0.113	0.114	0.115
1.25	0.112	0.114	0.112
1.5	0.112	0.114	0.113
1.75	0.113	0.114	0.112
2	0.113	0.115	0.113
.
.
.

Example subgroup file:
2243_1	2243_2	2243_3	11767_1	11767_2	11767_3
2243_1	2243_2	2243_3	11863_1	11863_2	11863_3

Example command execution:
$ python plot_growth.py datafile.tsv 0.75 subgroups.tsv

"""


import sys
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


# MATPLOTLIB GLOBAL PARAMS

params = {'legend.fontsize': 6,
          'legend.loc': 'upper left',
          'axes.labelsize': 6,
          'axes.titlesize': 6,
          'xtick.labelsize': 6,
          'ytick.labelsize': 6,
          'lines.linewidth': 0.25, 
          'errorbar.capsize': 0}
plt.rcParams.update(params)


# ARGUMENTS

# get data filename and y axis upper limit
if len(sys.argv) > 2:
    filename = sys.argv[1]
    print "\nData file: " + filename
    try: 
        ylimit = float(sys.argv[2])
        print "Y axis upper limit: " + str(ylimit)
    except:
        print "Whoops, please provide a numerical value for the y axis upper limit."
else:
    print "Whoops, please provide the data filename and the y axis upper limit."
    sys.exit()
    
# get subgroups file
if len(sys.argv) > 3:
    subgroups_filename = sys.argv[3]
    print "Subgroups file: " + subgroups_filename + "\n"

    
# FUNCTIONS 

# check if sample names are the same across replicates
def check_samplename(s1, s2, s3):
    
    # compare sample name by dropping the replicate number
    if len(s1.split("_")[0:-1]) > 0:
        base1 = ''.join(s1.split("_")[0:-1])
        base2 = ''.join(s2.split("_")[0:-1])
        base3 = ''.join(s3.split("_")[0:-1])

    if base1 == base2 and base2 == base3:
        return True
    else:
        return False
        
        
# PLOTTING

# load file with column names into numpy array
data = np.genfromtxt(filename, names=True, delimiter="\t")
col_names = data.dtype.names

# first column is time
time = data['Time']

# check number of samples is multiple of 3 (count columns minus the time column)
print "Checking sample number in data file is multiple of 3..."
num_samples = len(col_names) - 1
if num_samples % 3 != 0:
    print "Whoops, sample number is not a multiple of 3."
    sys.exit()

# after time, columns are samples, in triplicate; check sample names in batches of 3
print "Checking triplicate sample names in data file..."
for i in range(1, num_samples + 1, 3):
    check = check_samplename(col_names[i], col_names[i+1], col_names[i+2])
    if check == False:
        print "Whoops, check that your triplicate samples are labeled correctly."
        sys.exit()


# PLOT 1: SINGLE PLOT ALL SAMPLES (AS MEAN+STDEV)

print "Making plot of all samples..."
plot1 = PdfPages('plot_allsamples.pdf')
plot1fig = plt.figure(1, figsize=(11, 8))
for i in range(1, num_samples + 1, 3):
     
    # get the three samples into tuple
    first = data[col_names[i]]
    second = data[col_names[i+1]]
    third = data[col_names[i+2]]  
    three = (first, second, third) 
    
    # convert tuple to numpy array; calculate mean and stdev 
    three_array = np.asarray(three)
    mean = three_array.mean(axis=0)
    stdev = three_array.std(axis=0)
    
    # place subplot on right, with error bar as fill-between transluscent
    line = plt.plot(time, mean, label = ''.join(col_names[i][:-2]))
    plt.fill_between(time, mean - stdev, mean + stdev, 
                     facecolor = line[0].get_color(), alpha=0.1, lw=0)

# label axes and legend; plot and close figure and pdf    
plt.ylim(0,ylimit)
plt.xlabel('Time (h)')
plt.ylabel('OD600')
plt.legend()
plt.tight_layout()
plot1.savefig(plot1fig)
plt.close(plot1fig)
plot1.close()


# PLOT 2: MULTIPLOT TRIPLICATE SAMPLES (INDIV AND MEAN+STDEV)

print "Making plot of triplicates..."
plot2 = PdfPages('plot_triplicates.pdf')
for i in range(1, num_samples + 1, 3):
     
    # get the three samples 
    first = data[col_names[i]]
    second = data[col_names[i+1]]
    third = data[col_names[i+2]]   

    # place subplot of individual curves on left
    plot2fig = plt.figure(i, figsize=(8, 4))
    plt.subplot(1, 2, 1) #row x column, position
    plt.plot(time, first, label = col_names[i])
    plt.plot(time, second, label = col_names[i+1])
    plt.plot(time, third, label = col_names[i+2])
    plt.ylim(0,ylimit)
    plt.xlabel('Time (h)')
    plt.ylabel('OD600')
    plt.legend()
    
    # convert tuple to numpy array; calculate mean and stdev 
    three = (first, second, third)
    three_array = np.asarray(three)
    mean = three_array.mean(axis=0)
    stdev = three_array.std(axis=0)
    
    # place subplot of mean+stdev on right
    plt.subplot(1, 2, 2) #row x column, position
    line = plt.plot(time, mean, label = ''.join(col_names[i][:-2]))
    plt.fill_between(time, mean - stdev, mean + stdev, 
                     facecolor = line[0].get_color(), alpha=0.1, lw=0)
    
    # label axes and legend; plot and close figure
    plt.ylim(0,ylimit)
    plt.xlabel('Time (h)')
    plt.ylabel('OD600')
    plt.legend()
    plt.tight_layout()
    plot2.savefig(plot2fig)
    plt.close(plot2fig)
    
plot2.close()


# PLOT 3: MULTIPLOT SUBGROUPS (INDIV AND MEAN+STDEV)

# when subgroups file is provided, plot subgroups
if len(sys.argv) > 3:
    subgroups_file = open(subgroups_filename, "r")
    
    print "Checking triplicate sample names in subgroups file..."
    
    # check sample names in subgroups file
    for line in subgroups_file:
        
        # process non-empty lines only
        if line.strip() != "":
            line = line.strip()
            samples = line.split("\t")
            
            # check that sample names are in batches of 3
            for i in range(0, len(samples), 3):
                check = check_samplename(samples[i], samples[i+1], samples[i+2])
                if check == False:
                    print "Whoops, check that your subgroup sample names are labeled correctly."
                    sys.exit()
            
            # check that sample names correspond to data file sample names
            for i in range(0, len(samples), 3):
                if not (samples[i] in col_names) and (samples[i+1] in col_names) and (samples[i+2] in col_names):
                    print "Whoops, check that your subgroup sample names correspond to the sample names in your data file."
                    sys.exit() 

    
 
    #reset to start of subgroups file
    subgroups_file.seek(0)
    
    # plot the subgroups
    print "Making plot of subgroups..."
    plot3 = PdfPages('plot_subgroups.pdf')
    
    # each line is a different subgroup to plot
    subgroup_count = 0 
    
    for line in subgroups_file:   
        
        # process non-empty lines only
        if line.strip() != "":
            line = line.strip()
            samples = line.split("\t")
            
            # figure for subgroup
            plot3fig = plt.figure(subgroup_count, figsize=(8, 4))
            
            # place subplot of individual curves on left
            plt.subplot(1, 2, 1) #row x column, position
            
            # plot batches of 3
            for i in range(0, len(samples), 3):
                first = data[samples[i]]
                second = data[samples[i+1]]
                third = data[samples[i+2]] 
                plt.plot(time, first, label = samples[i])
                plt.plot(time, second, label = samples[i+1])
                plt.plot(time, third, label = samples[i+2])
            
            # label axes and legend
            plt.ylim(0,ylimit)
            plt.xlabel('Time (h)')
            plt.ylabel('OD600')
            plt.legend()
           
            # place subplot of mean+stdev on right
            plt.subplot(1, 2, 2) #row x column, position
            
            # plot batches of 3
            for i in range(0, len(samples), 3):
                first = data[samples[i]]
                second = data[samples[i+1]]
                third = data[samples[i+2]] 
                three = (first, second, third)
                three_array = np.asarray(three)
                mean = three_array.mean(axis=0)
                stdev = three_array.std(axis=0)
                line = plt.plot(time, mean, label = ''.join(samples[i][:-2]))
                plt.fill_between(time, mean - stdev, mean + stdev, 
                                 facecolor = line[0].get_color(), alpha=0.1, lw=0)
                
            # label axes and legend; plot and close figure    
            plt.ylim(0,ylimit)
            plt.xlabel('Time (h)')
            plt.ylabel('OD600')
            plt.legend()
            plt.tight_layout()
            plot3.savefig(plot3fig)
            plt.close(plot3fig)
            
            # increment subgroup count for next subgroup plot
            subgroup_count = subgroup_count + 1
        
    plot3.close()
    
else:
    print "No subgroups file provided; skipping subgroup plots..."

print "All done!\n"
