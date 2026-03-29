from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_CONFIG = ROOT / "experiments" / "stage0_baseline" / "v1_full" / "speech_lsf_resonance_candidate_v1.json"
DEFAULT_SWEEP_DIR = ROOT / "experiments" / "stage0_baseline" / "v1_full" / "lsf_machine_sweep_v2"
DEFAULT_PACK_ROOT = ROOT / "artifacts" / "listening_review" / "stage0_speech_lsf_machine_sweep_v2"
DEFAULT_INPUT_CSV = ROOT / "experiments" / "fixed_eval" / "v1_2" / "fixed_eval_review_final_v1_2.csv"


VARIANT_SPECS: list[dict[str, object]] = [
    {
        "variant_id": "masc_mid_focus_v2a",
        "description": "Keep feminine side near v1, but strengthen masculine F2 shift first to avoid bottle-heavy F1 overpull.",
        "overrides": {
            ("LibriTTS-R", "masculine"): {
                "center_shift_ratios": [0.90, 0.86, 0.96],
                "blend": 0.84,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "center_shift_ratios": [0.92, 0.88, 0.97],
                "blend": 0.80,
            },
        },
    },
    {
        "variant_id": "masc_uniform_push_v2b",
        "description": "Push masculine direction more uniformly across F1/F2/F3 while keeping feminine untouched for comparison.",
        "overrides": {
            ("LibriTTS-R", "masculine"): {
                "center_shift_ratios": [0.86, 0.90, 0.94],
                "blend": 0.85,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "center_shift_ratios": [0.88, 0.92, 0.95],
                "blend": 0.82,
            },
        },
    },
    {
        "variant_id": "balanced_pull_fem_push_masc_v2c",
        "description": "Pull back feminine brightness slightly while pushing masculine direction harder to improve directional balance.",
        "overrides": {
            ("LibriTTS-R", "feminine"): {
                "center_shift_ratios": [1.10, 1.07, 1.04],
                "blend": 0.74,
            },
            ("VCTK Corpus 0.92", "feminine"): {
                "center_shift_ratios": [1.08, 1.05, 1.03],
                "blend": 0.70,
            },
            ("LibriTTS-R", "masculine"): {
                "center_shift_ratios": [0.88, 0.86, 0.95],
                "blend": 0.84,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "center_shift_ratios": [0.90, 0.88, 0.96],
                "blend": 0.81,
            },
        },
    },
    {
        "variant_id": "order18_mid_focus_v2d",
        "description": "Raise LPC order to 18 and focus the extra strength into the mid band, testing whether v1 was under-resolved.",
        "overrides": {
            ("LibriTTS-R", "feminine"): {
                "lpc_order": 18,
                "center_shift_ratios": [1.11, 1.09, 1.05],
                "blend": 0.76,
            },
            ("VCTK Corpus 0.92", "feminine"): {
                "lpc_order": 18,
                "center_shift_ratios": [1.09, 1.07, 1.04],
                "blend": 0.72,
            },
            ("LibriTTS-R", "masculine"): {
                "lpc_order": 18,
                "center_shift_ratios": [0.90, 0.86, 0.95],
                "blend": 0.84,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "lpc_order": 18,
                "center_shift_ratios": [0.92, 0.88, 0.96],
                "blend": 0.80,
            },
        },
    },
    {
        "variant_id": "order18_vctk_rescue_v2e",
        "description": "Raise LPC order and retune VCTK search bands downward to rescue the weakest masculine cell without reopening WORLD/VTL.",
        "overrides": {
            ("LibriTTS-R", "feminine"): {
                "lpc_order": 18,
            },
            ("VCTK Corpus 0.92", "feminine"): {
                "lpc_order": 18,
            },
            ("LibriTTS-R", "masculine"): {
                "lpc_order": 18,
                "center_shift_ratios": [0.88, 0.87, 0.95],
                "blend": 0.84,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "lpc_order": 18,
                "search_ranges_hz": [[240.0, 920.0], [920.0, 2550.0], [2550.0, 4380.0]],
                "center_shift_ratios": [0.86, 0.89, 0.95],
                "blend": 0.84,
                "min_gap_hz": 65.0,
                "edge_gap_hz": 85.0,
            },
        },
    },
    {
        "variant_id": "conservative_order18_control_v2f",
        "description": "Use order 18 but pull overall blend down to test whether v1 artifacts were mostly reconstruction pressure rather than wrong direction.",
        "overrides": {
            ("LibriTTS-R", "feminine"): {
                "lpc_order": 18,
                "center_shift_ratios": [1.09, 1.07, 1.04],
                "blend": 0.70,
            },
            ("VCTK Corpus 0.92", "feminine"): {
                "lpc_order": 18,
                "center_shift_ratios": [1.07, 1.05, 1.03],
                "blend": 0.67,
            },
            ("LibriTTS-R", "masculine"): {
                "lpc_order": 18,
                "center_shift_ratios": [0.90, 0.88, 0.96],
                "blend": 0.78,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "lpc_order": 18,
                "center_shift_ratios": [0.92, 0.90, 0.97],
                "blend": 0.75,
            },
        },
    },
]


