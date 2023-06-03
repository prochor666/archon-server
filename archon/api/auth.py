from archon.models.users import users


def _soft_recovery(data_pass: dict = {}) -> dict:
    return users.recover(data_pass, True)


def _full_recovery(data_pass: dict = {}) -> dict:
    return users.recover(data_pass, False)


def _login(data_pass: dict = {}) -> dict:
    return {'status': True, 'message': "Logged in"}
