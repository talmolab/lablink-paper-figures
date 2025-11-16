# Spec: GPU Cost Visualization

## ADDED Requirements

### Requirement: Load GPU cost data from Epoch AI dataset
System SHALL load GPU pricing and performance data from the Epoch AI Machine Learning Hardware Database CSV file.

#### Scenario: Load valid dataset
```gherkin
Given the Epoch AI ML Hardware CSV exists at data/raw/gpu_prices/ml_hardware.csv
When the system loads the dataset
Then it SHALL parse all rows successfully
And it SHALL extract name, release_date, price, fp32_tflops fields
And it SHALL validate release_date is between 2006-2025
And it SHALL validate price > 0 for GPUs with pricing data
```

#### Scenario: Handle missing dataset
```gherkin
Given the Epoch AI dataset does NOT exist
When the system attempts to load data
Then it SHALL raise FileNotFoundError
And the error message SHALL include download instructions
And the error message SHALL include the Epoch AI URL
```

#### Scenario: Handle malformed dataset
```gherkin
Given a CSV file with missing required columns
When the system attempts to load data
Then it SHALL raise ValueError
And the error SHALL specify which columns are missing
```

---

### Requirement: Filter GPUs to ML-relevant hardware
System SHALL filter dataset to include only GPUs suitable for machine learning and scientific computing workloads.

#### Scenario: Include professional datacenter GPUs
```gherkin
Given a GPU with name containing "Tesla", "A100", "H100", "V100", or "P100"
When applying ML-relevance filter
Then the GPU SHALL be included in the filtered dataset
```

#### Scenario: Include consumer GPUs with sufficient performance
```gherkin
Given a consumer GPU (RTX/GTX series)
And the GPU has fp32_tflops >= 5.0
When applying ML-relevance filter
Then the GPU SHALL be included in the filtered dataset
```

#### Scenario: Exclude mobile and embedded GPUs
```gherkin
Given a GPU with name containing "mobile", "laptop", or "max-q"
When applying ML-relevance filter
Then the GPU SHALL be excluded from the filtered dataset
```

#### Scenario: Exclude low-performance consumer GPUs
```gherkin
Given a consumer GPU with fp32_tflops < 5.0
When applying ML-relevance filter
Then the GPU SHALL be excluded from the filtered dataset
```

---

### Requirement: Generate GPU price trends figure
System SHALL create a time-series visualization showing GPU launch prices from 2006-2025.

#### Scenario: Generate paper preset figure
```gherkin
Given filtered GPU dataset
And preset="paper"
When generating price trends figure
Then the figure SHALL have size 6.5" x 5"
And font size SHALL be 14pt
And DPI SHALL be 300
And the figure SHALL be saved as PNG and PDF
```

#### Scenario: Generate poster preset figure
```gherkin
Given filtered GPU dataset
And preset="poster"
When generating price trends figure
Then the figure SHALL have size 12" x 9"
And font size SHALL be 20pt
And DPI SHALL be 300
And line width SHALL be 3.0pt
And marker size SHALL be 10pt
```

#### Scenario: Plot professional vs consumer GPU prices
```gherkin
Given filtered GPU dataset with professional and consumer categories
When generating price trends figure
Then professional GPUs SHALL be plotted with solid line
And consumer GPUs SHALL be plotted with dashed line
And professional series SHALL use dark blue color
And consumer series SHALL use light blue color
And both series SHALL be labeled in legend
```

#### Scenario: Annotate key GPU releases
```gherkin
Given price trends figure
When rendering annotations
Then V100 (2017) SHALL be annotated
And RTX 2080 Ti (2018) SHALL be annotated
And A100 (2020) SHALL be annotated
And H100 (2022) SHALL be annotated
And annotations SHALL not overlap
```

---

### Requirement: Generate price-performance evolution figure (optional)
System SHALL optionally create a scatter plot showing FLOP/s per dollar improvements over time.

#### Scenario: Generate price-performance subplot
```gherkin
Given filtered GPU dataset
And --include-performance flag is set
When generating figure
Then a second subplot SHALL be created
And Y-axis SHALL use logarithmic scale
And X-axis SHALL show years 2006-2025
And each GPU SHALL be plotted as a point
And an exponential trend line SHALL be fitted
```

#### Scenario: Calculate FLOP/s per dollar
```gherkin
Given a GPU with fp32_tflops and price
When calculating price-performance
Then metric SHALL equal fp32_tflops / price
And result SHALL be in GFLOP/s per USD
```

---

### Requirement: Generate metadata documentation
System SHALL create a metadata text file documenting the GPU cost analysis.

