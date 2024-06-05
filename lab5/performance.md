# Test comprasion
```
## wrk -t4 -c100 -d30s 'http://localhost:8080/get_recipient_details?recipient_id=1'
```
| Metric          | Without Redis            | With Redis                |
|-----------------|--------------------------|---------------------------|
| Duration        | 30s                      | 30s                       |
| Threads         | 4                        | 4                         |
| Connections     | 100                      | 100                       |
| Avg Latency     | 109.58ms                 | 26.73ms                   |
| Latency Stdev   | 97.51ms                  | 11.18ms                   |
| Max Latency     | 1.05s                    | 372.96ms                  |
| Latency > Stdev | 88.33%                   | 92.73%                    |
| Avg Req/Sec     | 295.61                   | 936                       |
| Req/Sec Stdev   | 185.56                   | 129.14                    |
| Max Req/Sec     | 891                      | 1.44k                     |
| Req/Sec > Stdev | 74.37%                   | 78.35%                    |
| Total Requests  | 34294                    | 104998                    |
| Total Data Read | 7.58MB                   | 30.56MB                   |
| Requests/sec    | 1148.29                  | 4015.34                   |
| Transfer/sec    | 264.56KB                 | 1.04MB                    |

# Latency Distribution with Redis
     50%   36.35ms
     75%   42.31ms
     90%   54.30ms
     99%   91.19ms

# Latency Distribution without Redis
    50%    72.19ms
    75%    128.37ms
    90%    224.56ms
    99%    578.92ms
