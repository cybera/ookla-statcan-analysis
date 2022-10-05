from pathlib import Path
import dotenv



dotenv_path = dotenv.find_dotenv()

PROJECT_ROOT = Path(__file__).parents[1] # list entry 1 is 2 paths up (cuz 0 based list indexing)

DATA_DIRECTORY = PROJECT_ROOT / 'data' #default location
if 'DATA_DIRECTORY' in dotenv.dotenv_values():
    DATA_DIRECTORY = Path(dotenv.dotenv_values(dotenv_path)['DATA_DIRECTORY'])

OVERLAYS_DIR = DATA_DIRECTORY / 'boundary_overlays'


