# Snailz

<img src="https://raw.githubusercontent.com/gvwilson/snailz/main/pages/img/snail-logo.svg" alt="snail logo" width="200px">

`snailz` is a synthetic data generator
that models a study of snails in the Pacific Northwest
which are growing to unusual size as a result of exposure to pollution.
The package can generate fully-reproducible datasets of varying sizes and with varying statistical properties,
and is intended primarily for classroom use.
For example,
an instructor can give each learner a unique dataset to analyze,
while learners can test their analysis pipelines using datasets they generate themselves.
`snailz` can also be used to teach good software development practices:
it is well structured,
well tested,
and uses modern Python tools.

> *The Story*
>
> Years ago,
> logging companies dumped toxic waste in a remote region of Vancouver Island.
> As the containers leaked and the pollution spread,
> some of the tree snails in the region began growing unusually large.
> Your team is now collecting and analyzing specimens from affected regions
> to determine if a mutant gene makes snails more susceptible to the pollution.
>
> Each genomic assay is performed by putting samples of a snail's tissue
> into some small wells in a plastic [microplate][microplate].
> An inert material is placed in other wells as a control;
> the wells are then treated with chemicals and photographed,
> and the brightness of each well shows how reactive the material was.

`snailz` generates several related sets of data:

Persons
:   The scientists conducting the study.
    Persons are included in the dataset to simulate operator bias,
    i.e.,
    the tendency for different people to perform experiments in slightly different ways.

Machines
:   The equipment used to analyze the samples.
    Like persons, they are included to enable simulation of bias.

Specimens
:   The snails collected from the sites.
    The data records a short fragment of the specimen's genome.
    its mass,
    and when and where it was collected.

Assays
:   The chemical analysis of the snails' genomes.
    Each assay is stored in two files:
    a design file showing which wells contain samples and controls,
    and a readings file with the measured responses.
    The images that the readings are taken from are also stored.

## Usage

1.  `pip install snailz` (or the equivalent command for your Python environment).
1.  `snailz --help` to see available commands.

To generate example data in a fresh directory:

```
# Create and activate Python virtual environment
$ uv venv
$ source .venv/bin/activate

# Install snailz and dependencies
$ uv pip install snailz

# Write default parameter values to the ./params.json file
$ snailz params --defaults > params.json

# Generate all output files in the ./data directory
$ snailz data --params params.json --outdir data
```

## Parameters

`snailz` reads controlling parameters from a JSON file,
and can generate a file with default parameter values as a starting point.
The parameters, their meanings, and their properties are:

| Group             | Name                  | Purpose                                           | Default    |
| ----------------- | --------------------- | ------------------------------------------------- | ---------: |
| overall           | `rng_seed`            | random number generation seed                     | 123456     |
| `lab_params`      | `num_machines`        | number of lab machines used for assays            | 5          |
|                   | `num_persons`         | number of lab staff doing assays                  | 5          |
|                   | `locale`              | locale used for generating staff names            | `et_EE`    |
|                   | `assays_per_specimen` | number of assays done per specimen                | 2          |
| `assays_params`   | `plate_size`          | XY dimensions of assay plates                     | 4          |
|                   | `mean_control`        | mean plate reading for control wells              | 0.0        |
|                   | `mean_normal`         | mean plate reading for normal specimens           | 2.0        |
|                   | `mean_mutant`         | mean plate reading for mutant specimens           | 5.0        |
|                   | `reading_noise`       | noise applied to plate readings                   | 0.5        |
|                   | `image_noise`         | pixel noise applied to plate images               | 3          |
| `specimen_params` | `mass_mean`           | mean specimen mass                                | 10.0       |
|                   | `mass_sd`             | relative standard deviation of masses             | 1.0        |
|                   | `genome_length`       | number of bases in specimen genomes               | 20         |
|                   | `mut_mass_scale`      | scaling factor for mutant specimen masses         | 2.0        |
|                   | `mut_frac`            | fraction of specimens with significant mutation   | 0.2        |
|                   | `mut_prob`            | probability of non-significant mutations per base | 0.0        |
|                   | `start_date`          | start date of specimen sampling                   | 2025-04-01 |
|                   | `end_date`            | end date of specimen sampling                     | 2025-04-30 |
| `survey_params`   | `grid_size`           | XY dimensions of survey grids                     | 15         |
|                   | `num_sites`           | number of survey sites                            | 3          |
|                   | `num_specimens`       | average number of specimens per site              | 10         |

