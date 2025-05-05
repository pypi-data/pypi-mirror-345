import redis
import random
from simple_parsing import parse
from dataclasses import dataclass
from redis_command_generator.BaseGen import BaseGen

@dataclass
class ListGen(BaseGen):
    max_subelements: int = 10
    subval_size: int = 5
    
    def lpush(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._rand_key()
        
        items = [self._rand_str(self.subval_size) for _ in range(random.randint(1, self.max_subelements))]
        pipe.lpush(key, *items)
    
    def rpush(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._rand_key()
        
        items = [self._rand_str(self.subval_size) for _ in range(random.randint(1, self.max_subelements))]
        pipe.rpush(key, *items)
    
    def lpop(self, pipe: redis.client.Pipeline, key: str = None, replace_nonexist: bool = True) -> None:
        # Classification: removal
        redis_obj = self._pipe_to_redis(pipe)
        
        if key is None or (replace_nonexist and not redis_obj.exists(key)):
            key = self._scan_rand_key(redis_obj, "list")
        if not key: return
        
        pipe.lpop(key)
    
    def rpop(self, pipe: redis.client.Pipeline, key: str = None, replace_nonexist: bool = True) -> None:
        # Classification: removal
        redis_obj = self._pipe_to_redis(pipe)
        
        if key is None or (replace_nonexist and not redis_obj.exists(key)):
            key = self._scan_rand_key(redis_obj, "list")
        if not key: return
        
        pipe.rpop(key)
    
    def lrem(self, pipe: redis.client.Pipeline, key: str = None, replace_nonexist: bool = True) -> None:
        # Classification: removal
        redis_obj = self._pipe_to_redis(pipe)
        
        if key is None or (replace_nonexist and not redis_obj.exists(key)):
            key = self._scan_rand_key(redis_obj, "list")
        if not key: return
        
        list_length = redis_obj.llen(key)
        if not list_length: return
        
        rand_index = random.randint(0, list_length - 1)
        item = redis_obj.lindex(key, rand_index)
        if not item: return
        
        pipe.lrem(key, 0, item)

if __name__ == "__main__":
    list_gen = parse(ListGen)
    list_gen.distributions = '{"lpush": 100, "rpush": 100, "lpop": 100, "rpop": 100, "lrem": 100}'
    list_gen._run()
