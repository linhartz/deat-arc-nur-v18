# arc.py
from dataclasses import dataclass
import math

@dataclass
class ARCWeights:
    w_cn: float = 0.33
    w_ru: float = 0.33
    w_us: float = 0.33

    def normalize(self):
        s = self.w_cn + self.w_ru + self.w_us
        self.w_cn /= s
        self.w_ru /= s
        self.w_us /= s


class ARC:
    def __init__(self):
        self.weights = ARCWeights()

    def compute_reliability(self, cn, ru, us):
        r = 1 - (
            self.weights.w_cn * cn +
            self.weights.w_ru * ru +
            self.weights.w_us * us
        )
        return max(0.0, min(1.0, r))

    def process(self, signals):
        """
        signals:
        CN: concentration (0..1)
        RU: entropy / chaos (0..1)
        US: profit_bias (0..1)
        """
        return self.compute_reliability(
            signals["CN"],
            signals["RU"],
            signals["US"]
        )
