# Campus UAV Inspection Task Management System

> A Flask and GaussDB/openGauss application for scheduling campus drone inspections, managing equipment, and tracking abnormalities through repair.

## Features

- Dashboard for daily tasks, available drones and batteries, completed work, and pending abnormalities.
- Drone, battery, pilot, and inspection-area records.
- Task scheduling with availability, battery-level, pilot-status, and time-conflict checks.
- Inspection result submission and abnormality classification.
- Repair records with completion and review status.
- SQL schema, seed data, and verification queries for GaussDB/openGauss/PostgreSQL-compatible environments.

## Tech stack

- Python and Flask
- psycopg2
- python-dotenv
- GaussDB, openGauss, or PostgreSQL
- Server-rendered Jinja templates

## Repository structure

```text
uav_inspection_gaussdb/
├── app.py
├── requirements.txt
├── README_学校数据库运行说明.md
├── sql/
│   ├── schema_gaussdb.sql
│   ├── seed_gaussdb.sql
│   └── test_queries.sql
└── templates/
```

## Quick start

```bash
git clone https://github.com/KaiserIIII/-UAV-inspection-task-management-system-in-college-parks.git uav-inspection-manager
cd uav-inspection-manager/uav_inspection_gaussdb
python -m venv .venv
```

Activate the virtual environment and install dependencies:

```bash
python -m pip install -r requirements.txt
```

Create a `.env` file without committing it:

```dotenv
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=teaching
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_SCHEMA=yy_uav
```

Run `sql/schema_gaussdb.sql`, followed by `sql/seed_gaussdb.sql`, in the target database. Optionally run `sql/test_queries.sql` to verify the installation.

Start the application:

```bash
python app.py
```

Open `http://127.0.0.1:5000`.

## Business rules implemented

- A task end time must be later than its start time.
- A drone must be available.
- A battery must be available and at least 30% charged.
- A pilot must be idle.
- Active task windows cannot overlap for the same drone or pilot.
- Submitting an abnormal result creates an abnormality record for follow-up.

## Security notes

This repository is an educational prototype. Before deploying it:

- Replace the Flask development secret and disable debug mode.
- Hash passwords; the seed data and current schema are not production authentication.
- Restrict database and Web access to trusted networks.
- Use a least-privilege database account and keep credentials out of Git.
- Add CSRF protection, authorization checks, input validation, and production logging.

## License

No root license file is currently included. Add an explicit license before redistributing the project or accepting external contributions.
