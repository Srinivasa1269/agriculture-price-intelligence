# Run with Docker and deploy to Azure

## Run locally with Docker

The data file is not stored in Git (it is 62 MB), so put it in `data/` first.

```bash
mkdir -p data        # then copy agriculture_cleaned.csv into data/
docker build -t agri-price-intelligence .
docker run --rm -p 8501:8501 -v "$(pwd)/data:/app/data" agri-price-intelligence
```

Open http://localhost:8501.

Ollama is not inside the container, so the app shows
"not running - using the keyword parser" at the bottom. Questions and forecasts still work.

## Deploy to Azure Container Apps

> These steps have **not** been tested yet. Run them once yourself and fix anything that differs
> before you tell anyone that the app is deployed.

Needs an Azure account and the [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli).
`agriculture_cleaned.csv` must be inside `data/` on your machine, because the image is built from
your local folder (Git does not contain it).

```bash
az login
az extension add --name containerapp --upgrade
az group create --name agri-rg --location uksouth
az containerapp up \
  --name agri-price-intelligence \
  --resource-group agri-rg \
  --location uksouth \
  --source . \
  --ingress external \
  --target-port 8501
```

The command prints a public URL. When you are done, delete everything to avoid charges:

```bash
az group delete --name agri-rg --yes
```
