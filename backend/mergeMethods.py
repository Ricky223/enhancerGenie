# mergeMethods.py
# Generates chart data and performs analysis
# on results

import logging
import os
import numpy as np
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
logger = logging.getLogger('waitress')
logger.setLevel(logging.INFO)

colors = {
    "Distance": {"bgColor": "rgba(255, 0, 0, 0.3)", "borderColor": 'rgba(255, 0, 0, 0.7)'},  # red
    "eQTL": {"bgColor": "rgba(2, 185, 0, 0.3)", "borderColor": 'rgba(2, 185, 0, 0.7)'},  # green
    "Chromatin Loop": {"bgColor": "rgba(0,131,255,0.3)", "borderColor": 'rgba(0,131,255,0.7)'},  # light blue
    "Activity by Contact": {"bgColor": "rgba(255,146,0,0.3)", "borderColor": 'rgba(255,146,0,0.7)'},  # orange
    "Matches": {"bgColor": "rgba(108,0,255,0.3)", "borderColor": 'rgba(108,0,255,0.7)'},  # purple
    "Enhancers": {"bgColor": "rgba(255,209,0,0.3)", "borderColor": 'rgba(255,209,0,0.7)'},  # yellow
    "Genes": {"bgColor": "rgba(84, 255, 235, 0.5)", "borderColor": 'rgba(0, 255, 225, 0.5)'}  # teal
}


def checkAndSupplyFile(file):
    df = pd.DataFrame()
    try:
        df = pd.read_csv(file, sep='\t')
        return df
    except pd.errors.EmptyDataError as e:
        return df


def generateKey(df):
    return str(df['enh_id']) + '-' + str(df['gene_id'])


# counts total unique enhancers/genes/matches for each alg into json
def totalComparisons(df, title):
    # separate by algorithm
    algorithms = df['algorithm'].unique()
    algorithm_dfs = {algorithm: df[df['algorithm'] == algorithm] for algorithm in algorithms}

    datasets_by_alg = []
    for algorithm, dataframe in algorithm_dfs.items():
        matchTotal = dataframe['key'].nunique()
        enhancerTotal = dataframe['enh_id'].nunique()
        geneTotal = dataframe['gene_id'].nunique()
        datasets_by_alg.append({
            "label": algorithm,
            "data": [matchTotal, enhancerTotal, geneTotal]
        })

    # Create the final dataset with dynamic labels
    results = {
        "title": title,
        "labels": algorithms.tolist(),
        "datasets": [
            {
                "label": "Unique Matches",
                "data": [entry["data"][0] for entry in datasets_by_alg],
                "backgroundColor": colors["Matches"]["bgColor"],
                "borderColor": colors["Matches"]["borderColor"]
            },
            {
                "label": "Unique Enhancers",
                "data": [entry["data"][1] for entry in datasets_by_alg],
                "backgroundColor": colors["Enhancers"]["bgColor"],
                "borderColor": colors["Enhancers"]["borderColor"]
            },
            {
                "label": "Unique Genes",
                "data": [entry["data"][2] for entry in datasets_by_alg],
                "backgroundColor": colors["Genes"]["bgColor"],
                "borderColor": colors["Genes"]["borderColor"]
            }
        ],
        "ylabel": '',
        "xlabel": ''
    }

    return results


# calculates enhancer redundancy (x enhancers to 1 gene y times)
# for each alg into json
def enhancerRedundancy(df, title):
    # separate by algorithm
    algorithms = df['algorithm'].unique()
    algorithm_dfs = {algorithm: df[df['algorithm'] == algorithm] for algorithm in algorithms}

    datasets = []
    for algorithm, dataframe in algorithm_dfs.items():
        # Group by 'gene' and count the unique 'enhancer' values in each group
        groupedByGenes = dataframe.groupby('gene_id')
        # Count how many times gene_id appears 1, 2, 3, etc. times
        gene_id_counts = groupedByGenes['gene_id'].value_counts()
        counts_dict = gene_id_counts.value_counts().to_dict()
        # Initialize a dictionary with values from 1 to 100, all set to 0
        results = {i: 0 for i in range(1, 102)}
        # counts_dict: x enhancers - y times
        for num_enhancers, count in counts_dict.items():
            if num_enhancers <= 10:
                results[num_enhancers] = count
            elif num_enhancers <= 50:
                results[50] += count
            elif num_enhancers <= 100:
                results[100] += count
            else:
                results[101] += count
        # remove duplicated bins (ex: remove 17 enhancers: 0 times, since that data is in the <= 50 bin)
        results = {k: v for k, v in results.items()
                   if (k <= 10 or k % 50 == 0 or k == 101)}

        datasets.append({
            "label": algorithm,
            "data": list(results.values()),
            "backgroundColor": colors[algorithm]["bgColor"],
            "borderColor": colors[algorithm]["borderColor"]
        })

    # Create the final dataset with dynamic labels
    return {
        "title": title,
        "labels": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "\u2264 50", "\u2264 100", "> 100"],
        "datasets": datasets,
        "ylabel": 'Number of Occurrences',
        "xlabel": 'Number of Enhancers Per Gene'
    }


