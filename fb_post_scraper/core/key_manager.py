from typing import List

class APIKeyManager:
    '''
        The object that manage the keys, increase key if the key doesn't work
    '''

    def __init__(self, keys: List[str]):
        '''
            Params:
                keys (List): list of api keys
        '''

        self.keys = keys
        self.index = 0 # index of the current key
    
    def get(self) -> str:
        '''
            Get the key
        '''

        return self.keys[self.index]
    
    def switch(self) -> str:
        '''
            Increase key and return that key
        '''

        self.index = (self.index + 1) % len(self.keys)

        return self.get()