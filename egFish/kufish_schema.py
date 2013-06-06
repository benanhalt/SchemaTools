from specify.schema.base import Record, SchemaFamily, make_tree
from specify.schema.fields import Boolean, Text, Integer, Date, Link, required
import formatters, vocabularies

schema_family = SchemaFamily()
Schema = schema_family.Schema

class KUFish(Schema):

    class Agent(Record):
        agent_type = Text(required)
        title = Text()
        job_title = Text()
        last_name = Text()
        first_name = Text()
        middle_initial = Text()
        abbreviation = Text()
        email = Text()
        url = Text()

        class Address(Record):
            is_current = Boolean()
            address1 = Text()
            address2 = Text()
            city = Text()
            state = Text()
            country = Text()
            postal_code = Text()
            room_building = Text()
            phone1 = Text()
            phone2 = Text()
            fax = Text()

    class Taxon( make_tree("kingdom phylum class order family genus species subspecies") ):
        common_name = Text()
        source = Text()
        protected_status = Text()
        author = Text()
        accepted = Link("Taxon")

    class ReferenceWork(Record):
        type_of_work = Text()
        title = Text()
        publisher = Text()
        place_of_publication = Text()
        volume = Text()
        pages = Text()
        date_of_work = Text()
        url = Text()
        journal = Link("Journal")

        class Author(Record):
            agent = Link("Agent", required)

    class Journal(Record):
        name = Text()
        abbreviation = Text()

    class Accession(Record):
        accession_number = Text(required)
        status = Text()
        accession_type = Text()
        accession_date = Date()
        received_date = Date()
        number_of_lots = Integer()
        number_of_specimens = Integer()
        description = Text()

        class AccessionAgent(Record):
            agent = Link("Agent", required)
            role = Text()

    class Geography( make_tree("continent country state county city") ):
        accepted = Link("Geography")

    class Locality(Record):
        name = Text(required)
        geography = Link("Geography")
        water_type = Text()
        section = Text()
        township = Text()
        range = Text()
        island = Text()
        island_group = Text()
        water_body = Text()
        drainage = Text()

    class CollectingEvent(Record):
        field_number = Text(format=formatters.field_number)
        collecting_date = Date()
        gear = Text()
        locality = Link("Locality")
        trip = Link("CollectingTrip")

        class Collector(Record):
            agent = Link("Agent", required)

    class CollectingTrip(Record):
        vessel = Text()
        cruise = Text()
        haul = Text()

class KUFishVoucher(Schema):

    class CollectionObject(Record):
        catalog_number = Text(format=formatters.catalog_number)
        cataloged_date = Date()
        size = Text()
        sex = Text()
        weight = Text()
        cataloger = Link(KUFish.Agent)
        accession = Link(KUFish.Accession)
        collecting_event = Link(KUFish.CollectingEvent)

        class Determination(Record):
            determiner = Link(KUFish.Agent)
            determination_date = Date()
            type_status = Text()
            taxon = Link(KUFish.Taxon)

        class Preparation(Record):
            preparer = Link(KUFish.Agent)
            prep_date = Date()
            prep_type = Text(required, vocab=vocabularies.VoucherPrepType)
            count = Integer()
            on_loan = Boolean()

class KUFishTissue(Schema):

    class CollectionObject(Record):
        catalog_number = Text(format=formatters.catalog_number)
        cataloged_date = Date()
        preservation = Text()
        tissue_type = Text()
        size = Text()
        sex = Text()
        cataloger = Link(KUFish.Agent)
        accession = Link(KUFish.Accession)
        collecting_event = Link(KUFish.CollectingEvent)
        voucher = Link(KUFishVoucher.CollectionObject)

        class Determination(Record):
            determiner = Link(KUFish.Agent)
            determination_date = Date()
            type_status = Text()
            taxon = Link(KUFish.Taxon)

        class Preparation(Record):
            preparer = Link(KUFish.Agent)
            prep_date = Date()
            prep_type = Text(required, vocab=vocabularies.TissuePrepType)
            count = Integer()
            on_loan = Boolean()
            tubes = Integer()
            used_up = Boolean()
            storage = Text()

        class DNASequence(Record):
            bold_barcode_id = Text()
            molecule_type = Text()
            genbank_accession_number = Text()
            gene_sequence = Text()
            total_residues = Integer()
            comp_a = Integer()
            comp_c = Integer()
            comp_g = Integer()
            comp_t = Integer()
            ambiguous_residues = Integer()
            sequenced_by = Link(KUFish.Agent)
