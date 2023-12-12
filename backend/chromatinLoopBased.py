# chromatinLoopBased.py
# runs algorithm using chromatin loop database
# to match enhancers to genes

import logging
import pandas as pd
from pybedtools import BedTool
import os
import uuid
from Process import Process

logger = logging.getLogger('waitress')
logger.setLevel(logging.INFO)


def startPoint(inputBedFile, DBfile, outputFile, assembly):
    logger.info('Starting chromatin loop-based for ' + inputBedFile)

    # use database file to locate each halves of said file
    leftFile = 'database/chromatin-loop-based/'+assembly+'-loops/'+DBfile+'-left.loops'
    rightFile = 'database/chromatin-loop-based/'+assembly+'-loops/'+DBfile+'-right.loops'

    allDf = checkIfGeneOrEnhancer(inputBedFile, 'database/chromatin-loop-based/'+assembly+'-loops/'+
                                  assembly+'-genesTSS.bed', leftFile, rightFile)

    # enhancers & the region they live in from the left side of the chromatin file
    left_enhancer = allDf[0]
    # genes & the region they live in from the left side of the chromatin file
    left_gene = allDf[1]
    right_enhancer = allDf[2]
    right_gene = allDf[3]

    enh_geneDf = pd.DataFrame()
    gene_enhDf = pd.DataFrame()
    # if there are enhancers in the left side and genes in the right side
    if (left_enhancer.shape[0] != 0) and (right_gene.shape[0] != 0):
        # merge them on key - contains matches from an enhancer in region 1 of loop with gene from region 2 of loop
        enh_geneDf = pd.merge(left_enhancer, right_gene, how='inner', left_on=['loop_key'], right_on=['loop_key'])
    # if there are genes in left and enhancers in right
    if (right_enhancer.shape[0] != 0) and (left_gene.shape[0] != 0):
        gene_enhDf = pd.merge(right_enhancer, left_gene, how='inner', left_on=['loop_key'], right_on=['loop_key'])

    # get all matches
    matchesDf = pd.concat([enh_geneDf, gene_enhDf], axis=0)
    # ensure there is at least one match
    if matchesDf.shape[0] != 0:
        # drop any duplicate/unneeded columns - there probably is a better way to do this but
        matchesDf = matchesDf.drop('loop_chr_x', axis=1)
        matchesDf = matchesDf.drop('dist_score_x', axis=1)
        matchesDf = matchesDf.drop('dist_score_y', axis=1)
        matchesDf = matchesDf.drop('loop_key', axis=1)
        matchesDf = matchesDf.drop('loop_score_x', axis=1)
        matchesDf = matchesDf.drop('TSS', axis=1)
        matchesDf = matchesDf.drop('loop_start_x', axis=1)
        matchesDf = matchesDf.drop('loop_start_y', axis=1)
        matchesDf = matchesDf.drop('loop_end_x', axis=1)
        matchesDf = matchesDf.drop('loop_end_y', axis=1)
        matchesDf = matchesDf.drop('loop_chr_y', axis=1)
        # remove duplicate matches
        matchesDf = matchesDf.drop_duplicates(subset=['enh_id', 'gene_id'], keep='last')
        # rename column
        matchesDf = matchesDf.rename(columns={'loop_score_y': 'loop_score'})
        # sort
        matchesDf = matchesDf.sort_values(by=['enh_chr', 'enh_start'])

        # chromatin loop data for assembly 37 does not have loop scores
        if assembly == "GRCh37":
            matchesDf = matchesDf.drop('loop_score', axis=1)

    # write matches to output
    matchesDf.to_csv(outputFile, sep='\t', index=False)

    logger.info('Finished processing chromatin loop-based for ' + inputBedFile + ". Results in " + outputFile)
    return outputFile


def getClosestGeneWithinDistance(toMatchFile, matchToFile, maxDistance, numMatches, outputFile):
    toMatch = BedTool(toMatchFile).sort()
    matchTo = BedTool(matchToFile).sort()
    tempFile = 'temp/tempChromatinLoop'+str(uuid.uuid4())+".bed"
    toMatch.closest(matchTo, d=True, k=numMatches, output=tempFile)
    matchesDf = pd.read_csv(tempFile, sep='\t', header=None)
    # want matches where the distance is 0, where toMatch lives in the matchTo's domain
    matchesDf = matchesDf[matchesDf[len(matchesDf.columns)-1] == maxDistance]
    os.remove(tempFile)
    # write matchesDf to outputFile
    matchesDf.to_csv(outputFile, index=False, sep='\t')
    return outputFile

# outputs enhancers/genes which fall into a region from the right/left side chromatin loop file
# allows us to know what enhancers/genes live in each region from chromatin loop file
def checkIfGeneOrEnhancer(inputEnhancerFile, geneFile, leftLoopFile, rightLoopFile):
    tempFile = 'temp/tempChromatinLoop'+str(uuid.uuid4())
    enhancerLeftFile = tempFile + "_1.bed"
    geneLeftFile = tempFile + "_2.bed"
    enhancerRightFile = tempFile + "_3.bed"
    geneRightFile = tempFile + "_4.bed"

    p1 = Process(target=getClosestGeneWithinDistance, args=[inputEnhancerFile,leftLoopFile,0,1,enhancerLeftFile])
    p1.start()
    p2 = Process(target=getClosestGeneWithinDistance, args=[geneFile,leftLoopFile,0,1,geneLeftFile])
    p2.start()
    p3 = Process(target=getClosestGeneWithinDistance, args=[inputEnhancerFile,rightLoopFile,0,1,enhancerRightFile])
    p3.start()
    p4 = Process(target=getClosestGeneWithinDistance, args=[geneFile,rightLoopFile,0,1,geneRightFile])
    p4.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()

    enhancerLeft = pd.read_csv(enhancerLeftFile, sep='\t')
    enhancerLeft.columns = ['enh_chr', 'enh_start', 'enh_end', 'enh_id', 'loop_chr', 'loop_start', 'loop_end', 'loop_key', 'loop_score', 'dist_score']

    geneLeft = pd.read_csv(geneLeftFile, sep='\t')
    geneLeft.columns = ['gene_chr', 'TSS', 'TSS_dup', 'gene_start', 'gene_end', 'gene_id', 'loop_chr', 'loop_start',
                        'loop_end', 'loop_key', 'loop_score', 'dist_score']
    geneLeft = geneLeft.drop('TSS_dup', axis=1)

    enhancerRight = pd.read_csv(enhancerRightFile, sep='\t')
    enhancerRight.columns = ['enh_chr', 'enh_start', 'enh_end', 'enh_id', 'loop_chr', 'loop_start', 'loop_end', 'loop_key', 'loop_score', 'dist_score']

    geneRight = pd.read_csv(geneRightFile, sep='\t')
    geneRight.columns = ['gene_chr', 'TSS', 'TSS_dup', 'gene_start', 'gene_end', 'gene_id', 'loop_chr', 'loop_start', 'loop_end', 'loop_key', 'loop_score', 'dist_score']
    geneRight = geneRight.drop('TSS_dup', axis=1)

    # remove temp files
    os.remove(enhancerLeftFile)
    os.remove(geneLeftFile)
    os.remove(enhancerRightFile)
    os.remove(geneRightFile)

    return [enhancerLeft, geneLeft, enhancerRight, geneRight]
