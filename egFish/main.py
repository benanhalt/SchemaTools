import sqlalchemy

from kufish_schema import KUFish, KUFishVoucher, KUFishTissue

engine = sqlalchemy.create_engine(
    'postgresql+pypostgresql://master:master@localhost:5433/specify_future',
    echo=True)

metadata = sqlalchemy.MetaData()
KUFish.create(engine, metadata)
KUFishVoucher.create(engine, metadata)
KUFishTissue.create(engine, metadata)
metadata.create_all(engine)



