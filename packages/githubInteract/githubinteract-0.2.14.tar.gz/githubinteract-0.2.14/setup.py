
from setuptools import setup, find_packages
with open("README.md", "r") as fh: 
    long_description = fh.read() 

setup(
    name='githubInteract',
    version='0.2.14',
    author='Brigham Turner',
    author_email='brighamturner@narratebay.com',
    description='''# GitHub Automation Toolkit
This package provides a Python class `gh` for automating common GitHub and Git tasks using the GitHub API and the Git command-line interface. This is designed to shorten and simplify github commands.

## why this is different and needed:
I created it to simplify using github: many things i wish I could do in github with one command actually require several commands. For example:
- uploading an entire folder (which beforehand wasn't initiated into github) to a repo is one command in this package: `uploadFolderFileAsCommitToRepo(...)`. In normal git this would have been surprisingly complicated: first you would need to initiate the folder, but to initiate the folder you would need to pull from the original github repo, but that would then wipe all the contents of that folder or require a merging procedure.
- in this package you can push with one command: `uploadFolderFileAsCommitToRepo(...)`. Normally using github pushing requires 3 steps: 1) adding, committing, and pushing.
- Ultimately, there is a reason why github is so complex: it is intended to allow multiple users to work on the same project - but when you are just a single user this complexity is burdensome.

## Capabilities:
- **Repository Management**: Create and delete GitHub repositories.
- **Branch Management**: Create, checkout, and delete branches both locally and on GitHub.
- **Commit & Upload**: Upload a local folder to a GitHub repository as a commit, with support for automatic initialization and remote setup.
- **Version Comparison**: Compare differences between two Git commits based on timestamps using Git's internal log and diff mechanisms.''',
    long_description=long_description, 
    long_description_content_type="text/markdown", 
    packages=find_packages(),
    install_requires=["PyGithub","gitpython"], 
    license="MIT",
    classifiers=[
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)