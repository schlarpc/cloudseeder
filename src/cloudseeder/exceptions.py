class CloudSeederException(Exception):
    pass

class EventSerializationException(CloudSeederException):
    pass

class InvalidReturnTypeException(CloudSeederException):
    pass

class CloudFormationReportingException(CloudSeederException):
    pass

class UnknownResourceTypeException(CloudSeederException):
    pass
