import __future__
from collections import defaultdict
from pprint import pprint
from typing import Any

features = defaultdict(set)
feature: Any = None
for name in __future__.all_feature_names:
    exec(f'from __future__ import {name}\nfeature = {name}')
    features[feature.mandatory].add(name) # defaultdict is sorted for some reason
pprint(features)