V3_VARIANT_SPECS: list[dict[str, object]] = [
    {
        "variant_id": "asym_boost_v3a",
        "description": "Boost the newly audible v2 profile, but keep Libri feminine slightly trimmed to reduce the transient artifact noted in review.",
        "overrides": {
            ("LibriTTS-R", "feminine"): {
                "center_shift_ratios": [1.13, 1.09, 1.06],
                "blend": 0.76,
            },
            ("VCTK Corpus 0.92", "feminine"): {
                "center_shift_ratios": [1.14, 1.10, 1.06],
                "blend": 0.80,
            },
            ("LibriTTS-R", "masculine"): {
                "center_shift_ratios": [0.86, 0.85, 0.94],
                "blend": 0.88,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "center_shift_ratios": [0.84, 0.87, 0.94],
                "blend": 0.88,
            },
        },
    },
    {
        "variant_id": "vctk_rescue_plus_v3b",
        "description": "Keep Libri near v2 and spend almost all extra strength budget on the two VCTK cells, especially the still-weak masculine side.",
        "overrides": {
            ("VCTK Corpus 0.92", "feminine"): {
                "center_shift_ratios": [1.15, 1.11, 1.07],
                "blend": 0.82,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "center_shift_ratios": [0.83, 0.86, 0.94],
                "blend": 0.90,
                "min_gap_hz": 60.0,
            },
        },
    },
    {
        "variant_id": "masc_push_control_v3c",
        "description": "Leave feminine nearly untouched and push both masculine cells harder, testing whether the remaining weakness is almost entirely on the female-to-masculine side.",
        "overrides": {
            ("LibriTTS-R", "masculine"): {
                "center_shift_ratios": [0.85, 0.84, 0.94],
                "blend": 0.89,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "center_shift_ratios": [0.82, 0.85, 0.94],
                "blend": 0.90,
                "min_gap_hz": 60.0,
            },
        },
    },
    {
        "variant_id": "fem_artifact_guard_v3d",
        "description": "Pull Libri feminine back slightly while strengthening every other cell, explicitly trading a bit of male-to-feminine intensity for safer transients.",
        "overrides": {
            ("LibriTTS-R", "feminine"): {
                "center_shift_ratios": [1.11, 1.08, 1.05],
                "blend": 0.73,
            },
            ("VCTK Corpus 0.92", "feminine"): {
                "center_shift_ratios": [1.14, 1.10, 1.06],
                "blend": 0.80,
            },
            ("LibriTTS-R", "masculine"): {
                "center_shift_ratios": [0.86, 0.85, 0.94],
                "blend": 0.88,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "center_shift_ratios": [0.84, 0.87, 0.94],
                "blend": 0.89,
            },
        },
    },
    {
        "variant_id": "order20_rescue_v3e",
        "description": "Raise LPC order to 20 and add a moderate strength bump, testing whether the remaining weakness is partly under-resolution rather than blend alone.",
        "overrides": {
            ("LibriTTS-R", "feminine"): {
                "lpc_order": 20,
                "center_shift_ratios": [1.13, 1.09, 1.06],
                "blend": 0.77,
            },
            ("VCTK Corpus 0.92", "feminine"): {
                "lpc_order": 20,
                "center_shift_ratios": [1.14, 1.10, 1.06],
                "blend": 0.80,
            },
            ("LibriTTS-R", "masculine"): {
                "lpc_order": 20,
                "center_shift_ratios": [0.86, 0.85, 0.94],
                "blend": 0.88,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "lpc_order": 20,
                "center_shift_ratios": [0.84, 0.86, 0.94],
                "blend": 0.88,
                "search_ranges_hz": [[235.0, 910.0], [910.0, 2520.0], [2520.0, 4380.0]],
                "min_gap_hz": 60.0,
            },
        },
    },
]


