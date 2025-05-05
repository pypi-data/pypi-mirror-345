import redis
import random
from simple_parsing import parse
from dataclasses import dataclass
from redis_command_generator.BaseGen import BaseGen

geo_long_min: float = -180
geo_long_max: float = 180
geo_lat_min : float = -85.05112878
geo_lat_max : float = 85.05112878

@dataclass
class GeoGen(BaseGen):
    max_subelements: int = 10
    subval_size: int = 5
    
    def geoadd(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._rand_key()
        
        members = []
        for _ in range(random.randint(1, self.max_subelements)):
            members += [random.uniform(geo_long_min, geo_long_max), random.uniform(geo_lat_min, geo_lat_max), self._rand_str(self.subval_size)]
        pipe.geoadd(key, members)
    
    def geodel(self, pipe: redis.client.Pipeline, key: str = None, replace_nonexist: bool = True) -> None:
        # Classification: removal
        redis_obj = self._pipe_to_redis(pipe)
        
        if key is None or (replace_nonexist and not redis_obj.exists(key)):
            key = self._scan_rand_key(redis_obj, "geo")
        if not key: return
        
        members = [self._rand_str(self.subval_size) for _ in range(random.randint(1, self.max_subelements))]
        pipe.zrem(key, *members)

if __name__ == "__main__":
    geo_gen = parse(GeoGen)
    geo_gen.distributions = '{"geoadd": 100, "geodel": 100}'
    geo_gen._run()
