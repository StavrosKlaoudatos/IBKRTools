Contributing to IBKRTools
========================

Thank you for your interest in contributing to IBKRTools! We welcome all contributions, including bug reports, bug fixes, documentation improvements, and feature requests.

Ways to Contribute
------------------

- Report bugs
- Fix bugs
- Add new features
- Improve documentation
- Write tests
- Share ideas

Development Setup
----------------

1. Fork the repository on GitHub
2. Clone your fork locally:

   .. code-block:: bash

       git clone https://github.com/your-username/IBKRTools.git
       cd IBKRTools

3. Install the package in development mode:

   .. code-block:: bash

       pip install -e .
       pip install -r requirements-dev.txt

4. Create a branch for your changes:

   .. code-block:: bash

       git checkout -b your-feature-branch

5. Make your changes and ensure tests pass:

   .. code-block:: bash

       pytest

6. Commit your changes with a descriptive commit message:

   .. code-block:: bash

       git commit -m "Your detailed description of changes"

7. Push your branch to GitHub:

   .. code-block:: bash

       git push origin your-feature-branch

8. Open a pull request on GitHub

Coding Standards
----------------

- Follow `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_ style guide
- Use type hints for all function signatures
- Write docstrings following the Google style guide
- Keep lines under 88 characters (Black's default)
- Write tests for new functionality

Testing
-------

Run the test suite with:

.. code-block:: bash

    pytest

Write tests for new functionality and ensure all tests pass before submitting a pull request.

Documentation
-------------

Documentation is built using Sphinx. To build the documentation locally:

.. code-block:: bash

    cd docs
    make html

Open `_build/html/index.html` in your browser to view the documentation.

Code of Conduct
---------------

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms.

Bug Reports
-----------

When reporting a bug, please include:

- Your operating system name and version
- Any details about your local setup that might be helpful
- Detailed steps to reproduce the bug
- The expected behavior
- The actual behavior
- Any error messages or tracebacks

Feature Requests
----------------

We welcome feature requests! Please open an issue to discuss your idea before implementing it.

Pull Request Process
--------------------

1. Ensure any install or build dependencies are removed before the end of the layer when doing a build.
2. Update the README.md with details of changes to the interface, including new environment variables, exposed ports, useful file locations, and container parameters.
3. Increase the version numbers in any examples and the README.md to the new version that this Pull Request would represent. The versioning scheme we use is `SemVer <https://semver.org/>`_.
4. The PR must include tests that verify the changes work as expected.
5. The PR must pass all CI checks.
6. The PR should be reviewed by at least one maintainer before being merged.

Thank you for contributing to IBKRTools!
