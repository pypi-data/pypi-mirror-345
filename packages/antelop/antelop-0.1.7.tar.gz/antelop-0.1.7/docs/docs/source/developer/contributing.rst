
Contributing
============

Reporting Issues
----------------

If you run into an issue or have an idea for a new feature, please open an issue on our GitHub. When submitting an issue, include the following:

- A clear and descriptive title.
- A summary of the issue or feature request.
- Steps to reproduce (for bugs).
- Expected behavior.
- Any relevant logs or screenshots.

Thank you for helping improve the project! We appreciate all contributions.

Development Environment
-----------------------

We use `uv <https://docs.astral.sh/uv/>`_ to manage dependencies for development and require contributors to do the same.

All forks of the project will contain a `uv.lock` lockfile that will create your virtual environment on the fly. All commands must be run with `uv run`, for example::

   uv run antelop --debug

Code Style
----------

Antelop is written in `ruff <https://docs.astral.sh/ruff/formatter/>`_ codestyle, which is essentially black codestyle. Before committing any changes, please run `uvx ruff` in your local repository.

Debug mode
----------

To assist with debugging, we provide a `--debug` flag when running the GUI which returns more errors and sets the logging level lower.


Documentation
-------------

If you’re adding a new feature, don’t forget to update the documentation. We use reStructuredText (reST) for documentation along with `Read the Docs <https://readsthedocs.com/>` and Sphinx. This can be found under the `/docs` folder in the repository. At present, docs have to be built manually with each update on our Read the Docs account, but we may add a GitHub action for this in the future.

Unit Tests
----------

Due to Antelop's complexity, we currently have no automated unit tests. This is tricky to do properly for graphical software, for distributed cluster pipelines, etc. We instead have a few manual requirements developers must run before merging into main:

* If you are making changes to any user interface, such as the GUI, you must run succesfully in full the entire pipeline of inserting, processing, visualising and exporting data relelvant to the section of the interface you are modifying on sample data from the lab before merging.
* If you are modifying a cluster pipeline, you must run that pipeline succesfully to completion on sample data from the lab before merging.
* If you are modifying any analysis scripts, you must verify that it runs correctly on sample data from the lab before merging.
* For other types of changes, we leave it to your best discretion how to run tests.
* **However,** any major changes to Antelop's infrastructure, such as how it connects to the database or cluster, or how it imports analysis scripts, must be reviewed by the lead author prior to merging.

Contributing Changes
--------------------

Tripodi Lab Contributors
^^^^^^^^^^^^^^^^^^^^^^^^

Software developers in the Tripodi Lab have permission to directly push their changes to their working branch in the repository. We do strongly recommend using feature branches for this purpose. We leave it up to the developer as to when to merge their feature branch into main.

External Contributors
^^^^^^^^^^^^^^^^^^^^^

We welcome and appreciate bug fixes and new features added by external contributors. To do so, please submit a pull request from your own branch as follows:

Start by forking the repository to your own GitHub account. This gives you your own copy to work with.


Once you’ve forked the repo, clone it to your local machine::

    git clone https://github.com/your-username/project-name.git

It’s always a good idea to create a new branch for your work. Don’t mess with the main branch, it’s there for a reason. Create a new branch like so::

    git checkout -b feature-branch-name


Please use clear and concise commit messages. We like to use `gitmoji <https://gitmoji.dev/>`_.

Once you’ve made your changes, commit them and push your branch to your fork::

    git push origin feature-branch-name

Head over to GitHub and create a pull request (PR) from your fork’s branch to the main repository’s `main` branch. Be sure to:

- Provide a clear description of what your PR does.
- Mention any relevant issue numbers (e.g., `Closes #42`).

Once your pull request is submitted, project maintainers will review your code. Be open to feedback and ready to make changes as necessary. Once everything looks good, your PR will be merged into the main repo!
