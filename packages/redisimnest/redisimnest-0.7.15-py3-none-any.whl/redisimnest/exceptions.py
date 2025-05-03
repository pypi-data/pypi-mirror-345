class MissingParameterError(Exception):
    pass

class InvalidPrefixTemplateError(Exception):
    pass

class ParameterValidationError(ValueError): 
    pass

class KeyTypeValidationError(TypeError):
    pass

class MissingEncryptionKeyError(Exception):
    pass

class MissingDependencyError(ImportError):
    pass


class AccessDeniedError(Exception):
    pass