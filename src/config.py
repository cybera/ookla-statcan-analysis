from pathlib import Path
import dotenv


dotenv_path = dotenv.find_dotenv()
env_values = dotenv.dotenv_values(dotenv_path)

PROJECT_ROOT = Path(__file__).parents[
    1
]  # list entry 1 is 2 paths up (cuz 0 based list indexing)

DATA_DIRECTORY = PROJECT_ROOT / "data"  # default location
if "DATA_DIRECTORY" in env_values:
    DATA_DIRECTORY = Path(env_values["DATA_DIRECTORY"])

OVERLAYS_DIR = DATA_DIRECTORY / "boundary_overlays"
