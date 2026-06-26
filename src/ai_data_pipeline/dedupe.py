from __future__ import annotations

import hashlib
import re

from .models import ProcessedSample


def deduplicate_samples(
    samples: list[ProcessedSample],
    similarity_threshold: float = 0.88,
) -> tuple[list[ProcessedSample], dict[str, int]]:
    seen_exact: set[str] = set()
    accepted: list[ProcessedSample] = []
    stats = {"exact_duplicates": 0, "near_duplicates": 0, "kept": 0}

    for sample in samples:
        exact_key = _exact_key(sample)
        if exact_key in seen_exact:
            stats["exact_duplicates"] += 1
            continue

        duplicate = False
        for old_sample in accepted:
            similarity = jaccard_similarity(sample.question + sample.answer, old_sample.question + old_sample.answer)
            if similarity >= similarity_threshold:
                stats["near_duplicates"] += 1
                duplicate = True
                break

        if duplicate:
            continue

        seen_exact.add(exact_key)
        accepted.append(sample)
        stats["kept"] += 1

    return accepted, stats


def _exact_key(sample: ProcessedSample) -> str:
    return re.sub(r"\W+", "", (sample.question + sample.answer).lower())


class StreamingDeduper:
    def __init__(self) -> None:
        self.exact_keys: set[bytes] = set()
        self.near_keys: set[bytes] = set()
        self.stats = {"exact_duplicates": 0, "near_duplicates": 0, "kept": 0}

    def accept(self, sample: ProcessedSample) -> bool:
        exact_digest = hashlib.blake2b(_exact_key(sample).encode("utf-8"), digest_size=12).digest()
        if exact_digest in self.exact_keys:
            self.stats["exact_duplicates"] += 1
            return False

        near_digest = hashlib.blake2b(_near_key(sample).encode("utf-8"), digest_size=12).digest()
        if near_digest in self.near_keys:
            self.stats["near_duplicates"] += 1
            return False

        self.exact_keys.add(exact_digest)
        self.near_keys.add(near_digest)
        self.stats["kept"] += 1
        return True


def _near_key(sample: ProcessedSample) -> str:
    text = (sample.question + sample.answer).lower()
    replacements = {
        "如何": "怎么",
        "为什么": "为啥",
        "可以": "建议",
        "需要": "要",
        "，": ",",
        "。": ".",
        "？": "?",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return re.sub(r"\W+", "", text)


def jaccard_similarity(left: str, right: str, n: int = 3) -> float:
    left_grams = _char_ngrams(left, n)
    right_grams = _char_ngrams(right, n)
    if not left_grams or not right_grams:
        return 0.0
    return len(left_grams & right_grams) / len(left_grams | right_grams)


def _char_ngrams(text: str, n: int) -> set[str]:
    compact = re.sub(r"\s+", "", text.lower())
    if len(compact) <= n:
        return {compact} if compact else set()
    return {compact[index : index + n] for index in range(len(compact) - n + 1)}


def simhash(text: str, bits: int = 64) -> int:
    weights = [0] * bits
    for token in _char_ngrams(text, 3):
        digest = int.from_bytes(hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest(), "big")
        for bit in range(bits):
            if digest & (1 << bit):
                weights[bit] += 1
            else:
                weights[bit] -= 1

    fingerprint = 0
    for bit, weight in enumerate(weights):
        if weight >= 0:
            fingerprint |= 1 << bit
    return fingerprint


def simhash_bands(fingerprint: int, bands: int = 4, band_bits: int = 16):
    for band in range(bands):
        mask = (1 << band_bits) - 1
        yield band, (fingerprint >> (band * band_bits)) & mask


def hamming_distance(left: int, right: int) -> int:
    return (left ^ right).bit_count()
