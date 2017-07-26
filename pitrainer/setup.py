from setuptools import setup
from pip.req import parse_requirements
import pip.download

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements("requirements.txt",
        session=pip.download.PipSession())

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.req) for ir in install_reqs]

setup(
  name='PiTrainer',
  version='0.0.1',
  author='Richard Kirby',
  author_email='unknown@nothere.com',
  packages=['pitrainer'],
  license=['LICENSE.txt'],
  description=['Fighting fit using the Raspberry Pi'],
  install_requires=reqs,
  setup_requires=[
      'pytest-runner'
  ],
  tests_require=[
      'pytest',
      'pytest-flake8'
  ],
)
