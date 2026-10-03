# Security Policy

## Reporting a vulnerability

Please **do not** open a public issue for security problems.

Use GitHub's private vulnerability reporting on this repository:
**Security → Report a vulnerability** (<https://github.com/decano5107-boop/reviewer-skills/security/advisories/new>). It creates a private thread visible only to the maintainer.

You can expect an acknowledgement within 7 days and a status update within 30 days.

Disclosure is coordinated: once a fix is released, the advisory is published with credit to the
reporter, unless they prefer to stay anonymous.

## Scope

This project runs locally as developer tooling. The most relevant risks are:

- Prompt or template content that causes an agent to take an unintended action
- Configuration examples that could lead a user to commit a credential
- Dependencies with known vulnerabilities

## Supported versions

The latest released minor version receives fixes. Older versions do not.