# sort distance matches into bins based on dist_score
# store counts of each into json
def distanceScores(df, title):
    # sort into bins
    bin_edges = [-1, 0, 1, 2, 3, 4, 5, 6, float('inf')]
    labels = ['0', '\u2264 1', '\u2264 2', '\u2264 3', '\u2264 4', '\u2264 5', '\u2264 6', '> 6']
    df['bins'] = pd.cut(df['dist_score'], bins=bin_edges, labels=labels)
    # count how many results are in each bin
    bin_counts = df['bins'].value_counts()
    data = [int(bin_counts[label]) for label in labels]
    # write the counts to json
    return {
        "title": title,
        "labels": labels,
        "datasets": [
            {
                "label": 'Number of distance matches',
                "data": data,
                "backgroundColor": colors["Distance"]["bgColor"],
                "borderColor": colors["Distance"]["borderColor"]
            }
        ],
        "ylabel": '',
        "xlabel": 'Distance Score Distribution (Log Scale)'
    }


# sort chromatin loop matches into bins based on loop_score
def chromatinLoopScores(df, title):
    bins = [-1, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, float('inf')]
    labels = ['\u2264 0.65', '> 0.65', '> 0.7', '> 0.75', '> 0.8', '> 0.85', '> 0.9', '> 0.95']
    df['bins'] = pd.cut(df['loop_score'], bins=bins, labels=labels)
    bin_counts = df['bins'].value_counts()
    # reverse the order of the labels
    labels = labels[::-1]
    data = [int(bin_counts[label]) for label in labels]
    # write the counts to json
    return {
        "title": title,
        "labels": labels,
        "datasets": [
            {
                "label": 'Number of chromatin loop matches',
                "data": data,
                "backgroundColor": colors["Chromatin Loop"]["bgColor"],
                "borderColor": colors["Chromatin Loop"]["borderColor"]
            }
        ],
        "ylabel": '',
        "xlabel": 'Loop Score Distribution'
    }


# sort eqtl matches into bins based on var_pval
def eqtlScores(df, title):
    bin_edges = [0, 0.000000025, 0.00000005, 0.0000001, 0.0000002, 0.0000004,
                 0.0000006, 0.0000008, 0.000001, 0.000002, float('inf')]
    labels = ['\u2264 2.5e-8', '\u2264 5e-8', '\u2264 1e-7', '\u2264 2e-7', '\u2264 4e-7',
              '\u2264 6e-7', '\u2264 8e-7', '\u2264 1e-6', '\u2264 2e-6', '> 2e-6']
    df['bins'] = pd.cut(df['var_pval'], bins=bin_edges, labels=labels)
    bin_counts = df['bins'].value_counts()
    data = [int(bin_counts[label]) for label in labels]
    return {
        "title": title,
        "labels": labels,
        "datasets": [
            {
                "label": 'Number of eQTL matches',
                "data": data,
                "backgroundColor": colors["eQTL"]["bgColor"],
                "borderColor": colors["eQTL"]["borderColor"]
            }
        ],
        "ylabel": '',
        "xlabel": 'P-val Score Distribution'
    }


# sort eqtl matches into bins based on dist_score
def eqtlDistanceScores(df, title):
    # sort into bins
    bin_edges = [-1, 0, 1, 2, 3, 4, 5, 6, float('inf')]
    labels = ['0', '\u2264 1', '\u2264 2', '\u2264 3', '\u2264 4', '\u2264 5', '\u2264 6', '> 6']
    df['bins'] = pd.cut(df['dist_score'], bins=bin_edges, labels=labels)
    # count how many results are in each bin
    bin_counts = df['bins'].value_counts()
    data = [int(bin_counts[label]) for label in labels]
    # write the counts to json
    return {
        "title": title,
        "labels": labels,
        "datasets": [
            {
                "label": 'Number of eQTL matches',
                "data": data,
                "backgroundColor": colors["eQTL"]["bgColor"],
                "borderColor": colors["eQTL"]["borderColor"]
            }
        ],
        "ylabel": '',
        "xlabel": 'Distance Score Distribution (Log Scale)'
    }


