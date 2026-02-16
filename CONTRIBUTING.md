# Contributing to EPICS documentation

Found an issue? You can report it on [GitHub Issues](https://github.com/epics-docs/epics-docs/issues) or email <tech-talk@aps.anl.gov>.

## Documentation framework

This documentation follows the [Diátaxis framework](https://diataxis.fr/),
organizing content into four categories:

- **Tutorials** - for learning new concepts
- **How-to guides** - for achieving specific goals
- **Explanations** - for clarifying understanding
- **References** - for looking up information

Organize pages in this order within each topic.

## Tagging documents

Use [sphinx-tags](https://sphinx-tags.readthedocs.io/) to show the intended audience:

- `beginner` - installation and basic concepts
- `user` - using EPICS with client applications
- `developer` - developing IOCs, extensions, or drivers
- `advanced` - build system, specifications, protocol details

Add tags under the title in your source file:

For `.rst`:

``` 
.. tag::`beginner, user, developer`
```

For `.md`:

    ```{tags} beginner, developer
    ```

## Local development

### Using Poetry (recommended)

Install [Poetry](https://python-poetry.org/docs/#installation), then:

``` console
$ poetry install
$ poetry run sphinx-autobuild --re-ignore _tags/ . ./_build/html
```

Open <http://127.0.0.1:8000> in your browser.
Changes reload automatically.

### Using pip

``` console
$ python -m venv venv
$ . venv/bin/activate
$ pip install -r requirements-dev.txt
$ sphinx-autobuild --re-ignore _tags/ . ./_build/html
```

## Style guide

- Write new documentation in **Markdown** (`.md`)
- Use [semantic line breaks](https://sembr.org/) - break after sentences and clauses
- Run Vale for style checking: `vale path/to/your/file.md` (optional, not required)
- Keep commits focused and separate concerns

## Adding dependencies

When adding a Sphinx extension:

``` bash
poetry add sphinx-foo
```

Then add the pinned version from `pyproject.toml` to both `requirements.txt` and `requirements-dev.txt`:

```
sphinx-foo==1.1.2
```

## For maintainers

- Merge using merge commits (not fast-forward)
- Refrain from pushing to contributors' branches
