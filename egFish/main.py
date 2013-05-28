import sqlalchemy

from specify.schema import create_schema
import kufish_schema

engine = sqlalchemy.create_engine(
    'postgresql+pypostgresql://master:master@localhost:5433/specify_future',
    echo=True)

metadata = sqlalchemy.MetaData()
create_schema(engine, metadata, kufish_schema)


