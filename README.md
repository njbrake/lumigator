# Mozilla.ai Lumigator

Lumigator is an open-source platform built by [Mozilla.ai](https://www.mozilla.ai/) for guiding users through the process of selecting the right language model for their needs.
Currently, we support evaluating summarization tasks using sequence-to-sequence models like BART and BERT and causal architectures like GPT and Mistral,
but will be expanding to other machine learning tasks and use-cases.

See [example notebook](/notebooks/walkthrough.ipynb) for a platform API walkthrough.


> ⚠️ **NOTE**
>
> Lumigator is in the early stages of development.
> It is missing important features and documentation.
> You should expect breaking changes in the core interfaces and configuration structures
> as development continues.


# Docs

+ **Understanding Evaluation**
  + [Evaluating Large Language Models](./EVALUATION_GUIDE.md)
+ **Installing Lumigator**
  + Building
    + See below
  + Using/Testing
    + [Kubernetes Helm Charts](lumigator/infra/mzai/helm/lumigator/README.md)
    + [Local install documentation](./.devcontainer/README.md)
+ **Using Lumigator:**
  + [Platform Examples](notebooks/walkthrough.ipynb)
  + [Lumigator API](lumigator/README.md)
  + Offline Evaluations with [lm-buddy](https://github.com/mozilla-ai/lm-buddy)
+ **Extending Lumigator:**
  + [Creating a new Lumigator endpoint](lumigator/python/mzai/backend/api/README.md)


# Available Machine Learning Tasks

## Summarization

### Models for Online Ground Truth Generation

| Model Type | Model                                        | via HuggingFace | via API |
|------------|----------------------------------------------|-----------------|---------|
| seq2seq    | facebook/bart-large-cnn                      |       X         |         |
| causal     | gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo-0125 |                 |    X    |
| causal     | open-mistral-7b                              |                 |    X    |


### Models for Offline Evaluation

| Model Type | Model                                        | via HuggingFace | via API |
|------------|----------------------------------------------|-----------------|---------|
| seq2seq    | facebook/bart-large-cnn                      |       X         |         |
| seq2seq    | longformer-qmsum-meeting-summarization       |       X         |         |
| seq2seq    | mrm8488/t5-base-finetuned-summarize-news     |       X         |         |
| seq2seq    | Falconsai/text_summarization                 |       X         |         |
| causal     | gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo-0125 |                 |    X    |
| causal     | open-mistral-7b                              |                 |    X    |


### Metrics

+ ROUGE - (Recall-Oriented Understudy for Gisting Evaluation), which compares an automatically-generated summary to one generated by a machine learning model on a score of 0 to 1 in a range of metrics comparing statistical similarity of two texts.
+ METEOR - Looks at the harmonic mean of precision and recall
+ BERTScore - Generates embeddings of ground truth input and model output and compares their cosine similarity

[Check this link](docs/assets/metrics.png) for a list of pros and cons of each metric and an example of how they work


# Technical Overview

Lumigator is a Python-based FastAPI web app with REST API endpoints that allow for access to services for serving and evaluating large language models available as safetensor artifacts hosted on both HuggingFace and local stores, with our first primary focus being Huggingface access, and tracking the lifecycle of a model in the backend database (Postgres).
It consists of:

+ a FastAPI-based web app that includes  huggingface's `evaluate` library for those metrics
+ a **Ray cluster** to run offline evaluation jobs using `evaluator`
    + the `evaluator` module runs inference accessing different kind of models, accessible locally or via APIs, and evaluation with huggingface's `evaluate` library or lm-evaluation-harness
+ Artifact management (S3 in the cloud, localstack locally )
+ A Postgres database to track platform-level tasks and dataset metadata

# Get Started

You can build the local project `docker-compose` on Mac or Linux,  or into a distributed environment using Kubernetes [`Helm charts`](lumigator/infra/mzai/helm/lumigator/README.md)

## Local Requirements

+ [Docker](https://docs.docker.com/engine/install/)
    + On Linux, please also follow the [post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/).
+ System Python (that is: no version manager, such as pyenv, should be active).

# Running Lumigator

## Running Lumigator Locally

1. `git clone git@github.com:mozilla-ai/lumigator.git`
2. `make start-lumigator`
3. The REST API should be available at http://localhost:8000. (If you need to change the port, you can do it in the[`docker-compose`](docker-compose) )

## Running Lumigator with an external Ray cluster
To run Lumigator with an external Ray cluster you need to ensure the following variables are configured properly in the [`docker-compose`](docker-compose) file before you start Lumigator:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`
- `RAY_DASHBOARD_PORT`
- `RAY_HEAD_NODE_HOST`


Once that's done, you can start Lumigator with:

`make start-lumigator-external-ray`

## Local Development Setup (either Mac or Linux)
1. `git clone git@github.com:mozilla-ai/lumigator.git`
2. `make local-up`. For more on `docker-compose`, see the [local install documentation.](/.devcontainer/README.md).
3. To shut down app, `make local-down`

### Dev Environment Details

We use `uv` to manage dependencies. Each project under `.../lumigator/lumigator/python/mzai/` is an independent `uv` Python project to isolate dependencies.  Sub-projects are linked together using editable Python package installs.

For each project, here are some handy `uv` commands to work with the repo

Change directory to the project you want to work on  (ie. `lumigator/lumigator/python/mzai/backend`)

**Grab dependencies**

```
uv sync
```

**Run Tests**

```
uv run pytest
```

**Add Dependencies to a given project**

```
uv add package
```

Make sure to commit the updated uv.lock file

**Run the app locally via docker compose:**

```bash
make local-up
make local-logs # gets the logs from docker compose
make local-down # shuts it down
```

### Environment variable reference

The `docker-compose` setup described in the [corresponding README](./.devcontainer/README.md) needs several environment variables to work appropriately.

If the S3 storage service is used, the endpoint, key and secret are needed. The LocalStack implementation used also requires an authentication token.

| Environment variable name | Default value | Description |
| --- | :-: | --- |
| AWS_ENDPOINT_URL | "" | Endpoint URL for the S3 data storage service. |
| AWS_ACCESS_KEY_ID | "" | Key for the S3 data storage service. |
| AWS_SECRET_ACCESS_KEY | "" | Secret for the S3 data storage service. |
| AWS_DEFAULT_REGION | "" | Default region for the S3 service. |
| LOCALSTACK_AUTH_TOKEN | "" | Authentication token for the LocalStack service. |
| S3_BUCKET | lumigator-storage | "" | Bucket name to be used for S3 storage. |

 Models from Mistral or OpenAI can be used via API instead of instantiating them within Lumigator. In this case, the corresponding key is needed.

| Environment variable name | Default value | Description |
| --- | :-: | --- |
| MISTRAL_API_KEY | "" | Key for Mistral API models. |
| OPENAI_API_KEY | "" | Key for OpenAI API models. |

Lumigator uses a database to store its structured data. It needs a database user, a password and a default database.

| Environment variable name | Default value | Description |
| --- | :-: | --- |
| POSTGRES_HOST | "" | Host where the postgres db is available.  Currently pointing at `services.postgres`. |
| POSTGRES_PORT | "" | Port where the postgres db is available (usually 5432). |
| POSTGRES_USER | "" | Database user holding the lumigator structured data. Needs to match `postgres.environment.POSTGRES_DB`. |
| POSTGRES_DB | "" | Database name holding the lumigator structured data. Needs to match `postgres.environment.POSTGRES_DB`. |

The Ray cluster used for computing allows several settings through the following variables.

| Environment variable name | Default value | Description |
| --- | :-: | --- |
| RAY_DASHBOARD_PORT | "" | Port for accessing the Ray dashboards (usually 8265). |
| RAY_WORKER_GPUS | "" | Number of GPUs available for worker nodes. |
| RAY_WORKER_GPUS_FRACTION | "" | Fraction of available GPUs used by worker nodes. |


