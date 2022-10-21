###
set -euxo pipefail


echo 'I tried my besst. I hope this downloads all the things and processes them into data files.'
echo 'Requires an environment where "python" is the python3 command with installed libs'
echo 'And aws s3 must be installed'
echo ''

export PYTHONPATH="${PYTHONPATH-.}:./src"

##
SECONDS=0
echo "Downloading Ookla data from AWS"
now=$(date)
echo "S3 Download start at  ${now}"
aws s3 sync --no-sign-request --no-progress --region=us-west-2 s3://ookla-open-data/shapefiles ./data/ookla-raw 
now=$(date)
dl_duration=$SECONDS
echo "S3 Download completed at  ${now}"
duration=dl_duration
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."
echo ''
echo ''


##
SECONDS=0
now=$(date)
echo "Filtering to Canada starting at at  ${now}"
echo "Filtering global Ookla tiles to Canada only"
python scripts/data/process_raw_ookla_faster.py
now=$(date)
echo "Filtering to Canda ended at at ${now}"
filter_duration=$SECONDS
duration=filter_duration
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."
echo ''
echo ''


##
SECONDS=0
echo "Generating complex geometry overlays"
python scripts/data/create_overlays.py population_centres pops
# python scripts/data/create_overlays.py dissemination_areas das
overlay_duration=$SECONDS
duration=overlay_duration
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."
echo ''
echo ''


now=$(date)
echo "All completed at ${now}"

duration=$(($dl_duration+$filter_duration+$overlay_duration))
echo "S3 download time  $(($dl_duration / 60)) minutes and $(($dl_duration % 60))"
echo "Spatial join time $(($filter_duration / 60)) minutes and $(($filter_duration % 60))"
echo "Overlay time      $(($overlay_duration / 60)) minutes and $(($overlay_duration % 60))"
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."