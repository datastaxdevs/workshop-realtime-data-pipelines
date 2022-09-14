# TODO



> 🖥️ `lab4-04 output`
> ```sql
> user_id | idx   | detected_by        | r_score | r_text                                                  | tgt_id | tgt_name
>---------+-------+--------------------+---------+---------------------------------------------------------+--------+----------------
>    anne | 18745 | review_analyzer.py |     6.2 |                                 is ordinary we dish the | vegg00 | VeggieParadise
>    anne | 20587 | review_analyzer.py |     1.5 |         ordinary unsatisfactory with is eating terrible | gold_f |    Golden Fork
>    anne | 20754 | review_analyzer.py |     8.7 |                        superb superb eating ordinary is | gold_f |    Golden Fork
>    anne | 21476 | review_analyzer.py |     1.4 |        with disgusting the vomit despicable with we the | gold_f |    Golden Fork
>    anne | 28864 | review_analyzer.py |     4.2 |        with roast with we eating the ordinary we eating | pizzas |    Pizza Smile
>    botz | 18741 | review_analyzer.py |     5.6 | risotto cooked ordinary roast roast ordinary we risotto | vegg00 | VeggieParadise
>    botz | 19905 | review_analyzer.py |     5.1 |     with eating we with roast eating the eating risotto | pizzas |    Pizza Smile
>    botz | 28670 | review_analyzer.py |       0 |     unsatisfactory dish vomit dish vomit vomit ordinary | gold_f |    Golden Fork
>    botz | 28758 | review_analyzer.py |     7.6 |                                 tasty with we delicious | gold_f |    Golden Fork
> ```


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
