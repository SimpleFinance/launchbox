class Error(Exception): pass
class RequestError(Error): pass

class NotFoundError(Error): pass
class CookbookTarballNotFoundError(NotFoundError): pass
class CookbookMetadataNotFoundError(NotFoundError): pass
class DependencyNotFoundError(NotFoundError): pass