#### Scenario: Generate complete metadata
```gherkin
Given generated GPU cost figure
When creating metadata file
Then file SHALL be named gpu_cost_trends-metadata.txt
And SHALL include data source (Epoch AI with URL)
And SHALL include citation in APA format
And SHALL include generation timestamp
And SHALL include total GPUs analyzed
And SHALL include date range (min year to max year)
And SHALL include price statistics (min, max, median)
And SHALL include separate stats for professional vs consumer
```

#### Scenario: Report filtering statistics
```gherkin
Given filtered dataset
When generating metadata
Then SHALL report total GPUs in raw dataset
And SHALL report GPUs after ML-relevance filter
And SHALL report number of professional GPUs
And SHALL report number of consumer GPUs
And SHALL report GPUs excluded due to missing prices
```

---

### Requirement: Support multiple output formats
System SHALL generate figures in PNG and PDF formats matching repository conventions.

#### Scenario: Generate PNG output
```gherkin
Given preset configuration
And format="png"
When generating figure
Then output SHALL be saved with .png extension
And DPI SHALL match preset configuration
And file size SHALL be < 5MB
```

#### Scenario: Generate PDF output
```gherkin
Given preset configuration
And format="pdf"
When generating figure
Then output SHALL be saved with .pdf extension
And SHALL be vector format
And file size SHALL be < 2MB
```

#### Scenario: Generate both formats
```gherkin
Given no explicit format specified
When generating figure
Then both PNG and PDF SHALL be created
And both SHALL use identical preset configuration
And both SHALL have matching base filename
```

---

### Requirement: Follow established repository visualization patterns
System SHALL match styling conventions from existing figures (software complexity, SLEAP dependency graph).

#### Scenario: Apply consistent color scheme
```gherkin
Given any GPU cost figure
When applying colors
Then SHALL use colorblind-friendly palette
And SHALL use seaborn style "whitegrid"
And SHALL use consistent blue tones matching other figures
```

#### Scenario: Use preset configuration system
```gherkin
Given FORMAT_PRESETS dictionary
When user specifies --preset paper
Then ALL style parameters SHALL come from paper preset
And no hardcoded sizes SHALL override preset
And preset SHALL match software_complexity.py structure
```

#### Scenario: Generate with consistent file naming
```gherkin
Given output directory figures/main/
When generating figures
Then files SHALL follow pattern: gpu_cost_trends{_suffix}.{ext}
And metadata SHALL be gpu_cost_trends-metadata.txt
And naming SHALL match sleap-dependency-graph pattern
```

---

### Requirement: Provide clear data download instructions
System SHALL include documentation for obtaining the Epoch AI dataset.

#### Scenario: README in data directory
```gherkin
Given data/raw/gpu_prices/ directory
When system is distributed
Then README.md SHALL exist in that directory
And SHALL include Epoch AI download URL
And SHALL include step-by-step download instructions
And SHALL include citation requirements (CC BY)
And SHALL specify expected filename (ml_hardware.csv)
```

#### Scenario: Error messages guide user
```gherkin
Given missing dataset
When user runs plot_gpu_cost_trends.py
Then error message SHALL be helpful
And SHALL point to data/raw/gpu_prices/README.md
And SHALL include direct URL to dataset
```

---

### Requirement: Validate data quality
System SHALL verify dataset meets minimum quality standards before visualization.

#### Scenario: Check minimum GPU count
```gherkin
Given filtered dataset
When validating data quality
Then SHALL verify at least 50 GPUs remain after filtering
And if fewer, SHALL raise ValueError
And error SHALL indicate insufficient data
```

#### Scenario: Verify date range coverage
```gherkin
Given filtered dataset
When validating data quality
Then SHALL verify earliest year <= 2010
And SHALL verify latest year >= 2023
And if gaps > 5 years exist, SHALL log warning
```

#### Scenario: Check price data completeness
```gherkin
Given filtered dataset
When validating data quality
Then SHALL calculate percentage of GPUs with pricing
And if < 70% have prices, SHALL log warning
And SHALL report completeness in metadata
```

---

### Requirement: Support command-line configuration
System SHALL accept CLI arguments matching repository patterns.

#### Scenario: Specify preset via CLI
```gherkin
Given command: plot_gpu_cost_trends.py --preset poster
When parsing arguments
Then preset SHALL be set to "poster"
And all rendering SHALL use poster configuration
```

#### Scenario: Specify output path
```gherkin
Given command: --output figures/custom/gpu_analysis.png
When generating figure
Then SHALL save to specified path
And SHALL create directory if needed
And metadata SHALL be in same directory
```

#### Scenario: Enable price-performance subplot
```gherkin
Given command: --include-performance
When generating figures
Then SHALL create both price trends and performance plots
And both SHALL be in same output file (subplots)
```

#### Scenario: Specify data path
```gherkin
Given command: --data /custom/path/ml_hardware.csv
When loading dataset
Then SHALL load from specified path
And SHALL validate same schema
```
