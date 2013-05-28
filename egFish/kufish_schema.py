from specify.schema import Field, Link, Tree, Record
from specify.schema.field_types import text, date
from specify.schema.field_options import required
import formatters, vocabularies

class Agent(Record):
    pass

class Taxon( Tree("kingdom phylum class order family genus species subspecies") ):
    author = Link(Agent)

class ReferenceWork(Record):
    pass

class Accession(Record):
    pass

class Geography( Tree("continent country state county city") ):
    pass

class Locality(Record):
    name = Field(text, required)
    geography = Link(Geography)

class CollectingEvent(Record):
    field_number = Field(text, format=formatters.field_number)
    start_date = Field(date)
    end_date = Field(date)
    locality = Link(Locality)

