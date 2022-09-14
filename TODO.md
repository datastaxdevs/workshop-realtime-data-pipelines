# TODO

![Goal architecture](images/goal_arch.png)

Enforce schema in all topics except the "raw" one.

#### `✅.lab4-04`- Create a Sink with the CLI

- Replace SCB URL and TOKEN in SINK CONFIG FILE

> **TODO `astra db download-scb-url` does not exist**

```
ASTRA_DB_APP_TOKEN=`astra config get default --key ASTRA_DB_APPLICATION_TOKEN`
sed -i "s/__TOKEN__/${ASTRA_DB_APP_TOKEN}/" /workspace/workshop-realtime-data-pipelines/tools/config-sink.yaml

ASTRA_SCB_URL=`astra db scb-download-url workshops`
sed -i "s/__SCB__/${ASTRA_SCB_URL}/" /workspace/workshop-realtime-data-pipelines/tools/config-sink.yaml
```

- Start `pulsar-shell`

```bash
astra streaming pulsar-shell ${TENANT}
```


- Create the sink

```bash
admin sinks create \
   --name sink-with-cli \
   --tenant ${TENANT} \
   --namespace default \
   -t cassandra-enhanced \
   -i persistent://${TENANT}/default/rr-restaurant-anomalies \
  --sink-config-file /workspace/workshop-realtime-data-pipelines/tools/config-sink.yaml
```
