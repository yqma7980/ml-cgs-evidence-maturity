# WP9.3 Evidence-Dimension Relationship

## Non-compensatory relationship

```mermaid
flowchart LR
    E["ML-CGS workflow"]
    F["Field evidence<br/>Where was output evaluated?"]
    P["Physical consistency<br/>What physics was encoded or checked?"]
    U["Uncertainty<br/>Was confidence reliable and propagated?"]
    T["Transferability<br/>Did performance survive a defined shift?"]
    D["Decision readiness<br/>What action was evaluated and audited?"]
    Q["Bounded decision-support claim"]

    E --> F
    E --> P
    E --> U
    E --> T
    E --> D
    F --> Q
    P --> Q
    U --> Q
    T --> Q
    D --> Q
```

The arrows represent independent evidence contributions. They do not define a
weighted score. A bounded decision-support claim must state which layers are
present, missing, unclear, or not applicable.

## Boundary pairs

```mermaid
flowchart TB
    F1["Field evidence<br/>empirical anchoring"] --- T1["Transferability<br/>distribution shift"]
    P1["Physical consistency<br/>process diagnostic"] --- D1["Decision readiness<br/>action linkage"]
    U1["Uncertainty<br/>conditional reliability"] --- T2["Transferability<br/>shift robustness"]
    X["No arrow means equivalence.<br/>Each pair requires separate evidence."]
```

## Interpretation rules

1. Field evidence and transferability are orthogonal. A single field case is
   not a cross-site test. A simulated blind geology test can be OOD evidence
   without being field evidence.
2. Physical encoding and physical diagnosis are different levels. A
   physics-informed loss is not a reported mass, pressure, plume, geomechanical,
   geochemical, rock-physics, or detectability diagnostic.
3. A posterior or ensemble is not calibrated merely because it is
   probabilistic. Calibration requires a reliability check.
4. A storage-relevant prediction is not an evaluated decision. Decision score
   3 requires an explicit threshold, update, alarm, or optimization mechanism.
5. Unknown, unclear, and not reported are retained as missing evidence, not
   scored as zero.

This document is a framework artifact. It does not change the locked corpus,
figures, tables, or manuscript claims.
