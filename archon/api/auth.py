from archon.models.users import users


def _full_recovery(data_pass: dict = {}) -> dict:
    return users.recover(data_pass, False)


def _recover(data_pass: dict = {}) -> dict:
    return users.recover(unifield = data_pass['login'], http_origin = '', soft = True)


def _activate(data_pass: dict = {}) -> dict:
    return users.activate(data_pass)
