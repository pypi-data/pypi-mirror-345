from gibson.command.BaseCommand import BaseCommand


class Login(BaseCommand):
    def execute(self):
        authenticated = self.configuration.login()
        if authenticated:
            self.conversation.message_login_success()
        else:
            self.conversation.message_login_failure()
        self.conversation.newline()
