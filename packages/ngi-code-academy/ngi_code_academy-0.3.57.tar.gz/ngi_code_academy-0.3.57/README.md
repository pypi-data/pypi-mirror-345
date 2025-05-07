# NGI Code Academy

An example package for the NGI Course "How to collaborate on a software project".

Use at your own risk, made by developers in training!

If you are following the exam, see more information in [EXAM.md](./EXAM.md)

# Contributing

## Dependencies

- Python 3.13.2 (optionally use `pyenv`)
- Poetry

## Set up environment

Create a virtual environment an install the dependencies into it locally using

`poetry install`

Ensure you activate the virtual environment.

## Local code quality checks

Check linting rules: `ruff check .`
Check formatting: `ruff format --check`

## Run tests

```
pytest .
```

## (Optional) Pre commit hooks

Install pre commit hooks to automatically run linting, formatting checks and poetry checks before committing.

```
poetry run pre-commit install
```
