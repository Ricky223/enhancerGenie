# eQTLbased.py
# performs eQTL-based algorithm to match enhancer file to genes

import logging
import uuid
import pandas as pd
from pybedtools import BedTool
from pybedtools.helpers import BEDToolsError, cleanup
import os

logger = logging.getLogger('waitress')
logger.setLevel(logging.INFO)

def geneIDNorm(df):
    return df.gene_id.split('.')[0]

def startPoint(inputBedFile, pairsFile, helperFile, outputFile, assembly):
    logger.info('Starting eQTL-based for ' + inputBedFile)

    filepath = 'database/eqtl-based/'+assembly+'-GTEx_Analysis_v'+assembly[5]+'_eQTL/' + pairsFile
    try:
        matchesDf = getClosestGeneWithinDistance(inputBedFile, filepath, 1000000, 1)
    except BEDToolsError:
        raise Exception("ERROR in eqtlBased.py: startPoint(): Failed to call getClosestGeneWithinDistance()")

    geneInfoDf = pd.read_csv('database/eqtl-based/'+assembly+'-GTEx_Analysis_v'+assembly[5]+'_eQTL/'+helperFile, compression="gzip", sep='\t')
    # merge with helper file containing gene information on matching gene_ids
    finalDf = matchesDf.merge(geneInfoDf, left_on='var_gene_id', right_on='gene_id', how='left')
    # remove unnecessary columns from final dataframe
    finalDf = finalDf[['enh_chr', 'enh_start', 'enh_end', 'enh_id', 'gene_chr', 'gene_start', 'gene_end', 'gene_id',
                       'gene_name', 'dist_score', 'var_pval']]

    # filter out bad results by ensuring pval is positive
    finalDf = finalDf[finalDf['var_pval'] >= 0]
    # may need additional code to remove bad results ------------

    # set the data types of 'gene_start' and 'gene_end' columns to integers
    finalDf['gene_start'] = finalDf['gene_start'].astype(int)
    finalDf['gene_end'] = finalDf['gene_end'].astype(int)

    # remove the version ending from gene_id
    finalDf['gene_id'] = finalDf.apply(geneIDNorm, axis=1)

    # one enhancer can match with multiple variants of the same gene
    # but each enhancer-gene pair should be listed only once
    finalDf = finalDf.drop_duplicates(subset=['enh_id', 'gene_id'], keep='last')


    # write matches to output file
    finalDf.to_csv(outputFile, sep='\t', index=False)
    # removes any temp files
    cleanup()

    logger.info('Finished processing eQTL-based for ' + inputBedFile + ". Results in " + outputFile)
    return outputFile


# cleanData cleans the matches dataframe to remove bad entries/duplicates
#   returns cleaned dataframe
def cleanData(matchesDf, maxDistance, enhancerFile):
    # remove any matches that are further than the absolute value of maxDistance (in either direction)
    matchesDf = matchesDf[(matchesDf[len(matchesDf.columns) - 1].between(-maxDistance, maxDistance))]

    # store enhancer file as data frame
    enhancerDf = pd.read_csv(enhancerFile, sep='\t', header=None)
    # remove unneeded columns from matchesDf, if enhancer file contained extra columns
    matchesDf = matchesDf.copy()
    matchesDf.drop(columns=matchesDf.columns[4:len(enhancerDf.columns)],
        axis=1,
        inplace=True)

    # rename columns in the dataframe for ease of use
    matchesDf.columns = ['enh_chr', 'enh_start', 'enh_end', 'enh_id', 'var_chr', 'var_start', 'var_end',
                         'var_gene_id', 'var_pval', 'dist_score']

    # remove duplicates
    matchesDf = matchesDf.drop_duplicates().reset_index(drop=True)
    return matchesDf


# getClosestGeneWithinDistance finds matches for enhancer to variant, returning the matches in a dataframe
def getClosestGeneWithinDistance(enhancerFile, variantFile, maxDistance, numMatches):
    # sort enhancers by chromosome then start position increasing
    enhancers = BedTool(enhancerFile).sort()
    # variant database is pre-sorted
    variants = BedTool(variantFile)

    # get the closest gene to each enhancer
    #   d=True - store the distance
    #   k - report the k-closest hits (default is 1)
    #   put output in temp file
    tempFileName = 'temp/tempEQTL'+str(uuid.uuid4())+'.bed'
    enhancers.closest(variants, d=True, k=numMatches, output=tempFileName)
    # get matches and their distances as data frame
    matchesDf = pd.read_csv(tempFileName, sep='\t', header=None)
    # delete temp file
    os.remove(tempFileName)

    # remove bad entries and any duplicates
    matchesDf = cleanData(matchesDf, maxDistance, enhancerFile)

    # return data frame of matches
    return matchesDf
