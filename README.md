# DevOps Digital Twin

Turns DevOps system data into a single graph database using neo4j.

## Components

- Commits of a main branch (from which releases are built)
- All releases

## Quickstart

- Copy config.json.example to config.json and add your PAT from GitHub so rate limiting of GitHub API is less strict.
  The PAT can be added from [here](https://github.com/settings/tokens), and should only be given access to repositories
  you plan on using as a twin data source.  