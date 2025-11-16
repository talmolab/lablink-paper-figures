# os-distribution-analysis Specification

## Purpose
TBD - created by archiving change add-os-distribution-figure. Update Purpose after archive.
## Requirements
### Requirement: OS Distribution Data Structure
The system SHALL provide a simple data structure containing operating system distribution percentages for LabLink users.

#### Scenario: Static OS percentages
- **WHEN** OS distribution data is needed for visualization
- **THEN** the system provides a CSV file with columns: `os_name`, `percentage`
- **AND** the data contains: Windows 67%, Linux 19%, Mac 14%

### Requirement: Pie Chart Visualization
The system SHALL generate a publication-quality pie chart showing OS distribution percentages.

#### Scenario: Basic pie chart generation
- **WHEN** the plotting script is executed with default settings
- **THEN** a pie chart is created with three segments (Windows, Linux, Mac)
- **AND** each segment is labeled with OS name and percentage
- **AND** the chart uses colorblind-friendly colors
- **AND** the chart matches the visual style of other figures in the paper

#### Scenario: Percentage display
- **WHEN** rendering the pie chart
- **THEN** each segment displays both the OS name and its percentage
- **AND** percentages are formatted with one decimal place (e.g., "67.0%")
- **AND** labels are positioned clearly outside the pie with connection lines

### Requirement: Format Presets
The system SHALL support multiple output format presets matching existing figure scripts.

#### Scenario: Paper format preset
- **WHEN** the `--format paper` option is specified
- **THEN** the figure uses font size 14
- **AND** the figure size is (6.5, 5) inches
- **AND** the output DPI is 300
- **AND** the figure is optimized for two-column journal layout

#### Scenario: Poster format preset
- **WHEN** the `--format poster` option is specified
- **THEN** the figure uses font size 20
- **AND** the figure size is (12, 9) inches
- **AND** the output DPI is 300
- **AND** the figure is optimized for conference poster readability

### Requirement: Output Files
The system SHALL generate output files following project naming conventions.

#### Scenario: Multiple output formats
- **WHEN** the plotting script completes successfully
- **THEN** both PNG and PDF versions are generated
- **AND** files are named `os_distribution.png` and `os_distribution.pdf`
- **AND** files are saved to the specified output directory (default: `figures/main/`)

### Requirement: Command-Line Interface
The system SHALL provide a command-line interface consistent with other plotting scripts.

#### Scenario: Standard CLI options
- **WHEN** the script is invoked from the command line
- **THEN** it supports `--format` option with choices: paper, poster
- **AND** it supports `--output-dir` option to specify output location
- **AND** it supports `--verbose` flag for detailed logging
- **AND** it provides `--help` documentation

#### Scenario: Default behavior
- **WHEN** the script is run without arguments
- **THEN** it uses the paper format preset
- **AND** it outputs to `figures/main/` directory
- **AND** it reads data from `data/processed/os_distribution/os_stats.csv`

### Requirement: Visual Style Consistency
The system SHALL maintain visual consistency with other figures in the paper.

#### Scenario: Consistent styling
- **WHEN** generating the pie chart
- **THEN** it uses the seaborn "whitegrid" style (or appropriate style for pie charts)
- **AND** it uses colorblind-friendly colors from the "colorblind" palette
- **AND** font sizes and weights match the format preset specifications
- **AND** the figure includes a descriptive title

#### Scenario: Color scheme
- **WHEN** assigning colors to OS segments
- **THEN** colors are selected from seaborn's colorblind palette
- **AND** colors provide sufficient contrast between segments
- **AND** the same color is used consistently for each OS across regenerations

