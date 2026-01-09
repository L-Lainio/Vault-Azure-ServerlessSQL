# 🛡️ Vault: Azure Serverless & SQL

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Azure Functions](https://img.shields.io/badge/Azure_Functions-v2-0062AD?logo=microsoftazure)
![Azure SQL](https://img.shields.io/badge/Azure_SQL-PaaS-0078D4?logo=microsoftsqlserver)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Build Status](https://github.com/L-Lainio/Vault-Azure-ServerlessSQL/actions/workflows/deploy.yml/badge.svg)

**Vault** is a secure, cloud-native compliance engine designed to manage sensitive records with a "Security-First" architecture. This project pivots into the **Microsoft Azure ecosystem** using Python, emphasizing relational integrity and serverless scalability.

---

## 🏗️ System Architecture

* **Compute:** Azure Functions (Python 3.11, v2 programming model) for event-driven logic.
* **Database:** Azure SQL (PaaS) with ACID compliance and auditability.
* **Identity:** Passwordless access via Managed Identity + `azure-identity`.
* **Connectivity:** `pyodbc` with ODBC Driver 18 (Linux-friendly for GitHub runners).

---

## 🛡️ Security & Compliance Focus

* **Zero-Trust Credentials:** No passwords in code or settings; uses Managed Identity tokens.
* **SQL Injection Prevention:** Parameterized queries through `pyodbc` everywhere.
* **Auditability:** Built-in audit logging pattern for data access and writes.

---

## 🛠️ Tech Stack & Tools

| Component | Technology |
| :--- | :--- |
| **Cloud Platform** | Microsoft Azure |
| **Runtime** | Python 3.11 (Azure Functions v2) |
| **Database** | Azure SQL Server |
| **Auth** | Managed Identity (`DefaultAzureCredential`) |
| **Connectivity** | pyodbc + ODBC Driver 18 |
| **CI/CD** | GitHub Actions (.github/workflows/deploy.yml) |

---

## 📁 Getting Started

1. **Install dependencies**
	```bash
	pip install -r requirements.txt
	```
	On local Linux dev boxes, install ODBC headers first: `sudo apt-get update && sudo apt-get install -y unixodbc-dev`.

2. **Configure local settings** (`local.settings.json`)
	```json
	{
	  "IsEncrypted": false,
	  "Values": {
		 "AzureWebJobsStorage": "UseDevelopmentStorage=true",
		 "FUNCTIONS_WORKER_RUNTIME": "python",
		 "DB_SERVER": "your-server-name.database.windows.net",
		 "DB_NAME": "your-database-name"
	  }
	}
	```

3. **Run locally** (Functions Core Tools)
	```bash
	func start
	```

4. **Deploy**
	Push to `main` to trigger the GitHub Actions workflow (`deploy.yml`). The workflow installs `unixodbc-dev`, restores Python deps, and deploys to Azure Functions.

---

## 🔐 Managed Identity Setup (Azure SQL)

1. Enable System-Assigned (or User-Assigned) Managed Identity on the Function App.
2. In Azure SQL (master or target DB), create a user and grant roles:
	```sql
	CREATE USER [<function-app-name>] FROM EXTERNAL PROVIDER;
	ALTER ROLE db_datareader ADD MEMBER [<function-app-name>];
	ALTER ROLE db_datawriter ADD MEMBER [<function-app-name>];
	```
3. Set App Settings in Azure Function: `DB_SERVER`, `DB_NAME` (no password or user required).

---

**Developed by Lora — 2026 Portfolio**
