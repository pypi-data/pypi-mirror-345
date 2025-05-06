import contextlib
import logging
import os

import pytest

logging.basicConfig(level=logging.INFO)


with contextlib.suppress(ImportError):
    import ray

    # this is needed for the stateful udf test so that the test stateful udf class
    # is included in the python system class and packaged.
    @pytest.fixture(scope="session", autouse=True)
    def ray_with_test_path() -> None:
        with contextlib.suppress(Exception):
            ray.shutdown()

        test_path = os.path.abspath("src/tests")  # include test modules
        ray.init(
            runtime_env={
                "env_vars": {
                    "PYTHONPATH": f"{test_path}:{os.environ.get('PYTHONPATH', '')}"
                }
            }
        )
        yield
        ray.shutdown()
