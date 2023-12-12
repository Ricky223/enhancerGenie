# cleanVariantFiles.py
# Clean signif_variant_gene_pairs.txt,gz files from GTEx
# 1. split variant_id into 3 new columns: chrom, start, end
# 2. add chr to chrom
# 3. only store needed columns
# 4. sort by chrom and start
# 5. write results to file ending in -cleaned.txt.gz

import pandas as pd
import os
import glob

# update directory as needed
directory = "./GRCh37-GTEx_Analysis_v7_eQTL/"

# Use glob to find files ending with gene_pairs.txt.gz
filePattern = os.path.join(directory, '*gene_pairs.txt.gz')
files = glob.glob(filePattern)

# clean each file
for file in files:
    print("Working on " + file)
    # read file into dataframe
    df = pd.read_csv(file, sep='\t', compression='gzip')

    # split the "variant_id" column and create 3 new columns
    df[['chrom', 'start', 'end']] = df['variant_id'].str.extract(r'([^_]+)_(\d+)_\w+_(\w+)_b37')
    df['start'] = df['start'].astype(int)
    df['end'] = df['start'] + 1
    df['chrom'] = 'chr'+df['chrom'].astype(str)

    # store into cleaned dataframe containing only needed columns
    cleanedDf = df[['chrom', 'start', 'end', 'gene_id', 'pval_nominal']]
    # sort the dataframe
    cleanedDf = cleanedDf.sort_values(by=['chrom', 'start'], ascending=True)

    # Reset the index of the new DataFrame if needed
    cleanedDf = cleanedDf.reset_index(drop=True)

    # Save the cleaned DataFrame as a gzip-compressed text file
    filename = os.path.splitext(os.path.basename(file))[0]
    parts = filename.split('.')
    filename = parts[0] + '.' + parts[1] + '.' + parts[2]
    output_filename = directory+f'{filename}-cleaned.txt.gz'
    cleanedDf.to_csv(output_filename, sep="\t", index=False, compression='gzip', header=None)
    print("New file created for cleaned " + output_filename + "\n")
