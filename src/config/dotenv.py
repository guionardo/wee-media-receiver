import os
import logging


def load_dotenv(filename='.env', source: dict = {}):
    updates = dict()
    if source:
        updates = source
    else:
        if not os.path.isfile(filename):
            return
        with open(filename) as file:
            for line in file:
                line = line.strip()
                if line.startswith('#') or not line or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                updates[key] = value

    if updates:
        os.environ.update(updates)
        logging.getLogger(__name__).debug('Loaded %s -> %s', filename, updates)
