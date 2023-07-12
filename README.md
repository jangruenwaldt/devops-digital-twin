# DevOps Digital Twin

[![Python integration test](https://github.com/jangruenwaldt/devops-digital-twin/actions/workflows/ci.yaml/badge.svg)](https://github.com/jangruenwaldt/devops-digital-twin/actions/workflows/ci.yaml)

Fetch DevOps system data into JSON, and then store it in neo4j. Exploration and interface on top of neo4j is planned.

## What is this, and what makes it new and different?

DevOps teams have a lot of data that can be explored, evaluated, and analyzed, but most of this data lives in different
systems and is not combined. This project will move all this data into a neo4j database that can then be used for
further data analysis and exploration. Think of it as a DevOps data integration project to provide a unified view of
everything.

## Who is this for, and what will they do with it?

This is for team members of a DevOps team, or really anyone who is interested in getting a better perspective on the
team. If you would like to become more data-drive, this is for you. After you spun up a neo4j database and configured
the project with your own config.json file, just run `docker compose up --build` to have a docker container that will
update your data every 24 hours. Ideally you will just deploy this container on any cloud provider of your preference,
so you don't have to keep Docker running on your machine at all times.

## How do they get started and how do they use it?

1. Copy config.example.json and name it `config.json`. As you setup the project, this file will contain all config.
2. Then you should spin up a [cloud hosted neo4j database](https://neo4j.com/cloud/platform/aura-graph-database/), as
   that is where all data will be stored. Edit the config file according to your credentials. (db_address, db_user,
   db_pw)
3. Then you should provide the data sources. Edit `commit_data_source` and the other data source. Since currently only
   GitHub is supported, you will paste the same repo URL into all four settings.
4. Since the tool needs access to the repository, provide it with a `personal_access_token` that has read access to the
   repository. The PAT can be added from [here](https://github.com/settings/tokens). It should only be given access to
   repositories you plan on using as a twin data source.
5. Run `docker compose up --build` and it will spin up a container which contains a long-running script that will update
   the database every X hours (configurable via config).

## Currently supported

- Importing all components listed below into neo4j, exploration via any tool that supports neo4j.
- Calculating DORA metrics: lead time, deployment frequency, mean time to recovery, change failure rate.

## Components

- Commits of a main branch (from which releases are built)
- All releases (from GitHub)
- Issues and their labels (from GitHub)
- Automations and their run history (from GitHub actions)
