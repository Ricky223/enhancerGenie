# cleanBiomartExport.py - KayLynn Beard
# Cleans a biomart_export.txt file for use in distance and chromatin loop
# gene database

# Input: Ensembl biomart export file with attributes (in order):
#         Chromosome/scaffold name
#         Transcription start site (TSS)
#         Gene start (bp)
#         Gene end (bp)
#         Gene stable ID

# Output: GRCx##-genes.bed (for distance-based)
#         GRCx##-genesTSS.bed (for chromatin loop-based)

import pandas as pd
pd.set_option('display.max_columns', None)

fileDf = pd.read_csv("mart_export.txt", sep='\t')

# add chr to beginning of chromosome number
fileDf["Chromosome Name"] = "chr" + fileDf["Chromosome Name"].astype(str)

geneTSSDf = fileDf
# sort
geneTSSDf = geneTSSDf.sort_values(by=['Chromosome Name', 'Transcript Start (bp)'],
                                  ascending=[True, True])
# create a new column that holds a copy of TSS
new_column = geneTSSDf.iloc[:, 1].copy()
# insert the new column after the copied column
geneTSSDf.insert(2, 'TSS_dup', new_column)
# write to file
geneTSSDf.to_csv("GRCh37-genesTSS.bed", header=None, index=False, sep='\t')

# remove TSS
fileDf = fileDf.drop("Transcript Start (bp)", axis=1)
# sort
fileDf = fileDf.sort_values(by=['Chromosome Name', 'Gene Start (bp)', 'Gene End (bp)'],
                                  ascending=[True, True, True])
# remove duplicates
fileDf = fileDf.drop_duplicates()
# write to file
fileDf.to_csv("GRCh37-genes.bed", header=None, index=False, sep='\t')

