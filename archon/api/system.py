from archon.system import device

def _system(data_pass: dict = {}) -> dict:
    return device.sys_info()


def _network(data_pass: dict = {}) -> dict:
    return device.network_info()


def _cpu(data_pass: dict = {}) -> dict:
    return device.cpu_info()


def _memory(data_pass: dict = {}) -> dict:
    return device.memory_info()


def _disk(data_pass: dict = {}) -> dict:
    return device.disk_info()
