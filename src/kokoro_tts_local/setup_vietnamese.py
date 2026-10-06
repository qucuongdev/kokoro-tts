"""Download the pinned Vietnamese model and compatible voices."""

import argparse
import os
import tempfile
from pathlib import Path

from .console import enable_utf8_console
from .paths import get_vietnamese_model_dir, get_voices_dir
from .vietnamese import VI_MODEL_REPO, VI_MODEL_REVISION, VI_VOICES


def download_artifact(remote, target):
    """Download to a sibling temporary directory before publishing a file."""
    from huggingface_hub import hf_hub_download

    target = Path(target)
    if target.is_file() and target.stat().st_size > 0:
        print(f"Already downloaded: {target}", flush=True)
        return
    if target.exists():
        raise ValueError(f"Invalid artifact path: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=target.parent) as staging:
        source = hf_hub_download(
            repo_id=VI_MODEL_REPO,
            filename=remote,
            revision=VI_MODEL_REVISION,
            local_dir=staging,
        )
        if not Path(source).is_file() or Path(source).stat().st_size == 0:
            raise ValueError(f"Downloaded artifact is empty: {remote}")
        os.replace(source, target)
    print(f"Downloaded: {target}", flush=True)


def main():
    enable_utf8_console()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all-voices", action="store_true", help="Download all 14 voices")
    args = parser.parse_args()
    model_dir = get_vietnamese_model_dir()
    download_artifact("config.json", model_dir / "config.json")
    download_artifact("kokoro_vi.pth", model_dir / "kokoro_vi.pth")
    names = VI_VOICES if args.all_voices else ["diem_trinh"]
    for name in names:
        # Reuse either spelling accepted by the router.
        prefixed = get_voices_dir() / f"vi_{name}.pt"
        if prefixed.is_file() and prefixed.stat().st_size > 0:
            print(f"Already downloaded: {prefixed}", flush=True)
            continue
        download_artifact(f"voicepacks/{name}.pt", get_voices_dir() / f"{name}.pt")
    print("Vietnamese setup complete. Start CHAY_TTS.cmd and select vi_diem_trinh.")


if __name__ == "__main__":
    main()