# sort abc matches into bins based on ABC_score
def abcScores(df, title):
    bins = [0, 0.015, 0.0175, 0.02, 0.025, 0.03, 0.04, 0.06, 0.08, 0.1, 0.2, float('inf')]
    labels = ['\u2264 0.015', '\u2264 0.0175', '\u2264 0.02', '\u2264 0.025', '\u2264 0.03', '\u2264 0.04',
              '\u2264 0.06', '\u2264 0.08', '\u2264 0.1', '\u2264 0.2', '> 0.2']
    df['bins'] = pd.cut(df['ABC_score'], bins=bins, labels=labels)
    bin_counts = df['bins'].value_counts()
    # reverse the order of the labels
    labels = labels[::-1]
    data = [int(bin_counts[label]) for label in labels]
    # write the counts to json
    return {
        "title": title,
        "labels": labels,
        "datasets": [
            {
                "label": 'Number of activity by contact matches',
                "data": data,
                "backgroundColor": colors["Activity by Contact"]["bgColor"],
                "borderColor": colors["Activity by Contact"]["borderColor"]
            }
        ],
        "ylabel": '',
        "xlabel": 'ABC Score Distribution'
    }


# In[39]:
def startPoint(chiapetVal, distanceVal, eqtlVal, abcVal, imagesFileName, algorithms):
    logger.info("Started visualization")

    methods = []
    charts = []
    if 'chiaPet' in algorithms:
        chiaPet = checkAndSupplyFile(chiapetVal)
        if not chiaPet.empty:
            chiaPet['algorithm'] = 'Chromatin Loop'
            if (len(chiaPet['enh_id']) > 0) and (len(chiaPet['gene_id']) > 0):
                chiaPet['key'] = chiaPet.apply(generateKey, axis=1)
            methods.append(chiaPet)
            # only assembly 38 contains loop scores
            if 'loop_score' in chiaPet.columns:
                charts.append(chromatinLoopScores(chiaPet, "Chromatin Loop Matches By Loop Score"))
    if 'distance' in algorithms:
        distance = checkAndSupplyFile(distanceVal)
        if not distance.empty:
            distance['dist_score'] = distance['dist_score'].apply(lambda x: np.log10(x) if x != 0 else x)
            # add new column labeling which algorithm this result came from
            distance['algorithm'] = 'Distance'
            # generate new key column for unique ID
            if (len(distance['enh_id']) > 0) and (len(distance['gene_id']) > 0):
                distance['key'] = distance.apply(generateKey, axis=1)
            methods.append(distance)
            charts.append(distanceScores(distance, "Distance Matches By Distance Score"))
    if 'eqtl' in algorithms:
        eqTL = checkAndSupplyFile(eqtlVal)
        if not eqTL.empty:
            eqTL['dist_score'] = eqTL['dist_score'].apply(lambda x: np.log10(x) if x != 0 else x)
            eqTL['algorithm'] = 'eQTL'
            if (len(eqTL['enh_id']) > 0) and (len(eqTL['gene_id']) > 0):
                eqTL['key'] = eqTL.apply(generateKey, axis=1)
            methods.append(eqTL)
            charts.append(eqtlDistanceScores(eqTL, "eQTL Matches By Distance Score"))
            charts.append(eqtlScores(eqTL, "eQTL Matches By Pval Score"))
    if 'abc' in algorithms:
        abc = checkAndSupplyFile(abcVal)
        if not abc.empty:
            abc['algorithm'] = 'Activity by Contact'
            if (len(abc['enh_id']) > 0) and (len(abc['gene_id']) > 0):
                abc['key'] = abc.apply(generateKey, axis=1)
            methods.append(abc)
            charts.append(abcScores(abc, "Activity by Contact Matches by ABC Score"))

    if methods:
        # finalConcat is a huge dataframe of all results from all algorithms used
        finalConcat = pd.concat(methods)

        # generate some chart.py.js data and add to charts
        charts.append(totalComparisons(finalConcat, "Total Count Comparisons"))
        charts.append(enhancerRedundancy(finalConcat, "Enhancer Redundancy"))

    # imagesFileNameBar = imagesFileName + 'BarPlots/'
    # if not os.path.exists(imagesFileNameBar):
    #     # If it doesn't exist, create it
    #     os.makedirs(imagesFileNameBar)

    return charts
