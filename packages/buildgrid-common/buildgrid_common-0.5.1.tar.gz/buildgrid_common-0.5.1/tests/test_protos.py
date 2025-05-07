from buildgrid.common.protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Digest

"""
A dummy test file as a placeholder just to ensure test tooling works
Please remove this file once the package has any testable code
"""


def test_dummy() -> None:
    # Protos can be imported and used
    digest = Digest(hash="abc", size_bytes=123)
    assert digest.hash == "abc"
    assert digest.size_bytes == 123
