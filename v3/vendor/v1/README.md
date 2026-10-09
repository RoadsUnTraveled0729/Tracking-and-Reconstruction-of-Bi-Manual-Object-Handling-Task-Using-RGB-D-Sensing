# vendor/v1: verbatim v1 oracles

These files are VERBATIM copies from the thesis tree at master commit
ee7079f7157daf610608af93b4504dc6f9fad427 (copied 2026-08-06):

    kinematics/root_frame.py  -> root_frame.py
    kinematics/shoulder.py    -> shoulder.py
    kinematics/occlusion.py   -> occlusion.py

Rules:

1. NEVER edit these files. They are the numerical oracles that define
   the comparability contract: V3's convert.py must reproduce their
   angle output to 1e-9 deg on identical inputs.
2. MANIFEST.sha256 records their hashes at copy time;
   tests/test_vendor_integrity.py verifies the files still match. If a
   hash test fails, the copy was edited: restore it, never update the
   manifest to match an edit.
3. They import each other flat (occlusion.py does
   "from root_frame import ...", "from shoulder import ..."), so any
   V3 code using them puts THIS directory on sys.path. No V3 code ever
   adds the thesis tree to sys.path.