Notes:

1.  The pollution values in survey grids are generated by performing a random walk of the grid,
    adding one to each cell's value each time it is visited.
    The random walk starts when the polluted region reaches the boundary of the survey grid.

1.  All snail genome fragments are the same length,
    and are generated by mutating the bases at a few randomly-chosen locations.
    One of those locations and one of the variant bases is selected at random as significant;
    a snail with that mutant base in that location is a mutant of unusual size.

## Data Dictionary

All of the generated data is stored in CSV files.

### Persons

`persons.csv` contains information about the scientists performing the study.
The file looks like this:

| id     | personal | family   |
| :----- | :------- | :------- |
| P06 | Artur | Aasmäe |
| P07 | Katrin | Kool |
| …   | …      | … |

and its fields are:

| Field | Purpose | Properties |
| ----- | ------- | ---------- |
| `id` | identifier | text, unique, required |
| `personal` | personal name | text, required |
| `family` | family name | text, required |

### Machines

`machines.csv` contains information about the machines used in the study.
The file looks like this:

| id    | name |
| :---- | :--- |
| M01 | Aero Probe |
| M02 | Nano Counter |
| …     | … |


and its fields are:

| Field | Purpose | Properties |
| ----- | ------- | ---------- |
| `id` | identifier | text, unique, required |
| `name` | machine name | text, required |

Note that the systematic variation in readings introduced by different machines
is *not* stored in the generated data.

### Grids

The pollution readings for each survey grid are stored in a file <code>G<em>nn</em>.csv</code> (e.g., `G03.csv`).
These CSV files do *not* have column headers;
instead, each contains a square integer matrix of pollution readings.
A typical file is:

```
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
0,0,0,0,0,0,0,0,0,1,1,0,0,0,0
0,0,0,0,0,0,0,0,1,2,1,0,0,0,0
0,0,0,0,0,0,0,0,2,1,0,0,0,0,0
0,0,0,0,0,0,0,1,2,0,0,0,0,0,0
0,0,0,0,0,0,0,1,2,1,0,0,0,0,0
0,0,0,0,0,0,0,0,1,2,0,0,0,0,0
0,0,0,0,0,0,0,2,2,1,0,0,0,0,0
0,0,0,0,0,0,0,1,3,0,0,0,0,0,0
0,0,0,0,0,0,0,1,3,1,0,0,0,0,0
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
```

### Specimens

`specimens.csv` holds information about individual snails in CSV format (with column headers).
The file looks like this:

| id  | genome               | mass | grid | x | y |sampled |
| :----- | :------------------- | ---: | ---: | -: | -: | ---: |
| S0001 | GCAACCGGACCGCCGTAAGG | 3.82 | G01 | 5 | 2 | 2025-04-22 |
| S0002 | TCATACGGACCGCCGTAAGG | 3.53 | G02 | 3 | 7 | 2025-04-19 |
| … | … | … | … | … | … | … | … | … | … | … |

and its fields are:

| Field | Purpose | Properties |
| ----- | ------- | ---------- |
| `id` | specimen identifier | text, unique, required |
| `genome` | base sequence | text, required |
| `mass` | snail weight in grams | real, required |
| `grid` | sample grid ID | text, required |
| `x` | sample X coordinate | integer, required |
| `y` | sample Y coordinate | integer, required |
| `sampled` | date specimen was taken | date, required |

