class BaseError(Exception): pass

class ShellCommandError(BaseError): pass

class SendEmailError(BaseError): pass
class SendEmailAuthError(BaseError): pass

class CompilationError(BaseError): pass
class GodboltError(BaseError): pass

class InvalidCommandChannel(BaseError): pass

class UnknownUser(BaseError): pass