V4_VARIANT_SPECS: list[dict[str, object]] = [
    {
        "variant_id": "air_preserve_v4a",
        "description": "Preserve the third resonance proxy for female-to-masculine edits so the result stops sounding like broad high-frequency suppression.",
        "overrides": {
            ("LibriTTS-R", "masculine"): {
                "center_shift_ratios": [0.88, 0.86, 0.99],
                "blend": 0.86,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "center_shift_ratios": [0.86, 0.87, 0.99],
                "blend": 0.86,
                "min_gap_hz": 60.0,
            },
        },
    },
    {
        "variant_id": "mid_only_v4b",
        "description": "Hold F3 at neutral and concentrate the masculine move into F2, testing whether the bottle effect is mostly a too-broad downward shift.",
        "overrides": {
            ("LibriTTS-R", "masculine"): {
                "center_shift_ratios": [0.90, 0.84, 1.00],
                "blend": 0.88,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "center_shift_ratios": [0.89, 0.85, 1.00],
                "blend": 0.88,
                "min_gap_hz": 60.0,
            },
        },
    },
    {
        "variant_id": "f2_focus_v4c",
        "description": "Keep F1 and F3 near neutral while pushing F2 more assertively, aiming for tract-shape change without dulling upper-band air.",
        "overrides": {
            ("LibriTTS-R", "masculine"): {
                "center_shift_ratios": [0.95, 0.84, 1.00],
                "blend": 0.89,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "center_shift_ratios": [0.94, 0.85, 1.00],
                "blend": 0.89,
                "min_gap_hz": 60.0,
            },
        },
    },
    {
        "variant_id": "split_band_v4d",
        "description": "Retune masculine search bands downward for F1/F2 only, while leaving the top band almost untouched to avoid the muffled bottle impression.",
        "overrides": {
            ("LibriTTS-R", "masculine"): {
                "search_ranges_hz": [[240.0, 820.0], [880.0, 2200.0], [2500.0, 4300.0]],
                "center_shift_ratios": [0.90, 0.85, 1.00],
                "blend": 0.88,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "search_ranges_hz": [[240.0, 860.0], [930.0, 2280.0], [2550.0, 4380.0]],
                "center_shift_ratios": [0.89, 0.86, 1.00],
                "blend": 0.88,
                "min_gap_hz": 60.0,
            },
        },
    },
    {
        "variant_id": "conservative_air_v4e",
        "description": "Trade some masculine strength for safer high-band preservation, serving as a control against over-correction in the new selective-shift family.",
        "overrides": {
            ("LibriTTS-R", "masculine"): {
                "center_shift_ratios": [0.92, 0.88, 1.00],
                "blend": 0.82,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "center_shift_ratios": [0.91, 0.89, 1.00],
                "blend": 0.82,
                "min_gap_hz": 60.0,
            },
        },
    },
]


