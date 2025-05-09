# Changelog

All notable changes to this project will be documented in this file.

## [0.7.2] - 2025-05-09

### 🚀 Features

- Add TODOs for future enhancements in plagiarism visualizer
- Refactor PlagiarismMatch to use dataclass and add validation checks
- Add test function to process files and generate visualization
- Update dependencies and add new testing tools
- Set default output filenames based on input file if not provided.
- Implement text cleaning and segmentation for plagiarism detection
- Inline CSS and JS in HTML report generation, removing file copy
- Inline CSS and JS in plagiarism report template, removing external file references
- Add functionality to generate standalone HTML report with inlined CSS and JS
- Add logging for input and reference validation in PlagiarismMatch
- Enhance logging for match positions in text processing
- Add example usage and visualization for plagiarism detection

### 🐛 Bug Fixes

- Enhance sentence extraction by trimming trailing whitespace
- Change active_matches from set to list and prevent duplicates
- Change the way how the sentences are extracted.
- Update import paths in README for visualization modules
- Correct segment boundaries in text processing tests

### 💼 Other

- Update dev dependencies in pyproject.toml

### 🚜 Refactor

- Refactor HTML generation and add new utility functions
- Plagiarism visualizer into modular structure
- HTML generator by removing unused variables
- Move test class to a separate file
- Simplified the conditional logic
- Move output dir creation
- Remove unused output parameter from HTML generation

### 📚 Documentation

- Add comments
- Add comments to clarify sentence splitting in _split_texts_to_sentences
- Polish comments and improve code readability
- Update README with revised usage examples and visualization steps

### 🎨 Styling

- Format

### 🧪 Testing

- Add unit tests for split_text_into_segments function
- Refactor and expand tests for sentence splitting logic.
- Refactor and expand tests for plagiarism visualizer.
- Add tests for CLI input handling and output filename inference
- Remove unused print mock in plagiarism checker test

### ⚙️ Miscellaneous Tasks

- Update changelog for version 0.7.1
- Move the function to the end
- Minor edits
- Remove unnecessary blank line in sentence extraction
- Update version to 0.7.2 and adjust Python dependency range
- Update .gitignore to include output, scripts, and docs directories
- Add SIM117 to ignore list in ruff configuration
- Add pytest configuration file for standardized test setup

## [0.7.1] - 2025-05-07

### 🐛 Bug Fixes

- Improve segment splitting logic in plagiarism visualizer

### ⚙️ Miscellaneous Tasks

- Add changelog
- Bump version to 0.7.1

## [0.7.0] - 2025-05-07

### 🚀 Features

- Add plagiarism visualization
- Add plagiarism visualizer script and markdown dependency

### 🐛 Bug Fixes

- Refine sentence splitting regex to handle exclamation marks.
- Missing imports

### 📚 Documentation

- Update README and add image with visualization

### 🎨 Styling

- Reformat
- Improve comments for clarity in test assertions

### 🧪 Testing

- Edit test texts

### ⚙️ Miscellaneous Tasks

- Bump version to 0.6.0
- Bump version to 0.7.0

## [0.6.0] - 2025-05-07

### 🚀 Features

- Add JSON output with offsets

### 📚 Documentation

- Update README to include text output option and improve argument descriptions

### 🧪 Testing

- Refactor tests to include sentence indices and spans.

### ⚙️ Miscellaneous Tasks

- Update pytest configuration to include pytest-cov and enhance coverage reporting
- Update pytest-cov dependency to version 6.1.1
- Update dependencies for coverage and testing tools

## [0.5.0] - 2025-04-30

### 🚀 Features

- Add similarity metric selection for plagiarism checking

### 🐛 Bug Fixes

- Improve error handling in CLI and update argument parsing

### 📚 Documentation

- Update README to reflect new features and usage instructions

### 🧪 Testing

- Add metrics test

### ⚙️ Miscellaneous Tasks

- Bump version to 0.5.0
- Add GitHub Actions workflow for running Pytest with coverage

## [0.4.1] - 2025-04-30

### 🚀 Features

- Add minimum sentence length filter for plagiarism checking
- Add Makefile for project automation and management

### 💼 Other

- Add poetry.lock
- Update version to 0.4.0
- Update version to 0.4.0
- Update python version requirement to allow >=3.9
- Bump version to 0.4.1

### 🚜 Refactor

- Add type hints to similarity functions for better clarity

### 🎨 Styling

- Reformat
- Reformat

### 🧪 Testing

- Add unit tests

### ⚙️ Miscellaneous Tasks

- Add development dependencies and configuration for isort and black
- Update poetry.lock for dependency version upgrades and new packages
- Ruff.toml for project configuration

## [0.3.0] - 2023-08-29

### 💼 Other

- Enhance project metadata in pyproject.toml file.
- Bump-up version

### 🚜 Refactor

- Rebase

### 📚 Documentation

- Add README badges, fix project URL

<!-- generated by git-cliff -->
