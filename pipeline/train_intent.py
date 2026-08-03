"""Intent classifier — trained, not hand-written.

Why replace the regex cues:

    The rule-based router scores 33% on realistic paraphrases. It scores well on
    our own question bank because we wrote both the questions and the rules —
    which is a measurement of nothing. A reviewer typing "does vitamin c mess up
    the reading" falls through to GENERAL, evidence routing switches off, and the
    answer quality drops exactly when someone is watching.

Why NOT reach for an LLM here:

    This is a closed intent space with eleven stable classes. That is the textbook
    case for a lightweight classifier: single-digit-millisecond inference, no
    network call, no per-query cost, fully deterministic, and testable. An LLM
    router would add 300ms+, a per-query cost, and non-determinism to a decision a
    linear model makes correctly. Reserve generative capacity for problems that
    actually need dynamic reasoning.

Approach:
    * synthetic training data — templates x corpus entities x paraphrase frames
    * features: word 1-2 grams + character 3-5 grams
      (char n-grams are what buy robustness to typos, plurals and British/US
      spelling without a stemmer)
    * multinomial logistic regression, L2 regularised
    * exported as int8-quantised weights, ~40 KB, run in the browser

Run:  python -m pipeline.train_intent
"""
from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import FeatureUnion

random.seed(17)

# --------------------------------------------------------------------------- slots
PRODUCTS = [
    "StatStrip Glucose meter", "StatSensor Creatinine meter", "Lactate Plus meter",
    "Nova Allegro analyzer", "Stat Profile Prime Plus", "StatStrip Xpress2",
    "BioProfile FLEX2", "Nova Max", "Nova Primary analyzer", "the meter",
    "the analyzer", "the device", "the hospital meter", "the test strip",
]
ANALYTES = [
    "glucose", "lactate", "creatinine", "hematocrit", "ketone", "haemoglobin",
    "sodium", "potassium", "ionised calcium", "ionised magnesium", "bilirubin",
    "pH", "HbA1c", "urine albumin", "UACR", "eGFR", "blood urea nitrogen",
    "PCO2", "PO2", "osmolality",
]
SUBSTANCES = [
    "vitamin C", "ascorbic acid", "acetaminophen", "paracetamol", "uric acid",
    "maltose", "galactose", "bilirubin", "dopamine", "heparin", "icodextrin",
]

