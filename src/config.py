from pathlib import Path
import dotenv



DATA_DIRECTORY = Path(dotenv.dotenv_values()['DATA_DIRECTORY'])
OVERLAYS_DIR = DATA_DIRECTORY / 'boundary_overlays'

GRAPH_DIRECTORY = Path(dotenv.dotenv_values()['GRAPH_DIRECTORY'])

