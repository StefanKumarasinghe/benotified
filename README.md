# 🔔 Be Notified

### The Pulse of Incident Orchestration & Alert Management.

**Be Notified** is the high-performance engine that powers the alerting domain of the Be Observant platform. While Alertmanager handles the routing, **Be Notified** handles the *human* side of the equation—managing the full incident lifecycle, coordinating team collaborations, and bridging the gap between raw telemetry and external tools like Jira, Slack, and PagerDuty.

![BeNotified](assets/beobservant.png)

Designed as an internal-tier service, it provides a secure, multi-tenant layer to sync rules with Mimir and ensure that every alert is not just heard, but acted upon.

---

## ✨ Core Capabilities

* **⚡ Intelligent Ingestion:** Seamlessly processes webhooks from Alertmanager and translates them into actionable incidents.
* **📋 Incident Management:** A centralized hub for tracking status, adding notes, and assigning responders.
* **🔄 Mimir Rule Sync:** Automatically keeps your PromQL alert rules in sync with the Mimir ruler.
* **🔌 Enterprise Integrations:** Native, bi-directional integration with Jira and multi-channel delivery (Email, Slack, etc.).
* **🛡️ Secure Internal Proxy:** Proxies authenticated Alertmanager traffic from the main `beobservant` API.

---

## 🏗 System Architecture & Runtime

Be Notified is designed to run within your internal network, acting as a protected backend for the primary platform.

| Detail | Specification |
| --- | --- |
| **Service Port** | `4323` |
| **Internal Base Path** | `/internal/v1` |
| **Primary Dependency** | Alertmanager & Mimir |
| **Authentication** | Shared Service Token + Context JWT |

### Internal Communication

To maintain a strict security posture, all calls from the main service to Be Notified must include:

* `X-Service-Token`: A shared secret between internal services.
* `Authorization: Bearer <context-jwt>`: Signed user/tenant context.

---

## 🚀 Getting Started

### 1. Installation

Clone the repository alongside your other Be Observant services:

```bash
git clone https://github.com/observantio/benotified.git BeNotified
cd BeNotified

```

### 2. Run with Docker

Build and launch the notification engine:

```bash
docker build -t benotified:latest .
docker run --rm -it \
    -p 4323:4323 \
    --name benotified \
    benotified:latest

```

### 3. Required Environment

Ensure your `.env` or secret manager contains these critical variables:

```env
BENOTIFIED_DATABASE_URL=postgres://...
BENOTIFIED_EXPECTED_SERVICE_TOKEN=your-shared-secret
INBOUND_WEBHOOK_TOKEN=secure-webhook-token
MIMIR_URL=http://mimir:9009
ALERTMANAGER_URL=http://alertmanager:9093
```

---

## 🛠 Operational Workflow

### The Alert Journey

1. **Trigger:** An alert fires in Prometheus/Mimir based on your rules.
2. **Route:** Alertmanager sends a webhook to Be Notified.
3. **Create:** Be Notified validates the `INBOUND_WEBHOOK_TOKEN` and opens a new Incident.
4. **Notify:** Based on visibility (Private/Group/Tenant), notifications are dispatched to configured channels.
5. **Resolve:** The team collaborates in the UI; once resolved, the status is synced back across the ecosystem.

---

## 🤝 Development & Contribution

Be Notified is built with Python and FastAPI, optimized for low-latency incident processing.

**Running Tests:**

```bash
pytest -q
```

**Quality Gates:**
This repository is a core part of the **Be Observant** ecosystem. If you are contributing from the mono-repo root, your commits will be validated by `.pre-commit-config.yaml` to ensure cross-service compatibility.

---

## 📄 License

Licensed under the **Apache License 2.0**.

*Attribution: The notices included in the source code and headers must be preserved in all redistributions. This service is intended for internal network deployment and should not be exposed to the public internet.*
