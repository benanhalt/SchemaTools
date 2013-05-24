from schema import Field, Link, Tree
from schema.field_types import text, date
from schema.field_options import required
import formatters, vocabularies

class Agent:
    pass

class Taxon( Tree("kingdom phylum class order family genus species subspecies") ):
    author = Link(Agent)

class ReferenceWork:
    pass

class Accession:
    pass

class Geography( Tree("continent country state county city") ):
    pass

class Locality:
    name = Field(text, required)
    geography = Link(Geography)

class CollectingEvent:
    field_number = Field(text, format=formatters.field_number)
    start_date = Field(date)
    end_date = Field(date)
    locality = Link(Locality)
