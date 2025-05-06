from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info

def show_message():
    print("\033[93m" + """
╔════════════════════════ IMPORTANT NOTICE ════════════════════════╗
║                                                                  ║
║  This package has been renamed to 'agent-squad'                  ║
║  Please use 'pip install agent-squad' instead                    ║
║                                                                  ║
║  See: https://pypi.org/project/agent-squad                      ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""" + "\033[0m")

class CustomInstallCommand(install):
    def run(self):
        show_message()
        install.run(self)

class CustomDevelopCommand(develop):
    def run(self):
        show_message()
        develop.run(self)

class CustomEggInfoCommand(egg_info):
    def run(self):
        show_message()
        egg_info.run(self)

setup(
    cmdclass={
        'install': CustomInstallCommand,
        'develop': CustomDevelopCommand,
        'egg_info': CustomEggInfoCommand,
    },
)
