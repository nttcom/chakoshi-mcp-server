"""Tests for the post quantum attestation of moderation verdicts.

These tests need the pq extra (dilithium-py). They do not touch the network or
the chakoshi API, so they run without the chakoshi environment variables.
"""

import os
import tempfile

import pytest

pytest.importorskip("dilithium_py")

from chakoshi_server import pq_attestation as pqa  # noqa: E402

VERDICT = {
    "id": "chk_123",
    "guardrail_id": "gr_main",
    "assessments": [{"label": "safe", "score": 0.02}],
}


def test_build_and_verify_roundtrip():
    public_key, secret_key = pqa.generate_keypair()
    attestation = pqa.build_attestation(VERDICT, public_key, secret_key)
    assert attestation["scheme"] == "ML-DSA-65"
    assert attestation["issuer"] == "Quantova"
    assert pqa.verify_attestation(VERDICT, attestation) is True
    assert pqa.verify_attestation(VERDICT, attestation, expected_public_key=public_key) is True


def test_tampered_verdict_is_rejected():
    public_key, secret_key = pqa.generate_keypair()
    attestation = pqa.build_attestation(VERDICT, public_key, secret_key)
    altered = dict(VERDICT)
    altered["assessments"] = [{"label": "unsafe", "score": 0.99}]
    assert pqa.verify_attestation(altered, attestation) is False


def test_wrong_signer_is_rejected_when_pinned():
    public_key, secret_key = pqa.generate_keypair()
    other_public_key, _ = pqa.generate_keypair()
    attestation = pqa.build_attestation(VERDICT, public_key, secret_key)
    assert pqa.verify_attestation(VERDICT, attestation, expected_public_key=other_public_key) is False


def test_forged_signature_is_rejected():
    public_key, secret_key = pqa.generate_keypair()
    attestation = pqa.build_attestation(VERDICT, public_key, secret_key)
    attestation["signature"] = pqa.base64.b64encode(b"\x00" * 64).decode("ascii")
    assert pqa.verify_attestation(VERDICT, attestation) is False


def test_key_file_roundtrip():
    public_key, secret_key = pqa.generate_keypair()
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "signer.json")
        pqa.save_signer(path, public_key, secret_key)
        loaded_public, loaded_secret = pqa.load_signer(path)
    assert loaded_public == public_key
    assert loaded_secret == secret_key


def test_canonical_bytes_are_order_independent():
    first = pqa.canonical_bytes({"a": 1, "b": 2})
    second = pqa.canonical_bytes({"b": 2, "a": 1})
    assert first == second
