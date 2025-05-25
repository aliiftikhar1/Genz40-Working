from django.contrib.auth.tokens import PasswordResetTokenGenerator

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        """
        Generates a hash value based on user ID, timestamp, and activation status.
        Ensures token invalidation if user is activated.
        """
        return str(user.pk) + str(timestamp) + str(user.is_active)

# Create an instance of the token generator
account_activation_token = AccountActivationTokenGenerator()

