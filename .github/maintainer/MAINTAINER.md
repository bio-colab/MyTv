# Maintainer Guide

Guidelines for maintaining the **bio-colab/MyTv** repository:

1. **Reviewing PRs**:
   - Check that no core Android packages are disabled (`tools/check.py`).
   - Ensure regional streaming apps (Shahid, TOD, beIN, Watch IT, etc.) and AOSP app stores are protected.
   - Verify hardware tier requirements.

2. **After Merging TV Profiles**:
   - Run `python3 tools/gen_tables.py` to regenerate the TV models table.
   - Commit and push to `main`.
