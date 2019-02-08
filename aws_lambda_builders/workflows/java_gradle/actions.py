"""
Actions for the Java Gradle Workflow
"""

import os
from aws_lambda_builders.actions import ActionFailedError, BaseAction, Purpose
from .gradle import GradleExecutionError


class JavaGradleBuildAction(BaseAction):
    NAME = "GradleBuild"
    DESCRIPTION = "Building the project using Gradle"
    PURPOSE = Purpose.COMPILE_SOURCE

    INIT_SCRIPT = 'lambda-build-init.gradle'
    SCRATCH_DIR_PROPERTY = 'software.amazon.aws.lambdabuilders.scratch-dir'

    def __init__(self,
                 source_dir,
                 subprocess_gradle,
                 scratch_dir,
                 os_utils):
        self.source_dir = source_dir
        self.scratch_dir = scratch_dir
        self.subprocess_gradle = subprocess_gradle
        self.os_utils = os_utils

    def execute(self):
        init_script_file = self._copy_init_script()
        self._build_project(init_script_file)

    def _copy_init_script(self):
        try:
            src = os.path.join(os.path.dirname(__file__), 'resources', self.INIT_SCRIPT)
            dst = os.path.join(self.scratch_dir, self.INIT_SCRIPT)
            return self.os_utils.copy(src, dst)
        except Exception as ex:
            raise ActionFailedError(str(ex))

    def _build_project(self, init_script_file):
        try:
            self.subprocess_gradle.build(self.source_dir, init_script_file,
                                         {self.SCRATCH_DIR_PROPERTY: self.scratch_dir})
        except GradleExecutionError as ex:
            raise ActionFailedError(str(ex))


class JavaGradleCopyArtifactsAction(BaseAction):
    NAME = "CopyArtifacts"
    DESCRIPTION = "Copying the built artifacts"
    PURPOSE = Purpose.COPY_SOURCE

    def __init__(self,
                 source_dir,
                 artifacts_dir,
                 build_dir,
                 os_utils):
        self.source_dir = source_dir
        self.artifacts_dir = artifacts_dir
        self.build_dir = build_dir
        self.os_utils = os_utils

    def execute(self):
        self._copy_artifacts()

    def _copy_artifacts(self):
        lambda_build_output = os.path.join(self.build_dir, 'build', 'distributions', 'lambda-build')
        try:
            for f in self.os_utils.listdir(lambda_build_output):
                self.os_utils.copy(os.path.join(lambda_build_output, f), self.artifacts_dir)
        except Exception as ex:
            raise ActionFailedError(str(ex))
