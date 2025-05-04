from setuptools import setup, find_packages

with open('README.md', 'r') as readme:
	desc = readme.read()

setup (
	name='readable_code',
	version='0.2',
	description='Making totally readable code',
	packages=find_packages(),
	install_requires=[],
	long_description=desc,
	long_description_content_type='text/markdown',
)