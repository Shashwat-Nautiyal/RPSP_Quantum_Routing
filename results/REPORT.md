# Replication report (auto-generated)

## Instances

| sweep      |   ok |
|:-----------|-----:|
| gamma      |  600 |
| initial_ps |  700 |
| k          |  300 |
| nodes      | 1000 |
| requests   |  900 |

beta actually used by the generator (D6 fallback):

|                      |   mean |   min |   max |
|:---------------------|-------:|------:|------:|
| ('gamma', 0.35)      |  0.123 | 0.1   | 0.125 |
| ('gamma', 0.5)       |  0.1   | 0.1   | 0.1   |
| ('gamma', 0.7)       |  0.1   | 0.1   | 0.1   |
| ('gamma', 0.9)       |  0.1   | 0.1   | 0.1   |
| ('gamma', 1.1)       |  0.1   | 0.1   | 0.1   |
| ('gamma', 1.3)       |  0.1   | 0.1   | 0.1   |
| ('initial_ps', 0.0)  |  0.121 | 0.1   | 0.125 |
| ('initial_ps', 5.0)  |  0.122 | 0.1   | 0.125 |
| ('initial_ps', 10.0) |  0.123 | 0.1   | 0.156 |
| ('initial_ps', 15.0) |  0.122 | 0.1   | 0.125 |
| ('initial_ps', 20.0) |  0.121 | 0.1   | 0.125 |
| ('initial_ps', 25.0) |  0.121 | 0.1   | 0.125 |
| ('initial_ps', 30.0) |  0.122 | 0.1   | 0.156 |
| ('k', 1.0)           |  0.122 | 0.1   | 0.156 |
| ('k', 3.0)           |  0.121 | 0.1   | 0.156 |
| ('k', 5.0)           |  0.121 | 0.1   | 0.156 |
| ('nodes', 20.0)      |  0.308 | 0.195 | 0.381 |
| ('nodes', 40.0)      |  0.211 | 0.156 | 0.244 |
| ('nodes', 60.0)      |  0.18  | 0.156 | 0.195 |
| ('nodes', 80.0)      |  0.153 | 0.125 | 0.156 |
| ('nodes', 100.0)     |  0.133 | 0.1   | 0.156 |
| ('nodes', 120.0)     |  0.122 | 0.1   | 0.125 |
| ('nodes', 140.0)     |  0.106 | 0.1   | 0.125 |
| ('nodes', 160.0)     |  0.1   | 0.1   | 0.125 |
| ('nodes', 180.0)     |  0.1   | 0.1   | 0.1   |
| ('nodes', 200.0)     |  0.1   | 0.1   | 0.1   |
| ('requests', 10.0)   |  0.119 | 0.1   | 0.125 |
| ('requests', 25.0)   |  0.122 | 0.1   | 0.156 |
| ('requests', 50.0)   |  0.123 | 0.1   | 0.156 |
| ('requests', 75.0)   |  0.121 | 0.1   | 0.125 |
| ('requests', 100.0)  |  0.124 | 0.1   | 0.156 |
| ('requests', 125.0)  |  0.124 | 0.1   | 0.156 |
| ('requests', 150.0)  |  0.121 | 0.1   | 0.125 |
| ('requests', 175.0)  |  0.123 | 0.1   | 0.156 |
| ('requests', 200.0)  |  0.122 | 0.1   | 0.156 |

## FIG3 - paired savings of RPSP-APSP (%)

