# TODO

![Goal architecture](images/goal_arch.png)

Persistence to Astra DB for restaurant/user data (maybe with timeseries for a plotting client, TTL)

A mini-API returning said data (from Astra DB)

Avro schema in all topics except the 'raw' one

Switch from dockerized Pulsar to Astra Streaming (adapting .env, etc)

(a couple of plots to show the relation between restaurants' "real score" slow oscillations, individual users' fuzzed review scores, and rolling averages?)
