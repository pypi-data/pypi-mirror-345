import redis
import random
from simple_parsing import parse
from dataclasses import dataclass
from redis_command_generator.BaseGen import BaseGen

@dataclass
class StringGen(BaseGen):
    subval_size: int = 5
    incrby_min: int = -1000
    incrby_max: int = 1000
    
    def set(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._rand_key()
        
        pipe.set(key, self._rand_str(self.subval_size))
    
    def append(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._rand_key()
        
        pipe.append(key, self._rand_str(self.subval_size))
    
    def incrby(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._rand_key()
        
        pipe.incrby(key, random.randint(self.incrby_min, self.incrby_max))
    
    def delete(self, pipe: redis.client.Pipeline, key: str = None, replace_nonexist: bool = True) -> None:
        # Classification: removal
        redis_obj = self._pipe_to_redis(pipe)
        
        if key is None or (replace_nonexist and not redis_obj.exists(key)):
            key = self._scan_rand_key(redis_obj, "string")
        if not key: return
        
        pipe.delete(key)

if __name__ == "__main__":
    string_gen = parse(StringGen)
    string_gen.distributions = '{"set": 100, "append": 100, "incrby": 100, "delete": 100}'
    string_gen._run()

