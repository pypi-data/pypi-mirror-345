# ☁️ cloud\_auto\_deployor

**cloud\_auto\_deployor** is a Python package that simplifies end-to-end deployment of test automation projects to Azure using Docker and Azure Container Instances (ACI). 
Ideal for local developers, QA teams, and CI/CD use cases.

---

## 🚀 Features

* Auto-builds Docker image from your automation project
* Pushes the image to Azure Container Registry (ACR)
* Deploys the container to Azure Container Instance (ACI)
* Automatically runs your test suite (e.g. Pytest) in the container
* No manual Azure Portal steps required

---

## 📦 Installation

```bash
pip install git+https://github.com/<your-username>/cloud_auto_deployor.git@main
```

> Make sure you have `git`, `Docker`, and `Azure CLI` installed and logged in (`az login`).

---

## 🛠️ Setup

Your test automation project should include:

```
demo_project/
├── Dockerfile
├── requirements.txt
├── tests/
│   └── test_example.py
├── run_tests.py           # Triggers pytest
└── config.json            # Azure details (see below)
```

### 🔧 Example `config.json`

```json
{
  "resource_group": "demo-deploy-group",
  "acr_name": "myacrdeploymentdemo",
  "image_name": "demo_project",
  "image_tag": "v1",
  "container_name": "demo-container",
  "location": "eastus"
}
```

---

## 🧪 Usage

From your test project root (where `config.json` lives), run:

```bash
python -m cloud_auto_deployor.main
```

### What happens:

1. Reads `config.json`
2. Builds Docker image using your Dockerfile
3. Pushes to ACR (auto-creates if needed)
4. Deploys container instance (ACI)
5. Automatically triggers `run_tests.py` to run your tests
6. ✅ Results appear in Azure Portal Logs

---

## 💻 Sample `run_tests.py`

```python
import pytest
import os
import sys

def run_tests():
    sys.path.insert(0, os.getcwd())
    exit_code = pytest.main(["-vv", "tests/"])
    return exit_code

if __name__ == "__main__":
    run_tests()
```

---

## 📥 Uninstall / Clean Up

To remove the container:

```bash
az container delete --name demo-container --resource-group demo-deploy-group --yes
```

To remove the image from ACR:

```bash
az acr repository delete --name myacrdeploymentdemo --image demo_project:v1 --yes
```

---

## 👥 Author

Developed by \ Raja Periyasamy – Automation Lead | Azure DevOps Follower
📧 \[cloudautodeployer@gmail.com](mailto:cloudautodeployer@gmail.com)]

---

## 🪪 License

MIT License
