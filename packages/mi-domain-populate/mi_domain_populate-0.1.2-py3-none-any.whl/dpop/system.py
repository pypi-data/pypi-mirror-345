""" System.py -- A Shlaer-Mellor Executable UML System of modeled Domains in a metamodel database """

# System
import logging
from pathlib import Path

# Model Integration
from pyral.relation import Relation

# Domain Populate
from dpop.metamodel_db import MetamodelDB
from dpop.domain_model_db import DomainModelDB
from dpop.db_names import mmdb
from dpop.exceptions import *

_logger = logging.getLogger(__name__)

class System:
    """
    In Shlaer-Mellor Executable UML, a System consists of one or more modeled and non-modeled Domains.

    Here we are focused exclusively on the modeled Domains populated into a metamodel database.

    The System's role here is to output a separate TclRAL database file
    for each domain populated into a metamodel database.
    """

    def __init__(self, mmdb_path: Path, context_path: Path, types_path: Path, output_text: bool,
                 verbose: bool, debug: bool = False):
        """
        Create a domain database for each domain in the populated metamodel and then populate each of these
        domains with instances specified context.

        :param mmdb_path: Path to the populated metamodel *.ral TclRAL
        :param context_path: A *.sip file specifying an instance population for each domain
        :param type_mapping: A *.yaml file specifying a mapping of domain to TclRAL data types
        param verbose: Verbose mode has been set
        :param output_text: If true, each populated domain db is displayed as tables on the console
        :param debug: Debug mode - prints schemas and other info to the console if true
        """
        self.mmdb_path = mmdb_path
        self.context_path = context_path
        self.output_text = output_text
        self.types_path = types_path
        self.verbose = verbose
        self.debug = debug

        # Load a metamodel file populated with a system
        MetamodelDB.load(mmdb_path=self.mmdb_path)
        if self.verbose:
            MetamodelDB.display()
        if self.debug:
            MetamodelDB.print()

        # Set the system name
        # There should be one System instance in the System name from the populated metamodel
        system_r = Relation.restrict(db=mmdb, relation='System')  # System relation with one tuple
        if not system_r.body:
            msg = f"System name not found in the populated metamodel db"
            _logger.exception(msg)
            raise MMDBDataMissing(msg)

        self.name = system_r.body[0]['Name']

        # Create a database schema for each domain
        domain_r = Relation.restrict(db=mmdb, relation='Domain')
        if not domain_r.body:
            msg = f"No domains defined for system in metamodel"
            _logger.exception(msg)
            raise MMDBDataMissing(msg)

        self.domain_dbs = {d['Alias']: DomainModelDB(name=d['Name'], alias=d['Alias'], system=self)
                           for d in domain_r.body}
        pass
        #
        # # Populate each of these schemas with the corresponding *.sip file found in the context_dir
        # cls.system.populate(context_dir=context_dir)
        #
        # # Activate the system (build the dynamic components within)
        # cls.system.activate()
        #
        # # The system is now ready to react to external input
        #
        # # Run the scenario (sequence of interactions)
        # Scenario.run(sys_domains=cls.system.domains)
        # pass