# --------------------------------------------------------------------------- templates
# Each intent gets many surface forms, deliberately including casual and
# abbreviated phrasings — that is what real users type and what the regex missed.
TEMPLATES: dict[str, list[str]] = {
    "CLINICAL_SIGNIFICANCE": [
        "what is the clinical significance of {a}", "why is {a} measured",
        "why do clinicians track {a}", "what does {a} tell a doctor",
        "what does an elevated {a} level mean", "clinical utility of {a}",
        "reason for monitoring {a}", "what is {a} used for clinically",
        "why does {a} matter in patient care", "what does {a} indicate",
        "significance of measuring {a}", "why would you test {a}",
        "what condition does {a} point to", "value of measuring {a}",
        "how is {a} interpreted clinically", "purpose of measuring {a}",
        "what do abnormal {a} results signify", "why order a {a} test",
    ],
    "INTENDED_USE": [
        "what is the intended use of {p}", "what is {p} used for",
        "who is {p} meant for", "what population is {p} approved for",
        "indications for use of {p}", "can I use {p} in a hospital",
        "is {p} for clinics or labs", "what settings is {p} designed for",
        "who should use {p}", "what is {p} indicated for",
        "is {p} approved for point of care", "intended purpose of {p}",
        "what patients can {p} be used on", "is {p} for professional use",
    ],
    "INTERFERENCE": [
        "what substances interfere with {a} results", "does {s} affect {a}",
        "will {s} skew {a} readings", "does {s} mess up the {a} reading",
        "anything that throws off {a}", "what compounds distort {a} values",
        "which drugs interfere with {a}", "is {a} affected by {s}",
        "does {s} cause a false {a} result", "interference from {s}",
        "what gives a false high {a}", "cross reactivity with {s}",
        "substances that affect {a} accuracy", "can {s} bias the {a} result",
    ],
    "MECHANISM": [
        "how does the {a} sensor work", "what is the measurement principle for {a}",
        "what chemistry is behind the {a} strip", "explain the {a} sensor technology",
        "what reaction produces the current in the {a} test",
        "inner workings of the {a} biosensor", "how is {a} detected",
        "what methodology does {p} use", "principle of operation for {p}",
        "how does {p} determine {a}", "what enzyme is used for {a}",
        "describe the electrochemistry of the {a} test",
        "on what basis does {p} measure {a}",
    ],
    "CAUSAL": [
        "how does {a} affect {a2} measurement", "what is the effect of {a} on {a2}",
        "if {a} is high what happens to {a2}", "impact of {s} on {a} readings",
        "does temperature change {a} results", "what shifts the {a} value",
        "does {a} influence {a2}", "how does {s} alter {a}",
        "what causes erroneous {a} readings", "why would {a} read low",
        "does altitude change {a} results", "what makes {a} inaccurate",
        "how is {a} impacted by {a2}",
    ],
    "SPECIFICATION": [
        "what is the measurement range for {a}", "what sample volume does {p} need",
        "smallest drop of blood needed for {a}", "upper limit {p} can read",
        "how many seconds for a {a} result", "how long does the {a} test take",
        "storage temperature limits for {p}", "what is the reportable range for {a}",
        "operating temperature of {p}", "shelf life of the {a} strips",
        "precision of the {a} measurement", "accuracy of {p}",
        "what is the detection limit for {a}", "how much sample for {p}",
        "linearity range of the {a} assay",
    ],
    "PROCEDURE": [
        "how do I run a quality control test on {p}", "steps to calibrate {p}",
        "walk me through running a control on {p}", "how to prep a fingerstick sample",
        "way to clean {p}", "how do I change the cartridge on {p}",
        "procedure for testing {a}", "instructions for using {p}",
        "how should {p} be stored", "how do I perform a {a} test",
        "what is the process for calibrating {p}", "steps to replace the sensor",
        "how do I start up {p}", "correct technique for a capillary sample",
    ],
    "REGULATORY": [
        "which 510k covers {p}", "what is the FDA clearance number for {p}",
        "was {p} recalled", "which recalls affected {p}",
        "what predicate device did {p} cite", "fda product code for {p}",
        "is {p} substantially equivalent to a predicate",
        "what regulation covers {p}", "what software defects caused a recall",
        "which product code applies to {a} testing",
        "clearance history for {p}", "what class of device is {p}",
        "21 cfr regulation for {a} measurement",
    ],
    "TEMPORAL": [
        "when was {p} cleared by the FDA", "what year did {p} get approval",
        "date of the {p} clearance", "how recent is {p}",
        "when did the {p} recall happen", "what date was {p} submitted",
        "how old is the {p} clearance", "when was {p} first approved",
    ],
    "COMPARISON": [
        "what is the difference between {p} and {p2}", "{p} versus {p2}",
        "how does {p} compare to {p2}", "which is better {p} or {p2}",
        "compare {a} and {a2} measurement", "difference between capillary and venous samples",
        "{p} vs {p2} for point of care", "how do {p} and {p2} differ",
        "which of {p} or {p2} handles {a} better",
    ],
    "DEFINITION": [
        "what is {a}", "define {a}", "meaning of {a}", "what does {a} stand for",
        "what is a predicate device", "define substantially equivalent",
        "what does {a} mean", "explain what {a} is",
        "what is point of care testing", "definition of {a}",
        "what are the limitations of {p}",
    ],
}


def fill(t: str) -> str:
    a, a2 = random.sample(ANALYTES, 2)
    p, p2 = random.sample(PRODUCTS, 2)
    return (t.replace("{a2}", a2).replace("{a}", a)
             .replace("{p2}", p2).replace("{p}", p)
             .replace("{s}", random.choice(SUBSTANCES)))


