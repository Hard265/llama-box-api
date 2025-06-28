# Cloud Backend

**Cloud** is a secure and extensible backend platform for file and folder storage, sharing, and collaboration. It supports user-controlled permissions, token-based access, and integrates seamlessly with **Nucleus** identity providers.

## Features

- 📁 File and folder upload, download, and management
- 🔗 Shareable links with expiration and permissions
- 🔐 Token-based access control
- 👥 Multi-user sharing support
- 📄 GraphQL and RESTful APIs
- 🗂️ Organized storage structure per user
- ⚡ FastAPI + async architecture for high performance

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite3
- **Storage**: Local
- **Auth**: JWT (via Nucleus IAM)
- **API Layer**: GraphQL (Strawberry)

## Getting Started

### Requirements

- Python 3.11+
- SQLite3

### Installation

```bash
git clone https://github.com/Hard265/cloud
cd cloud
pip install -r requirements.txt
```
