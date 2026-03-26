# arXiv QEC Triage Guidelines

## Strong Positive Signals

- `quantum error correction`
- `quantum error correcting`
- `fault tolerant`
- `fault-tolerant`
- `decoder` or `decoding`
- `syndrome`
- `BP-OSD`
- `BB codes`
- `surface code`
- `stabilizer code`
- `LDPC`
- `quantum LDPC`
- `QLDPC`
- `bosonic code`
- `cat code`
- `topological code`
- `threshold`
- `logical qubit`
- `magic state` when clearly tied to FTQC
- `erasure` when tied to coding or decoding

## Adjacent Signals

- `quantum memory`
- `transversal`
- `lattice surgery`
- `distillation`
- `syndrome extraction`
- `leakage reduction`
- `subsystem code`
- `Floquet code`
- `homological product`
- `Tanner graph`

## Weak or Negative Signals

Deprioritize titles that look like:

- Generic quantum algorithms with no coding or fault-tolerance angle
- Application papers in chemistry, optimization, or machine learning
- Pure communication or networking papers unless they mention coding structures relevant to QEC
- Device or materials papers with no stabilization, decoding, or logical-qubit angle

## Recommended Output Style

- Return a short shortlist with one-line reasons.
- Keep an "adjacent but maybe relevant" bucket for ambiguous titles.
- If asked to improve automation, convert these heuristics into labels or scores instead of hard deletion first.
