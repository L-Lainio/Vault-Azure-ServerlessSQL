# 🛡️ Vault: Azure Serverless & SQL

**Vault** is a secure, cloud-native compliance engine designed to manage sensitive records with a "Security-First" architecture. This project represents a strategic pivot from the MERN stack into the **Microsoft Azure ecosystem**, emphasizing relational data integrity and serverless scalability.

---

## 🏗️ System Architecture



* **Compute:** **Azure Functions (Serverless Node.js V4)** provide event-driven logic without the overhead of permanent servers.
* **Database:** **Azure SQL (PaaS)** ensures high-performance relational storage and strict ACID compliance.
* **Connectivity:** Integrated via the **Azure Resources** extension for seamless cloud management directly from VS Code.

---

## 🛡️ Security & Compliance Focus

Drawing on a professional background as a PTIN-registered tax specialist, this project addresses the unique challenges of handling **PII (Personally Identifiable Information)**:

* **SQL Injection Prevention:** Implementation of parameterized queries using the `tedious` driver to sanitize all database inputs.
* **Zero-Trust Credentials:** Environment secrets are isolated in `local.settings.json` and managed via Azure App Settings to prevent credential leakage in source control.
* **Auditability:** Designed with a relational schema that supports comprehensive audit logs for tracking data access events.

---

## 🛠️ Tech Stack & Tools

| Component | Technology |
| :--- | :--- |
| **Cloud Platform** | Microsoft Azure |
| **Runtime** | Node.js (Azure Functions V4) |
| **Database** | Azure SQL Server |
| **Development** | VS Code (Azure Resources & Functions extensions) |

---

## 🚀 Strategic Roadmap

To ensure this architecture meets enterprise standards, development is being synchronized with the following Microsoft Technical Briefs:

* **Upcoming Session:** *Migrate and Modernize Linux, PostgreSQL, and Java to Azure* (January 30, 2026).

---

## 📁 Getting Started

1.  **Repository Setup:** Clone the repository and run `npm install` to load dependencies like `tedious`.
2.  **Azure Configuration:** Sign in to your Azure Tenant via the VS Code sidebar.
3.  **Local Environment:** Configure your `local.settings.json` with your Azure SQL connection string.
4.  **Launch:** Run `func start` to test the secure endpoints locally.

---

**Developed by Lora — 2026 Portfolio**
