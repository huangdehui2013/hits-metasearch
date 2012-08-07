# todo

- lines
    -- best underlying system
    -- hits, 10 & 100 iterations, even edges
    -- hits, 10 & 100 iterations, linearly decaying edges
    -- hits, 10 & 100 iterations, decaying edges

- graph
    y:MAP over all queries
    x:document cutoff
- graph
    y:MAP over all queries
    x:iteration

- write routines to rate performance to provide a baseline/control on which to improve
- weight graph edges with system document scores in a custom update_fn
- research stopping conditions to come up with a better way to detect that the hubs/authorities may have reached a local extrema
