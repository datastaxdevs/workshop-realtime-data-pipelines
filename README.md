# README

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

### notes

test reading is in `tools`: `./reader.py`, but check the topic defined in the script.

generation of sample data has now 1 item creation for testing