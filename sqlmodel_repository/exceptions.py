class RepositoryException(Exception):
    """Base exception for all repository exceptions"""


class EntityNotFoundException(RepositoryException):
    """Exception raised when an entity is not found"""


class CouldNotCreateEntityException(RepositoryException):
    """Exception raised when an entity could not be created"""


class CouldNotDeleteEntityException(RepositoryException):
    """Exception raised when an entity could not be deleted"""


class EntityDoesNotPossessAttributeException(RepositoryException):
    """Exception raised when an entity does not possess an attribute"""
