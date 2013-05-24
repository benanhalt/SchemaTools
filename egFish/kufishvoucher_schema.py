from specify.schema import Field, Link
from specify.schema.field_types import text, date
from specify.schema.field_options import required

import formatters, vocabularies
import kufish_schema as KUFish

class CollectionObject:
    catalog_number = Field(text, format=formatters.catalog_number)
    cataloged_date = Field(date)
    accession = Link(KUFish.Accession)

    class Determination:
        determiner = Link(KUFish.Agent)
        determination_date = Field(date)
        taxon = Link(KUFish.Taxon, required)

        class Citation:
            reference_work = Link(KUFish.ReferenceWork, required)

    class Preparation:
        preparer = Link(KUFish.Agent)
        prep_date = Field(date)
        prep_type = Field(text, required, vocab=vocabularies.VoucherPrepType)


