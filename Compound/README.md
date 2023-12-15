# Introduction 
Compound is a project for hosting development documentation in the cloud only internally available.

# Pipelines

## [Compound-disaster-preparation](https://dev.azure.com/asml/ESDCloudOp/_build?definitionId=5706)

- Triggered daily midnight
- This pipeline destroys all content in the DEV resource group

## [Compound-infra](https://dev.azure.com/asml/ESDCloudOp/_build?definitionId=5707)

- Triggered on every modification on a pull request
  - Will deploy to NO environment
- Triggered on succesfull Compound-disaster-preparation run
  - Will deploy to DEV environment
- Triggered on every commit on MAIN
  - Will deploy to every environment
- This pipeline builds all content in all resource groups
- This pipeline will also use templates for deploying the source

## [Compound-src](https://dev.azure.com/asml/ESDCloudOp/_build?definitionId=5572)

- Triggered on every commit on MAIN
  - Will deploy to every environment
- This pipeline deploys the source in all resource groups
