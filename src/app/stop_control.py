import os

import lockfile
from src import __appname__


class StopControl:

    def __init__(self):
        self.control_file = os.path.abspath(f'./{__appname__}.ctrl')
        self.lockfile = lockfile.FileLock(self.control_file)
        self.stop_file = os.path.abspath(f'./{__appname__}.stop')

    def stop(self):
        with open(self.stop_file, 'w') as f:
            f.write('1')
    
    @property
    def stopping(self):
        return os.path.exists(self.stop_file)

    def can_start(self) -> bool:
        try:
            # Skiping            
            # self.lockfile.acquire(2)
            return True
        except lockfile.LockTimeout:
            return False

    def __delete__(self):
        if self.lockfile.is_locked():
            self.lockfile.release()
