"""
Commonly used utilities
"""

import os
import platform
import shutil
import subprocess
from aws_lambda_builders.utils import which


class OSUtils(object):
    """
    Convenience wrapper around common system functions
    """

    def popen(self, command, stdout=None, stderr=None, env=None, cwd=None):
        p = subprocess.Popen(command, stdout=stdout, stderr=stderr, env=env, cwd=cwd)
        return p

    def is_windows(self):
        return platform.system().lower() == 'windows'

    def copy(self, src, dst):
        shutil.copy2(src, dst)
        return dst

    def listdir(self, d):
        return os.listdir(d)

    def scandir(self, d):
        return os.scandir(d)

    def exists(self, p):
        return os.path.exists(p)

    def which(self, executable, executable_search_paths=None):
        return which(executable, executable_search_paths=executable_search_paths)

    def copytree(self, src, dst):
        return shutil.copytree(src, dst)

    def makedirs(self, d):
        return os.makedirs(d, exist_ok=True)

    @property
    def pipe(self):
        return subprocess.PIPE
