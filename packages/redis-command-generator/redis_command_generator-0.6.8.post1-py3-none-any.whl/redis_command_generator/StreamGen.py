import redis
import random
from simple_parsing import parse
from dataclasses import dataclass
from redis_command_generator.BaseGen import BaseGen

@dataclass
class StreamGen(BaseGen):
    max_subelements: int = 10
    subkey_size: int = 5
    subval_size: int = 5
    
    def xadd(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._rand_key()
        
        fields = {self._rand_str(self.subkey_size): self._rand_str(self.subval_size) for _ in range(random.randint(1, self.max_subelements))}
        pipe.xadd(key, fields)
    
    def xdel(self, pipe: redis.client.Pipeline, key: str = None, replace_nonexist: bool = True) -> None:
        # Classification: removal
        redis_obj = self._pipe_to_redis(pipe)
        
        if key is None or (replace_nonexist and not redis_obj.exists(key)):
            key = self._scan_rand_key(redis_obj, "stream")
        if not key: return
        
        stream_len = random.randint(0, 10)
        if stream_len > 0:
            stream_id = f"{random.randint(1, 1000)}-0"
            pipe.xdel(key, stream_id)

if __name__ == "__main__":
    stream_gen = parse(StreamGen)
    stream_gen.distributions = '{"xadd": 100, "xdel": 100}'
    stream_gen._run()
