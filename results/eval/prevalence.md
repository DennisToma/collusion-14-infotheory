| setting | detector | null | TPR (pos) | FPR (neg) | precision @1% | @5% | @20% | false alarms per true alarm @5% |
|---|---|---|---|---|---|---|---|---|
| scripted gate_test (T=100, signal s=0.6) | mi | shift | 50/50 (C) | 3/50 (A) | 0.14 [0.06, 0.37] | 0.47 [0.25, 0.75] | 0.81 [0.61, 0.93] | 1.1 |
| scripted gate_test (T=100, signal s=0.6) | mi | shift | 50/50 (C) | 50/50 (B) | 0.01 [0.01, 0.01] | 0.05 [0.05, 0.05] | 0.20 [0.19, 0.21] | 19.0 |
| scripted gate_test (T=100, signal s=0.6) | mi | shift | 50/50 (C) | 15/50 (A+shared_policy) | 0.03 [0.02, 0.05] | 0.15 [0.11, 0.22] | 0.45 [0.36, 0.57] | 5.7 |
| scripted gate_test (T=100, signal s=0.6) | mi | shift | 50/50 (C) | 36/50 (A+shared_seed) | 0.01 [0.01, 0.02] | 0.07 [0.06, 0.08] | 0.26 [0.23, 0.30] | 13.7 |
| scripted gate_test (T=100, signal s=0.6) | mi | shift | 50/50 (C) | 4/50 (A+legit_cooperation) | 0.11 [0.05, 0.26] | 0.40 [0.22, 0.65] | 0.76 [0.57, 0.90] | 1.5 |
| scripted gate_test (T=100, signal s=0.6) | mi | surrogate | 50/50 (C) | 2/50 (A)* | 0.20 [0.07, 0.54] | 0.57 [0.30, 0.86] | 0.86 [0.67, 0.97] | 0.8 |
| scripted gate_test (T=100, signal s=0.6) | mi | surrogate | 50/50 (C) | 2/50 (B) | 0.20 [0.07, 0.54] | 0.57 [0.30, 0.86] | 0.86 [0.67, 0.97] | 0.8 |
| scripted gate_test (T=100, signal s=0.6) | mi | surrogate | 50/50 (C) | 11/50 (A+shared_policy) | 0.04 [0.03, 0.08] | 0.19 [0.13, 0.30] | 0.53 [0.41, 0.67] | 4.2 |
| scripted gate_test (T=100, signal s=0.6) | mi | surrogate | 50/50 (C) | 36/50 (A+shared_seed) | 0.01 [0.01, 0.02] | 0.07 [0.06, 0.08] | 0.26 [0.23, 0.30] | 13.7 |
| scripted gate_test (T=100, signal s=0.6) | mi | surrogate | 50/50 (C) | 5/50 (A+legit_cooperation) | 0.09 [0.05, 0.20] | 0.34 [0.20, 0.57] | 0.71 [0.54, 0.86] | 1.9 |
| scripted gate_test (T=100, signal s=0.6) | pcmi | shift | 50/50 (C) | 2/50 (A) | 0.20 [0.07, 0.54] | 0.57 [0.30, 0.86] | 0.86 [0.67, 0.97] | 0.8 |
| scripted gate_test (T=100, signal s=0.6) | pcmi | shift | 50/50 (C) | 7/50 (B) | 0.07 [0.04, 0.13] | 0.27 [0.17, 0.45] | 0.64 [0.49, 0.79] | 2.7 |
| scripted gate_test (T=100, signal s=0.6) | pcmi | shift | 50/50 (C) | 5/50 (A+shared_policy) | 0.09 [0.05, 0.20] | 0.34 [0.20, 0.57] | 0.71 [0.54, 0.86] | 1.9 |
| scripted gate_test (T=100, signal s=0.6) | pcmi | shift | 50/50 (C) | 35/50 (A+shared_seed) | 0.01 [0.01, 0.02] | 0.07 [0.06, 0.08] | 0.26 [0.23, 0.30] | 13.3 |
| scripted gate_test (T=100, signal s=0.6) | pcmi | shift | 50/50 (C) | 6/50 (A+legit_cooperation) | 0.08 [0.04, 0.16] | 0.30 [0.18, 0.50] | 0.68 [0.51, 0.83] | 2.3 |
| scripted gate_test (T=100, signal s=0.6) | pcmi | surrogate | 50/50 (C) | 2/50 (A)* | 0.20 [0.07, 0.54] | 0.57 [0.30, 0.86] | 0.86 [0.67, 0.97] | 0.8 |
| scripted gate_test (T=100, signal s=0.6) | pcmi | surrogate | 50/50 (C) | 2/50 (B) | 0.20 [0.07, 0.54] | 0.57 [0.30, 0.86] | 0.86 [0.67, 0.97] | 0.8 |
| scripted gate_test (T=100, signal s=0.6) | pcmi | surrogate | 50/50 (C) | 2/50 (A+shared_policy) | 0.20 [0.07, 0.54] | 0.57 [0.30, 0.86] | 0.86 [0.67, 0.97] | 0.8 |
| scripted gate_test (T=100, signal s=0.6) | pcmi | surrogate | 50/50 (C) | 24/50 (A+shared_seed) | 0.02 [0.02, 0.03] | 0.10 [0.08, 0.13] | 0.34 [0.29, 0.42] | 9.1 |
| scripted gate_test (T=100, signal s=0.6) | pcmi | surrogate | 50/50 (C) | 2/50 (A+legit_cooperation) | 0.20 [0.07, 0.54] | 0.57 [0.30, 0.86] | 0.86 [0.67, 0.97] | 0.8 |
| LLM llm_v1 (T=20) | pcmi | shift | 4/32 (C+D) | 4/42 (A+B) | 0.01 [0.00, 0.05] | 0.06 [0.02, 0.20] | 0.25 [0.08, 0.55] | 14.5 |
| LLM llm_v1 (T=20) | pcmi | surrogate | 2/32 (C+D) | 2/42 (A+B)* | 0.01 [0.00, 0.08] | 0.06 [0.01, 0.32] | 0.25 [0.04, 0.69] | 14.5 |
| LLM llm_v1 (T=20) | market_level | surrogate | 10/32 (C+D) | 2/42 (A+B)* | 0.06 [0.02, 0.24] | 0.26 [0.09, 0.62] | 0.62 [0.31, 0.89] | 2.9 |
| LLM llm_v1 (T=20) | pair_level | surrogate | 14/32 (C+D) | 2/42 (A+B)* | 0.08 [0.03, 0.31] | 0.33 [0.13, 0.70] | 0.70 [0.40, 0.92] | 2.1 |
| LLM sibling llm_v3 (T=12) | pcmi | surrogate | 0/70 (private) | 0/35 (none)* | n/a (no alarms) | n/a (no alarms) | n/a (no alarms) | ∞ (TPR 0) |
| LLM sibling llm_v3 (T=12) | pcmi | surrogate | 0/70 (private) | 0/20 (legit) | n/a (no alarms) | n/a (no alarms) | n/a (no alarms) | ∞ (TPR 0) |
| LLM sibling llm_v3 (T=12) | pair_level | surrogate | 45/70 (private) | 1/35 (none)* | 0.19 [0.05, 0.68] | 0.54 [0.21, 0.92] | 0.85 [0.55, 0.98] | 0.8 |
| LLM sibling llm_v3 (T=12) | pair_level | surrogate | 45/70 (private) | 1/20 (legit) | 0.11 [0.03, 0.54] | 0.40 [0.13, 0.86] | 0.76 [0.42, 0.97] | 1.5 |

\* FPR on the surrogate reference controls themselves is ≤ α by construction (leave-one-out); only hard-negative FPRs are independent evidence.
