# Data Quality Check System

This project is a data quality pipeline built by our team using Python and Prefect, with a PostgreSQL database and Alembic migrations.  
It provides a structured foundation for identifying and handling invalid or rejected transactions in a data stream.

# **Project Setup and Installation**

## **Prerequisites**

To run this code, you need the following tools and packages (the team has successfully run the code using PyCharm):

- alembic
- prefect
- pandas
- great-expectations
- logging
- psycopg2
- sqlalchemy
- contextlib
- subprocess
- sys

## **Database Setup**

Before running `main.py`, you need to establish a local database connection.

### **Configuration Files**

You must configure your local database connection by specifying the connection to `@localhost` with the appropriate connection port, username, and password in the following files:

- `alembic.ini`
- `db.py`
- `main.py`

### **Important Pre-execution Step**

**CRITICAL:** Before running any code, ensure that `target_metadata = Base.metadata` is correctly configured in the `env.py` file located in the alembic folder.

## **Running the Application**

### **Automated Migration**

Once the above configuration is complete, you can run the `run_migrations.py` file for an automated variant of alembic migration.

### **Manual Migration (Optional)**

If you prefer to run alembic commands manually and locally in your terminal, this is also perfectly fine to do.

### **Starting the System**

After completing the migration process, simply run the code to start the system we have built as the foundation.

## **Contributors**

This project was developed by the following team members:

- MakkanTV
- nikkicci
- Milan624
- OmidLarizadeh