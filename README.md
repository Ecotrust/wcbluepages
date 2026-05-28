# wcbluepages
West Coast Blue Pages: ID WCOA contacts for all topics

## Installation

Clone the repo locally:
```
git clone https://github.com/Ecotrust/wcbluepages
cd wcbluepages
```
### Run with docker

- Prerequisites:
  - docker

- Create copy of the `.env.dev` file  as `.env` in the `wcbluepages` directory. Add your environment variables to that file.

- If it is your first time running the containers, build them first: `docker compose build`

- Run the containers: `docker compose up`

- View the app at: `http://localhost:8000`

## Building a New Image

This project publishes Docker images to [Github Packages](https://github.com/Ecotrust/wcbluepages/pkgs/container/wcbluepages). To create a new Docker image, create a new [release](https://github.com/Ecotrust/wcbluepages/releases) with the semver version you would like. The [Github Action](https://github.com/Ecotrust/wcbluepages/blob/main/.github/workflows/create-and-publish-docker-images.yaml) will create new image will be taged with `latest` and the semver verion you chose. 

## Deploying to Production 

To deploy to production, we have a [Github Action](https://github.com/Ecotrust/wcbluepages/actions/workflows/deploy-ec2-production.yaml) to deploy to the EC2 instance running the production site. The Github Action only runs when triggered manually. 