# Surface noise a real user introduces. Applied randomly so the model learns to
# ignore politeness, punctuation and case rather than keying on them.
def perturb(s: str) -> str:
    r = random.random()
    if r < 0.14:
        s = s + "?"
    elif r < 0.22:
        s = s.capitalize() + "?"
    elif r < 0.28:
        s = "can you tell me " + s
    elif r < 0.33:
        s = "I need to know " + s
    elif r < 0.37:
        s = s.upper()
    if random.random() < 0.10:
        s = s.replace(" the ", " ")
    return s


def build_dataset(per_intent: int = 260) -> tuple[list[str], list[str]]:
    X, y = [], []
    for intent, templates in TEMPLATES.items():
        seen = set()
        tries = 0
        while len([1 for lbl in y if lbl == intent]) < per_intent and tries < per_intent * 30:
            tries += 1
            s = perturb(fill(random.choice(templates)))
            key = s.lower()
            if key in seen:
                continue
            seen.add(key)
            X.append(s)
            y.append(intent)
    return X, y


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--tenant", help="write the model into that tenant's data directory")
    args, _ = ap.parse_known_args()
    globals()["_TENANT"] = args.tenant

    X, y = build_dataset()
    labels = sorted(set(y))
    print(f"[1/4] synthetic corpus: {len(X)} examples across {len(labels)} intents")
    for lbl in labels:
        print(f"      {lbl:24} {y.count(lbl)}")

    # Word n-grams carry phrasing; character n-grams carry morphology and absorb
    # typos, plurals and spelling variants without needing a stemmer.
    word = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True,
                           max_features=2600, lowercase=True,
                           token_pattern=r"[A-Za-z0-9]{2,}")
    char = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=3,
                           sublinear_tf=True, max_features=2600, lowercase=True)
    feats = FeatureUnion([("w", word), ("c", char)])

    Xv = feats.fit_transform(X)
    print(f"\n[2/4] features: {Xv.shape[1]} "
          f"({len(word.vocabulary_)} word + {len(char.vocabulary_)} char)")

    clf = LogisticRegression(max_iter=2000, C=4.0, class_weight="balanced")
    scores = cross_val_score(clf, Xv, y, cv=5, n_jobs=1)
    print(f"[3/4] 5-fold CV accuracy: {scores.mean():.3f} (+/- {scores.std():.3f})")
    clf.fit(Xv, y)

    # ---- export ---------------------------------------------------------
    W = clf.coef_.astype(np.float32)              # (n_classes, n_features)
    b = clf.intercept_.astype(np.float32)
    scale = float(np.abs(W).max()) or 1.0
    Wq = np.clip(np.round(W / scale * 127), -127, 127).astype(np.int8)

    word_vocab = sorted(word.vocabulary_.items(), key=lambda kv: kv[1])
    char_vocab = sorted(char.vocabulary_.items(), key=lambda kv: kv[1])

    model = {
        "version": 1,
        "method": "tfidf(word 1-2gram + char_wb 3-5gram) -> multinomial logistic regression",
        "classes": list(clf.classes_),
        "cv_accuracy": round(float(scores.mean()), 4),
        "word": {
            "terms": [t for t, _ in word_vocab],
            "idf": [round(float(v), 4) for v in word.idf_],
        },
        "char": {
            "terms": [t for t, _ in char_vocab],
            "idf": [round(float(v), 4) for v in char.idf_],
        },
        "weights": Wq.tolist(),
        "weight_scale": scale,
        "bias": [round(float(v), 5) for v in b],
        "n_word": len(word_vocab),
        "n_char": len(char_vocab),
    }

    tenant = globals().get("_TENANT")
    out = (Path("site/t") / tenant / "data" / "intent_model.json") if tenant \
        else Path("site/data/intent_model.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(model, separators=(",", ":")))
    kb = out.stat().st_size / 1024
    print(f"[4/4] wrote {out} ({kb:.0f} KB)")
    if kb > 700:
        print("      ! large for a client-side payload — consider trimming max_features")


if __name__ == "__main__":
    main()
