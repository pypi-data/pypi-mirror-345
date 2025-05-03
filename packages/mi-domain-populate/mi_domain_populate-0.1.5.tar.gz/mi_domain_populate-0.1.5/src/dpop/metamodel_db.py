""" metamodel_db.py -- Loads a metamodel database populated with a system of one or more modeled domains """

# System
import logging
from pathlib import Path
from contextlib import redirect_stdout

# Model Integration
from pyral.database import Database
from pyral.relvar import Relvar

# Model Execution
from dpop.db_names import mmdb

_logger = logging.getLogger(__name__)

class MetamodelDB:

    filename = None

    @classmethod
    def load(cls, mmdb_path: Path):
        """ Let's load and print out the metamodel database """

        cls.filename = mmdb_path

        _logger.info(f"Loading the metamodel database from: [{mmdb_path}]")
        Database.open_session(name=mmdb)
        Database.load(db=mmdb, fname=str(mmdb_path))

    @classmethod
    def print(cls):
        """
        Print out the populated metamodel
        """
        with open("mmdb.txt", 'w') as f:
            with redirect_stdout(f):
                Relvar.printall(db=mmdb)

    @classmethod
    def display(cls):
        # Print out the populated metamodel
        msg = f"Metamodel populated from {cls.filename}"
        print(f"\n*** {msg} ***")
        Relvar.printall(db=mmdb)
        print(f"\n^^^ {msg} ^^^\n")
