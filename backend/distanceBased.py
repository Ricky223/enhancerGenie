# distanceBased.py
# performs distance-based algorithm to match enhancer file to genes

import logging
import pandas as pd
from pybedtools import BedTool
from pybedtools.helpers import BEDToolsError, cleanup
import os
import uuid

logger = logging.getLogger('waitress')
logger.setLevel(logging.INFO)

# getClosestGeneWithinDistance finds matches for enhancer to gene, returning the matches in a dataframe
def getClosestGeneWithinDistance(enhancerFile, geneFile, maxDistance, numMatches):
    # sort enhancers by chromosome then start position increasing
    enhancers = BedTool(enhancerFile).sort()
    # gene database is pre-sorted
    genes = BedTool(geneFile)

    # get the closest gene to each enhancer
    #   d=True - store the distance
    #   k - report the k-closest hits (default is 1)
    #   io - ignore overlap, we want features that do not overlap at all
    #   put output in temp file
    tempFileName = 'temp/tempDistance' + str(uuid.uuid4()) + '.bed'
    enhancers.closest(genes, d=True, k=numMatches, io=True, output=tempFileName)

    # get matches and their distances as data frame
    matchesDf = pd.read_csv(tempFileName, sep='\t', header=None)
    # remove bad entries and any duplicates
    matchesDf = cleanData(matchesDf, maxDistance, enhancerFile)

    # delete temp file
    os.remove(tempFileName)
    # return data frame of matches
    return matchesDf

# previewDataframe - displays size of dataframe and some contents
def previewDataframe(dataframe):
    print(dataframe.head())
    print(dataframe.tail())
    print("Length of dataframe: " + str(len(dataframe)))

# cleanData cleans the matches dataframe to remove bad entries/duplicates
#   returns cleaned dataframe
def cleanData(matchesDf, maxDistance, enhancerFile):
    # remove any matches that are further than the absolute value of maxDistance (in either direction)
    matchesDf = matchesDf[(matchesDf[len(matchesDf.columns) - 1].between(-maxDistance, maxDistance))]

    # store files as data frames
    enhancerDf = pd.read_csv(enhancerFile, sep='\t', header=None)
    # remove unneeded columns from matchesDf, if enhancer file contained extra columns
    matchesDf = matchesDf.copy()
    matchesDf.drop(columns=matchesDf.columns[4:len(enhancerDf.columns)],
                   axis=1,
                   inplace=True)
    # rename columns in the dataframe for ease of use
    matchesDf.columns = ['enh_chr', 'enh_start', 'enh_end', 'enh_id', 'gene_chr', 'gene_start', 'gene_end',
                         'gene_id', 'dist_score']
    # remove lines that don't contain a geneID, are invalid
    matchesDf = matchesDf[matchesDf['gene_id'].astype(str).str.contains('ENSG')]

    # remove duplicates
    matchesDf = matchesDf.drop_duplicates().reset_index(drop=True)
    return matchesDf


# startPoint - function called by executor.py
# finds and converts matches to a file using distance-based algorithm
def startPoint(inputBedFile, outputFile, assembly):
    logger.info('Starting distance-based for ' + inputBedFile)

    try:
        matchesDf = getClosestGeneWithinDistance(inputBedFile, 'database/distance-based/'+assembly+'-genes.bed', 1000000, 1)
    except BEDToolsError:
        raise Exception("ERROR in distanceBased.py: startPoint(): Failed to call getClosestGeneWithinDistance()")

    # write matches to output file
    matchesDf.to_csv(outputFile, sep='\t', index=False)
    # removes any temp files
    cleanup()

    logger.info('Finished processing distance-based for ' + inputBedFile + ". Results in " + outputFile)
    return outputFile
