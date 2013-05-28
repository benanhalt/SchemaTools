import sqlalchemy

from specify.schema import schema_to_sqlalchemy
import kufish_schema

metadata = sqlalchemy.MetaData()

print(metadata.create_all())
