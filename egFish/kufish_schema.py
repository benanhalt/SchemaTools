from specify.schema.base import Field, Link, Record, Schema, make_tree
from specify.schema.field_types import text, date
from specify.schema.field_options import required
import formatters, vocabularies

class KUFish(Schema):

    class Agent(Record):
        pass

    class Taxon( make_tree("kingdom phylum class order family genus species subspecies") ):
        author = Link("Agent")

    class ReferenceWork(Record):
        pass

    class Accession(Record):
        pass

    class Geography( make_tree("continent country state county city") ):
        pass

    class Locality(Record):
        name = Field(text, required)
        geography = Link("Geography")

    class CollectingEvent(Record):
        field_number = Field(text, format=formatters.field_number)
        start_date = Field(date)
        end_date = Field(date)
        locality = Link("Locality")

class KUFishVoucher(Schema):

    class CollectionObject(Record):
        catalog_number = Field(text, format=formatters.catalog_number)
        cataloged_date = Field(date)
        accession = Link(KUFish.Accession)
        collecting_event = Link(KUFish.CollectingEvent)

        class Determination(Record):
            determiner = Link(KUFish.Agent)
            determination_date = Field(date)
            taxon = Link(KUFish.Taxon, required)

            class Citation(Record):
                reference_work = Link(KUFish.ReferenceWork, required)

        class Preparation(Record):
            preparer = Link(KUFish.Agent)
            prep_date = Field(date)
            prep_type = Field(text, required, vocab=vocabularies.VoucherPrepType)

class KUFishTissue(Schema):

    class CollectionObject(Record):
        catalog_number = Field(text, format=formatters.catalog_number)
        cataloged_date = Field(date)
        accession = Link(KUFish.Accession)
        voucher = Link(KUFishVoucher.CollectionObject)

        class Determination(Record):
            determiner = Link(KUFish.Agent)
            determination_date = Field(date)
            taxon = Link(KUFish.Taxon, required)

        class Preparation(Record):
            preparer = Link(KUFish.Agent)
            prep_date = Field(date)
            prep_type = Field(text, required, vocab=vocabularies.TissuePrepType)
