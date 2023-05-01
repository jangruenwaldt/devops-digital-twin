# DevOps Digital Twin

[![Python integration test](https://github.com/jangruenwaldt/devops-digital-twin/actions/workflows/ci.yaml/badge.svg)](https://github.com/jangruenwaldt/devops-digital-twin/actions/workflows/ci.yaml)
[![Create/update DevOps digital twin](https://github.com/jangruenwaldt/devops-digital-twin/actions/workflows/create_twin.yaml/badge.svg)](https://github.com/jangruenwaldt/devops-digital-twin/actions/workflows/create_twin.yaml)

Fetch DevOps system data into JSON, and then store it in neo4j. Exploration and interface on top of neo4j is planned.

## Structure

- Step 1: download the required data into JSON. If the data source is GitHub, use GitHubDataAdapter.
- Step 2: Construct the twin - either provide individual JSON file URLs, or call TwinBuilder.from_github(), which
  assumes the filenames used by GitHubDataAdapter. To do this, the twin data should be its own repository hosted on
  GitHub.

## Currently supported

- Importing all components listed below into neo4j, exploration via any tool that supports neo4j.
- Calculating DORA metrics: lead time, deployment frequency, mean time to recovery, change failure rate.

## Components

- Commits of a main branch (from which releases are built)
- All releases (from GitHub)
- Issues and their labels (from GitHub)

## Quickstart

- Copy config.json.example to config.json
- Add your neo4j connection credentials. It can be a local or cloud-hosted instance, like auraDB.
- Add your PAT from GitHub so rate limiting of GitHub API is less strict.
  The PAT can be added from [here](https://github.com/settings/tokens), and should only be given access to repositories
  you plan on using as a twin data source.  
