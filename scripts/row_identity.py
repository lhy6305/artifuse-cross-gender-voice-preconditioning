from __future__ import annotations

import hashlib
import re


_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


def _slugify_fragment(value: str) -> str:
    text = value.strip().lower()
    text = _NON_ALNUM_RE.sub("_", text)
    return text.strip("_") or "na"


def build_record_id(
    *,
    dataset_name: str,
    speaker_id: str,
    utt_id: str,
    path_raw: str = "",
) -> str:
    digest_source = path_raw or "|".join([dataset_name, speaker_id, utt_id])
    digest = hashlib.sha1(digest_source.encode("utf-8")).hexdigest()[:10]
    return "__".join(
        [
            _slugify_fragment(dataset_name),
            _slugify_fragment(speaker_id),
            _slugify_fragment(utt_id),
            digest,
        ]
    )


def get_record_id(row: dict[str, str]) -> str:
    existing = row.get("record_id", "").strip()
    if existing:
        return existing
    return build_record_id(
        dataset_name=row.get("dataset_name", ""),
        speaker_id=row.get("speaker_id", ""),
        utt_id=row.get("utt_id", ""),
        path_raw=row.get("path_raw", ""),
    )


def get_filename_token(row: dict[str, str]) -> str:
    return _slugify_fragment(get_record_id(row))
