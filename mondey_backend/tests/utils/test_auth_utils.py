from mondey_backend.users import is_test_account_user


# It would probably be better to use the User class, and add the email field to it, than to use a mock user
class MockUser:
    def __init__(self, email, **kwargs):
        self.email = email
        for key, value in kwargs.items():
            setattr(self, key, value)

def test_is_test_account():
    tester_email = '123tester@testaccount.com'
    nontester_email = 'heidelberguser@uni-heidelberg.de'
    nontester_email_2 = 'Contester@gmail.com'

    assert is_test_account_user(MockUser(email=tester_email))
    assert False == is_test_account_user(MockUser(email=nontester_email))
    assert False == is_test_account_user(MockUser(email=nontester_email_2))

    try:
        assert False == is_test_account_user() # When no email is present
    except TypeError:
        pass # expected
    # any other exception will cause the test to fail.
