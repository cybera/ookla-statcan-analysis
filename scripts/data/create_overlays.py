import datasets.overlays

files = [
    ('dissemination_areas', 'das'),
    ('census_subdivisions', 'subdivs'),
    ('population_centres', 'popctrs'),
]


for name, short_name in files:
    datasets.overlays.save_overlay(name, short_name)
    print()
    print()