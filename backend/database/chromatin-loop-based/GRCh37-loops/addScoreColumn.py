# addScoreColumn.py
# adds a score column containing 0's for all entries
# in chromatin loop GRCh37 files so that it matches the format
# for the GRCh38 files

import pandas as pd
import glob

files = glob.glob('*merged.loops')
for file in files:
	print("Working on " + file)
	df = pd.read_csv(file, sep='\t', header=None)
	df['loop_score'] = 0.0

	df.to_csv(file, index=False, sep='\t', header=None)