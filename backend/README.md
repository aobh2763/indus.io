# indus.io Backend

This is the FastAPI backend for **indus.io** — the premier Industrial Production Line Simulation and AI Management Platform.

## 🏗️ Architecture

The backend is built as a **Modular Monolith** using **Domain-Driven Design (DDD)**. Instead of separating files by their technical type (e.g., all models in one folder, all routers in another), the codebase is organized by **business domain**. 

This makes the code highly scalable and easier to maintain.

### Modules (`app/modules/`)
*   **`identity`**: User authentication, JWT tokens, and System-Level Access (Global Roles: `ADMIN`, `USER`).
*   **`project`**: Workspace management and Project-Level RBAC (`OWNER`, `SUPERVISOR`, `COLLABORATOR`, `VIEWER`).
*   **`production`**: The core graph. Manages `Machines`, `Connections` (edges), and machine specific attributes (`AttributeDefinitions`).
*   **`simulation`**: The simulation engine, tracking runs and detailed `SimulationLogs`.
*   **`analytics`**: Key Performance Indicators (`KPI` and `KPIValue`) tracked at both the line and machine level.
*   **`telemetry`**: High-frequency IoT `SensorData` ingestion.
*   **`intelligence`**: `AIAgent` management and AI-generated `Suggestions` with actionable JSON payloads.
*   **`monitoring`**: Anomaly detection and threshold `Alerts`.

## 🗄️ Database Strategy: The Graph-Relational Hybrid

We use **PostgreSQL** paired with **Apache AGE**.

*   **Relational Power**: All transactional data (users, projects, logs, auth) is stored in standard, highly reliable PostgreSQL tables using SQLAlchemy.
*   **Graph Brain**: The production line topology (`Machines` as nodes, `Connections` as edges) lives inside a Graph Workspace (`indus_production`). This allows the AI to use **Cypher** queries to instantly traverse the factory, find bottlenecks, and understand downstream impacts without complex SQL joins.

## 🔒 Security & Access Control

Access control is split into two distinct layers:

1.  **System Level (GlobalRoles)**
    *   `ADMIN`: Full system access. Can perform CRUD operations on all users.
    *   `USER`: Standard access. Can only manage their own profile and access their projects.
2.  **Project Level (RBAC)**
    *   `OWNER`: Can delete the project and manage team access.
    *   `SUPERVISOR`: Can edit production lines and manage simulations.
    *   `COLLABORATOR`: Can view data and interact with simulations.
    *   `VIEWER`: Read-only access.

## 🚀 Getting Started

### Prerequisites
*   Docker & Docker Compose

### Running the Application

The entire stack is containerized. To spin up the backend, frontend, and the Graph-enabled database:

```bash
docker compose up -d --build
```

### Accessing the API
Once the containers are running, you can access the interactive API documentation (Swagger UI) at:
*   **http://localhost:8000/docs**

### Database Initialization
The database tables are automatically created on startup via SQLAlchemy (`Base.metadata.create_all`). The Graph Workspace (`indus_production`) is initialized using the custom SQL script in `app/db/init_graph.sql`.
