import sys
sys.path.append("..")
import src.config
from src.datasets.loading import statcan, ookla
import numpy as np 
import pandas as pd
import geopandas as gp
import re


def import_table(download=False):
    ookla_tiles = ookla.canada_tiles()
    da_pops = statcan.dissemination_areas_populations()
    ookla_tiles_w_centroid =ookla_tiles.copy()
    ookla_tiles_w_centroid['coordinate']=ookla_tiles.geometry.centroid
    ookla_tiles_w_centroid["lat"]=ookla_tiles_w_centroid["coordinate"].apply(lambda x:x.x) 
    ookla_tiles_w_centroid["lon"]=ookla_tiles_w_centroid["coordinate"].apply(lambda x:x.y) 
    ookla_tiles_w_centroid.drop(columns=['coordinate'],inplace=True)

    o = gp.read_file(src.config.OVERLAYS_DIR / 'tile_das_overlay') #this can take a few minutes to load.
    tile_da_label = o.dropna(subset=['DAUID','quadkey']).sort_values(by=['quadkey','tile_frac'],ascending=False).drop_duplicates(subset='quadkey', keep='first')
    tile_da_label['quadkey'] = tile_da_label['quadkey'].astype(int)
    tile_da_label['DAUID'] = tile_da_label['DAUID'].astype(int)

    last_4_quarters = ookla.speed_data(ookla.available_files().loc[('fixed',2021,3):('fixed',2022,2)].path)

    down = last_4_quarters.groupby('quadkey').apply(lambda s:np.average(s.avg_d_kbps, weights=s.tests)).rename('avg_d_kbps')
    up = last_4_quarters.groupby('quadkey').apply(lambda s:np.average(s.avg_u_kbps, weights=s.tests)).rename('avg_u_kbps')
    tests = last_4_quarters.groupby('quadkey')['tests'].sum()
    devices = last_4_quarters.groupby('quadkey')['devices'].sum()
    last4_agg = pd.concat([down, up, tests, devices],axis=1)

    ## merge dissemination area (DA) populations with ookla tiles (already combined with other statcan data)
    features_table = tile_da_label.merge(da_pops, on='DAUID', how='left')
    features_table['DAPOP'] = features_table['DAPOP'].fillna(0).astype(int)
    del features_table['GEO_NAME']
    features_table = pd.DataFrame(features_table)
    del features_table['geometry']
    features_table['POP_DENSITY'] = features_table['DAPOP']/features_table['das_area']*1000**2 #people per square kilometer

    # take all ookla tiles, merge the speeds data and tile labels and populations
    features_table = ookla_tiles_w_centroid.merge(last4_agg, on='quadkey').merge(features_table, on='quadkey')

    # compute spatial joins to identify if area is a population centre
    pop_info = statcan.boundary('population_centres').to_crs('epsg:4326')
    pop_info = pop_info[['PCUID', 'PCNAME', 'PCTYPE', 'PCPUID', 'PCCLASS', 'geometry']] ##removes some redundant cols from DAs
    features_table = features_table.sjoin(pop_info, how='left')
    del features_table['index_right']
    features_table = features_table.sort_values(by=['PCUID','quadkey']).drop_duplicates(subset=['quadkey'])
    if download==True:
        features_table.to_pickle("cluster_table")
    return features_table

