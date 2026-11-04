# Replication report (auto-generated)

## Instances

| sweep      |   ok |
|:-----------|-----:|
| gamma      |    3 |
| initial_ps |    3 |
| requests   |    3 |

beta actually used by the generator (D6 fallback):

|                      |   mean |   min |   max |
|:---------------------|-------:|------:|------:|
| ('gamma', 1.3)       |  0.1   | 0.1   | 0.1   |
| ('initial_ps', 15.0) |  0.125 | 0.125 | 0.125 |
| ('requests', 200.0)  |  0.125 | 0.125 | 0.125 |

## FIG3 - paired savings of RPSP-APSP (%)

| sweep      |   value | baseline   |   n_paired |   saving_pct |
|:-----------|--------:|:-----------|-----------:|-------------:|
| gamma      |     1.3 | RAS        |          3 |        85.54 |
| gamma      |     1.3 | SPS        |          3 |        79.07 |
| initial_ps |    15   | RAS        |          3 |        61.34 |
| initial_ps |    15   | SPS        |          3 |        52.53 |
| requests   |   200   | RAS        |          2 |        61.36 |
| requests   |   200   | SPS        |          2 |        58.54 |

non-ok (timeout/error/skipped) rows: 1

## FIG4 - paired savings of RPSP (%)

| sweep      |   value | baseline     |   n_paired |   saving_pct |
|:-----------|--------:|:-------------|-----------:|-------------:|
| gamma      |     1.3 | RPD+GD       |          3 |         0    |
| gamma      |     1.3 | RPD+GD-naive |          3 |        10.13 |
| gamma      |     1.3 | SP+PSP       |          3 |        27.55 |
| initial_ps |    15   | RPD+GD       |          3 |         0    |
| initial_ps |    15   | RPD+GD-naive |          3 |         4.85 |
| initial_ps |    15   | SP+PSP       |          3 |        20.33 |
| requests   |   200   | RPD+GD       |          2 |         0    |
| requests   |   200   | RPD+GD-naive |          2 |         3.64 |
| requests   |   200   | SP+PSP       |          2 |        41.44 |

non-ok (timeout/error/skipped) rows: 3

## Replication vs. paper

| comparison | this run: max saving over all sweeps (where) | paper |
|---|---|---|

| fig3 RPSP vs RAS | 85.5% (gamma=1.3) | up to 98.33% (gamma=1.3); 89% over node sweep; abstract: 87% |

| fig3 RPSP vs SPS | 79.1% (gamma=1.3) | up to 98.13% (gamma=1.3); 93% over node sweep |

| fig4 RPSP vs RPD+GD | 0.0% (requests=200.0) | up to 51% (node sweep); 43.76% at 200 requests; abstract: 36% |

| fig4 RPSP vs SP+PSP | 41.4% (requests=200.0) | up to 46% (node sweep); 27.09% at 200 requests; 26% in summary |


The paper itself quotes different headline numbers in the abstract (87% / 36%), the findings list (98.33% / 98.13%, 36% / 26%) and Sec. V-C (51% / 46%), so no single 'target' exists. Discrepancy notes are in REPLICATION_NOTES.md.
