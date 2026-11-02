# Available text and inventories

All 321 monthly inventories are included. The full historical text collection is not distributed; the appendix supplies a 191-document example for 7–8 December 2020. The 704 records without text remain in the inventories.

The example pack is example/output/run/packs/text-2020-12.tar.xz, relative to the appendix folder. Check it and generate reading copies with:

    python3 tool/verify.py --repo example/output/run/collection --packs-dir example/output/run/packs --all
    python3 tool/clean_text.py example/output/run/packs/text-2020-12.tar.xz --out my-clean

The expected result is 191 verified files, then 191 reading copies. Supplied text has email addresses removed. Cleaning does not restore images or validate interpretation.

The original comparison found 169 raw-file matches and 22 unresolved differences. Original fingerprints are retained in example/historical/; original text is withheld. A replay of the released copies is a separate comparison, as explained in the README.