V5_VARIANT_SPECS: list[dict[str, object]] = [
    {
        "variant_id": "presence_bypass_v5a",
        "description": "Use a gradual original-band bypass above 1.8kHz so female-to-masculine keeps air while F1/F2 still move downward.",
        "overrides": {
            ("LibriTTS-R", "masculine"): {
                "center_shift_ratios": [0.90, 0.86, 0.99],
                "blend": 0.86,
                "preserve_original_from_hz": 1800.0,
                "preserve_original_full_hz": 3200.0,
                "preserve_original_mix": 0.85,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "center_shift_ratios": [0.89, 0.86, 0.99],
                "blend": 0.86,
                "min_gap_hz": 60.0,
                "preserve_original_from_hz": 1800.0,
                "preserve_original_full_hz": 3200.0,
                "preserve_original_mix": 0.90,
            },
        },
    },
    {
        "variant_id": "presence_bypass_plus_v5b",
        "description": "Push F2 a bit harder than v5a while still bypassing the upper presence and brilliance region from the original signal.",
        "overrides": {
            ("LibriTTS-R", "masculine"): {
                "center_shift_ratios": [0.90, 0.84, 0.99],
                "blend": 0.88,
                "preserve_original_from_hz": 1750.0,
                "preserve_original_full_hz": 3150.0,
                "preserve_original_mix": 0.88,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "center_shift_ratios": [0.89, 0.84, 0.99],
                "blend": 0.88,
                "min_gap_hz": 60.0,
                "preserve_original_from_hz": 1750.0,
                "preserve_original_full_hz": 3150.0,
                "preserve_original_mix": 0.92,
            },
        },
    },
    {
        "variant_id": "f2_only_bypass_v5c",
        "description": "Keep F1/F3 near neutral and rely on F2 plus an upper-band bypass, testing the narrowest tract-shift version of male direction.",
        "overrides": {
            ("LibriTTS-R", "masculine"): {
                "center_shift_ratios": [0.96, 0.84, 1.00],
                "blend": 0.89,
                "preserve_original_from_hz": 1700.0,
                "preserve_original_full_hz": 3000.0,
                "preserve_original_mix": 0.92,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "center_shift_ratios": [0.95, 0.84, 1.00],
                "blend": 0.89,
                "min_gap_hz": 60.0,
                "preserve_original_from_hz": 1700.0,
                "preserve_original_full_hz": 3000.0,
                "preserve_original_mix": 0.95,
            },
        },
    },
    {
        "variant_id": "vctk_bypass_focus_v5d",
        "description": "Keep Libri masculine moderate but use a stronger bypass on the weakest VCTK masculine cell, targeting the main failure case first.",
        "overrides": {
            ("LibriTTS-R", "masculine"): {
                "center_shift_ratios": [0.91, 0.87, 0.99],
                "blend": 0.84,
                "preserve_original_from_hz": 1850.0,
                "preserve_original_full_hz": 3250.0,
                "preserve_original_mix": 0.82,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "center_shift_ratios": [0.88, 0.84, 0.99],
                "blend": 0.88,
                "min_gap_hz": 60.0,
                "preserve_original_from_hz": 1700.0,
                "preserve_original_full_hz": 3000.0,
                "preserve_original_mix": 0.98,
            },
        },
    },
    {
        "variant_id": "gentle_bypass_control_v5e",
        "description": "Use a lighter F1/F2 shift with a strong original-band bypass as a control for separating muffling risk from sheer strength loss.",
        "overrides": {
            ("LibriTTS-R", "masculine"): {
                "center_shift_ratios": [0.93, 0.89, 1.00],
                "blend": 0.80,
                "preserve_original_from_hz": 1750.0,
                "preserve_original_full_hz": 3050.0,
                "preserve_original_mix": 0.95,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "center_shift_ratios": [0.92, 0.89, 1.00],
                "blend": 0.80,
                "min_gap_hz": 60.0,
                "preserve_original_from_hz": 1750.0,
                "preserve_original_full_hz": 3050.0,
                "preserve_original_mix": 0.98,
            },
        },
    },
]


V6_VARIANT_SPECS: list[dict[str, object]] = [
    {
        "variant_id": "lower_geom_v6a",
        "description": "Switch masculine rules to formant-lowering-with-air-preserve and widen the first two pairs slightly while keeping F3 neutral.",
        "overrides": {
            ("LibriTTS-R", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.94, 0.90, 1.00],
                "pair_width_ratios": [1.18, 1.10, 1.00],
                "blend": 0.86,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.93, 0.90, 1.00],
                "pair_width_ratios": [1.16, 1.12, 1.00],
                "blend": 0.86,
                "min_gap_hz": 60.0,
            },
        },
    },
    {
        "variant_id": "lower_geom_v6b",
        "description": "Concentrate more movement into F2 plus width expansion, testing a lower-formant geometry change without a broad dark tilt.",
        "overrides": {
            ("LibriTTS-R", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.97, 0.88, 1.00],
                "pair_width_ratios": [1.08, 1.20, 1.00],
                "blend": 0.88,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.96, 0.88, 1.00],
                "pair_width_ratios": [1.06, 1.22, 1.00],
                "blend": 0.88,
                "min_gap_hz": 60.0,
            },
        },
    },
    {
        "variant_id": "lower_geom_v6c",
        "description": "Use moderate center shifts but stronger pair-width growth, probing whether the audible male cue is more bandwidth-like than centroid-like.",
        "overrides": {
            ("LibriTTS-R", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.96, 0.92, 1.00],
                "pair_width_ratios": [1.28, 1.18, 1.00],
                "blend": 0.84,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.95, 0.92, 1.00],
                "pair_width_ratios": [1.24, 1.20, 1.00],
                "blend": 0.84,
                "min_gap_hz": 60.0,
            },
        },
    },
    {
        "variant_id": "vctk_geom_focus_v6d",
        "description": "Keep Libri conservative but push VCTK masculine geometry harder, since the weakest failures have concentrated there so far.",
        "overrides": {
            ("LibriTTS-R", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.95, 0.91, 1.00],
                "pair_width_ratios": [1.10, 1.10, 1.00],
                "blend": 0.84,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.92, 0.88, 1.00],
                "pair_width_ratios": [1.18, 1.24, 1.00],
                "blend": 0.88,
                "min_gap_hz": 60.0,
                "search_ranges_hz": [[235.0, 880.0], [900.0, 2250.0], [2550.0, 4380.0]],
            },
        },
    },
    {
        "variant_id": "conservative_geom_v6e",
        "description": "A conservative control for the new formant-lowering family: smaller center moves, modest width changes, and more blend restraint.",
        "overrides": {
            ("LibriTTS-R", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.97, 0.94, 1.00],
                "pair_width_ratios": [1.10, 1.08, 1.00],
                "blend": 0.78,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.96, 0.94, 1.00],
                "pair_width_ratios": [1.08, 1.10, 1.00],
                "blend": 0.78,
                "min_gap_hz": 60.0,
            },
        },
    },
]