| sweep      |   value | baseline   |   n_paired |   saving_pct |
|:-----------|--------:|:-----------|-----------:|-------------:|
| gamma      |    0.35 | RAS        |        100 |        61.3  |
| gamma      |    0.35 | SPS        |        100 |        52.58 |
| gamma      |    0.5  | RAS        |        100 |        62.35 |
| gamma      |    0.5  | SPS        |        100 |        53.84 |
| gamma      |    0.7  | RAS        |         97 |        71.53 |
| gamma      |    0.7  | SPS        |         97 |        62.08 |
| gamma      |    0.9  | RAS        |         98 |        76.82 |
| gamma      |    0.9  | SPS        |         98 |        67.02 |
| gamma      |    1.1  | RAS        |         97 |        82.57 |
| gamma      |    1.1  | SPS        |         97 |        74.03 |
| gamma      |    1.3  | RAS        |         99 |        86.58 |
| gamma      |    1.3  | SPS        |         99 |        79.14 |
| initial_ps |    0    | RAS        |        100 |        54.52 |
| initial_ps |    0    | SPS        |        100 |        45.03 |
| initial_ps |    5    | RAS        |        100 |        57.59 |
| initial_ps |    5    | SPS        |        100 |        48.74 |
| initial_ps |   10    | RAS        |        100 |        58.95 |
| initial_ps |   10    | SPS        |        100 |        50.37 |
| initial_ps |   15    | RAS        |         94 |        61.6  |
| initial_ps |   15    | SPS        |         94 |        53.77 |
| initial_ps |   20    | RAS        |         99 |        63.42 |
| initial_ps |   20    | SPS        |         99 |        55.91 |
| initial_ps |   25    | RAS        |        100 |        66.16 |
| initial_ps |   25    | SPS        |        100 |        58.85 |
| initial_ps |   30    | RAS        |        100 |        68.79 |
| initial_ps |   30    | SPS        |        100 |        61.71 |
| nodes      |   20    | RAS        |        100 |        61.82 |
| nodes      |   20    | SPS        |        100 |        61.82 |
| nodes      |   40    | RAS        |        100 |        58.63 |
| nodes      |   40    | SPS        |        100 |        57.08 |
| nodes      |   60    | RAS        |        100 |        59.68 |
| nodes      |   60    | SPS        |        100 |        56.91 |
| nodes      |   80    | RAS        |        100 |        59.77 |
| nodes      |   80    | SPS        |        100 |        54.9  |
| nodes      |  100    | RAS        |        100 |        59.69 |
| nodes      |  100    | SPS        |        100 |        53.17 |
| nodes      |  120    | RAS        |        100 |        60.93 |
| nodes      |  120    | SPS        |        100 |        52.62 |
| nodes      |  140    | RAS        |         97 |        59.99 |
| nodes      |  140    | SPS        |         97 |        50.26 |
| nodes      |  160    | RAS        |         92 |        62.06 |
| nodes      |  160    | SPS        |         92 |        50.89 |
| nodes      |  180    | RAS        |         86 |        64.9  |
| nodes      |  180    | SPS        |         86 |        51.43 |
| nodes      |  200    | RAS        |         67 |        68.14 |
| nodes      |  200    | SPS        |         67 |        53.02 |
| requests   |   10    | RAS        |        100 |        85.96 |
| requests   |   10    | SPS        |        100 |        45.23 |
| requests   |   25    | RAS        |        100 |        76.17 |
| requests   |   25    | SPS        |        100 |        48.52 |
| requests   |   50    | RAS        |        100 |        69.62 |
| requests   |   50    | SPS        |        100 |        53.37 |
| requests   |   75    | RAS        |        100 |        63.67 |
| requests   |   75    | SPS        |        100 |        52.68 |
| requests   |  100    | RAS        |        100 |        61.79 |
| requests   |  100    | SPS        |        100 |        53.6  |
| requests   |  125    | RAS        |        100 |        61.08 |
| requests   |  125    | SPS        |        100 |        54.23 |
| requests   |  150    | RAS        |         94 |        58.52 |
| requests   |  150    | SPS        |         94 |        53.38 |
| requests   |  175    | RAS        |         84 |        58.47 |
| requests   |  175    | SPS        |         84 |        54.67 |
| requests   |  200    | RAS        |         75 |        57.7  |
| requests   |  200    | SPS        |         75 |        54.5  |

non-ok (timeout/error/skipped) rows: 121

## FIG4 - paired savings of RPSP (%)

