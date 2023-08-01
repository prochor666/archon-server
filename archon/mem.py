class Mem():
    def __init__(self):
        self.mem = {}
    
    def r(self, key: str = '', value: dict | str | list = ''):
        if type(key) is str and len(key) > 0:
            if type(value) is not None:
                self.mem[key] = value
            return self.mem[key]
        return None

    def a(self):
        return self.mem;

    def remove(self, key: str = 'key'):
        if type(key) is str and len(key) > 0 and key in self.mem:
            del self.mem[key]
            return True
        return False