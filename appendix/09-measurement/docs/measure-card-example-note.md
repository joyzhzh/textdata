# Worked measure card

[The teaching card](../example/input/ASKIN_MEASURE_CARD.jsonl) documents a musical-typicality measure using sonic features. It demonstrates a reusable record format, not a validated text measure. Uninspected details remain unknown.

Each field is `reported`, `unknown`, `not_applicable` or `proposed`. Reported values need source locators; unknown and inapplicable fields stay empty and give reasons. Proposed choices cannot be presented as published methods.

From the component folder:

```sh
python3 tool/scripts/validate_measure_cards.py example/input/ASKIN_MEASURE_CARD.jsonl
python3 tool/scripts/validate_measure_cards.py --submission example/input/ASKIN_MEASURE_CARD.jsonl
```

The first checks structure; the second refuses teaching material as intended. Neither checks source support or scientific validity. See [the full citation and licences](../NOTICE.md).
