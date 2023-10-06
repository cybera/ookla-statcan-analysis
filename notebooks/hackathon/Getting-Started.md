# Getting Started
## Clone this git repo:
```bash
git clone https://github.com/cybera/ookla-statcan-analysis.git
cd ookla-statcan-analysis
```

Install necessary python libraries in requirements.txt (pip) or environment.yaml (conda). 
Recommendation is to use either a virtual environment with pip or a conda environment (install
miniconda).

## Download data:
```bash
mkdir data/hackathon
curl -O https://swift-yyc.cloud.cybera.ca:8080/v1/AUTH_233e84cd313945c992b4b585f7b9125d/ookla-statcan-analysis/data/hackathon/geometry.gpkg 
curl -O https://swift-yyc.cloud.cybera.ca:8080/v1/AUTH_233e84cd313945c992b4b585f7b9125d/ookla-statcan-analysis/data/hackathon/speeds.csv
```
# Explore Data

## Verify Data Loads
Check `Basic-EDA.ipynb` notebook works.
Do some exploratory data analysis of your own.

## Review statcan definitions and ookla definitions: 
Review data contents and check for values and definitions in the related web resources:
- https://www.ookla.com/ookla-for-good/open-data
- https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/boundary-limites/index2021-eng.cfm?year=21 
- https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/page.cfm?Lang=E&GENDERlist=1,2,3&STATISTIClist=1,4&HEADERlist=0&DGUIDlist=2021A00054806016&SearchText=calgary 

# Plan With Group
Decide on question to answer or data analysis approach for your group. Brainstorm on approach/goal/question for your team's hackathon activity.

Define 3-6 tasks with defineable end points that are accomplishable within 1 day.
- One of which should be to fork this github repository and add team members.
- Assign tasks; touch base at next standup.
- Discuss each others' progress and refine any current tasks that need it; 
continue with new tasks if done.

Make a demo for end of hackathon period.