### Assays

Summary information about all assays is stored in `assay_summary.csv`.
The file looks like this:

| id | specimen | machine | person | row | col | treatment | reading |
| -- | -------- | ------- | ------ | --- | --- | --------- | ------- |
| A0001 | S0001 | M00 | P03 | 1 | A | C | 0.56 |
| A0001 | S0001 | M00 | P03 | 2 | A | C | 1.16 |
| … | … | … | … | … | … | … | … |

and its fields are:

| Field | Purpose | Properties |
| ----- | ------- | ---------- |
| `id` | assay identifier | text, required |
| `specimen` | specimen identifier | text, required |
| `machine` | machine used | text, required |
| `person` | scientist identifier | text, required |
| `row` | assay plate row | integer, required |
| `col` | assay plate column | text, required |
| `treatment` | control "C" or specimen "S" | text, required |
| `reading` | well reading | real, required |

The directory also contains four files for each assay:

1.  a design file <code>A<em>nnnn</em>_treatments.csv</code>
    showing whether specimen samples or control material was placed in each well of the assay plate;

2.  a readings file <code>A<em>nnnn</em>_readings.csv</code>
    with the readings from each well;

3.  a "raw" readings file <code>A<em>nnnn</em>_raw.csv</code>
    with the raw readings from each well;
    and

3.  an image file <code><em>nnnn</em>.png</code> showing the image that the readings were taken from.

Each CSV file contains a multi-line header with metadata followed by
a table of well values with row and column labels.
A typical treatments file is:

```
id,A0001
specimen,S0001
machine,M00
person,P03
,A,B,C,D
1,0.56,2.22,2.17,0.55
2,1.16,2.33,2.18,0.11
3,0.35,2.13,2.82,0.08
4,1.38,1.74,2.2,1.0
```

while a typical readings file is:

```
id,A0001
specimen,S0001
machine,M00
person,P03
,A,B,C,D
1,C,S,S,C
2,C,S,S,C
3,C,S,S,C
4,S,S,S,S
```

The first four rows of each file are:

| Field | Purpose | Properties |
| ----- | ------- | ---------- |
| `id`  | assay identifier | text, required |
| `specimen` | specimen identifier | text, required |
| `machine` | machine identifier | text |
| `person` | scientist identifier | text |

The "raw" files are copies of the readings files with deliberate formatting errors,
and can be used to teach students how to deal with realistic data.

## Colophon

`snailz` was inspired by the [Palmer Penguins][penguins] dataset
and by conversations with [Rohan Alexander][alexander-rohan]
about his book [*Telling Stories with Data*][telling-stories].

The snail logo was created by [sunar.ko][snail-logo].

My thanks to everyone who built the tools this project relies on, including:

-   [`mkdocs`][mkdocs] for documentation.
-   [`pydantic`][pydantic] for storing and validating data (including parameters).
-   [`pytest`][pytest], [`pyfakefs`][pyfakefs], and [`faker`][faker] for testing.
-   [`ruff`][ruff] for checking the code.
-   [`uv`][uv] for managing packages and the virtual environment.

[alexander-rohan]: https://rohanalexander.com/
[faker]: https://faker.readthedocs.io/
[mkdocs]: https://www.mkdocs.org/
[microplate]: https://en.wikipedia.org/wiki/Microplate
[penguins]: https://allisonhorst.github.io/palmerpenguins/
[pydantic]: https://docs.pydantic.dev/
[pyfakefs]: https://pypi.org/project/pyfakefs/
[pytest]: https://docs.pytest.org/
[ruff]: https://docs.astral.sh/ruff/
[snail-logo]: https://www.vecteezy.com/vector-art/7319786-snails-logo-vector-on-white-background
[telling-stories]: https://tellingstorieswithdata.com/
[uv]: https://docs.astral.sh/uv/
