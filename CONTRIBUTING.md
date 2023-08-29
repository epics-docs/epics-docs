# Documentation contribution guide

## For new contributors

"I'm a newcomer, and I'd like to fix an issue."

### Contacting another developer

If you have found a small error or missing piece of information
and are unable to fix it yourself,
you can email Tech-talk at <tech-talk@aps.anl.gov>.
Provide the details of the issue
and another member of the community should be able to fix it for you.
You can more information about using Tech-talk can be found at <https://epics.anl.gov/tech-talk/>.

### Creating an issue on GitHub

#### Finding the GitHub page and signing up

You can suggest a fix by yourself in the [epics-docs GitHub repository].
If you would like to create a new page or move information between pages,
please refer to the style guide later in this page.
For instances where you wish to edit a page,
follow the GitHub link in the top-right of the page.

Following this link, will take you to the source page.
If you don't already have a GitHub account,
go to the [join GitHub] page and follow the instructions.

  [epics-docs GitHub repository]: https://github.com/epics-docs/epics-docs
  [join GitHub]: https://github.com/join

#### Creating an issue

At the top of the GitHub page,
click on the "Issues" tab.
If there are no issues already listed about the problem that you want fixed,
click the "New issue" button,
give your issue a title and
write a brief description,
then submit it.
If nobody has picked up your issue after several days,
email Tech-talk and
a developer should pick it up.

## Making a contribution

### Structure

This documentation follows the [Diátaxis] documentation framework.
We recommend reading the [Diátaxis] documentation.

What this means for the EPICS documentation,
is that documentation falls into 4 categories:

-   Tutorials: for users to learn new concepts
-   How-to guides: for users to achieve specific, predefined goals
-   References: for users to consult,
    when looking for information
-   Explanations: for users to clarify their understanding of a concept

TODO: explain where users should contribute, when we figure out if we merge every documentation in the same place.

  [Diátaxis]: https://diataxis.fr/

#### Forking the repository

Once logged in and viewing the page on GitHub you wish to edit,
click on the pencil icon to the top-right of the content.
If this is your first time editing,
you will see with a page asking you to fork the repository before being able to edit.
Click through the link to do this,
and GitHub will create a copy of the entire repository linked to your own account.
Feel free to edit any page in this repository,
as your changes won't reflection the main repository or the Read the Docs site until you make a pull request.

### Local setup and build

"How do I build the epics-doc documentation locally,
and how do I serve it locally?"
Being able to do this can be of interest to check how your contribution will render before sharing it.

#### Using poetry

A practical solution to build the epics-docs documentation is to use [Poetry].
Poetry is a tool for dependency management and packaging in Python.
It's reproducible,
no matter what your environment is,
and multi-platform (it works equally well on Linux, macOS and Windows).

Please follow [the Poetry documentation] to install it.

Once installed,
you can setup, build, and serve the epics-docs documentation in two steps:

1.  Clone (with SSH) the epics-docs fork you have made in the [Forking the repository] section and change directory into it:

``` console
$ git clone git@github.com:your-user-name/epics-docs.git
$ cd epics-docs
```

2.  Install Poetry dependencies (the "setup") and build + serve the epics-docs documentation:

``` console
$ poetry install
$ poetry run sphinx-autobuild . ./_build/html
```

At this point,
you can open <http://127.0.0.1:8000> in your internet browser,
and check the generated documentation by yourself.

  [Poetry]: https://python-poetry.org/docs/
  [the Poetry documentation]: https://python-poetry.org/docs/#system-requirements
  [Forking the repository]: #forking-the-repository

#### Using pip

Another solution for local builds is to use [pip]
(ideally in a [virtual environment]),
which comes pre-installed with most modern python installations.
From the pip website:

> pip is the package installer for Python.
> You can use it to install packages from the Python Package Index and other indexes

1. Follow the first step in the [Using poetry] section to locally clone the epics-docs repository.

2. Install the pip dependencies from `requirements-dev.txt`

``` console
$ python -m venv venv                  # Create a virtual environment for your local build
$ . venv/bin/activate                  # Activate it
$ pip install -r requirements-dev.txt
$ sphinx-autobuild . ./_build/html
```

At this point,
as above,
you can open <http://127.0.0.1:8000> in your internet browser,
and check the generated documentation by yourself.

  [pip]: https://pip.pypa.io/en/stable/
  [virtual environment]: https://docs.python.org/3/library/venv.html
  [Using poetry]: #using-poetry

#### Reference setup and build

You can check for yourself how the project is built here: <https://readthedocs.org/projects/epics/builds/>,
and then click on the last "Passed" build (that is, the last build that succeeded),
for example: <https://readthedocs.org/projects/epics/builds/21001074/>.

::: {warning}
Those commands are oriented to optimize the build in the Read the Docs environment.
This might not always be reproducible on your computer without some level of modifications,
depending on your own local environment,
such as your OS, your distribution, your shell interpreter, etc.
This way is the how Read the Docs builds the documentation,
but isn't the most practical way (at least not for development/contribution purposes).
:::

### Edit and view your changes

Now that you know how to clone, setup, build, and serve the epics-docs documentation,
you can edit any `.rst` or `.md` file and check how sphinx will render your contribution.

After running `$ poetry run sphinx-autobuild . ./_build/html`, like described earlier,
any modification will update <http://127.0.0.1:8000> automatically.

### Style guide

This section covers the conventions when writing documentation.

You should write new documentation in Markdown.
Some existing documentation might be in reStructuredText (RST),
but these pages should progressively be converted to Markdown.

If you're unfamiliar with Markdown,
you can look at the [Basic Syntax] page from the [Markdown Guide] website.

Another convention used is [Semantic line breaks][]:
make sure to add line breaks after each sentence,
comma,
and before every relative clause.

A configuration for [Vale] also exists in the repository,
to help you write English documentation.
You are *not* required to fix every Vale warning,
these are meant as advice.

To see those Vale warnings,
install Vale by following the [Vale Installation] guide,
and run `vale path/to/your/file.md`.

  [Basic Syntax]: https://www.markdownguide.org/basic-syntax/
  [Markdown Guide]: https://www.markdownguide.org/
  [Semantic line breaks]: https://sembr.org/
  [Vale]: https://vale.sh/
  [Vale Installation]: https://vale.sh/docs/vale-cli/installation/

### Making a pull request

After you are satisfied with your changes,
commit and push them to your fork,
and submit them for review by creating a pull request.

To Make a pull request,
first click on the "Pull requests" tab at the top of GitHub.
From here, click the green "New pull request" button,
which should take you to a page comparing the main repository to your fork.
You should see any commits you have made listed here.
Clicking "Create pull request" will give you the opportunity to give your edits a title
and a brief description,
before you submit them for review.

At this point,
a maintainer of the repository will be able to review your changes
to ensure they're sensible and don't break anything.
If all is well, they will approve the changes and merge them into the main repo.
After the reviewer has merged the pull request,
Read the Docs will recompile the page and publish your changes.

## Reviewing pull requests

From the point of view of a reviewer.

TODO: how to merge (merge commit (not FF))
TODO: say if pushing to PRs from a reviewer point of view is acceptable
