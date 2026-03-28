# Machine-First Review Gate v1

## Background

By `2026-03-28`, many experiment packs could be built and quantified, but many still failed human review with uniformly weak or null outcomes. The project therefore moved from a pack-first workflow to a machine-first workflow.

## Default Flow

1. Build the listening pack.
2. Build the quantified review queue.
3. Run the machine gate.
4. Send a pack to formal human review only if the machine gate allows it.
5. If the pack fails the machine gate, continue machine-only iteration first.

## Gate Thresholds

A pack is allowed for human review when all of the following hold:

- `avg_auto_quant_score >= 65`
- `avg_auto_direction_score >= 45`
- `avg_auto_effect_score >= 45`
- and either:
  - `top_auto_quant_score >= 75`
  - or `strongish_rows >= 2`

Here `strongish_rows = strong_pass + pass + borderline`.

## What This Gate Is For

The gate is not meant to prove that a method works. It is meant to answer a narrower question:

- Is this pack strong enough to justify another round of human listening time?

The gate still allows packs that later fail subjectively. It exists mainly to block obviously weak packs from repeatedly consuming manual review time.

## Post-Review Strength Escalation Rule

Machine gating alone is not enough. A pack may pass the gate and still fail human review because the whole pack is simply too weak.

The current process therefore adds one more rule after human review:

- If a reviewed pack is dominated by `strength_fit = too_weak`
- and artifact notes are not the main failure mode
- then the next step is not another same-strength human pack
- the next step is `escalate_strength_before_next_human`

This rule is implemented in:

- `scripts/build_listening_machine_gate_report.py`

The report now records:

- `reviewed_too_weak_rows`
- `strength_escalation_recommendation`
- `strength_escalation_reason`

## Current Operational Meaning

- Weak packs should be filtered by machine metrics before formal listening.
- Packs that pass the gate but come back uniformly too weak should be strengthened before the next human review.
- Human review time should go to packs that are both machine-viable and strong enough to test the real subjective failure mode.
