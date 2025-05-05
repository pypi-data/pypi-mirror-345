import redis
import random
from simple_parsing import parse
from dataclasses import dataclass
from redis_command_generator.BaseGen import BaseGen

@dataclass
class ZSetGen(BaseGen):
    max_subelements: int = 10
    subval_size: int = 5
    
    def zadd(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._rand_key()
        
        members = {self._rand_str(self.subval_size): random.random() for _ in range(random.randint(1, self.max_subelements))}
        pipe.zadd(key, mapping=members)
    
    def zincrby(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._rand_key()
        
        member = self._rand_str(self.subval_size)
        increment = random.random()
        pipe.zincrby(key, increment, member)
    
    def zrem(self, pipe: redis.client.Pipeline, key: str = None, replace_nonexist: bool = True) -> None:
        # Classification: removal
        redis_obj = self._pipe_to_redis(pipe)
        
        if key is None or (replace_nonexist and not redis_obj.exists(key)):
            key = self._scan_rand_key(redis_obj, "zset")
        if not key: return
        
        members = [self._rand_str(self.subval_size) for _ in range(random.randint(1, self.max_subelements))]
        pipe.zrem(key, *members)

if __name__ == "__main__":
    zset_gen = parse(ZSetGen)
    zset_gen.distributions = '{"zadd": 100, "zincrby": 100, "zrem": 100}'
    zset_gen._run()
