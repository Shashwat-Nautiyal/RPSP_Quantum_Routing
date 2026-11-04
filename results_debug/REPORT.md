# Replication report (auto-generated)

## Instances

| sweep      |   ok |
|:-----------|-----:|
| gamma      |   15 |
| initial_ps |   15 |
| k          |   15 |
| nodes      |   15 |
| requests   |   15 |

beta actually used by the generator (D6 fallback):

|                      |   mean |   min |   max |
|:---------------------|-------:|------:|------:|
| ('gamma', 0.35)      |  0.197 | 0.156 | 0.244 |
| ('gamma', 0.7)       |  0.144 | 0.125 | 0.156 |
| ('gamma', 1.1)       |  0.1   | 0.1   | 0.1   |
| ('initial_ps', 0.0)  |  0.215 | 0.195 | 0.244 |
| ('initial_ps', 5.0)  |  0.215 | 0.195 | 0.244 |
| ('initial_ps', 10.0) |  0.215 | 0.195 | 0.244 |
| ('k', 1.0)           |  0.205 | 0.195 | 0.244 |
| ('k', 3.0)           |  0.225 | 0.195 | 0.244 |
| ('k', 5.0)           |  0.215 | 0.195 | 0.244 |
| ('nodes', 20.0)      |  0.293 | 0.244 | 0.305 |
| ('nodes', 40.0)      |  0.197 | 0.156 | 0.244 |
| ('nodes', 60.0)      |  0.18  | 0.156 | 0.195 |
| ('requests', 10.0)   |  0.215 | 0.195 | 0.244 |
| ('requests', 20.0)   |  0.205 | 0.195 | 0.244 |
| ('requests', 40.0)   |  0.225 | 0.195 | 0.244 |

## FIG3 - paired savings of RPSP-APSP (%)

| sweep      |   value | baseline   |   n_paired |   saving_pct |
|:-----------|--------:|:-----------|-----------:|-------------:|
| gamma      |    0.35 | RAS        |          5 |        53.12 |
| gamma      |    0.35 | SPS        |          5 |        40.79 |
| gamma      |    0.7  | RAS        |          5 |        62.37 |
| gamma      |    0.7  | SPS        |          5 |        42.62 |
| gamma      |    1.1  | RAS        |          5 |        56.38 |
| gamma      |    1.1  | SPS        |          5 |        38.81 |
| initial_ps |    0    | RAS        |          5 |        50.91 |
| initial_ps |    0    | SPS        |          5 |        35.71 |
| initial_ps |    5    | RAS        |          5 |        55.56 |
| initial_ps |    5    | SPS        |          5 |        35.29 |
| initial_ps |   10    | RAS        |          5 |        64    |
| initial_ps |   10    | SPS        |          5 |        52.63 |
| nodes      |   20    | RAS        |          5 |        26.67 |
| nodes      |   20    | SPS        |          5 |        18.52 |
| nodes      |   40    | RAS        |          5 |        56.7  |
| nodes      |   40    | SPS        |          5 |        39.13 |
| nodes      |   60    | RAS        |          5 |        55.78 |
| nodes      |   60    | SPS        |          5 |        32.29 |
| requests   |   10    | RAS        |          5 |        65.96 |
| requests   |   10    | SPS        |          5 |        37.25 |
| requests   |   20    | RAS        |          5 |        56.57 |
| requests   |   20    | SPS        |          5 |        40.28 |
| requests   |   40    | RAS        |          5 |        51.04 |
| requests   |   40    | SPS        |          5 |        45.35 |

non-ok (timeout/error/skipped) rows: 0

## FIG4 - paired savings of RPSP (%)

| sweep      |   value | baseline   |   n_paired |   saving_pct |
|:-----------|--------:|:-----------|-----------:|-------------:|
| gamma      |    0.35 | RPD+GD     |          5 |         0    |
| gamma      |    0.35 | SP+PSP     |          5 |         9.46 |
| gamma      |    0.7  | RPD+GD     |          5 |         0    |
| gamma      |    0.7  | SP+PSP     |          5 |         9.3  |
| gamma      |    1.1  | RPD+GD     |          5 |         0    |
| gamma      |    1.1  | SP+PSP     |          5 |        13.19 |
| initial_ps |    0    | RPD+GD     |          5 |         0    |
| initial_ps |    0    | SP+PSP     |          5 |        10.09 |
| initial_ps |    5    | RPD+GD     |          5 |         0    |
| initial_ps |    5    | SP+PSP     |          5 |        11.65 |
| initial_ps |   10    | RPD+GD     |          5 |         1.79 |
| initial_ps |   10    | SP+PSP     |          5 |        17.91 |
| nodes      |   20    | RPD+GD     |          5 |         1.15 |
| nodes      |   20    | SP+PSP     |          5 |         3.37 |
| nodes      |   40    | RPD+GD     |          5 |         1.49 |
| nodes      |   40    | SP+PSP     |          5 |        12    |
| nodes      |   60    | RPD+GD     |          5 |         0    |
| nodes      |   60    | SP+PSP     |          5 |        -2.35 |
| requests   |   10    | RPD+GD     |          5 |         0    |
| requests   |   10    | SP+PSP     |          5 |        14.29 |
| requests   |   20    | RPD+GD     |          5 |         0    |
| requests   |   20    | SP+PSP     |          5 |        22.35 |
| requests   |   40    | RPD+GD     |          5 |         0    |
| requests   |   40    | SP+PSP     |          5 |        13.77 |

non-ok (timeout/error/skipped) rows: 0

## Sensitivity to k (D2), mean time slots

|   value |   RPD+GD |   RPSP |   SP+PSP |
|--------:|---------:|-------:|---------:|
|       1 |     21   |   21   |     21   |
|       3 |     12.2 |   12.2 |     18.2 |
|       5 |     12.8 |   12.8 |     15.6 |

## Replication vs. paper

| comparison | this run: max saving over all sweeps (where) | paper |
|---|---|---|

| fig3 RPSP vs RAS | 66.0% (requests=10.0) | up to 98.33% (gamma=1.3); 89% over node sweep; abstract: 87% |

| fig3 RPSP vs SPS | 52.6% (initial_ps=10.0) | up to 98.13% (gamma=1.3); 93% over node sweep |

| fig4 RPSP vs RPD+GD | 1.8% (initial_ps=10.0) | up to 51% (node sweep); 43.76% at 200 requests; abstract: 36% |

| fig4 RPSP vs SP+PSP | 22.4% (requests=20.0) | up to 46% (node sweep); 27.09% at 200 requests; 26% in summary |


The paper itself quotes different headline numbers in the abstract (87% / 36%), the findings list (98.33% / 98.13%, 36% / 26%) and Sec. V-C (51% / 46%), so no single 'target' exists. Discrepancy notes are in REPLICATION_NOTES.md.
