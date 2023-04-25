# Async FastAPI Boilerplate V2

An API Boilerplate written in python with FastAPI. Write restful API with fast development and developer friendly.

## Architecture

In this project use 3 layer architecture

-   models
-   repository
-   usecase

## Features

-   Create, read, delete, update
-   Authentication: Jwt access, refresh token. Save refresh token in redis
-   Redis caching

## Technical

-   fastapi
-   sqlalchemy 2.0
-   celery
-   loguru

## Start Application

### Run

-   `docker compose up`

## TODO

-   Sentry
-   Forgot password
-   Verify account
-   Github actions: cache docker build, cache pip install
