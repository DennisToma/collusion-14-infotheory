No remaining material correctness issues in the latest diff. No files edited.

- **Table checking:** [check()/normalized()](/home/factory/collusion/collusion-14-infotheory/scripts/report_tables.py:269) covers all 11 quantitative tables, including headers and 404 body cells. Overview and pilot history are explicitly excluded. Numeric mutations in every table, plus sign, inequality, CI-bound, and header mutations, were rejected.
- **Sweep summary:** The gap identified during review was fixed concurrently. [sweep()](/home/factory/collusion/collusion-14-infotheory/scripts/report_tables.py:95) now checks every selected pCMI top-1 value; the previously accepted source-data mutation now fails.
- **Release runner:** [RECOMPUTE/RENDER](/home/factory/collusion/collusion-14-infotheory/scripts/verify_release.py:31) uses committed local inputs, with no LLM calls or live sibling-data access. Its documented scope is later analyses and rendering; primary evaluations remain stored inputs. Exit codes and output hashes determine failure.
- **PDF export:** [main()](/home/factory/collusion/collusion-14-infotheory/scripts/export_pdf.py:139) now exits unsuccessfully for missing text, incorrect slide count, or detected overflow.

All three display corrections match source JSON: maximum TE top-1 **0.175 → ≤0.18**, TFT MI range **0.525–0.55 → 0.53–0.55**, and preplay CI upper bound **1.625 → 1.62** under the formatter’s rounding.

Table and checksum checks ran successfully. The full release/export pipeline was reviewed statically, not executed, because it writes files.