V7_VARIANT_SPECS: list[dict[str, object]] = [
    {
        "variant_id": "stronger_geom_v7a",
        "description": "Raise blend and F2/width strength off the v6 winner so the new masculine family stops landing as uniformly too weak.",
        "overrides": {
            ("LibriTTS-R", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.96, 0.85, 1.00],
                "pair_width_ratios": [1.10, 1.24, 1.00],
                "blend": 0.92,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.95, 0.85, 1.00],
                "pair_width_ratios": [1.08, 1.26, 1.00],
                "blend": 0.92,
                "min_gap_hz": 60.0,
            },
        },
    },
    {
        "variant_id": "stronger_geom_v7b",
        "description": "Keep F1 near v6 but push F2 and pair width harder, testing a more forceful male cue without reviving broad dark tilt.",
        "overrides": {
            ("LibriTTS-R", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.98, 0.84, 1.00],
                "pair_width_ratios": [1.08, 1.28, 1.00],
                "blend": 0.93,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.97, 0.84, 1.00],
                "pair_width_ratios": [1.06, 1.30, 1.00],
                "blend": 0.93,
                "min_gap_hz": 60.0,
            },
        },
    },
    {
        "variant_id": "vctk_strong_geom_v7c",
        "description": "Spend most of the extra strength budget on VCTK masculine, while only modestly increasing Libri masculine to avoid needless artifact risk.",
        "overrides": {
            ("LibriTTS-R", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.97, 0.87, 1.00],
                "pair_width_ratios": [1.08, 1.22, 1.00],
                "blend": 0.89,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.95, 0.83, 1.00],
                "pair_width_ratios": [1.10, 1.32, 1.00],
                "blend": 0.94,
                "min_gap_hz": 60.0,
                "search_ranges_hz": [[270.0, 990.0], [980.0, 2660.0], [2700.0, 4500.0]],
            },
        },
    },
    {
        "variant_id": "balanced_strong_v7d",
        "description": "Increase both feminine and masculine strength one notch so the next human package is not dominated by a global too-weak verdict.",
        "overrides": {
            ("LibriTTS-R", "feminine"): {
                "center_shift_ratios": [1.15, 1.11, 1.07],
                "blend": 0.82,
            },
            ("VCTK Corpus 0.92", "feminine"): {
                "center_shift_ratios": [1.16, 1.12, 1.08],
                "blend": 0.84,
            },
            ("LibriTTS-R", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.97, 0.85, 1.00],
                "pair_width_ratios": [1.10, 1.24, 1.00],
                "blend": 0.92,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.96, 0.85, 1.00],
                "pair_width_ratios": [1.08, 1.26, 1.00],
                "blend": 0.92,
                "min_gap_hz": 60.0,
            },
        },
    },
    {
        "variant_id": "conservative_plus_v7e",
        "description": "A milder strength bump control, useful if the stronger v7 variants jump too fast into artifact-heavy territory.",
        "overrides": {
            ("LibriTTS-R", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.97, 0.86, 1.00],
                "pair_width_ratios": [1.09, 1.22, 1.00],
                "blend": 0.90,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.96, 0.86, 1.00],
                "pair_width_ratios": [1.07, 1.24, 1.00],
                "blend": 0.90,
                "min_gap_hz": 60.0,
            },
        },
    },
]




