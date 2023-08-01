from archon import config as configurator, db
from archon.mem import Mem

class Boot(Mem):
    def __init__(self):
        self.mem = Mem()
        self._mode = 'initial'
        self._config = configurator.configure()
        self._store = {}

    @property
    def config(self) -> dict: 
        return self._config

    @property
    def db_driver(self) -> str: 
        return self.config['db_driver']

    @property
    def db_client(self):
        return db.connect(self.config['db'][self.config['db_driver']])

    @property
    def db(self):
        return db.init(self.db_client)

    @property
    def mode(self) -> str: 
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value

    @property
    def store(self) -> dict: 
        return self._store

    @store.setter
    def store(self, key, value): 
        self._store[key] = value

