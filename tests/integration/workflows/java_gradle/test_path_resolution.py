import os
from unittest import TestCase

from aws_lambda_builders.path_resolver import PathResolver

class TestPathResolution(TestCase):

    def setUp(self):
        self.search_path = os.path.join(os.path.dirname(__file__), "testdata", "single-build", "with-deps-gradlew")


    def test_gradlew_resolution(self):
        r = PathResolver(binary='gradlew', runtime=None, executable_search_paths=[self.search_path])
        self.assertEqual(len(r.exec_paths), 1)