| sweep      |   value | baseline     |   n_paired |   saving_pct |
|:-----------|--------:|:-------------|-----------:|-------------:|
| gamma      |    0.35 | RPD+GD       |        100 |         0.1  |
| gamma      |    0.35 | RPD+GD-naive |        100 |         4.92 |
| gamma      |    0.35 | SP+PSP       |        100 |        28.03 |
| gamma      |    0.5  | RPD+GD       |        100 |         0.09 |
| gamma      |    0.5  | RPD+GD-naive |        100 |         3.15 |
| gamma      |    0.5  | SP+PSP       |        100 |        24.75 |
| gamma      |    0.7  | RPD+GD       |         97 |         0    |
| gamma      |    0.7  | RPD+GD-naive |         97 |         3.55 |
| gamma      |    0.7  | SP+PSP       |         97 |        25.22 |
| gamma      |    0.9  | RPD+GD       |         98 |         0.07 |
| gamma      |    0.9  | RPD+GD-naive |         98 |         3.79 |
| gamma      |    0.9  | SP+PSP       |         98 |        26.38 |
| gamma      |    1.1  | RPD+GD       |         97 |         0.07 |
| gamma      |    1.1  | RPD+GD-naive |         97 |         5.02 |
| gamma      |    1.1  | SP+PSP       |         97 |        23.95 |
| gamma      |    1.3  | RPD+GD       |         99 |         0.15 |
| gamma      |    1.3  | RPD+GD-naive |         99 |         4.72 |
| gamma      |    1.3  | SP+PSP       |         99 |        27.12 |
| initial_ps |    0    | RPD+GD       |        100 |         0    |
| initial_ps |    0    | RPD+GD-naive |        100 |         1.49 |
| initial_ps |    0    | SP+PSP       |        100 |        17.97 |
| initial_ps |    5    | RPD+GD       |        100 |         0.03 |
| initial_ps |    5    | RPD+GD-naive |        100 |         2.21 |
| initial_ps |    5    | SP+PSP       |        100 |        20.93 |
| initial_ps |   10    | RPD+GD       |        100 |         0.03 |
| initial_ps |   10    | RPD+GD-naive |        100 |         3.35 |
| initial_ps |   10    | SP+PSP       |        100 |        24.99 |
| initial_ps |   15    | RPD+GD       |         93 |         0.1  |
| initial_ps |   15    | RPD+GD-naive |         93 |         4.03 |
| initial_ps |   15    | SP+PSP       |         93 |        26.37 |
| initial_ps |   20    | RPD+GD       |         99 |         0.32 |
| initial_ps |   20    | RPD+GD-naive |         99 |         5.51 |
| initial_ps |   20    | SP+PSP       |         99 |        29.32 |
| initial_ps |   25    | RPD+GD       |        100 |         0.18 |
| initial_ps |   25    | RPD+GD-naive |        100 |         5.93 |
| initial_ps |   25    | SP+PSP       |        100 |        28.12 |
| initial_ps |   30    | RPD+GD       |        100 |         0.43 |
| initial_ps |   30    | RPD+GD-naive |        100 |         7.45 |
| initial_ps |   30    | SP+PSP       |        100 |        32.8  |
| nodes      |   20    | RPD+GD       |        100 |         4.56 |
| nodes      |   20    | RPD+GD-naive |        100 |         5.83 |
| nodes      |   20    | SP+PSP       |        100 |        17.95 |
| nodes      |   40    | RPD+GD       |        100 |         0.53 |
| nodes      |   40    | RPD+GD-naive |        100 |         5.86 |
| nodes      |   40    | SP+PSP       |        100 |        23.07 |
| nodes      |   60    | RPD+GD       |        100 |         0.52 |
| nodes      |   60    | RPD+GD-naive |        100 |         7.25 |
| nodes      |   60    | SP+PSP       |        100 |        28.51 |
| nodes      |   80    | RPD+GD       |        100 |         0.39 |
| nodes      |   80    | RPD+GD-naive |        100 |         5.3  |
| nodes      |   80    | SP+PSP       |        100 |        24.02 |
| nodes      |  100    | RPD+GD       |        100 |         0.18 |
| nodes      |  100    | RPD+GD-naive |        100 |         5.01 |
| nodes      |  100    | SP+PSP       |        100 |        26.87 |
| nodes      |  120    | RPD+GD       |        100 |         0.03 |
| nodes      |  120    | RPD+GD-naive |        100 |         4.27 |
| nodes      |  120    | SP+PSP       |        100 |        26.05 |
| nodes      |  140    | RPD+GD       |         97 |         0.03 |
| nodes      |  140    | RPD+GD-naive |         97 |         2.87 |
| nodes      |  140    | SP+PSP       |         97 |        23.05 |
| nodes      |  160    | RPD+GD       |         92 |         0    |
| nodes      |  160    | RPD+GD-naive |         92 |         3.15 |
| nodes      |  160    | SP+PSP       |         92 |        24.84 |
| nodes      |  180    | RPD+GD       |         86 |         0.07 |
| nodes      |  180    | RPD+GD-naive |         86 |         3.05 |
| nodes      |  180    | SP+PSP       |         86 |        25.43 |
| nodes      |  200    | RPD+GD       |         67 |         0.05 |
| nodes      |  200    | RPD+GD-naive |         67 |         3.26 |
| nodes      |  200    | SP+PSP       |         67 |        27.95 |
| requests   |   10    | RPD+GD       |        100 |         0    |
| requests   |   10    | RPD+GD-naive |        100 |         3.35 |
| requests   |   10    | SP+PSP       |        100 |         9.96 |
| requests   |   25    | RPD+GD       |        100 |         0.08 |
| requests   |   25    | RPD+GD-naive |        100 |         4.31 |
| requests   |   25    | SP+PSP       |        100 |        22.14 |
| requests   |   50    | RPD+GD       |        100 |         0.15 |
| requests   |   50    | RPD+GD-naive |        100 |         4.21 |
| requests   |   50    | SP+PSP       |        100 |        21.71 |
| requests   |   75    | RPD+GD       |        100 |         0.17 |
| requests   |   75    | RPD+GD-naive |        100 |         3.32 |
| requests   |   75    | SP+PSP       |        100 |        24.19 |
| requests   |  100    | RPD+GD       |        100 |         0.19 |
| requests   |  100    | RPD+GD-naive |        100 |         5.35 |
| requests   |  100    | SP+PSP       |        100 |        25.43 |
| requests   |  125    | RPD+GD       |        100 |         0.08 |
| requests   |  125    | RPD+GD-naive |        100 |         5.72 |
| requests   |  125    | SP+PSP       |        100 |        28.37 |
| requests   |  150    | RPD+GD       |         94 |         0.14 |
| requests   |  150    | RPD+GD-naive |         94 |         5    |
| requests   |  150    | SP+PSP       |         94 |        25.68 |
| requests   |  175    | RPD+GD       |         84 |         0.04 |
| requests   |  175    | RPD+GD-naive |         84 |         2.99 |
| requests   |  175    | SP+PSP       |         84 |        27.11 |
| requests   |  200    | RPD+GD       |         75 |         0.07 |
| requests   |  200    | RPD+GD-naive |         75 |         4.02 |
| requests   |  200    | SP+PSP       |         75 |        31.54 |

