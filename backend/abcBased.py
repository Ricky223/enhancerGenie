# abcBased.py
# runs algorithm using activity by contact database
# to match enhancers to genes

import logging
import pandas as pd
from pybedtools import BedTool
import os
import uuid

from pybedtools.helpers import BEDToolsError

logger = logging.getLogger('waitress')
logger.setLevel(logging.INFO)

def startPoint(inputBedFile, DBfile, outputFile):
    logger.info('Starting activity by contact-based for ' + inputBedFile)

    try:
        matchesDf = getClosestGeneWithinDistance(inputBedFile, 'database/abc-based/'+DBfile, 0, 1)
    except BEDToolsError:
        raise Exception("ERROR in abcBased.py: startPoint(): Failed to call getClosestGeneWithinDistance()")

    # write matches to output
    matchesDf.to_csv(outputFile, sep='\t', index=False)
    logger.info('Finished processing activity by contact-based for ' + inputBedFile + ". Results in " + outputFile)
    return outputFile


def getClosestGeneWithinDistance(enhancerFile, geneFile, maxDistance, numMatches):
    enhancers = BedTool(enhancerFile).sort()
    genes = BedTool(geneFile).sort()
    tempFileName = 'temp/tempABC' + str(uuid.uuid4()) + '.bed'
    # find overlap between enhancers and regions from ABC method
    enhancers.closest(genes, d=True, k=numMatches, output=tempFileName)
    matchesDf = pd.read_csv(tempFileName, sep='\t', header=None)
    matchesDf = cleanData(matchesDf, maxDistance, enhancerFile)
    os.remove(tempFileName)
    return matchesDf


def cleanData(matchesDf, maxDistance, enhancerFile):
    # distance should be 0 (where they overlap)
    matchesDf = matchesDf[matchesDf[len(matchesDf.columns)-1] == maxDistance]
    enhancerDf = pd.read_csv(enhancerFile, sep='\t', header=None)
    matchesDf = matchesDf.copy()
    matchesDf.drop(columns=matchesDf.columns[4:len(enhancerDf.columns)],
                   axis=1,
                   inplace=True)
    # rename columns in the dataframe for ease of use
    matchesDf.columns = ['enh_chr', 'enh_start', 'enh_end', 'enh_id', 'NA', 'NA', 'NA', 'NA', 'NA',
                         'gene_id', 'NA', 'NA', 'NA', 'NA', 'NA', 'ABC_score', 'NA', 'NA', 'NA']
    # remove unused columns
    matchesDf = matchesDf.drop(columns=['NA'])
    # remove duplicates
    matchesDf = matchesDf.drop_duplicates().reset_index(drop=True)
    matchesDf = matchesDf.drop_duplicates(subset=['enh_id', 'gene_id'], keep='first')
    return matchesDf

