from specify.schema.conversion import  Record, SchemaFamily, source_table, Tree, skip
from specify.schema.conversion_field_types import Enum, Column, ForeignKey, ReverseJoin
from specify.schema.tree_conversion import Sp6Tree

schema_family = SchemaFamily()
Schema = schema_family.Schema

def to_int(value):
    return int(value) if value is not None else None

class KUFish(Schema):

    @source_table("agent")
    class Agent(Record):
        agent_type = Enum("AgentType", "Organization Person Other Group")
        title = Column("Title")
        job_title = Column("JobTitle")
        last_name = Column("LastName")
        first_name = Column("FirstName")
        middle_initial = Column("MiddleInitial")
        abbreviation = Column("Abbreviation")
        email = Column("Email")
        url = Column("URL")

        @source_table("address", order_by="Ordinal", parent_field="AgentID")
        class Address(Record):
            is_current = Column("IsCurrent")
            address1 = Column("Address")
            address2 = Column("Address2")
            city = Column("City")
            state = Column("State")
            country = Column("Country")
            postal_code = Column("PostalCode")
            room_building = Column("RoomOrBuilding")
            phone1 = Column("Phone1")
            phone2 = Column("Phone2")
            fax = Column("Fax")

    @source_table("taxon")
    class Taxon( Sp6Tree(treedef_table="taxontreedef", treedef_id=1) ):
        common_name = Column("CommonName")
        source = Column("Source")
        protected_status = Column("EnvironmentalProtectionStatus")
        author = Column("Author")
        accepted = ForeignKey("AcceptedID")

    @source_table("referencework")
    class ReferenceWork(Record):
        type_of_work = Enum("ReferenceWorkType", 'Book ElectronicMedia Paper TechnicalReport Thesis SectionInBook'),
        title = Column("Title")
        publisher = Column("Publisher")
        place_of_publication = Column("PlaceOfPublication")
        volume = Column("Volume")
        pages = Column("Pages")
        date_of_work = Column("WorkDate")
        url = Column("URL")
        journal = ForeignKey("JournalID")

        @source_table("author", order_by="OrderNumber", parent_field="ReferenceWorkID")
        class Author(Record):
            agent = ForeignKey("AgentID")

    @source_table("journal")
    class Journal(Record):
        name = Column("JournalName")
        abbreviation = Column("JournalAbbreviation")

    @source_table("accession")
    class Accession(Record):
        accession_number = Column("AccessionNumber")
        status = Column("Status")
        accession_type = Column("Type")
        accession_date = Column("DateAccessioned")
        received_date = Column("DateReceived")
        number_of_lots = Column("Number1", process=to_int)
        number_of_specimens = Column("Number2", process=to_int)
        description = Column("Text1")

        @source_table("accessionagent", parent_field="AccessionID")
        class AccessionAgent(Record):
            agent = ForeignKey("AgentID")
            role = Column("Role")

    @source_table("geography")
    class Geography(Tree):
        accepted = ForeignKey("AcceptedID")

    @source_table("locality")
    class Locality(Record):
        name = Column("LocalityName")
        geography = ForeignKey("GeographyID")
        water_type = Column("ElevationMethod")

        locality_detail = ReverseJoin('localitydetail', "LocalityID")

        section = Column([locality_detail, "Section"])
        township = Column([locality_detail, "Township"])
        range = Column([locality_detail, "RangeDesc"])
        island = Column([locality_detail, "Island"])
        island_group = Column([locality_detail, "IslandGroup"])
        water_body = Column([locality_detail, "WaterBody"])
        drainage = Column([locality_detail, "Drainage"])

    @source_table("collectingevent")
    class CollectingEvent(Record):
        field_number = Column("StationFieldNumber")
        collecting_date = Column("StartDate")
        gear = Column("Method")
        locality = ForeignKey("LocalityID")
        trip = ForeignKey("CollectingTripID")

        @source_table("collector", order_by="OrderNumber", parent_field="CollectingEventID")
        class Collector(Record):
            agent = ForeignKey("AgentID")

    @source_table("collectingtrip")
    class CollectingTrip(Record):
        vessel = Column("CollectingTripName")
        cruise = Column("StartDateVerbatim")
        haul = Column("EndDateVerbatim")

class KUFishVoucher(Schema):

    @source_table("collectionobject", where=lambda table: table.c.CollectionID == 4)
    class CollectionObject(Record):
        catalog_number = Column("CatalogNumber")
        cataloged_date = Column("CatalogedDate")
        size = Column(["CollectionObjectAttributeID", "Text11"])
        sex = Column(["CollectionObjectAttributeID", "Text8"])
        weight = Column(["CollectionObjectAttributeID", "Text2"])
        cataloger = ForeignKey("CatalogerID")
        accession = ForeignKey("AccessionID")
        collecting_event = ForeignKey("CollectingEventID")

        @source_table("determination", parent_field="CollectionObjectID")
        class Determination(Record):
            determiner = ForeignKey("DeterminerID")
            determination_date = Column("DeterminedDate")
            type_status = Column("TypeStatusName")
            taxon = ForeignKey("TaxonID")

        @source_table("preparation", parent_field="CollectionObjectID")
        class Preparation(Record):
            preparer = ForeignKey("PreparedByID")
            prep_date = Column("PreparedDate")
            prep_type = Column(["PrepTypeID", "Name"])
            count = Column("CountAmt")

class KUFishTissue(Schema):

    @source_table("collectionobject", where=lambda table: table.c.CollectionID == 32768)
    class CollectionObject(Record):
        catalog_number = Column("CatalogNumber")
        cataloged_date = Column("CatalogedDate")
        preservation = Column(["CollectionObjectAttributeID", "Text10"])
        tissue_type = Column(["CollectionObjectAttributeID", "Text12"])
        size = Column(["CollectionObjectAttributeID", "Text11"])
        sex = Column(["CollectionObjectAttributeID", "Text8"])
        cataloger = ForeignKey("CatalogerID")
        accession = ForeignKey("AccessionID")
        collecting_event = ForeignKey("CollectingEventID")
        #voucher = Column("collectionreltype")

        @source_table("determination", parent_field="CollectionObjectID")
        class Determination(Record):
            determiner = ForeignKey("DeterminerID")
            determination_date = Column("DeterminedDate")
            type_status = Column("TypeStatusName")
            taxon = ForeignKey("TaxonID")

        @source_table("preparation", parent_field="CollectionObjectID")
        class Preparation(Record):
            preparer = ForeignKey("PreparedByID")
            prep_date = Column("PreparedDate")
            prep_type = Column(["PrepTypeID", "Name"])
            count = Column("CountAmt")
            tubes = Column("Number1", process=to_int)
            used_up = Column("YesNo1")
            storage = Column("Text1")

        @source_table("dnasequence", parent_field="CollectionObjectID")
        class DNASequence(Record):
            bold_barcode_id = Column("BOLDBarcodeID")
            molecule_type = Column("MoleculeType")
            genbank_accession_number = Column("GenBankAccessionNumber")
            gene_sequence = Column("GeneSequence")
            total_residues = Column("TotalResidues")
            comp_a = Column("CompA")
            comp_c = Column("CompC")
            comp_g = Column("CompG")
            comp_t = Column("compT")
            ambiguous_residues = Column("AmbiguousResidues")
            sequenced_by = ForeignKey("AgentID")
