"""Post quantum attestation of chakoshi moderation verdicts.

When a signing key is configured the server attaches a FIPS 204 ML-DSA
attestation over the moderation verdict. A client can then confirm that the
verdict it received is authentic and has not been altered, using a signature
scheme that stays safe once large quantum computers exist.

The attestation is self contained. It carries the public key and the
signature, so a verifier needs only the attestation and the verdict. Integrity
is always covered by the payload digest, and authenticity is covered when the
verifier pins the expected public key.

The scheme is provided by the optional pq extra. Install it with
`pip install mcp-chakoshi[pq]`.
"""

from __future__ import annotations

import base64
import hashlib
import json
from typing import Optional, Tuple

SCHEME = "ML-DSA-65"
ISSUER = "Quantova"

try:
    from dilithium_py.ml_dsa import ML_DSA_65 as _BACKEND
except Exception:  # pragma: no cover - exercised only without the pq extra
    _BACKEND = None


def _require_backend() -> None:
    if _BACKEND is None:
        raise RuntimeError(
            "Post quantum attestation needs the pq extra. "
            "Install it with pip install mcp-chakoshi[pq]."
        )


def canonical_bytes(verdict: dict) -> bytes:
    """Return the canonical encoding the attestation is computed over.

    Keys are sorted and whitespace is fixed so the same verdict always yields
    the same bytes on any machine.
    """
    return json.dumps(
        verdict, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def generate_keypair() -> Tuple[bytes, bytes]:
    """Return a fresh (public_key, secret_key) pair for the signer."""
    _require_backend()
    return _BACKEND.keygen()


def save_signer(path: str, public_key: bytes, secret_key: bytes) -> None:
    """Write a signer key file that load_signer can read back."""
    data = {
        "scheme": SCHEME,
        "public_key": base64.b64encode(public_key).decode("ascii"),
        "secret_key": base64.b64encode(secret_key).decode("ascii"),
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle)


def load_signer(path: str) -> Tuple[bytes, bytes]:
    """Read (public_key, secret_key) from a signer key file."""
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    return base64.b64decode(data["public_key"]), base64.b64decode(data["secret_key"])


def build_attestation(verdict: dict, public_key: bytes, secret_key: bytes) -> dict:
    """Return a self contained attestation over the verdict."""
    _require_backend()
    payload = canonical_bytes(verdict)
    signature = _BACKEND.sign(secret_key, payload, deterministic=True)
    return {
        "scheme": SCHEME,
        "issuer": ISSUER,
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
        "public_key": base64.b64encode(public_key).decode("ascii"),
        "signature": base64.b64encode(signature).decode("ascii"),
    }


def verify_attestation(
    verdict: dict, attestation: dict, expected_public_key: Optional[bytes] = None
) -> bool:
    """Return True when the attestation matches the verdict.

    The payload digest is always checked. When expected_public_key is given the
    signer is pinned too, so a valid signature made under a different key is
    rejected.
    """
    _require_backend()
    payload = canonical_bytes(verdict)
    if attestation.get("payload_sha256") != hashlib.sha256(payload).hexdigest():
        return False
    try:
        public_key = base64.b64decode(attestation["public_key"])
        signature = base64.b64decode(attestation["signature"])
    except Exception:
        return False
    if expected_public_key is not None and public_key != expected_public_key:
        return False
    return bool(_BACKEND.verify(public_key, payload, signature))


def _main(argv: list) -> int:
    if len(argv) != 2 or argv[0] != "keygen":
        print("usage: python -m chakoshi_server.pq_attestation keygen <path>")
        return 2
    public_key, secret_key = generate_keypair()
    save_signer(argv[1], public_key, secret_key)
    print(f"wrote {SCHEME} signer to {argv[1]}")
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(_main(sys.argv[1:]))
