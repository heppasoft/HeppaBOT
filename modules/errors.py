class ShellCommandError(Exception): pass

class SendEmailError(Exception): pass
class SendEmailAuthError(Exception): pass

class InvalidCommandChannel(Exception): pass

class UnknownUser(Exception): pass

class CompilationError(Exception): pass
class GodboltError(Exception): pass