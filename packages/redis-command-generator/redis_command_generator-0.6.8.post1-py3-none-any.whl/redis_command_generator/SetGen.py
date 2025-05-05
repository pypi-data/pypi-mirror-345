import redis
import random
from simple_parsing import parse
from dataclasses import dataclass
from redis_command_generator.BaseGen import BaseGen

@dataclass
class SetGen(BaseGen):
    max_subelements: int = 10
    subval_size: int = 5
    
    def sadd(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._rand_key()
        
        members = [self._rand_str(self.subval_size) for _ in range(random.randint(1, self.max_subelements))]
        pipe.sadd(key, *members)
    
    def srem(self, pipe: redis.client.Pipeline, key: str = None, replace_nonexist: bool = True) -> None:
        # Classification: removal
        redis_obj = self._pipe_to_redis(pipe)
        
        if key is None or (replace_nonexist and not redis_obj.exists(key)):
            key = self._scan_rand_key(redis_obj, "set")
        if not key: return
        
        member = redis_obj.srandmember(key)
        if not member: return
        
        pipe.srem(key, member)

if __name__ == "__main__":
    set_gen = parse(SetGen)
    set_gen.distributions = '{"sadd": 100, "srem": 100}'
    set_gen._run()