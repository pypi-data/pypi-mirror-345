import redis
import random
from simple_parsing import parse
from dataclasses import dataclass
from redis_command_generator.BaseGen import BaseGen

@dataclass
class HyperLogLogGen(BaseGen):
    max_subelements: int = 10
    
    def pfadd(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._rand_key()
        
        elements = [self._rand_str(self.def_key_size) for _ in range(random.randint(1, self.max_subelements))]
        pipe.pfadd(key, *elements)
    
    def pfmerge(self, pipe: redis.client.Pipeline, key: str = None, replace_nonexist: bool = True) -> None:
        # Classification: removal
        redis_obj = self._pipe_to_redis(pipe)
        
        if key is None or (replace_nonexist and not redis_obj.exists(key)):
            key = self._scan_rand_key(redis_obj, "hyperloglog")
        if not key: return
        
        source_keys = [self._rand_key() for _ in range(random.randint(1, self.max_subelements))]
        pipe.pfmerge(key, *source_keys)

if __name__ == "__main__":
    hyper_log_log_gen = parse(HyperLogLogGen)
    hyper_log_log_gen.distributions = '{"pfadd": 100, "pfmerge": 100}'
    hyper_log_log_gen._run()
