# deployment-impact-visualization Specification

## Purpose
TBD - created by archiving change add-deployment-impact-figure. Update Purpose after archive.
## Requirements
### Requirement: Workshop Data Structure
The system SHALL provide a structured dataset containing workshop deployment metrics for LabLink.

#### Scenario: Workshop metadata
- **WHEN** deployment impact data is needed for visualization
- **THEN** the system provides a CSV file with columns: `date`, `event_name`, `location`, `participants`, `audience_type`, `notes`
- **AND** the data spans from February 2024 to October 2025
- **AND** the data includes 14 unique workshops/courses with 635 total participants

#### Scenario: Audience type categorization
- **WHEN** categorizing workshop audiences
- **THEN** each event is assigned one of: K-12, K-12 Educators, Undergraduate/Graduate, Graduate/Faculty, Community/Mixed, Graduate/Faculty/RSE
- **AND** categories reflect the primary participant demographics

### Requirement: Timeline Visualization
The system SHALL generate a publication-quality timeline figure showing workshop deployments over time.

#### Scenario: Basic timeline chart
- **WHEN** the plotting script is executed with default settings
- **THEN** a horizontal timeline is created showing workshops from Feb 2024 to Oct 2025
- **AND** each workshop is represented as a bar with height proportional to participant count
- **AND** bars are color-coded by audience type
- **AND** the chart uses colorblind-friendly colors

#### Scenario: Participant count display
- **WHEN** rendering the timeline
- **THEN** each bar displays the number of participants
- **AND** workshop names are labeled clearly
- **AND** major events (>100 participants) are visually highlighted

### Requirement: Summary Statistics
The system SHALL include summary statistics highlighting deployment impact.

#### Scenario: Key metrics display
- **WHEN** generating the figure
- **THEN** the visualization includes total participant count (635)
- **AND** displays total number of events (14)
- **AND** shows audience diversity (K-12 through faculty)
- **AND** optionally includes zero-setup success rate (100%)

#### Scenario: Geographic reach
- **WHEN** summarizing deployment locations
- **THEN** the figure indicates international reach (US, Portugal, Croatia)
- **AND** highlights diverse institutional types (universities, research institutes, K-12 schools)

### Requirement: Format Presets
The system SHALL support multiple output format presets matching existing figure scripts.

#### Scenario: Paper format preset
- **WHEN** the `--format paper` option is specified
- **THEN** the figure uses font size 14
- **AND** the figure size is (8, 5) inches for timeline readability
- **AND** the output DPI is 300
- **AND** the figure is optimized for two-column journal layout

#### Scenario: Poster format preset
- **WHEN** the `--format poster` option is specified
- **THEN** the figure uses font size 20
- **AND** the figure size is (14, 10) inches
- **AND** the output DPI is 300
- **AND** the figure is optimized for conference poster readability

### Requirement: Output Files
The system SHALL generate output files following project naming conventions.

#### Scenario: Multiple output formats
- **WHEN** the plotting script completes successfully
- **THEN** both PNG and PDF versions are generated
- **AND** files are named `deployment_impact.png` and `deployment_impact.pdf`
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
- **AND** it reads data from `data/processed/deployment_impact/workshops.csv`

### Requirement: Visual Style Consistency
The system SHALL maintain visual consistency with other figures in the paper.

#### Scenario: Consistent styling
- **WHEN** generating the timeline visualization
- **THEN** it uses the seaborn "whitegrid" style
- **AND** it uses colorblind-friendly colors from the "colorblind" palette
- **AND** font sizes and weights match the format preset specifications
- **AND** the figure includes a descriptive title

#### Scenario: Color scheme for audience types
- **WHEN** assigning colors to audience categories
- **THEN** colors are selected from seaborn's colorblind palette
- **AND** colors provide sufficient contrast between categories
- **AND** K-12 events are visually distinct from graduate-level events
- **AND** the same color is used consistently for each audience type across regenerations

### Requirement: Temporal Accuracy
The system SHALL accurately represent the timeline of deployments.

#### Scenario: Date ordering
- **WHEN** plotting workshops on the timeline
- **THEN** events are ordered chronologically by date
- **AND** the x-axis spans from February 2024 to October 2025
- **AND** month/year labels are clearly visible

#### Scenario: Time-based grouping
- **WHEN** displaying workshops close in time
- **THEN** bars do not overlap or obscure each other
- **AND** labels remain legible for all events
- **AND** spacing accommodates dense periods (e.g., summer 2025)

