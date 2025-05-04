from setuptools import setup
from setuptools.command.build_py import build_py
import subprocess
import platform
from pathlib import Path

ext = {"Linux": ".so", "Darwin": ".dylib", "Windows": ".dll"}.get(
    platform.system(), ".so"
)
root_dir = Path(__file__).parent


class CustomBuildPy(build_py):
    def run(self) -> None:
        subprocess.check_call(["make"], cwd=root_dir)
        super().run()


setup(
    cmdclass={"build_py": CustomBuildPy},
    package_data={"pygnuregex": ["stub" + ext]},
    exclude_package_data={"pygnuregex": ["stub.c"]},
)
