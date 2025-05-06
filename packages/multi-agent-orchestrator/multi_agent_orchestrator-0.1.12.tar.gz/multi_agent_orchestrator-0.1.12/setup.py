from setuptools import setup
from setuptools.command.install import install
import sys

class CustomInstallCommand(install):
    def run(self):
        print("\033[93m" + """
╔════════════════════════ IMPORTANT NOTICE ════════════════════════╗
║                                                                  ║
║  This package has been renamed to 'agent-squad'                  ║
║  Please use 'pip install agent-squad' instead                    ║
║                                                                  ║
║  See: https://pypi.org/project/agent-squad                       ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""" + "\033[0m")
        install.run(self)

setup(
    name="multi-agent-orchestrator",
    version="0.1.12",
    cmdclass={
        'install': CustomInstallCommand,
    },
)
