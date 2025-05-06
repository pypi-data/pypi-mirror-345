from setuptools import setup, find_packages

setup(
    name='slack_blockkit_builder',
    version='0.1.0',
    description='Python wrapper for Slack Block Kit JSON construction',
    author='Abhishek Singh',
    author_email='abhisheksinghaz@outlook.com',
    packages=find_packages(),
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License'
    ],
)
