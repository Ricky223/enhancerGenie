import pandas as pd

# chr	start	end	name	class	TargetGene	TargetGeneTSS	TargetGeneIsExpressed	distance
# isSelfPromoter	ABC.Score.Numerator	ABC.Score	CellType	id

file = "AllPredictions.AvgHiC.ABC0.015.minus150.ForABCPaperV3"
print("Working on " + file + ".txt")

# read file into dataframe
df = pd.read_csv(file + ".txt", sep='\t')
columns_to_keep = ['chr', 'start', 'end', 'name', 'class', 'TargetGene', 'TargetGeneTSS', 'TargetGeneIsExpressed',
				   'distance', 'isSelfPromoter', 'ABC.Score.Numerator', 'ABC.Score', 'CellType']
# Create a DataFrame containing only the specified columns
df = df[columns_to_keep]

# remove rows with cell type ending with x
rowsToRemove = df['CellType'].str.endswith('2016')
df = df[~rowsToRemove]
rowsToRemove = df['CellType'].str.endswith('Engreitz')
df = df[~rowsToRemove]
rowsToRemove = df['CellType'].str.endswith('2014')
df = df[~rowsToRemove]
rowsToRemove = df['CellType'].str.endswith('2017')
df = df[~rowsToRemove]
rowsToRemove = df['CellType'].str.endswith('h')
df = df[~rowsToRemove]

rowsToRemove = df['CellType'].str.match(r'^[A-Z]')
df = df[~rowsToRemove]

strings_to_match = ['thyroid_gland-ENCODE', 'trophoblast_cell-ENCODE', 'placenta-Roadmap', 'osteoblast-ENCODE',
					'astrocyte-ENCODE', 'adrenal_gland_fetal-ENCODE', 'bipolar_neuron_from_iPSC-ENCODE',
					'foreskin_fibroblast-Roadmap', 'hepatocyte-ENCODE', 'iPS_DF_19.11_Cell_Line-Roadmap',
					'induced_pluripotent_stem_cell-ENCODE', 'keratinocyte-Roadmap', 'muscle_of_leg_fetal-Roadmap',
					'muscle_of_trunk_fetal-Roadmap', 'myotube_originated_from_skeletal_muscle_myoblast-Roadmap',
					'endothelial_cell_of_umbilical_vein-Roadmap', 'gastrocnemius_medialis-ENCODE',
					'mammary_epithelial_cell-Roadmap', 'fibroblast_of_arm-ENCODE', 'fibroblast_of_dermis-Roadmap',
					'large_intestine_fetal-Roadmap', 'stomach_fetal-Roadmap', 'spinal_cord_fetal-ENCODE',
					'body_of_pancreas-ENCODE', 'adipose_tissue-ENCODE', 'cardiac_muscle_cell-ENCODE',
					'heart_ventricle-ENCODE']
rowsToRemove = df['CellType'].isin(strings_to_match)
df = df[~rowsToRemove]

# get id into separate column
df['id'] = df['name'].str.extract(r'\|(.*?)$')

# sort entries by cell/tissue type and put into individual files
grouped = df.groupby('CellType')
for tissue, group in grouped:
	filename = f"{tissue}.AvgHiC.ABC0.015.minus150.ForABCPaperV3.txt"
	group.to_csv(filename, index=False, sep='\t')

output_filename = file + ".txt"
df.to_csv(output_filename+"-filtered.txt", index=False, sep='\t')
