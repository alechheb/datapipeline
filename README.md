# datapipeline

# FeedBack

1. [Part 1: Python](feedback/feedback.md)
1. [Part 2: SQL](feedback/ventes.md)

## Prerequisites

Create a new virtual environment using conda:
````bash
conda create -n datapipeline python=3.8
````

## Setup
To use this project, you need to clone this repo and run `make setup`:

```bash
git clone https://github.com/alechheb/datapipeline.git
cd datapipeline
make setup
```
The `make setup` command will:
1. Install the requirements in the virtual env created above.
2. Install pre-commit hooks to maintain code standard (code format, Prevent commit into protected branches....)

## Good to know
A set of commands exists to facilitate the developer experience:
* make format: Check Code format using `Black`
* make test: Run unit tests using `pytest`
  Please run `make help` for more information.

## Usage

To run the project, you need to `cd` into the root of the project and run:
```bash
python -m datapipeline
```
The json file will be generated in the fixtures directory under `graph_link` name

## Unit Test

To run unit tests:
```bash
make test
```
