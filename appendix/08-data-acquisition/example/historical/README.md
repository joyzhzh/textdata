# Historical comparison records

These are records of the two official-site retrievals on 31 October 2026, before the email removal applied to the released text copies. The inventory and reading-copy fingerprints describe the original files, which are not distributed here. The recorded result remains 191 matching identifiers, 169 historical raw-file matches, 22 unresolved discrepancies, and identical original reading copies for all 191 documents across the two sites.

`../verify_historical.py` recomputes the original raw-file comparison from these fingerprint records and the retained December 2020 inventory. It verifies the recorded equality of the two sets of original reading-copy fingerprints. It cannot re-hash the withheld original text or establish the cause of the 22 discrepancies. `../RELEASE_PROVENANCE.json` links the released text copies to their recorded original fingerprints and lists the transformation counts.

The files under `../output/` instead describe the email-redacted release copies. Replaying those copies is a different check; its comparison with historical hashes must not be substituted for the original 169/22 result. Source timestamps and historical labels in this directory are unchanged.
