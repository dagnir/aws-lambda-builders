"""
Java Gradle Workflow
"""

from aws_lambda_builders.workflow import BaseWorkflow, Capability
from .actions import JavaGradleBuildAction, JavaGradleCopyArtifactsAction
from .gradle import SubprocessGradle
from .gradle_resolver import GradleResolver
from .utils import OSUtils


class JavaGradleWorkflow(BaseWorkflow):
    """
    A Lambda builder workflow that knows how to build Java projects using Gradle.
    """
    NAME = "JavaGradleWorkflow"

    CAPABILITY = Capability(language="java",
                            dependency_manager="gradle",
                            application_framework=None)

    INIT_FILE = "lambda-build-init.gradle"

    def __init__(self,
                 source_dir,
                 artifacts_dir,
                 scratch_dir,
                 manifest_path,
                 **kwargs):
        super(JavaGradleWorkflow, self).__init__(source_dir,
                                                 artifacts_dir,
                                                 scratch_dir,
                                                 manifest_path,
                                                 **kwargs)

        self.os_utils = OSUtils()
        subprocess_gradle = SubprocessGradle(self.binaries['gradle'], self.os_utils)
        artifact_mapping = self._resolve_artifact_mapping()

        self.actions = [
            JavaGradleBuildAction(source_dir,
                                  subprocess_gradle,
                                  scratch_dir,
                                  self.os_utils),
            JavaGradleCopyArtifactsAction(source_dir,
                                          artifacts_dir,
                                          artifact_mapping,
                                          self.os_utils)
        ]

    def get_resolvers(self):
        return [GradleResolver(self.source_dir, self.os_utils)]

    @property
    def artifact_mapping(self):
        return self._resolve_artifact_mapping()

    def _resolve_artifact_mapping(self):
        """
        Creates the map from the source of a single Lambda function (under source_dir), to the sub-directory under
        artifacts_dir where the function's artifact is to be placed.

        :return: The artifact mapping.
        """
        if not self.options or not self.options.get('artifact_mapping'):
            return {'.': '.'}
        return self.options['artifact_mapping']
