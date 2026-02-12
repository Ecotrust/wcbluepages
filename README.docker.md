# Docker Setup for WC Bluepages

## Quick Start

### Pre-requisites

- Have a dump of the database called `db_dump.sql` in the `wcbluepages` directory. This is necessary to alter the tables to the expected form until the migrations work correctly.

### 1. Build and start the containers:

```bash
docker-compose up --build
```

### 2. Access the application:

- Web application: http://localhost:8000
- Admin interface: http://localhost:8000/admin
