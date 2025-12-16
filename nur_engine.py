# nur_engine.py
import math

class NUREngine:
    """
    NUR = schopnost jednotlivce přežít a rozhodovat klidně
    i při extrémních kombinacích CN–RU–US + CR
    """

    def compute_base_stability(self, assets):
        """
        assets = dict of stabilizační hodnoty
        """
        weights = {
            "real_estate": 0.35,
            "cash": 0.20,
            "bank": 0.15,
            "funds": 0.10,
            "stocks": 0.10,
            "gold": 0.10
        }

        score = 0.0
        for k, w in weights.items():
            score += w * math.log1p(assets.get(k, 0))

        return score

    def compute_air(self, air):
        """
        AIR = aktivní individuální rozvoj
        """
        skill = air.get("skills", 0)
        tech = air.get("tech", 0)
        adaptability = air.get("adaptability", 0)

        return (skill * 0.4 + tech * 0.4 + adaptability * 0.2)

    def stabilize(
        self,
        arc_reliability,
        chaotic_risk,
        assets,
        air=None,
        rsz=None
    ):
        base = self.compute_base_stability(assets)
        air_score = self.compute_air(air or {})

        rsz_damp = 1.0
        if rsz:
            rsz_damp = 1.2 - min(1.0, rsz.get("stability", 0)) * 0.5

        # CR působí destruktivně
        stress = chaotic_risk * (1 - arc_reliability)

        nur_raw = (base + air_score) * arc_reliability * rsz_damp
        nur_final = max(0.0, nur_raw - stress)

        return {
            "nur_score": round(nur_final, 6),
            "stress": round(stress, 6),
            "arc_reliability": round(arc_reliability, 6),
            "survival": nur_final > 0.5
        }
