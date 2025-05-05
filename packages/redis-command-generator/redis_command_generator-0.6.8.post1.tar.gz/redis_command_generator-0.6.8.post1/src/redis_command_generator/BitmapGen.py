import redis
import random
from simple_parsing import parse
from dataclasses import dataclass
from redis_command_generator.BaseGen import BaseGen

@dataclass
class BitmapGen(BaseGen):
    max_subelements: int = 1000
    
    def setbit(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._rand_key()
        
        offset = random.randint(0, self.max_subelements)
        value = random.randint(0, 1)
        pipe.setbit(key, offset, value)
    
    def getbit(self, pipe: redis.client.Pipeline, key: str = None, replace_nonexist: bool = True) -> None:
        # Classification: observational
        redis_obj = self._pipe_to_redis(pipe)
        
        if key is None or (replace_nonexist and not redis_obj.exists(key)):
            key = self._scan_rand_key(redis_obj, "bitmap")
        if not key: return
        
        offset = random.randint(0, self.max_subelements)
        pipe.getbit(key, offset)

if __name__ == "__main__":
    bitmap_gen = parse(BitmapGen)
    bitmap_gen.distributions = '{"setbit": 100, "getbit": 100}'
    bitmap_gen._run()
