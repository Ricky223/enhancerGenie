# splitHalves.py
# splits each of the two regions from the loop files
# into their own file for use in the algorithm

import pandas as pd
import glob

def getKey(df):
	# concats each value in the row with dashes
	return str(df[0]) + '_' + str(df[1]) + '_' + str(df[2]) + '_' + str(df[3]) + '_' + str(df[4]) + '_' + str(df[5])


files = glob.glob('*merged.loops')
for file in files:
	print("Working on " + file)
	df = pd.read_csv(file, sep='\t', header=None)

	# add new key column to df where key is a concat of the entire row minus last column
	df['key'] = df.apply(getKey, axis=1)

	# split dataframe into 2 and sort - data cleaning
	leftDf = df[[0, 1, 2, 'key', 6]]
	rightDf = df[[3, 4, 5, 'key', 6]]
	leftDf.columns = ["chr", "start", "end", "key", "val"]
	rightDf.columns = ["chr", "start", "end", "key", "val"]
	leftDf = leftDf.sort_values(by=["chr", "start"], ascending=True)
	rightDf = rightDf.sort_values(by=["chr", "start"], ascending=True)

	# write each half to a new file
	leftDf.to_csv(file+'-left.loops', sep='\t', index=False, header=None)
	rightDf.to_csv(file+'-right.loops', sep='\t', index=False, header=None)

