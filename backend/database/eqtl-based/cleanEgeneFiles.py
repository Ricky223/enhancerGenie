# cleanEgeneFiles.py
# cleans *egenes.txt.gz files from GTEx
# 1. filters all rows to remove genes with qval > 0.05 (so that it contains only egenes)
# 2. removes unneeded columns and adds 'chr' to chromosome number
# 3. stores new data into file ending in -filtered.txt

import pandas as pd
import os
import glob

# update directory as needed
directory = "./GRCh37-GTEx_Analysis_v7_eQTL/"
filePattern = os.path.join(directory, '*egenes.txt.gz')
files = glob.glob(filePattern)

# clean each file
for file in files:
    print("Working on " + file)
    # read file into dataframe
    df = pd.read_csv(file, compression='gzip', sep='\t')

    # Filter rows where qval <= 0.05
    filtered_data = df[df['qval'] <= 0.05]

    # Specify the columns to keep
    columns_to_keep = ['gene_id', 'gene_name', 'gene_chr', 'gene_start', 'gene_end']
    # Create a DataFrame containing only the specified columns
    cleanedDf = filtered_data[columns_to_keep]

    cleanedDf['gene_chr'] = 'chr'+cleanedDf['gene_chr'].astype(str)

    # sort the dataframe
    cleanedDf = cleanedDf.sort_values(by=['gene_chr', 'gene_start'], ascending=True)

    # Reset the index of the new DataFrame if needed
    cleanedDf = cleanedDf.reset_index(drop=True)

    filename = os.path.splitext(os.path.basename(file))[0]
    parts = filename.split('.')
    filename = parts[0]+'.'+parts[1]
    # Specify the output filename
    output_filename = directory+f'{filename}.egenes-filtered.txt.gz'
    # Save the cleaned DataFrame as a gzip-compressed text file
    cleanedDf.to_csv(output_filename, index=False, compression='gzip', sep='\t')
    print("New file created for cleaned " + file + "\n")
