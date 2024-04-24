from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from models import Base

# Create a database connection
DATABASE_URL = "sqlite:///database.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_database():
    Base.metadata.create_all(bind=engine)

    # Inspect the database
    inspector = inspect(engine)

    for table_name in Base.metadata.tables:
        # Fetch existing columns from the database for the current table
        existing_columns = [col["name"] for col in inspector.get_columns(table_name)]

        # Get the columns of the model
        model_columns = Base.metadata.tables[table_name].columns.keys()

        # Determine which columns are missing
        missing_columns = set(model_columns) - set(existing_columns)

        # Add missing columns to the table
        with engine.connect() as conn:
            for column_name in missing_columns:
                column_type = str(Base.metadata.tables[table_name].columns[column_name].type)
                sql_command = text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
                conn.execute(sql_command)