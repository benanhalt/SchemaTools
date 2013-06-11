import sqlalchemy

from specify.schema import to_sqlalchemy, conversion
from specify.schema.to_json import to_json

import kufish_schema
import kufish_conversion

engine = sqlalchemy.create_engine(
    'postgresql+pypostgresql://master:master@localhost:5435/specify_future',
    echo=True)

mysql_engine = sqlalchemy.create_engine(
    'mysql+pymysql://Master:Master@localhost/ku_fish_tissue_201302_django15',
    echo=True)

metadata = sqlalchemy.MetaData(bind=engine)
schemas = to_sqlalchemy.process_schemas(metadata, kufish_schema.schema_family)
to_sqlalchemy.create_schemas(engine, metadata, kufish_schema.schema_family)

mysql_metadata = sqlalchemy.MetaData(bind=mysql_engine)
conversion.reflect_database(mysql_metadata, kufish_conversion.schema_family)

conversion.join_schema_family_with_conversion(kufish_schema.schema_family,
                                              kufish_conversion.schema_family)

conversion.do_conversion(kufish_conversion.schema_family, metadata)

print(to_json(kufish_schema.schema_family))