V8_VARIANT_SPECS: list[dict[str, object]] = [
    {
        "variant_id": "balanced_stronger_v8a",
        "description": "Uniform strength escalation from v7d: push both directions one clear notch above the too_weak baseline.",
        "overrides": {
            ("LibriTTS-R", "feminine"): {
                "center_shift_ratios": [1.19, 1.14, 1.09],
                "blend": 0.88,
            },
            ("VCTK Corpus 0.92", "feminine"): {
                "center_shift_ratios": [1.20, 1.15, 1.10],
                "blend": 0.90,
            },
            ("LibriTTS-R", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.95, 0.82, 1.00],
                "pair_width_ratios": [1.14, 1.30, 1.00],
                "blend": 0.94,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.94, 0.82, 1.00],
                "pair_width_ratios": [1.12, 1.32, 1.00],
                "blend": 0.94,
                "min_gap_hz": 60.0,
            },
        },
    },
    {
        "variant_id": "masc_width_focus_v8b",
        "description": "Push masculine pair-width harder than center shift, targeting resonance spread rather than pure centroid lowering.",
        "overrides": {
            ("LibriTTS-R", "feminine"): {
                "center_shift_ratios": [1.18, 1.13, 1.08],
                "blend": 0.86,
            },
            ("VCTK Corpus 0.92", "feminine"): {
                "center_shift_ratios": [1.19, 1.14, 1.09],
                "blend": 0.88,
            },
            ("LibriTTS-R", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.97, 0.84, 1.00],
                "pair_width_ratios": [1.18, 1.36, 1.00],
                "blend": 0.93,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.96, 0.84, 1.00],
                "pair_width_ratios": [1.16, 1.38, 1.00],
                "blend": 0.93,
                "min_gap_hz": 60.0,
            },
        },
    },
    {
        "variant_id": "high_blend_v8c",
        "description": "Push blend to 0.96 for masculine and 0.92 for feminine, with moderate center/width moves: tests whether blend ceiling is the bottleneck.",
        "overrides": {
            ("LibriTTS-R", "feminine"): {
                "center_shift_ratios": [1.17, 1.13, 1.08],
                "blend": 0.92,
            },
            ("VCTK Corpus 0.92", "feminine"): {
                "center_shift_ratios": [1.18, 1.14, 1.09],
                "blend": 0.93,
            },
            ("LibriTTS-R", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.96, 0.84, 1.00],
                "pair_width_ratios": [1.12, 1.28, 1.00],
                "blend": 0.96,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.95, 0.84, 1.00],
                "pair_width_ratios": [1.10, 1.30, 1.00],
                "blend": 0.96,
                "min_gap_hz": 60.0,
            },
        },
    },
    {
        "variant_id": "fem_focus_v8d",
        "description": "Spend most of the extra strength on feminine direction to test whether male-to-feminine weakness is the dominant remaining problem.",
        "overrides": {
            ("LibriTTS-R", "feminine"): {
                "center_shift_ratios": [1.22, 1.17, 1.11],
                "blend": 0.90,
            },
            ("VCTK Corpus 0.92", "feminine"): {
                "center_shift_ratios": [1.23, 1.18, 1.12],
                "blend": 0.92,
            },
            ("LibriTTS-R", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.97, 0.84, 1.00],
                "pair_width_ratios": [1.11, 1.26, 1.00],
                "blend": 0.93,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.96, 0.84, 1.00],
                "pair_width_ratios": [1.09, 1.28, 1.00],
                "blend": 0.93,
                "min_gap_hz": 60.0,
            },
        },
    },
    {
        "variant_id": "conservative_v8e",
        "description": "Conservative v8 control: modest step above v7d, serving as safety baseline if stronger variants collapse preservation.",
        "overrides": {
            ("LibriTTS-R", "feminine"): {
                "center_shift_ratios": [1.17, 1.12, 1.08],
                "blend": 0.84,
            },
            ("VCTK Corpus 0.92", "feminine"): {
                "center_shift_ratios": [1.18, 1.13, 1.09],
                "blend": 0.86,
            },
            ("LibriTTS-R", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.97, 0.84, 1.00],
                "pair_width_ratios": [1.11, 1.26, 1.00],
                "blend": 0.93,
            },
            ("VCTK Corpus 0.92", "masculine"): {
                "action_family": "formant_lowering_preserve_air",
                "center_shift_ratios": [0.96, 0.84, 1.00],
                "pair_width_ratios": [1.09, 1.28, 1.00],
                "blend": 0.93,
                "min_gap_hz": 60.0,
            },
        },
    },
]

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preset", choices=["v2", "v3", "v4", "v5", "v6", "v7", "v8"], default="v2")
    parser.add_argument("--base-config", default=str(DEFAULT_BASE_CONFIG))
    parser.add_argument("--input-csv", default=str(DEFAULT_INPUT_CSV))
    parser.add_argument("--sweep-dir", default=str(DEFAULT_SWEEP_DIR))
    parser.add_argument("--pack-root", default=str(DEFAULT_PACK_ROOT))
    parser.add_argument("--variants", default="", help="Comma-separated variant ids. Empty means all.")
    parser.add_argument("--force-rebuild", action="store_true")
    parser.add_argument("--min-avg-quant", type=float, default=65.0)
    parser.add_argument("--min-avg-direction", type=float, default=45.0)
    parser.add_argument("--min-avg-effect", type=float, default=45.0)
    parser.add_argument("--min-top-score", type=float, default=75.0)
    parser.add_argument("--min-strongish-rows", type=int, default=2)
    return parser.parse_args()


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def variant_selection(args: argparse.Namespace) -> list[dict[str, object]]:
    if args.preset == "v2":
        available_specs = VARIANT_SPECS
    elif args.preset == "v3":
        available_specs = V3_VARIANT_SPECS
    elif args.preset == "v4":
        available_specs = V4_VARIANT_SPECS
    elif args.preset == "v5":
        available_specs = V5_VARIANT_SPECS
    elif args.preset == "v6":
        available_specs = V6_VARIANT_SPECS
    elif args.preset == "v7":
        available_specs = V7_VARIANT_SPECS
    else:
        available_specs = V8_VARIANT_SPECS
    if not args.variants.strip():
        return available_specs
    selected = {item.strip() for item in args.variants.split(",") if item.strip()}
    return [spec for spec in available_specs if spec["variant_id"] in selected]


