"""Engine location + snapshot-dir redirect for the standalone GCC repo.

The `final_earnings` engine is consumed as a git submodule (./final_earnings).
Snapshots, however, live in THIS repo's data/marketscreener/ — not inside the
submodule — so they're versioned here. use_gcc_snapshots() points the engine's
snapshot locator at our dir for both reads (daily refresh) and writes (the
snapshot-refresh Action).

Resolution order for the engine root:
  1. $ENGINE_ROOT
  2. ./final_earnings   (submodule, on CI and after `git submodule update`)
  3. ~/final_earnings   (local dev fallback)
"""
from __future__ import annotations
import os, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SNAP_DIR = HERE / "data" / "marketscreener"


def _engine_root() -> Path:
    # Require the engine's company_master.json so a half-cloned submodule
    # doesn't shadow a working local checkout.
    for cand in (os.environ.get("ENGINE_ROOT"), HERE / "final_earnings",
                 Path.home() / "final_earnings"):
        if cand and (Path(cand) / "data" / "company_master.json").exists():
            return Path(cand)
    raise RuntimeError("final_earnings engine not found — set ENGINE_ROOT or add the submodule")


ENGINE_ROOT = _engine_root()
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))


def use_gcc_snapshots() -> Path:
    """Redirect the engine's MS snapshot locator to this repo's data dir."""
    SNAP_DIR.mkdir(parents=True, exist_ok=True)
    import src.providers.marketscreener_pages as msp

    def _patched(cache_slug: str):
        safe = re.sub(r"[^a-zA-Z0-9-]", "_", cache_slug)[:80]
        return SNAP_DIR / f"ms_{safe}.html"

    msp._snapshot_path_for = _patched
    return SNAP_DIR
