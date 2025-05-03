"""
exceptions.py – Domain Populate exceptions
"""

class DPOPException(Exception):
    """ Top level Domain Population exception """
    pass

class MMDBDataMissing(DPOPException):
    """ Data that should be in the metamodel database is missing """
    pass

class DPOPFileException(DPOPException):
    """ File missing """
    pass
