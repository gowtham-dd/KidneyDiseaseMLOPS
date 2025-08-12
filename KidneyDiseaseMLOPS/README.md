# Kidney-Disease-Classification-MLflow-DVC

## Workflows

- Update `config.yaml`
- Update `secrets.yaml` [Optional]
- Update `params.yaml`
- Update the entity
- Update the configuration manager in `src/config`
- Update the components
- Update the pipeline
- Update the `main.py`
- Update the `dvc.yaml`
- `app.py`

---


## How to run?

### STEPS:

### Clone the repository

```bash
git clone https://github.com/gowtham-dd/KidneyDiseaseMLOPS
````

### STEP 01 - Create a conda environment after opening the repository

```bash
conda create -n cnncls python=3.8 -y
conda activate cnncls
```

### STEP 02 - Install the requirements

```bash
pip install -r requirements.txt
```

### Finally run the following command

```bash
python app.py
```

### Now,

Open up your localhost and port.

---

## MLflow

### Documentation

[MLflow tutorial](https://www.mlflow.org/docs/latest/index.html)

```bash
mlflow ui
```

### Dagshub

```env
MLFLOW_TRACKING_URI=<your_mlflow_tracking_uri>
MLFLOW_TRACKING_USERNAME=<your_mlflow_username>
MLFLOW_TRACKING_PASSWORD=<your_mlflow_password>
```

```bash
python script.py
```

#### Run this to export as env variables:

```bash
export MLFLOW_TRACKING_URI=<your_mlflow_tracking_uri>
export MLFLOW_TRACKING_USERNAME=<your_mlflow_username>
export MLFLOW_TRACKING_PASSWORD=<your_mlflow_password>
```

---

## DVC Commands

```bash
dvc init
dvc repro
dvc dag
```

---

## About MLflow & DVC

### MLflow

* Production grade
* Trace all of your experiments
* Logging & tagging your model

### DVC

* Very lightweight (for POCs)
* Lightweight experiment tracker
* Can perform orchestration (creating pipelines)

---

## AWS-CICD-Deployment-with-Github-Actions

### 1. Login to AWS console.

### 2. Create IAM user for deployment with specific access

**Access Required:**

* EC2 access (Virtual machine)
* ECR (Elastic Container Registry to save your Docker image in AWS)

---

### Deployment Description

1. Build Docker image of the source code
2. Push your Docker image to ECR
3. Launch your EC2
4. Pull your image from ECR in EC2
5. Launch your Docker image in EC2

---

### IAM Policies:

* `AmazonEC2ContainerRegistryFullAccess`
* `AmazonEC2FullAccess`

---

### 3. Create ECR repo to store/save docker image

Save the URI:

```
<your_aws_ecr_login_uri>/<your_repo_name>
```

---

### 4. Create EC2 machine (Ubuntu)

### 5. Install Docker in EC2 Machine

**Optional:**

```bash
sudo apt-get update -y
sudo apt-get upgrade
```

**Required:**

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
newgrp docker
```

---

### 6. Configure EC2 as self-hosted runner

GitHub → Settings → Actions → Runners → New self-hosted runner → Choose OS → Run commands one by one

---

### 7. Setup GitHub Secrets

* `AWS_ACCESS_KEY_ID=`
* `AWS_SECRET_ACCESS_KEY=`
* `AWS_REGION=us-east-1`
* `AWS_ECR_LOGIN_URI=<your_aws_ecr_login_uri>`
* `ECR_REPOSITORY_NAME=<your_ecr_repository_name>`
