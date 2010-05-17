import pam

def authenticate(user, password):
    if not user or not password:
        return False
    return pam.authenticate(user, password, service="passwd")
