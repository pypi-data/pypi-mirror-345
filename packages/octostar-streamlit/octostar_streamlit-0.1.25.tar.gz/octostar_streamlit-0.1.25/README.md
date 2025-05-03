## Local setup
 - This package uses poetry for dependency management, `brew install poetry` if not already present.

 - Install dependencies in a virtual python env:
```sh
python -m venv venv
poetry install
```

 - To run and debug the example APP alongside the local SDK, use `[Debug] Streamlit start` in VSCode debug menu and create a remote page for URL `http://localhost:8501/` in Octostar with all permissions selected.

## Links

Poetry publishing process:

- [Publishing](https://python-poetry.org/docs/libraries/);
- [Credentials](https://python-poetry.org/docs/repositories/#configuring-credentials);

Github actions:

- [Reference action for Poetry publishing](https://github.com/code-specialist/pypi-poetry-publish/blob/main/action.yaml);
