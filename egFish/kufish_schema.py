from specify.schema.base import Field, Link, Record, Schema, make_tree
from specify.schema.field_types import text, date, integer, boolean
from specify.schema.field_options import required
import formatters, vocabularies

class KUFish(Schema):

    class Agent(Record):
        agent_type = Field(text, required)
        title = Field(text)
        job_title = Field(text)
        last_name = Field(text)
        first_name = Field(text)
        middle_initial = Field(text)
        abbreviation = Field(text)
        email = Field(text)
        url = Field(text)

        class Address(Record):
            is_current = Field(boolean)
            address1 = Field(text)
            address2 = Field(text)
            city = Field(text)
            state = Field(text)
            country = Field(text)
            postal_code = Field(text)
            room_building = Field(text)
            phone1 = Field(text)
            phone2 = Field(text)
            fax = Field(text)

    class Taxon( make_tree("kingdom phylum class order family genus species subspecies") ):
        common_name = Field(text)
        source = Field(text)
        protected_status = Field(text)
        author = Link("Agent")
        accepted = Link("Taxon")

    class ReferenceWork(Record):
        type_of_work = Field(text, required)
        title = Field(text)
        publisher = Field(text)
        place_of_publication = Field(text)
        volume = Field(text)
        pages = Field(text)
        date_of_work = Field(date)
        url = Field(text)
        journal = Link("Journal")

        class Author(Record):
            agent = Link("Agent")

    class Journal(Record):
        name = Field(text)
        abbreviation = Field(text)

    class Accession(Record):
        accession_number = Field(text, required)
        status = Field(text)
        accession_type = Field(text)
        accession_date = Field(date)
        received_date = Field(date)
        number_of_lots = Field(integer)
        number_of_specimens = Field(integer)
        description = Field(text)

        class AccessionAgent(Record):
            agent = Link("Agent")
            role = Field(text)

    class Geography( make_tree("continent country state county city") ):
        accepted = Link("Geography")

    class Locality(Record):
        name = Field(text, required)
        geography = Link("Geography")
        water_type = Field(text)
        section = Field(text)
        township = Field(text)
        range = Field(text)
        island = Field(text)
        island_group = Field(text)
        water_body = Field(text)
        drainage = Field(text)

    class CollectingEvent(Record):
        field_number = Field(text, format=formatters.field_number)
        collecting_date = Field(date)
        gear = Field(text)
        locality = Link("Locality")
        trip = Link("CollectingTrip")

        class Collector(Record):
            agent = Link("Agent")

    class CollectingTrip(Record):
        vessel = Field(text)
        cruise = Field(text)
        haul = Field(text)

class KUFishVoucher(Schema):

    class CollectionObject(Record):
        catalog_number = Field(text, format=formatters.catalog_number)
        cataloged_date = Field(date)
        size = Field(text)
        sex = Field(text)
        weight = Field(text)
        cataloger = Link(KUFish.Agent)
        accession = Link(KUFish.Accession)
        collecting_event = Link(KUFish.CollectingEvent)

        class Determination(Record):
            determiner = Link(KUFish.Agent)
            determination_date = Field(date)
            type_status = Field(text)
            taxon = Link(KUFish.Taxon, required)

        class Preparation(Record):
            preparer = Link(KUFish.Agent)
            prep_date = Field(date)
            prep_type = Field(text, required, vocab=vocabularies.VoucherPrepType)
            count = Field(integer)
            on_loan = Field(boolean)

class KUFishTissue(Schema):

    class CollectionObject(Record):
        catalog_number = Field(text, format=formatters.catalog_number)
        cataloged_date = Field(date)
        preservation = Field(text)
        tissue_type = Field(text)
        size = Field(text)
        sex = Field(text)
        cataloger = Link(KUFish.Agent)
        accession = Link(KUFish.Accession)
        collecting_event = Link(KUFish.CollectingEvent)
        voucher = Link(KUFishVoucher.CollectionObject)

        class Determination(Record):
            determiner = Link(KUFish.Agent)
            determination_date = Field(date)
            type_status = Field(text)
            taxon = Link(KUFish.Taxon, required)

        class Preparation(Record):
            preparer = Link(KUFish.Agent)
            prep_date = Field(date)
            prep_type = Field(text, required, vocab=vocabularies.TissuePrepType)
            count = Field(integer)
            on_loan = Field(boolean)
            tubes = Field(integer)
            used_up = Field(boolean)
            storage = Field(text)
