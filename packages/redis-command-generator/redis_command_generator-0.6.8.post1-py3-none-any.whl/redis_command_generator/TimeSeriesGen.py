import redis
import sys
import random
from simple_parsing import parse
from dataclasses import dataclass
from redis_command_generator.BaseGen import BaseGen

@dataclass
class TimeSeriesGen(BaseGen):
    max_actions: int = 5
    max_float = sys.maxsize
    timestamp = int(random.uniform(0, 1000000))
    labels_dict = {
        "furniture": ["chair", "table", "desk", "mouse", "keyboard", "monitor", "printer", "scanner"],
        "fruits": ["apple", "banana", "orange", "grape", "mango"],
        "animals": ["dog", "cat", "elephant", "lion", "tiger"]
    }
    def tscreate(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: addition
        if key is None:
            key = self._rand_key()

        key = "ts-" + key
        pipe.ts().create(key)

    def tsadd(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: addition

        if key is None:
            key = self._rand_key()
        key = "ts-" + key

        timestamp = int(random.uniform(0, 1000000))  # Generate a random timestamp

        for _ in range(random.randint(2, self.max_actions)):
            self.timestamp += 1
            value = random.uniform(1, self.max_float)  # Generate a random float value
            pipe.ts().add(key=key, timestamp=self.timestamp, value=value, duplicate_policy="last")

    def tsalter (self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: alteration
        redis_obj = self._pipe_to_redis(pipe)

        if key is None or not redis_obj.exists(key):
            key = self._scan_rand_key(redis_obj, "TSDB-TYPE")
        if not key: return

        laebl1 = random.choice(list(self.labels_dict.keys()))
        label2 = random.choice(list(label for label in self.labels_dict.keys() if label != laebl1))
        label3 = random.choice(list(label for label in self.labels_dict.keys() if label not in [laebl1, label2]))
        # Generate a random label value
        label1_value = random.choice(self.labels_dict[laebl1])
        label2_value = random.choice(self.labels_dict[label2])
        label3_value = random.choice(self.labels_dict[label3])

        pipe.ts().alter(key, retention_msecs=random.randint(1000,100000), labels={laebl1: label1_value, label2: label2_value, label3: label3_value})

    def tsqueryindex(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: retrieval
        redis_obj = self._pipe_to_redis(pipe)

        label = random.choice(list(self.labels_dict.keys()))
        label_value = random.choice(self.labels_dict[label])

        pipe.ts().queryindex([f"{label}={label_value}"])

    def tsmget(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: retrieval
        redis_obj = self._pipe_to_redis(pipe)
        filter = self._generate_filter()

        # Geneerate the rest of the optional options
        latest = random.choice([True,False])
        withlabels = random.choice([True,False])
        select_labels = [random.choice(list(self.labels_dict.keys()))] if not withlabels else None

        pipe.ts().mget(filters = filter, latest=latest, with_labels=withlabels, select_labels=select_labels)

    def tsmrange_tsmrevrange(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: range-query
        redis_obj = self._pipe_to_redis(pipe)

        # Generate random filters
        filter = self._generate_filter()

        # Generate random timestamps for the range
        from_timestamp = random.randint(0, 500000)
        to_timestamp = random.randint(from_timestamp, 1000000)

        # Optional parameters
        aggregation_type = random.choice(["avg", "sum", "min", "max", None])
        bucket_size_msec = random.randint(1000, 10000) if aggregation_type else None
        count = random.randint(1, 100) if random.choice([True, False]) else None
        with_labels = random.choice([True, False])
        group_by = random.choice(random.choice(list(self.labels_dict.keys()))) if random.choice([True, False]) else None
        latest = random.choice([True, False])

        # Choose to run tsmrange or tsrevrange
        mrange_or_revrange = random.choice(["mrange", "mrevrange"])

        # Execute the command
        if mrange_or_revrange == "mrange":
            pipe.ts().mrange(from_time = from_timestamp, to_time= to_timestamp, aggregation_type = aggregation_type,
                         bucket_size_msec = bucket_size_msec, count = count, with_labels = with_labels, filters = filter
                         , groupby = group_by, latest = latest)
        else:
            pipe.ts().mrevrange(from_time = from_timestamp, to_time= to_timestamp, aggregation_type = aggregation_type,
                         bucket_size_msec = bucket_size_msec, count = count, with_labels = with_labels, filters = filter
                         , groupby = group_by, latest = latest)

    def tsdel(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: removal-value
        redis_obj = self._pipe_to_redis(pipe)

        if key is None or not redis_obj.exists(key):
            key = self._scan_rand_key(redis_obj, "TSDB-TYPE")
        if not key: return

        pipe.ts().delete(key, 0, int(1e12))

    def tsdelkey(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: removal-key
        redis_obj = self._pipe_to_redis(pipe)

        if key is None or not redis_obj.exists(key):
            key = self._scan_rand_key(redis_obj, "TSDB-TYPE")
        if not key: return

        pipe.delete(key)

    def _generate_filter(self):
        filter = []

        # Choosing a filter (label!=, label=value, label=(value1, value2), label=, label!=value, label!=(value1,value2))
        matcher_label = random.choice(list(self.labels_dict.keys()))
        filter.append(f"{matcher_label}={random.choice(self.labels_dict[matcher_label])}")

        filter_label = random.choice([label for label in self.labels_dict.keys() if label != matcher_label])
        value_filter_label_1 = random.choice(self.labels_dict[filter_label])
        value_filter_label_2 = random.choice(
            [value for value in self.labels_dict[filter_label] if value != value_filter_label_1] + [None]
        )
        filter_label2 = random.choice([label for label in self.labels_dict.keys() if label not in {matcher_label, filter_label}])
        value_filter_label2_1= random.choice(self.labels_dict[filter_label2] + [None]) if filter_label2 else None
        equal_filter_2 = random.choice(["=", "!="])


        if value_filter_label_2:
                filter.append(f"{filter_label}=({value_filter_label_1},{value_filter_label_2})")
        else:
                filter.append(f"{filter_label}={value_filter_label_1}")

        if filter_label2:
            if value_filter_label2_1:
                filter.append(f"{filter_label2}{equal_filter_2}{value_filter_label2_1}")
            else:
                filter.append(f"{filter_label2}{equal_filter_2}")

        return filter


if __name__ == "__main__":
    ts_gen = parse(TimeSeriesGen)
    ts_gen.distributions = '{"tscreate":100, "tsadd": 100, "tsdel": 100, "tsalter":100, "tsqueryindex":100, "tsmget":100, "tsmrange_tsmrevrange":100}'
    ts_gen._run()