def apply_variant(base_config: dict, spec: dict[str, object], *, preset: str) -> dict:
    payload = deepcopy(base_config)
    payload["config_version"] = f"stage0_speech_lsf_machine_sweep_{spec['variant_id']}"
    payload["source"] = f"representation_layer_lsf_machine_sweep_{preset}"
    payload["selection_policy"]["purpose"] = f"lsf_machine_sweep_{spec['variant_id']}"
    payload["variant_description"] = spec["description"]

    overrides: dict[tuple[str, str], dict[str, object]] = spec["overrides"]  # type: ignore[assignment]
    for rule in payload["rules"]:
        key = (rule["match"]["group_value"], rule["target_direction"])
        params = rule["method_params"]
        if key in overrides:
            for param_name, param_value in overrides[key].items():
                if param_name in {"action_family", "signal_name"}:
                    rule[param_name] = param_value
                else:
                    params[param_name] = param_value
        rule["rule_id"] = re.sub(r"_v\d+$", "", rule["rule_id"]) + f"_{spec['variant_id']}"
        rule["strength"]["label"] = spec["variant_id"]
        rule["notes"] = f"{rule.get('notes', '')} [machine_sweep={spec['variant_id']}]".strip()
    return payload


def run_python(arguments: list[str]) -> None:
    command = [str(ROOT / "python.exe"), *arguments]
    subprocess.run(command, cwd=ROOT, check=True)


def parse_float(value: str) -> float:
    return float(value)


def gate_decision(
    *,
    avg_quant: float,
    avg_direction: float,
    avg_effect: float,
    top_score: float,
    strongish_rows: int,
    args: argparse.Namespace,
) -> tuple[str, str]:
    quant_ok = avg_quant >= float(args.min_avg_quant)
    direction_ok = avg_direction >= float(args.min_avg_direction)
    effect_ok = avg_effect >= float(args.min_avg_effect)
    top_ok = top_score >= float(args.min_top_score)
    rows_ok = strongish_rows >= int(args.min_strongish_rows)
    if quant_ok and direction_ok and effect_ok and (top_ok or rows_ok):
        return "allow_human_review", "meets_primary_machine_gate"
    if top_ok and direction_ok and avg_effect >= float(args.min_avg_effect) * 0.8:
        return "borderline_review_optional", "has_high_top_score_but_pack_average_is_weaker"
    return "skip_human_review", "machine_gate_not_met"


