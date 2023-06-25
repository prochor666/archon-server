from archon import config as configurator, db

class QBus():

    def __init__(self):
        self._mode = 'initial'
        self._config = configurator.configure()
        self._store = {}

    @property
    def chanells(self) -> dict: 
        return True

    @property
    def unregister(self) -> str: 
        return True

    @property
    def db_client(self):
        return db.connect(self.config['db'][self.config['db_driver']])

    @property
    def store(self) -> dict: 
        return self._store

    @store.setter
    def store(self, key, value): 
        self._store[key] = value

