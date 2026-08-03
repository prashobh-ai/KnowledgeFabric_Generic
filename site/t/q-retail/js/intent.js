// ============================================================================
// Intent classifier — trained model, browser inference
// ============================================================================
//
// Replaces hand-written regex cues with a multinomial logistic regression
// trained on synthetic data (pipeline/train_intent.py).
//
// Why this and not an LLM router: eleven stable intent classes is precisely the
// case a linear model handles correctly in under a millisecond, offline, with no
// per-query cost and fully deterministic output. An LLM router would add
// hundreds of milliseconds, a per-query bill, and non-determinism to a decision
// that does not need dynamic reasoning. Generative capacity should be spent
// where it earns its latency, not on routing.
//
// Why it matters here: the regex router scored 33% on realistic paraphrases. It
// scored well on our own question bank because we wrote both the questions and
// the rules. A reviewer typing their own words fell through to GENERAL, which
// switched evidence routing off — the answer got worse at precisely the moment
// someone was watching.
//
// Inference is a sparse dot product against ~4,300 features: TF-IDF over word
// 1-2 grams and character 3-5 grams, then argmax over class scores. The
// character features are what absorb typos, plurals and spelling variants
// without a stemmer.

const WORD_RE = /[A-Za-z0-9]{2,}/g;

export class IntentClassifier {
  constructor(model) {
    this.ready = false;
    if (!model || !model.classes) return;

    this.classes = model.classes;
    this.nWord = model.n_word;
    this.nChar = model.n_char;
    this.bias = Float32Array.from(model.bias);
    this.scale = model.weight_scale / 127;
    this.cvAccuracy = model.cv_accuracy;
    this.method = model.method;

    this.wordIdx = new Map();
    model.word.terms.forEach((t, i) => this.wordIdx.set(t, i));
    this.wordIdf = Float32Array.from(model.word.idf);

    this.charIdx = new Map();
    model.char.terms.forEach((t, i) => this.charIdx.set(t, i));
    this.charIdf = Float32Array.from(model.char.idf);

    // Flatten the weight matrix once — a flat typed array keeps the hot loop
    // cache-friendly and avoids per-row bounds checks.
    const C = this.classes.length;
    const F = this.nWord + this.nChar;
    this.W = new Float32Array(C * F);
    for (let c = 0; c < C; c++) {
      const row = model.weights[c];
      for (let f = 0; f < F; f++) this.W[c * F + f] = row[f] * this.scale;
    }
    this.F = F;
    this.ready = true;
  }

  /** Mirrors sklearn's TfidfVectorizer: sublinear tf, idf weighting, L2 norm. */
  _features(text) {
    const s = String(text).toLowerCase();
    const counts = new Map();

    // word 1-2 grams
    const toks = s.match(WORD_RE) || [];
    const bump = (idx) => counts.set(idx, (counts.get(idx) || 0) + 1);
    for (let i = 0; i < toks.length; i++) {
      let id = this.wordIdx.get(toks[i]);
      if (id !== undefined) bump(id);
      if (i + 1 < toks.length) {
        id = this.wordIdx.get(`${toks[i]} ${toks[i + 1]}`);
        if (id !== undefined) bump(id);
      }
    }

    // char_wb 3-5 grams: sklearn pads each word with spaces, then slides
    for (const w of toks) {
      const padded = ` ${w} `;
      for (let n = 3; n <= 5; n++) {
        for (let i = 0; i + n <= padded.length; i++) {
          const id = this.charIdx.get(padded.slice(i, i + n));
          if (id !== undefined) bump(id + this.nWord);
        }
      }
    }
    if (!counts.size) return null;

    // sublinear tf * idf, then L2 normalise
    let norm = 0;
    const feats = [];
    for (const [idx, tf] of counts) {
      const idf = idx < this.nWord ? this.wordIdf[idx] : this.charIdf[idx - this.nWord];
      const v = (1 + Math.log(tf)) * idf;
      feats.push([idx, v]);
      norm += v * v;
    }
    norm = Math.sqrt(norm) || 1;
    for (const f of feats) f[1] /= norm;
    return feats;
  }

  /** @returns {{name:string, confidence:number, scores:Object}|null} */
  predict(text) {
    if (!this.ready) return null;
    const feats = this._features(text);
    if (!feats) return null;

    const C = this.classes.length;
    const logits = new Float32Array(C);
    for (let c = 0; c < C; c++) {
      let z = this.bias[c];
      const base = c * this.F;
      for (const [idx, v] of feats) z += this.W[base + idx] * v;
      logits[c] = z;
    }

    // softmax, max-shifted for numerical stability
    let max = -Infinity;
    for (let c = 0; c < C; c++) if (logits[c] > max) max = logits[c];
    let sum = 0;
    const probs = new Float32Array(C);
    for (let c = 0; c < C; c++) { probs[c] = Math.exp(logits[c] - max); sum += probs[c]; }

    let best = 0;
    const scores = {};
    for (let c = 0; c < C; c++) {
      probs[c] /= sum;
      scores[this.classes[c]] = +probs[c].toFixed(4);
      if (probs[c] > probs[best]) best = c;
    }
    return { name: this.classes[best], confidence: probs[best], scores };
  }
}

/** Lazy load. A failure here must never take routing down — the rule cues remain
 *  as a fallback, so the system degrades to its previous behaviour rather than
 *  to no behaviour. */
export async function loadIntentClassifier(url = 'data/intent_model.json') {
  try {
    const res = await fetch(url, { cache: 'no-cache' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const clf = new IntentClassifier(await res.json());
    if (clf.ready) {
      console.info(`[fabric] intent model online — ${clf.classes.length} classes, ` +
                   `${(clf.cvAccuracy * 100).toFixed(1)}% CV`);
    }
    return clf;
  } catch (err) {
    console.warn('[fabric] intent model unavailable, using rule cues:', err.message);
    return new IntentClassifier(null);
  }
}
