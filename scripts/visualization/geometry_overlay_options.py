import enum
from datasets.loading import statcan 
import numpy as np 
import geopandas as gp 
import matplotlib.pyplot as plt 

hierarchichal_boundaries = [
    'provinces',
    'economic_regions',
    'census_divisions',
    'census_subdivisions',
    'dissemination_areas',
    'dissemination_blocks',
]

pop_boundaries = [
    'population_centres'#,'population_ecumene'
]

CRS = statcan.boundary('provinces').crs

(top_x, top_y), (bot_x, bot_y) = (51.47158855784268, -115.93481725971563), (50.596251846138934, -113.09019534018066)
points = gp.points_from_xy(y=[top_x, top_x, bot_x, bot_x, top_x], x=[top_y, bot_y, bot_y, top_y, top_y], crs='epsg:4326').to_crs(CRS)

areas = gp.GeoDataFrame(data={'area':['Calgary']*len(points)}, geometry=points).dissolve().convex_hull


fig, ax = plt.subplots(figsize=(20,20))

hexagons = statcan.hexagons().to_crs(CRS)
hexagons.clip(areas).to_crs('epsg:4326').boundary.plot(color='k', label='Hexagons', ax=ax, lw=0.5)

linestyles = ['solid','dashed', 'dashdot', 'dotted', 'dotted', 'dotted']
for i, boundary_name in enumerate((hierarchichal_boundaries[::-1])):
    boundary = statcan.boundary(boundary_name)
    boundary.clip(areas).to_crs('epsg:4326').boundary.plot(
        ax=ax, label=boundary_name, 
        color=f'C{i}', ls=linestyles[i]
        )

boundary_name = 'population_centres'
boundary = statcan.boundary(boundary_name)
boundary.clip(areas).to_crs('epsg:4326').plot(
    ax=ax, label=boundary_name, 
    color='gray',
    alpha=0.5, edgecolor='k'
    )

ax.legend()



areas = statcan.boundary('provinces').loc[lambda s:s.PRNAME=='Alberta']
fig, ax = plt.subplots(figsize=(20,20))

hexagons = statcan.hexagons().to_crs(CRS)
hexagons.clip(areas).to_crs('epsg:4326').boundary.plot(color='k', label='Hexagons', ax=ax, lw=0.5)

linestyles = ['solid','solid','dashed', 'dashdot', 'dotted']
for i, boundary_name in enumerate((hierarchichal_boundaries[:-1])):
    boundary = statcan.boundary(boundary_name)
    boundary.clip(areas).to_crs('epsg:4326').boundary.plot(
        ax=ax, label=boundary_name, 
        color=f'C{i}', ls=linestyles[i])

boundary_name = 'population_centres'
boundary = statcan.boundary(boundary_name)
boundary.clip(areas).to_crs('epsg:4326').plot(
    ax=ax, label=boundary_name, 
    color='gray',
    alpha=0.5, edgecolor='k')

ax.legend()

