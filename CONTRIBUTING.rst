.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/nicmostert/annalist.git.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

Annalist could always use more documentation, whether as part of the
official Annalist docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/nicmostert/annalist.git.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `annalist` for local development.

1. Fork the `annalist` repo on GitLab.
2. Clone your fork locally::

    $ git clone https://github.com/nicmostert/annalist.git

3. Install your local copy into a venv. This is how you set up your fork for local development:

Switch to the newly created root directory of the project::

    $ cd annalist/

Create a virtual environment for this project. Ensure that you are using the correct version of python (3.11)::

    $ python -m venv path/to/venv/location/

Activate the virtual environment:

Unix::

    $ source path/to/venv/location/

Windows (Powershell)::

    $ ./path/to/venv/location/Scripts/Activate.ps1

Windows (cmd)::

    $ ./path/to/venv/location/Scripts/activate.bat

Once within the venv, install the package in "editable" (or "develop") mode. The extras also install the dependencies for development (``dev``), documentation (``docs``) and testing (``test``).::

    $ python -m pip install -e ".[dev,docs,test]"

4. Create a branch for local development

In order to track local changes, you must create a branch for local development.
This command creates a local branch, then switches to that branch.::

    $ git checkout -b name-of-you-bugfix-or-feature

Now you can make your changes locally.

    *NOTE: It is good practive to give your branch a name based on the changes you are planning to make. E.g. "adding-parsing-functionality" or "fixing-logging-bug".*

5. When you're done making changes, verify that all tests still pass on your branch::

    $ pytest

Your branch will not be allowed to merge if all tests do not pass. [*NOTE: This is not technically true yet, but it will be once I figure it out.*]

6. When you're done making changes, commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."

This project makes use of various pre-commit hooks. Among other things, this code-base conforms to `black` and `ruff` formatting, and is checked with `ruff` and `bandit`. If your test fails, follow the instructions on how to fix any problems, and then repeat the commit command. In some cases, the pre-commit hooks will automatically fix all problems. In such cases, changes need to be staged with `git add .` again, before committing again. Since the failed commit didn't go through, feel free to use the same commit message as before.

To run all the pre-commit hooks without making a commit (e.g. to check if the auto-fixes solved all the problems), you can run::

    $ pre-commit run --all-files

When all checks pass and your changes are committed successfully, you may push your changes to the remote version of your branch::

    $ git push origin branch-name

7. Submit a pull request through the GitHub website. Provide a detailed description of the changes you have made to ensure that they can be merged efficiently.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.

Releaseing to PyPI
------------------

A reminder for the maintainers on how to deploy.

1. Make sure all your changes are committed (including an entry in HISTORY.rst, documentation, etc.)

2. Then run `bump-my-version` to increment the release tags in the appropriate places. Consider using the `--dry-run` flag to make sure there are no erros::

    $ bump-my-version bump -v --dry-run patch  # Optional, just to test if it runs without errors
    $ bump-my-version bump patch  # For real this time. Possible values: major, minor, patch

3. Install the local development version of the package (make sure you're in the package root directory, where pyproject.toml is). You should see the package install with the correct version number.::

    $ pip install -e ".[dev,docs,test]"

4. Run the tests to see that they still work with this local install::

    $ pytest

5. Push the commit::

    $ git push

6. Push the tags to GitHub. (Note that we don't actually release on GitHub though. We want to keep the releases to PyPI so there's less ambiguity about how to install it.)::

    $ git push --tags

7. Do the release.

    * If using the Makefile (i.e. you have `make` installed and can run `make help` without errors) you can simply run::

        $ make release

    * Otherwise, you would have to do the release manually.

        a. Clean up all the artifact files::

            $ rm -fr build/
            $ rm -fr dist/
            $ rm -fr .eggs/
            $ find . -name '*.egg-info' -exec rm -fr {} +
            $ find . -name '*.egg' -exec rm -fr {} +
            $ find . -name '*.pyc' -exec rm -fr {} +
            $ find . -name '*.pyo' -exec rm -fr {} +
            $ find . -name '*~' -exec rm -fr {} +
            $ find . -name '__pycache__' -exec rm -fr {} +

        b. Build the source and wheel packages::

            $ python -m build
            $ ls -l dist

        c. Use twine to release to PyPI. You'll be asked for authentication. Use the username `__token__`, along with the API key I gave you.::

            $ twine upload dist/*
