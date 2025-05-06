from ..storage import storage_login


def login(ak, sk):

    data = storage_login.login(ak, sk)

    return data.get("token")
