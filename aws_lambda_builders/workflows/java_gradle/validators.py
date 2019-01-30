"""
Java Runtime Validation
"""

import logging
import re

from aws_lambda_builders.exceptions import MisMatchRuntimeError
from .utils import OSUtils

LOG = logging.getLogger(__name__)


class JavaRuntimeValidator(object):
    SUPPORTED_RUNTIMES = {
        "java",
        "java8"
    }

    def __init__(self, runtime, os_utils=None):
        self.language = "java"
        self.runtime = runtime
        self.os_utils = OSUtils() if not os_utils else os_utils
        self._valid_runtime_path = None

    def has_runtime(self):
        """
        Checks if the runtime is supported.
        :param string runtime: Runtime to check
        :return bool: True, if the runtime is supported.
        """
        return self.runtime in self.SUPPORTED_RUNTIMES

    def validate(self, runtime_path):
        """
        Checks if the language supplied matches the required lambda runtime
        :param string runtime_path: runtime to check eg: /usr/bin/python3.6
        :raises MisMatchRuntimeError: Version mismatch of the language vs the required runtime
        """
        if not self.has_runtime():
            LOG.warning("'%s' runtime is not "
                        "a supported runtime", self.runtime)
            return

        expected_mv = self.runtime[4:]
        runtime_mv = self._get_major_version(runtime_path)

        # just 'java'
        if not expected_mv:
            self._valid_runtime_path = runtime_path
            return self._valid_runtime_path

        if expected_mv == runtime_mv:
            self._valid_runtime_path = runtime_path
            return self._valid_runtime_path
        else:
            raise MisMatchRuntimeError(language=self.language,
                                       required_runtime=self.runtime,
                                       runtime_path=runtime_path)

    def _get_major_version(self, runtime_path):
        vs = self._get_version_string(runtime_path)
        m = re.search('java version "(.*)"', vs)
        version = m.group(1).split('.')
        # For Java 8 or earlier, version strings begin with 1.{Major Version}
        if version[0] == '1':
            return version[1]
        # Starting with Java 9, the major version is first
        return version[0]

    def _get_version_string(self, runtime_path):
        p = self.os_utils.popen([runtime_path, '-version'], stdout=self.os_utils.pipe, stderr=self.os_utils.pipe)
        _, stderr = p.communicate()
        if p.returncode != 0:
            raise MisMatchRuntimeError(language=self.language,
                                       required_runtime=self.runtime,
                                       runtime_path=runtime_path)
        return str(stderr.splitlines()[0])

    @property
    def validated_runtime_path(self):
        return self._valid_runtime_path


class GradleBinaryValidator(object):
    def __init__(self):
        self._valid_runtime_path = None

    def validate(self, binary_path):
        # We just need Gradle to be available on the PATH for now
        self._valid_runtime_path = binary_path
        return self._valid_runtime_path

    @property
    def validated_runtime_path(self):
        return self._valid_runtime_path
