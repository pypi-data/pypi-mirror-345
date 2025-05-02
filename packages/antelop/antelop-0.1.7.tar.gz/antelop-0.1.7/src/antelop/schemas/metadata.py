import datajoint as dj


def schema(conn, classes):
    schema = dj.Schema(
        schema_name="antelop_metadata", connection=conn, create_tables=True
    )

    @schema
    class Experimenter(classes["lookup"]):
        definition = """
		# Researchers using this database
		experimenter : varchar(40) # Experimenter username
		---
		full_name : varchar(40) # Full name
		group : varchar(40) # Research group/lab
		institution : varchar(40) # Research institution
		admin : enum('False', 'True') # Admin privileges
		"""

    @schema
    class Experiment(classes["manual"]):
        definition = """
		# A cohesive collection of animals and recordings operating under the same paradigm
		-> Experimenter
		experiment_id : smallint # Unique experiment ID (auto_increment)
		---
		experiment_name : varchar(40) # Short experiment description
		experiment_notes : varchar(1000) # Optional experiment annotations
		experiment_deleted = 'False' : enum('False', 'True') # Implements a temporary delete function
		"""

    @schema
    class Animal(classes["manual"]):
        definition = """
		# Animal with genetic information and other metadata
		-> Experiment
		animal_id : int # Unique mouse ID (auto_increment)
		---
		age = NULL : varchar(20) # Age of the animal in ISO 8601 duration format
		age_reference = NULL : enum('birth', 'gestational') # Reference point for the age
		genotype = NULL : varchar(100) # Mouse genotype
		sex = 'U' : enum('M', 'F', 'U', 'O') # Sex of the animal
		species : varchar(40) # Species of the animal
		weight = NULL : varchar(40) # Weight of the animal including units
		animal_name : varchar(40) # Unique animal name
		animal_notes : varchar(1000) # Optional mouse annotations
		animal_deleted = 'False' : enum('False', 'True') # Implements a temporary delete function
		"""

    @schema
    class Session(classes["manual"]):
        definition = """
		# Represents a single recording session
		-> Experiment
		session_id : int # Unique session ID (auto_increment)
		---
		session_name : varchar(40) # Short session description
		session_timestamp : timestamp # Date and time of start of session (YYYY-MM-DD HH:MM:SS)
		session_duration = NULL : int # Duration of the session in seconds
		session_notes : varchar(1000) # Optional session annotations
		session_deleted = 'False' : enum('False', 'True') # Implements a temporary delete function
		"""

    tables = {
        "Experimenter": Experimenter,
        "Experiment": Experiment,
        "Animal": Animal,
        "Session": Session,
    }

    return tables, schema
