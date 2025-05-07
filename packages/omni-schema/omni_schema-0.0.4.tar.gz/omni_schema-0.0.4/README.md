# omni-schema

Data model for omnibenchmark.

## Website

[https://omnibenchmark.github.io/omni-schema](https://omnibenchmark.github.io/omni-schema)

## Repository Structure

* [examples/](examples/) - example data
* [project/](project/) - project files (do not edit these)
* [src/](src/) - source files (edit these)
  * [omni_schema](src/omni_schema)
    * [schema](src/omni_schema/schema) -- LinkML schema
      (edit this)
    * [datamodel](src/omni_schema/datamodel) -- generated
      Python datamodel
* [tests/](tests/) - Python tests

## Developer Documentation

<details>

Edit the following files to add fields to the schema:
main file:

* [src/omni_schema/schema/omni_schema.yaml](src/omni_schema/schema/omni_schema.yaml)

test files:

* [src/data/examples/data.py](src/data/examples/data.py)
* [src/data/examples/Benchmark_001.yaml](src/data/examples/Benchmark_001.yaml)
* [examples/Benchmark_001.yaml](examples/Benchmark_001.yaml)

Use the `make` command to generate project artefacts:

* `make all`: make everything
* `make deploy`: deploys site
</details>

## Credits

This project was made with
[linkml-project-cookiecutter](https://github.com/linkml/linkml-project-cookiecutter).
