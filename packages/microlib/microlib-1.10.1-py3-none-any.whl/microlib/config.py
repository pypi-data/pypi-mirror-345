import os
from dotenv import load_dotenv, find_dotenv

# Automatic loading of an .env file
load_dotenv()
load_dotenv(find_dotenv(usecwd=True), override=True)


def get_config(name: str, default=None):
    return os.environ.get(f'MICROLIB_{name.upper()}', default)
