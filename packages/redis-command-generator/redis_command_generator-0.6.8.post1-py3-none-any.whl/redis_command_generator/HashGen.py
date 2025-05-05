import redis
import random
from simple_parsing import parse
from dataclasses import dataclass
from redis_command_generator.BaseGen import BaseGen

@dataclass
class HashGen(BaseGen):
    max_subelements: int = 10
    subkey_size: int = 5
    subval_size: int = 5
    incrby_min: int = -1000
    incrby_max: int = 1000
    
    def hset(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._rand_key()
        
        fields = {self._rand_str(self.subkey_size): self._rand_str(self.subval_size) for _ in range(random.randint(1, self.max_subelements))}
        pipe.hset(key, mapping=fields)
    
    def hincrby(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._rand_key()
        
        field = self._rand_str(self.def_key_size)
        increment = random.randint(self.incrby_min, self.incrby_max)
        pipe.hincrby(key, field, increment)
    
    def hdel(self, pipe: redis.client.Pipeline, key: str = None, replace_nonexist: bool = True) -> None:
        # Classification: removal
        redis_obj = self._pipe_to_redis(pipe)
        
        if key is None or (replace_nonexist and not redis_obj.exists(key)):
            key = self._scan_rand_key(redis_obj, "hash")
        if not key: return
        
        fields = [self._rand_str(self.subkey_size) for _ in range(random.randint(1, self.max_subelements))]
        pipe.hdel(key, *fields)

if __name__ == "__main__":
    hash_gen = parse(HashGen)
    hash_gen.distributions = '{"hset": 100, "hincrby": 100, "hdel": 100}'
    hash_gen._run()
