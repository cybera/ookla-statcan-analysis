###

echo 'I tried my besst. I hope this downloads all the things and processes them into data files.'
echo 'Requires an environment where "python" is the python3 command with installed libs'
echo 'And aws s3 must be installed'
echo ''

export PYTHONPATH="${PYTHONPATH}:./src"

# #
echo 'Downloading Ookla data from AWS'
aws s3 sync --no-sign-request --region=us-west-2 s3://ookla-open-data/shapefiles ./data/ookla-raw 

echo 'Filtering global Ookla tiles to Canada only'
#conda run -n ookla-statcan scripts/data/process_raw_ookla_faster.py
python scripts/data/process_raw_ookla_faster.py

echo 'Generating complex geometry overlays'
# conda run -n ookla-statcan scripts/data/create_overlays.py population_centres popctrs 
# conda run -n ookla-statcan scripts/data/create_overlays.py dissemination_areas das
python scripts/data/create_overlays.py population_centres popctrs 
python scripts/data/create_overlays.py dissemination_areas das

