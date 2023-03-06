import pandas as pd
import numpy as np
import json
from ferm_analysis.api import FermentationAPI

def query_data(project_id, hermes_runs):
    api = FermentationAPI()
    # pulling data from API base on project id
    data = api.search(project_id = project_id)
    all_hermes = list(data['hermes_run'])
    #print(all_hermes)
    
    filter = data[(data['hermes_run'].isin(hermes_runs)) & (data['hermes_run'] is not None)]
    
    hermes_run_id_df = filter[['run_id','hermes_run']]
    #print(hermes_run_id_df)
    measurements = filter.get_measurements() #will get all the measurements including the acquisition measurements
    measurements['measurement_set'].unique() #shows table names
    
    # break the data table into constituent tables
    biomass = measurements[(measurements['measurement_set'] == 'Biomass')]
    RCS = measurements[(measurements['measurement_set'] == 'Run Calculator Source')]
    titer = measurements[(measurements['measurement_set'] ==  'SOP01222_Demon FLO titer by GC-FID')] # is there a way to automate this?
    ferm_lucullus_trend = measurements[(measurements['measurement_set'] == 'Lucullus')]
    
    # apply pivoting to the measurement tables and titer tables
    biomass_cleaned = clean_pivot_table(biomass, hermes_run_id_df)
    RCS_cleaned = clean_pivot_table(RCS, hermes_run_id_df)
    titer_cleaned = clean_pivot_table_demon_titer(titer, hermes_run_id_df)
    lucullus_cleaned = clean_pivot_table(ferm_lucullus_trend, hermes_run_id_df, time_gap = 0) # time gap override the function setting
    
    # merge RCS and titer. Suffix is to avoid having duplicate names labeled as 'something'_x
    RCS_df = pd.merge(RCS_cleaned, titer_cleaned, on = ['run_id', 'sample_time','hermes_run'], how = 'left', suffixes = [None, '_duplicate'])
    
    # merge RCS and lucullus
    RCS_lucullus = combine_lucullus_RCS(RCS_df, lucullus_cleaned, time_gap = 0.25)
    
    return (biomass_cleaned, titer_cleaned, RCS_df, lucullus_cleaned, RCS_lucullus)


def clean_pivot_table(df, hermes_run_id_df, time_gap = 10):
    
    #pivoting input table to be index by run_id and sample_time
    df_pivoted = pd.pivot_table(df, values = 'value', index=['run_id','sample_time'], columns = 'measurement_name')

    # replace NaN with 0
    df_pivoted = df_pivoted.fillna(0)
    
    # reset index generated from pivot
    df_pivoted = df_pivoted.reset_index()
    
    # start a new dataframe
    df_cleaned = pd.DataFrame()
    
    # combining rows with similar time from each run into one row base on time gap
    for run in df_pivoted['run_id'].unique():
        for t in df_pivoted['sample_time']:
            df = df_pivoted[(df_pivoted['sample_time'] >= (t-time_gap)) & (df_pivoted['sample_time'] <= (t+time_gap)) & (df_pivoted['run_id'] == run)].max()
            df_cleaned = df_cleaned.append(df, ignore_index = True)
    
    # grouping duplicated rows in each run
    df_cleaned = df_cleaned.groupby(['run_id','sample_time'],as_index=False).mean()
    
    #joining cleaned up dataframe with hermes run id dataframe by run_id key
    df_cleaned = pd.merge(df_cleaned,hermes_run_id_df, on = 'run_id')
    
    
    return df_cleaned

def clean_pivot_table_demon_titer(df, hermes_run_id_df, time_gap = 10):
    
    #pivoting input table to be index by run_id and sample_time
    df_pivoted = pd.pivot_table(df, values = 'value', index=['run_id','sample_time'], columns = ['measurement_name', 'sample_type', 'unit'])
    df_pivoted.columns = [' '.join(col) for col in df_pivoted.columns.values]
    
    #print(df_pivoted)
    # replace NaN with 0
    df_pivoted = df_pivoted.fillna(0)
    
    # reset index generated from pivot
    df_pivoted = df_pivoted.reset_index()
    
    # start a new dataframe
    df_cleaned = pd.DataFrame()
    
    # combining rows with similar time from each run into one row base on time gap
    for run in df_pivoted['run_id'].unique():
        for t in df_pivoted['sample_time']:
            df = df_pivoted[(df_pivoted['sample_time'] >= (t-time_gap)) & (df_pivoted['sample_time'] <= (t+time_gap)) & (df_pivoted['run_id'] == run)].max()
            df_cleaned = df_cleaned.append(df, ignore_index = True)
    
    # grouping duplicated rows in each run
    df_cleaned = df_cleaned.groupby(['run_id','sample_time'],as_index=False).mean()
    
    #joining cleaned up dataframe with hermes run id dataframe by run_id key
    df_cleaned = pd.merge(df_cleaned,hermes_run_id_df, on = 'run_id')
    
    
    return df_cleaned

def combine_lucullus_RCS(RCS_df, lucullus, time_gap = 0.25):
    
    # combine two dataframe together and order by sample time
    RCS_lucullus=pd.merge_ordered(RCS_df,lucullus, on=['hermes_run','sample_time'], suffixes = [None, '_duplicate'])
    
    df_cleaned = pd.DataFrame()
    RCS_time = RCS_df[['hermes_run','sample_time']]
    
    for run in RCS_lucullus['hermes_run'].unique():
    # df.loc[df['col1'] == value]
    # extracting sample time from the location of dataframe where hermes run in RCS = hermes run in RCS_Lucullus
        for t in RCS_time.loc[RCS_time['hermes_run'] == run]['sample_time']:
            df = RCS_lucullus[(RCS_lucullus['sample_time'] < 170) & (RCS_lucullus['sample_time'] > (t-time_gap)) & 
                              (RCS_lucullus['sample_time'] < (t+time_gap)) & (RCS_lucullus['hermes_run'] == run)].max()
            df_cleaned = df_cleaned.append(df, ignore_index = True)
    
    df_combined = df_cleaned.groupby(['run_id','hermes_run','sample_time'],as_index=False).mean() #if groupby run_id, hermes_run disappears    
    
    return df_combined