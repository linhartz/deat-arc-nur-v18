-- stats_schema.sql

-- Průměrné NUR skóre při vysokém CR
SELECT AVG(nur_score)
FROM experiments
WHERE chaotic_risk > 0.7;

-- Míra přežití při vysokém chaosu
SELECT AVG(survival)
FROM experiments
WHERE chaotic_risk > 0.7;

-- Rozptyl NUR vs ARC reliability
SELECT arc_reliability, AVG(nur_score)
FROM experiments
GROUP BY arc_reliability;