non-ok (timeout/error/skipped) rows: 365

## Sensitivity to k (D2), mean time slots

|   value |   RPD+GD |   RPD+GD-naive |   RPSP |   SP+PSP |
|--------:|---------:|---------------:|-------:|---------:|
|       1 |    44.31 |          44.89 |  44.31 |    44.31 |
|       3 |    33.55 |          34.97 |  33.52 |    46.76 |
|       5 |    32.42 |          34.08 |  32.37 |    44.56 |

## Replication vs. paper

| comparison | this run: max saving over all sweeps (where) | paper |
|---|---|---|

| fig3 RPSP vs RAS | 86.6% (gamma=1.3) | up to 98.33% (gamma=1.3); 89% over node sweep; abstract: 87% |

| fig3 RPSP vs SPS | 79.1% (gamma=1.3) | up to 98.13% (gamma=1.3); 93% over node sweep |

| fig4 RPSP vs RPD+GD | 4.6% (nodes=20.0) | up to 51% (node sweep); 43.76% at 200 requests; abstract: 36% |

| fig4 RPSP vs SP+PSP | 32.8% (initial_ps=30.0) | up to 46% (node sweep); 27.09% at 200 requests; 26% in summary |


The paper itself quotes different headline numbers in the abstract (87% / 36%), the findings list (98.33% / 98.13%, 36% / 26%) and Sec. V-C (51% / 46%), so no single 'target' exists. Discrepancy notes are in REPLICATION_NOTES.md.
