from specify.schema.conversion import  Record, Schema, source_table, Enum, Tree, outerjoin

class KUFish(Schema):

    @source_table("agent")
    class Agent(Record):
        agent_type = Enum('AgentType', 'Organization Person Other Group')
        title = 'Title'
        job_title = 'JobTitle'
        last_name = 'LastName'
        first_name = 'FirstName'
        middle_initial = 'MiddleInitial'
        abbreviation = 'Abbreviation'
        email = 'Email'
        url = 'URL'

        @source_table("address", order_by="Ordinal")
        class Address(Record):
            _parent_field = "AgentID"
            is_current = "IsCurrent"
            address1 = "Address"
            address2 = "Address2"
            city = "City"
            state = "State"
            country = "Country"
            postal_code = "PostalCode"
            room_building = "RoomOrBuilding"
            phone1 = "Phone1"
            phone2 = "Phone2"
            fax = "Fax"

    @source_table("taxon")
    class Taxon(Tree):
        common_name = "CommonName"
        source = "Source"
        protected_status = "EnvironmentalProtectionStatus"
        author = "Author"
        accepted = "AcceptedID"

    @source_table("referencework")
    class ReferenceWork(Record):
        type_of_work = Enum("ReferenceWorkType", 'Book ElectronicMedia Paper TechnicalReport Thesis SectionInBook'),
        title = "Title"
        publisher = "Publisher"
        place_of_publication = "PlaceOfPublication"
        volume = "Volume"
        pages = "Pages"
        date_of_work = "WorkDate"
        url = "URL"
        journal = "JournalID"

        @source_table("author", order_by="OrderNumber")
        class Author(Record):
            _parent_field = "ReferenceWorkID"
            agent = "AgentID"

    @source_table("journal")
    class Journal(Record):
        name = "JournalName"
        abbreviation = "JournalAbbreviation"

    @source_table("accession")
    class Accession(Record):
        accession_number = "AccessionNumber"
        status = "Status"
        accession_type = "Type"
        accession_date = "DateAccessioned"
        received_date = "DateReceived"
        number_of_lots = "Number1"
        number_of_specimens = "Numeber2"
        description = "Text1"

        @source_table("accessionagent")
        class AccessionAgent(Record):
            _parent_field = "AccessionID"
            agent = "AgentID"
            role = "Role"

    @source_table("geography")
    class Geography(Tree):
        accepted = "AcceptedID"

    @source_table("locality")
    class Locality(Record):
        name = "LocalityName"
        geography = "GeographyID"
        water_type = "ElevationMethod"
        # section = outerjoin("localitydetail").field("Section")
        # township = outerjoin("localitydetail")
        # range = Field(text)
        # island = Field(text)
        # island_group = Field(text)
        # water_body = Field(text)
        # drainage = Field(text)

    @source_table("collectingevent")
    class CollectingEvent(Record):
        field_number = "StationFieldNumber"
        collecting_date = "StartDate"
        gear = "Method"
        locality = "LocalityID"
        trip = "CollectingTripID"

        @source_table("collector", order_by="OrderNumber")
        class Collector(Record):
            _parent_field = "CollectingEventID"
            agent = "AgentID"

    @source_table("collectingtrip")
    class CollectingTrip(Record):
        vessel = "CollectingTripName"
        cruise = "StartDateVerbatim"
        haul = "EndDateVerbatim"

class KUFishVoucher(Schema):

    @source_table("collectionobject", where=lambda table: table.collection_id == 4)
    class CollectionObject(Record):
        catalog_number = "CatalogNumber"
        cataloged_date = "CatalogedDate"
        size = outerjoin("collectionobjectattribute", "Text11")
        sex = outerjoin("collectionobjectattribute", "Text8")
        weight = outerjoin("collectionobjectattribute", "Text2")
        cataloger = "CatalogerID"
        accession = "AccessionID"
        collecting_event = "CollectingEventID"

        @source_table("determination")
        class Determination(Record):
            _parent_field = "CollectionObjectID"
            determiner = "DeterminerID"
            determination_date = "DeterminedDate"
            type_status = "TypeStatusName"
            taxon = "AcceptedID"

        @source_table("preparation")
        class Preparation(Record):
            _parant_field = "CollectionObjectID"
            preparer = "PreparedByID"
            prep_date = "PreparedDate"
            prep_type = "PrepTypeID"
            count = "CountAmount"

class KUFishTissue(Schema):

    @source_table("collectionobject", where=lambda table: table.collection_id == 32768)
    class CollectionObject(Record):
        catalog_number = "CatalogNumber"
        cataloged_date = "CatalogedDate"
        preservation = outerjoin("collectionobjectattribute", "Text10")
        tissue_type = outerjoin("collectionobjectattribute", "Text12")
        size = outerjoin("collectionobjectattribute", "Text11")
        sex = outerjoin("collectionobjectattribute", "Text8")
        cataloger = "CatalogerID"
        accession = "AccessionID"
        collecting_event = "CollectingEventID"
        #voucher = outerjoin("collectionreltype")

        @source_table("determination")
        class Determination(Record):
            _parent_field = "CollectionObjectID"
            determiner = "DeterminerID"
            determination_date = "DeterminedDate"
            type_status = "TypeStatusName"
            taxon = "AcceptedID"

        @source_table("preparation")
        class Preparation(Record):
            _parent_field = "CollectionObjectID"
            preparer = "PreparedByID"
            prep_date = "PreparedDate"
            prep_type = "PrepTypeID"
            count = "CountAmount"
            tubes = "Number1"
            used_up = "YesNo1"
            storage = "Text1"

        @source_table("dnasequence")
        class DNASequence(Record):
            _parent_field = "CollectionObjectID"
            bold_barcode_id = "BOLDBarcodeID"
            molecule_type = "MoleculeType"
            genbank_accession_number = "GenBankAccessionNumber"
            gene_sequence = "GeneSequence"
            total_residues = "TotalResidues"
            comp_a = "CompA"
            comp_c = "CompC"
            comp_g = "CompG"
            comp_t = "CompT"
            ambiguous_residues = "AmbiguousResidues"
            sequenced_by = "AgentID"