def build_variant_summary(queue_csv: Path, spec: dict[str, object], args: argparse.Namespace) -> dict[str, str]:
    with queue_csv.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    avg_quant = sum(parse_float(row["auto_quant_score"]) for row in rows) / len(rows)
    avg_direction = sum(parse_float(row["auto_direction_score"]) for row in rows) / len(rows)
    avg_effect = sum(parse_float(row["auto_effect_score"]) for row in rows) / len(rows)
    top_score = max(parse_float(row["auto_quant_score"]) for row in rows)
    strong_pass = sum(1 for row in rows if row["auto_quant_grade"] == "strong_pass")
    passed = sum(1 for row in rows if row["auto_quant_grade"] == "pass")
    borderline = sum(1 for row in rows if row["auto_quant_grade"] == "borderline")
    fail = sum(1 for row in rows if row["auto_quant_grade"] == "fail")
    strongish_rows = strong_pass + passed + borderline
    decision, reason = gate_decision(
        avg_quant=avg_quant,
        avg_direction=avg_direction,
        avg_effect=avg_effect,
        top_score=top_score,
        strongish_rows=strongish_rows,
        args=args,
    )
    return {
        "variant_id": str(spec["variant_id"]),
        "description": str(spec["description"]),
        "queue_csv": str(queue_csv),
        "avg_auto_quant_score": f"{avg_quant:.2f}",
        "avg_auto_direction_score": f"{avg_direction:.2f}",
        "avg_auto_effect_score": f"{avg_effect:.2f}",
        "top_auto_quant_score": f"{top_score:.2f}",
        "strong_pass_rows": str(strong_pass),
        "pass_rows": str(passed),
        "borderline_rows": str(borderline),
        "fail_rows": str(fail),
        "strongish_rows": str(strongish_rows),
        "machine_gate_decision": decision,
        "machine_gate_reason": reason,
    }


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError("No rows to write.")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_markdown(rows: list[dict[str, str]], args: argparse.Namespace) -> str:
    lines = [
        f"# LSF Machine Sweep {args.preset.upper()}",
        "",
        "## Gate Thresholds",
        "",
        f"- `avg_auto_quant_score >= {args.min_avg_quant:.2f}`",
        f"- `avg_auto_direction_score >= {args.min_avg_direction:.2f}`",
        f"- `avg_auto_effect_score >= {args.min_avg_effect:.2f}`",
        f"- and (`top_auto_quant_score >= {args.min_top_score:.2f}` or `strongish_rows >= {args.min_strongish_rows}`)",
        "",
        "## Variant Ranking",
        "",
    ]
    for row in rows:
        lines.extend(
            [
                f"### `{row['variant_id']}`",
                "",
                f"- decision: `{row['machine_gate_decision']}`",
                f"- reason: `{row['machine_gate_reason']}`",
                f"- avg quant / direction / effect: `{row['avg_auto_quant_score']}` / `{row['avg_auto_direction_score']}` / `{row['avg_auto_effect_score']}`",
                f"- top score: `{row['top_auto_quant_score']}`",
                f"- strong/pass/borderline/fail: `{row['strong_pass_rows']}` / `{row['pass_rows']}` / `{row['borderline_rows']}` / `{row['fail_rows']}`",
                f"- description: {row['description']}",
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    base_config = load_json(resolve_path(args.base_config))
    sweep_dir = resolve_path(args.sweep_dir)
    pack_root = resolve_path(args.pack_root)
    selected_specs = variant_selection(args)
    if not selected_specs:
        raise ValueError("No LSF sweep variants selected.")

    summary_rows: list[dict[str, str]] = []
    for spec in selected_specs:
        variant_id = str(spec["variant_id"])
        config_payload = apply_variant(base_config, spec, preset=args.preset)
        config_path = sweep_dir / "configs" / f"{variant_id}.json"
        pack_dir = pack_root / variant_id
        summary_csv = pack_dir / "listening_pack_summary.csv"
        queue_csv = pack_dir / "listening_review_queue.csv"
        summary_md = pack_dir / "listening_review_quant_summary.md"

        save_json(config_path, config_payload)

        if args.force_rebuild or not summary_csv.exists():
            run_python(
                [
                    str(ROOT / "scripts" / "build_stage0_speech_lsf_listening_pack.py"),
                    "--rule-config",
                    str(config_path),
                    "--input-csv",
                    str(resolve_path(args.input_csv)),
                    "--output-dir",
                    str(pack_dir),
                ]
            )

        run_python(
            [
                str(ROOT / "scripts" / "build_stage0_rule_review_queue.py"),
                "--rule-config",
                str(config_path),
                "--summary-csv",
                str(summary_csv),
                "--output-csv",
                str(queue_csv),
                "--summary-md",
                str(summary_md),
                "--reuse-cache",
            ]
        )

        summary_rows.append(build_variant_summary(queue_csv, spec, args))

    summary_rows.sort(
        key=lambda row: (
            row["machine_gate_decision"] != "allow_human_review",
            -float(row["avg_auto_quant_score"]),
            row["variant_id"],
        )
    )
    write_rows(sweep_dir / "lsf_machine_sweep_pack_summary.csv", summary_rows)
    markdown_name = f"LSF_MACHINE_SWEEP_{args.preset.upper()}.md"
    (sweep_dir / markdown_name).write_text(build_markdown(summary_rows, args), encoding="utf-8")
    print(f"Wrote {sweep_dir / 'lsf_machine_sweep_pack_summary.csv'}")
    print(f"Wrote {sweep_dir / markdown_name}")
    print(f"Variants: {len(summary_rows)}")


if __name__ == "__main__":
    main()
