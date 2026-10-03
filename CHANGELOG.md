# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `scripts/lint_skills.py`: a structural lint of every skill (frontmatter, name, description
  length, referenced files, manifests, README coverage), with a self-test, run in CI.
- CodeQL workflow and Dependabot updates for GitHub Actions.

### Changed
- Renamed to Reviewer Skills (`reviewer-skills`): skills that review rather than produce.
- `strategic-advisor` is described by its method; it no longer uses a persona.
- GitHub Actions are pinned to full commit SHAs.
- SECURITY.md links the private reporting form and states the disclosure policy.

### Removed
- `doc-to-audio`, `prompt-coach` and `prompt-insights`, with the prompt-coach hook.
- CITATION.cff.

## [0.1.0] - 2026-09-29

### Added
- Initial public release.
