import subprocess

from unittest import TestCase
from mock import patch

from aws_lambda_builders.binary_path import BinaryPath
from aws_lambda_builders.workflows.java_gradle.gradle import SubprocessGradle, GradleExecutionError
from aws_lambda_builders.workflows.java_gradle.gradlew_resolver import GradlewResolver


class FakePopen:
    def __init__(self, out=b'out', err=b'err', retcode=0):
        self.out = out
        self.err = err
        self.returncode = retcode

    def communicate(self):
        return self.out, self.err

    def wait(self):
        pass


class TestSubprocessGradle(TestCase):

    @patch("aws_lambda_builders.workflows.java_gradle.utils.OSUtils")
    def setUp(self, MockOSUtils):
        self.os_utils = MockOSUtils.return_value
        self.popen = FakePopen()
        self.os_utils.popen.side_effect = [self.popen]

        self.gradlew_path = '/path/to/gradlew'
        self.gradle_binary_path = '/path/to/gradle'
        self.gradlew = BinaryPath(None, None, 'gradlew', binary_path=self.gradlew_path)
        self.gradle_binary = BinaryPath(None, None, 'gradle', binary_path=self.gradle_binary_path)
        self.source_dir = '/foo/bar/baz'
        self.init_script = '/path/to/init'

    def test_no_os_utils_build_init_throws(self):
        with self.assertRaises(ValueError) as err_assert:
            SubprocessGradle(gradlew=self.gradlew, gradle_binary=self.gradle_binary)
        self.assertEquals(err_assert.exception.args[0], 'Must provide OSUtils')

    def test_no_gradle_exec_init_throws(self):
        with self.assertRaises(ValueError) as err_assert:
            SubprocessGradle(None, None)
        self.assertEquals(err_assert.exception.args[0], 'Must provide Gradle BinaryPath')

    def test_build_no_init_script(self):
        gradle = SubprocessGradle(gradlew=self.gradlew, gradle_binary=self.gradle_binary, os_utils=self.os_utils)
        gradle.build(self.source_dir)
        self.os_utils.popen.assert_called_with([self.gradlew_path, 'build'], cwd=self.source_dir,
                                               stderr=subprocess.PIPE,
                                               stdout=subprocess.PIPE)

    def test_gradlew_path_is_dummy_uses_gradle_binary(self):
        dummy_binary = BinaryPath(None, None, 'gradlew', binary_path=GradlewResolver.DUMMY_PATH)
        gradle = SubprocessGradle(gradlew=dummy_binary, gradle_binary=self.gradle_binary, os_utils=self.os_utils)
        gradle.build(self.source_dir)
        self.os_utils.popen.assert_called_with([self.gradle_binary_path, 'build'], cwd=self.source_dir,
                                               stderr=subprocess.PIPE,
                                               stdout=subprocess.PIPE)

    def test_build_with_init_script(self):
        gradle = SubprocessGradle(gradlew=self.gradlew, gradle_binary=self.gradle_binary, os_utils=self.os_utils)
        gradle.build(self.source_dir, init_script_path=self.init_script)
        self.os_utils.popen.assert_called_with([self.gradlew_path, 'build', '--init-script', self.init_script],
                                               cwd=self.source_dir, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    def test_raises_exception_if_retcode_not_0(self):
        self.popen = FakePopen(retcode=1, err=b'Some Error Message')
        self.os_utils.popen.side_effect = [self.popen]
        gradle = SubprocessGradle(gradlew=self.gradlew, gradle_binary=self.gradle_binary, os_utils=self.os_utils)
        with self.assertRaises(GradleExecutionError) as err:
            gradle.build(self.source_dir)
        self.assertEquals(err.exception.args[0], 'Gradle Failed: Some Error Message')

    def test_includes_build_properties_in_command(self):
        gradle = SubprocessGradle(gradlew=self.gradlew, gradle_binary=self.gradle_binary, os_utils=self.os_utils)
        gradle.build(self.source_dir, init_script_path=self.init_script, properties={'foo': 'bar'})
        self.os_utils.popen.assert_called_with(
            [self.gradlew_path, 'build', '-Dfoo=bar', '--init-script', self.init_script],
            cwd=self.source_dir, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
