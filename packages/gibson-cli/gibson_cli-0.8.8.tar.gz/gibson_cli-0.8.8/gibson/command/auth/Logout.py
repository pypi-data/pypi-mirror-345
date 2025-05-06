from gibson.command.BaseCommand import BaseCommand


class Logout(BaseCommand):
    def execute(self):
        self.configuration.set_auth_tokens(None, None)
        self.conversation.type("You are now logged out.")
        self.conversation.newline()
