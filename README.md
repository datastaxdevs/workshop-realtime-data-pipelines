# README

![Current architecture](images/current_arch.png)

## Review generation

Several reviewers on several targets (restaurants, hotels, unspecified).
The "real rating" varies slowly, individual reviews fluctuate - too much for some reviewers.

Also there is a review text (poorly faked) that may or may not reflect the numeric value (trollish)

A machine that creates reviews as stringy jsons, but sometimes there's gibberish in them (and also a field may have one of two names, another may not exist.

### To a pulsar topic

All this goes to a first Pulsar topic, `rr-raw-in`.

For this we create a dockerized pulsar:

    docker run -it -p 6650:6650  -p 8080:8080 --mount source=pulsardata,target=/pulsar/data --mount source=pulsarconf,target=/pulsar/conf apachepulsar/pulsar:2.9.1 bin/pulsar standalone

Note that ports 6650 (and 8080) are accessible from outside docker (we're gonna use this)

We have to set up the topics (four of them in total) within the container: first

    docker exec -it $CONTAINER_ID bash

then:

```
    mkdir /root/functions   # while we're at it, for later

    ./bin/pulsar-admin topics list public/default

    ./bin/pulsar-admin topics create persistent://public/default/rr-raw-in
    ./bin/pulsar-admin topics create persistent://public/default/rr-hotel-reviews
    ./bin/pulsar-admin topics create persistent://public/default/rr-restaurant-reviews
    ./bin/pulsar-admin topics create persistent://public/default/rr-restaurant-anomalies

    ./bin/pulsar-admin topics list public/default
```

### Install the routing function

First must copy the appropriate `py` file over to within Docker: in your local shell,

    docker cp pulsar_routing_function/review_router.py $CONTAINER_ID:/root/functions

Go to the in-container bash again:

```
    ls /root/functions    # check py file is there

    ./bin/pulsar-admin functions create \
      --py /root/functions/review_router.py \
      --classname review_router.ReviewRouter \
      --tenant public \
      --namespace default \
      --name rrouter-function \
      --inputs rr-raw-in

    ./bin/pulsar-admin functions list \
      --tenant public \
      --namespace default
```

(by the way, you would delete it with `./bin/pulsar-admin functions delete --tenant public --namespace default --name rrouter-function`).

### Running py code

Make a Python 3.6+ virtual env, install the dependencies in `requirements.txt`
and add this repo's root dir to the `PYTHONPATH`.

Commands for three shells at best:
```
./revGenerator/review_generator.py -r 1000
./revAnalyzer/review_analyzer.py -r -o -f 50
./tools/reader.py -t rr-restaurant-anomalies
```

### Setup and testing so far

_Note_: obsolete: to update. Renamed directories, don't mention docker stuff here,
need more instructions on `.env`.

_All this outside of Docker. Mind that this is a very basic and approximate "test"._

Check the `.env.sample`, copy it to `.env` and make sure of its config. In particular, the IP address of the container
(`docker inspect $CONTAINER_ID`). The rest should be ok.

Also create a Python3 virtualenv or anyway install the dependencies in `requirements.txt`.

As a mini test of the above function, you can run the following in two shells (Note: obsolete setup instructions):

```
# one shell:
./tools/reader.py -t rr-restaurant-reviews      # Ctrl-C to stop it

# and now in another shell you generate a handful of reviews:
./review_generator/review_generator.py -r 2 -n 10
```

You should see restaurant-only (normalized, cleaned) reviews being printed in the
first shell (as they are consumed from the topic the function is routing messages to).

### DB setup

this part to write

### Review analyzer (engine only)

So far it prints to stdout. It reads from the restaurants-only topic
and updates a state to maintain rolling averages: it is then able to
detect outliers and (by comparing text and number score of each review)
users who presumably are trolling.

In one shell, try

    ./review_analyzer/review_analyzer.py -f 200 -o -r -t

and then, in another, you launch the review generator with e.g.

    ./review_generator/review_generator.py -r 50

The first shell will report outliers and periodically give an update
on its status.

### Query the Astra DB REST API

```
. .env

ASTRA_URL_ROOT="https://${ASTRA_DB_ID}-${ASTRA_DB_REGION}.apps.astra.datastax.com/api/rest/v1/keyspaces/${ASTRA_DB_KEYSPACE}/tables"

curl -X GET \
    "${ASTRA_URL_ROOT}/known_ids_per_type/rows/restaurant" \
    -H "accept: application/json" \
    -H "X-Cassandra-Token: ${ASTRA_DB_APP_TOKEN}" | python -mjson.tool

curl -X GET \
    "${ASTRA_URL_ROOT}/known_ids_per_type/rows/reviewer" \
    -H "accept: application/json" \
    -H "X-Cassandra-Token: ${ASTRA_DB_APP_TOKEN}" | python -mjson.tool

curl -X GET \
    "${ASTRA_URL_ROOT}/restaurants_by_id/rows/vegg00" \
    -H "accept: application/json" \
    -H "X-Cassandra-Token: ${ASTRA_DB_APP_TOKEN}" | python -mjson.tool

curl -X GET \
    "${ASTRA_URL_ROOT}/reviewers_by_id/rows/geri" \
    -H "accept: application/json" \
    -H "X-Cassandra-Token: ${ASTRA_DB_APP_TOKEN}" | python -mjson.tool

curl -X GET \
    "${ASTRA_URL_ROOT}/restaurants_by_id_time/rows/gold_f" \
    -H "accept: application/json" \
    -H "X-Cassandra-Token: ${ASTRA_DB_APP_TOKEN}" | python -mjson.tool
```

### Switch to Astra Streaming

Create an Astra Streaming tenant in your Astra Account (link to wiki).
Call it e.g. `trollsquad` (beware: tenant names are unique, pick yours!)

Use the `default` namespace in that tenant.

Create (with the Astra UI) the four topics (persistent=yes, partitioned=no):
`rr-raw-in`, `rr-hotel-reviews`, `rr-restaurant-reviews`
and `rr-restaurant-anomalies`.

Retrieve the Broker Service URL and the Streaming Token (link to wiki).

Edit the `.env` to the right `PULSAR_MODE` and subsequent variables, including
the tenant name later.

#### Function:

in the Astra UI, pick your tenant and the "Functions" tab.

"Create Function".

**IMPORTANT**: manually edit tenant name in the `DST_TOPIC_MAP` in the Python
file before uploading. It must reflect your unique tenant name!

- Name = `rrouter-function`, namespace = `default`;
- upload the `pulsar_routing_function/review_router.py` and pick the `ReviewRouter` function name;
- input topic: `default` and `rr-raw-in`;
- leave output/log topics empty;
- do not touch Advanced Configuration;
- no need for any further option configuration. Hit "Create".

The function will display as "Initializing" in the listing for some time
(20 s perhaps), then "Running".