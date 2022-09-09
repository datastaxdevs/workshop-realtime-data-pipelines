## 🎓 Real-Time data pipelines with Apache Pulsar™ and Apache Cassandra™

[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/datastaxdevs/workshop-realtime-data-pipelines)
[![License Apache2](https://img.shields.io/hexpm/l/plug.svg)](http://www.apache.org/licenses/LICENSE-2.0)
[![Discord](https://img.shields.io/discord/685554030159593522)](https://discord.com/widget?id=685554030159593522&theme=dark)

Welcome to the *RealTime data pipeline with Apache Pulsar and Apache Cassandra** workshop! In this two-hour workshop, we will show you a sample architecture making use of Apache Pulsar™ and Pulsar Functions for real-time, event-streaming-based data ingestion, cleaning and processing.

⏲️ **Duration :** 2 hours

🎓 **Level** Beginner to Intermediate

![](images/splash.png)

> [🔖 Accessing HANDS-ON](#-start-hands-on)

## 📋 Table of contents

- [**HouseKeeping**](#objectives)
  - [Objectives](#frequently-asked-questions)
  - [Frequently asked questions](#frequently-asked-questions)
  - [Materials for the Session](#materials-for-the-session)
- [**Architecture Design**](#user-case)
  - [Architecture overview](#)
  - [Injector Component](#)
  - [Analyzer Component](#)
- [**Setup - Initialize your environment**](#)
  - [S.1 Create Astra Account](#)
  - [S.2 Create Astra Credentials (token)](#)
  - [S.3 Start Gitpod IDE](#)
  - [S.4 Setup `Astra CLI`](#)
- [**LAB1 - Producer and Consumer**](#)
  - [1.1 Create tenant](#)
  - [1.2 Create topics](#)
  - [1.3 Start injector (producer)](#)
  - [1.4 Visualize messages (consumer)](#)
- [**LAB2 - Pulsar functions**](#)  
  - [2.1 Create function](#)
  - [2.2 Deploy function](#)
  - [2.3 Run Demo](#)
- [**LAB3 - Pulsar Sinks and Analyzer**](#)  
  - [3.1 Create DB](#)
  - [3.2 Create Schema](#)
  - [3.3 Setup sink](#)
- [Homework](#7-homework)
- [What's NEXT ](#8-whats-next-)
<p>

## Objectives

- 🎯 Give you an understanding and how and where to position Apache Pulsar

- 🎯 Give an overview of  streaming and datascience ecosystem**

- 🎯 Give you an understanding of Apache Cassandra NoSQL Database

- 🎯 Create your first pipeline with streaming and database.

- 🚀 Have fun with an interactive session

## Frequently asked questions

<p/>
<details>
<summary><b> 1️⃣ Can I run this workshop on my computer?</b></summary>
<hr>
<p>There is nothing preventing you from running the workshop on your own machine. If you do so, you will need the following:
<ol>
<li><b>git</b>
<li><b>Python 3.6+</b>
<li><b>Astra Cli</b>
<li><b>Pulsar Shell or Pulsar-Client</b>
</ol>
</p>
In this readme, we try to provide instructions for local development as well - but keep in mind that the main focus is development on Gitpod, hence <strong>we can't guarantee live support</strong> about local development in order to keep on track with the schedule. However, we will do our best to give you the info you need to succeed.
</details>
<p/>
<details>
<summary><b> 2️⃣ What other prerequisites are required?</b></summary>
<hr>
<ul>
<li>You will need enough *real estate* on screen, we will ask you to open a few windows and it would not fit on mobiles (tablets should be OK)
<li>You will need an Astra account: don't worry, we'll work through that in the following
<li>As "Intermediate level" we expect you to know what java and Spring are. 
</ul>
</p>
</details>
<p/>
<details>
<summary><b> 3️⃣ Do I need to pay for anything for this workshop?</b></summary>
<hr>
<b>No.</b> All tools and services we provide here are FREE. FREE not only during the session but also after.
</details>
<p/>
<details>
<summary><b> 4️⃣ Will I get a certificate if I attend this workshop?</b></summary>
<hr>
Attending the session is not enough. You need to complete the homework detailed below and you will get a nice badge that you can share on linkedin or anywhere else *(open badge specification)*
</details>
<p/>

## Materials for the session

It doesn't matter if you join our workshop live or you prefer to work at your own pace,
we have you covered. In this repository, you'll find everything you need for this workshop:

- [Slide deck](/slides/slides.pdf)
- [Discord chat](https://dtsx.io/discord)
- [Questions and Answers](https://community.datastax.com/)
- [Twitch backup](https://www.twitch.tv/datastaxdevs)

## Architecture Design

_Reviews of various venues (hotels/restaurants), written by various users, keep pouring in. We need a way to clean, normalize and filter them, removing trolls and flagging blatant outlier reviews, and make the running results available to the end user._

### Architecture overview

<img src="./images/current_arch.png"/>

<details>
<summary><b> Show Detailed explanations</b></summary>

<ul>
<li>A stream of "events" (messages), some of which are reviews, is poured into a Pulsar topic for "raw reviews".
<li>A Pulsar function filters out malformed items and those that do not specify their target type (restaurant/hotel). This function takes care of normalizing the incoming reviews, since - as is often the case in real life - certain field names in the incoming reviews can have multiple forms. All reviews are encoded as JSON strings. The Pulsar function singles out hotel and restaurant reviews and routes them, after normalizing their structure, to two specific topics. 
<li>We happen to be interested in restaurants, so we have a long-running process ("analyzer") performing the actual analysis on these. Heavy artillery, such as AI/ML-based classifiers, code with fat dependencies and the like, would be placed here (i.e outside Pulsar).

<li>The analyzer keeps listening to the restaurant topic and ingests all incoming reviews: it keeps and update a state with key information, such as a rolling average score per each restaurant.

<li>As new items arrive, they are checked if they are "troll reviews" (review text in heavy disagreement with the numeric score) and, if so, discarded. Otherwise they enter the rolling average for the target restaurant.

<li>The analyzer periodically publishes an assessment for users and restaurants to a database, ready to be queried by any service that may need this data. (The output can also go to console if so desired). The destination DB also offers a ready-to-use REST API that allows to retrieve its data with simple HTTP requests, making it easy to build panels and UIs on top of this pipeline. The analyzer also reroutes "outlier reviews" (scores much different than the current rolling average) to another Pulsar topic, for a hypothetical manual inspection of such outliers.
</ul>
</p>
</details>

### Injector Component

<img src="./images/plots/02_reviews.png"/>

<details>
<summary><b> Show Details</b></summary>
<p>
There is a pseudorandom procedure to generate reviews with features that fluctuate in a predictable
way: it is all in the `revGenerator` directory.

There is no "time" in the generation: to keep things simple, we use a "sequence index" in place of
time. Also, some of the "reviews" are not even valid JSON strings but contain gibberish instead,
as is often the case in real-life data ingestion pipelines!

Each time a review is created, a venue (target) and a user (reviewer) are chosen at random: then,
score and text are also created according to the following rules:

Each venue has a "true" quality that is slowly oscillating in time, see for example these two restaurants:

<img src="./images/plots/01_real-values.png"/>

Each reviewer has an associate amplitude that dictates how widely the scores they produce
may fluctuate away from the "true" value for that venue at that "time": in this example, the individual
scores emitted by two different reviewers, having a large and small associated amplitude, are plotted:

<img src="./images/plots/02_reviews.png"/>

While reviews by Rita will presumably all fall in the "expected" region around the current average,
a large fraction of the reviews by Anne will be too far away from
it and thus be flagged as "outlier reviews".

Each review comes with an associated text, which in this toy
example is simply a bunch of words strung together, some positive ("delicious") and some negative ("disgusting").
Each reviewer, however, has a Boolean "trolliness" flag: if true, then this text is built in strong
disagreement with the numeric score in the review.
</p>
</details>


### Analyzer Component

<img src="./images/plots/03_moving-average.png"/>

<details>
<summary><b> Show Details</b></summary>
<p>
On the **analyzer side**, the reconstructed rolling average roughly follows the "true" quality for
a venue, and is used to detect "outliers": each review that differs too much from the current rolling
average is deemed an outlier. Here the rolling average corresponding to the above restaurant is plotted:

<img src="./images/plots/03_moving-average.png"/>

The analyzer also discards troll reviews and keeps a running 
counter of them, both per-user and per-restaurant, ready to be exposed with the other data. To do so, a toy version of a sentiment analysis is implemented (simply based on some words with positive
and negative connotation) and used to compare with the numeric
score given in the review.

</p>
</details>

--- 

# 🏁 Start Hands-on

## Setup - Initialize your environment

#### ✅ S.1 Create Astra Account

_**`ASTRA`** is the simplest way to run both Cassandra and Pulsat with zero operations at all - just push the button and get your clusters. No credit card required_

Leveraging [Database creation guide](https://awesome-astra.github.io/docs/pages/astra/create-instance/#c-procedure) create a database. *Right-Click the button* with *Open in a new TAB.*

<a href="https://astra.dev/yt-9-14"><img src="images/create_astra_db_button.png?raw=true" /></a>

#### ✅ S.2 Create Astra Credentials (token)

Create an application token by following <a href="https://awesome-astra.github.io/docs/pages/astra/create-token/" target="_blank">these instructions</a>. 

Skip this step is you already have a token. You can reuse the same token in our other workshops, too.

> Your token should look like: `AstraCS:....`

#### ✅ S.3 Start Gitpod IDE

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/datastaxdevs/workshop-realtime-data-pipelines) *(right-click -> open in new TAB)*



#### ✅ S.4  Setup Astra CLI by providing your application token

- Provide your token

```
astra setup
```

> 🖥️ Output
>
> ```
> +-------------------------------+
> +-     Astra CLI SETUP         -+
> +-------------------------------+
> 
> Welcome to Astra Cli. We will guide you to start.
> 
> [Astra Setup]
> To use the cli you need to:
 > • Create an Astra account on : https://astra.datastax.com
 > • Create an Authentication token following: https://dtsx.io/create-astra-token
> 
> [Cli Setup]
> You will be asked to enter your token, it will be saved locally in ~/. astrarc
> 
> • Enter your token (starting with AstraCS) : 
> AstraCS:AAAAAA
> [ INFO ] - Configuration Saved.
> 
> 
> [cedrick.lunven@gmail.com]
> ASTRA_DB_APPLICATION_TOKEN=AstraCS:AAAAAAAA
> 
> [What's NEXT ?]
> You are all set.(configuration is stored in ~/.astrarc) You can now:
>    • Use any command, 'astra help' will get you the list
>    • Try with 'astra db list'
>    • Enter interactive mode using 'astra'
> 
> Happy Coding !
> ```

- List your existing Astra DB databases:

```
astra db list
```

> 🖥️ Output
>
> ```
> +---------------------+--------------------------------------+---------------------+----------------+
> | Name                | id                                   | Default Region      | Status         |
> +---------------------+--------------------------------------+---------------------+----------------+
> | workshops           | bb61cfd6-2702-4b19-97b6-3b89a04c9be7 | us-east-1           | ACTIVE         |
> +---------------------+--------------------------------------+---------------------+----------------+
> ```



[Gitpod](https://www.gitpod.io/) est un IDE 100% dans le cloud. Il s'appuie sur [VS Code](https://github.com/gitpod-io/vscode/blob/gp-code/LICENSE.txt?lang=en-US) et fournit de nombreux outils pour développer dans plusieurs langages.

#### `✅.001`- _Click-Droit_ sur le bouton pour ouvrir Gitpod dans un nouveau onglet sur votre navigateur.

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/datastaxdevs/workshop-realtime-data-pipelines)

## 1.2 - Apache Cassandra™ dans `Docker`

> ℹ️ Lors du premier copier-coller dans `Gitpod` le navigateur vous invite à autoriser les copies depuis le presse-papier, il est nécessaire de le faire.

Lorsque Gitpod est démarré, localiser le terminal `cassandra-docker`. Il devrait contenir uniquement un message en bleu.

```
------------------------------------------------------------
---        Bienvenue à Devoxx France 2022                ---
--           Local Cassandra (Docker)                    ---
------------------------------------------------------------
```

### 1.2.1 - Démarrage du cluster

Dans le répertoire `labs` repérer le fichier `docker-compose.yml`. Nous allons utiliser l'[image officielle Docker Apache Cassandra™](https://hub.docker.com/_/cassandra/).

#### `✅.002`- Ouvrir le fichier et visualiser comment le `seed` est un service séparé des autres nœuds. La recommandation est de 2 à 3 `seeds` par datacenter (anneau).

```bash
gp open /workspace/conference-2022-devoxx/labs/docker-compose.yml
```

#### `✅.003`- Démarrer 2 noeuds avec `docker-compose`

```bash
cd /workspace/conference-2022-devoxx/labs/
docker-compose up -d
```

> 🖥️ Résultat
>
> ```
> [+] Running 3/3
>  ⠿ Network labs_cassandra           Created      0.0s
>  ⠿ Container labs-dc1_seed-1        Started      0.4s
>  ⠿ Container labs-dc1_noeud-1       Started      1.2s
> ```

The setup involves an event streaming platform and a database.

### Database

An Astra DB instance is required to collect the data for persistence.
What is needed for the Astra DB part is the creation of a DB (preferrably
called `workshops`) and a keyspace in it (called `trollsquad`) as described
[here](https://github.com/datastaxdevs/awesome-astra/wiki/Create-an-AstraDB-Instance).
Then you should create a DB Token (role "API Read/Write User" is sufficient)
as described [here](https://github.com/datastaxdevs/awesome-astra/wiki/Create-an-Astra-Token)
and keep the "Token" value handy.

### Pulsar/Astra Streaming


A Pulsar instance is needed to provide the streaming infrastructure. This demo
can run both on a standard Pulsar installation or an Astra Streaming instance:
the following instructions will cover both cases.

Choose your path:

#### If you use Astra Streaming

The Streaming creation and retrieval of secrets is described in detail
[here](https://github.com/datastaxdevs/awesome-astra/wiki/Create-an-AstraStreaming-Topic).

Create an Astra Streaming tenant in your Astra Account:
Call it e.g. something like `trollsquad` (beware: tenant names are unique,
pick yours and write it down for later).

Use the `default` namespace in that tenant.

Create (with the Astra UI) the four topics (`persistent=yes`, `partitioned=no`):
`rr-raw-in`, `rr-hotel-reviews`, `rr-restaurant-reviews`
and `rr-restaurant-anomalies`.

Retrieve the Broker Service URL and the Streaming Token (again, see [here](https://github.com/datastaxdevs/awesome-astra/wiki/Create-an-AstraStreaming-Topic#-step-4-retrieve-the-broker-url)).

**Function:**

In the Astra UI, click on your tenant and go to the "Functions" tab.
Hit "Create Function".

_IMPORTANT_: You must now manually edit the tenant name in all entries of the
`DST_TOPIC_MAP` in the Python file before uploading:
**it must reflect your unique tenant name**.

When creating the function through the Astra Streaming UI:

- Name = `rrouter-function`, namespace = `default`;
- upload the `pulsar_routing_function/review_router.py` and pick the `ReviewRouter` function name;
- input topic: `default` and `rr-raw-in`;
- leave output/log topics empty;
- do not touch Advanced Configuration;
- no need for any further option configuration. Hit "Create".

The function will display as "Initializing" in the listing for some time
(20 s perhaps), then "Running". You're all set now.

#### If you use standard Pulsar

We assume in the following a [fresh dockerized Pulsar installation](https://pulsar.apache.org/docs/en/standalone-docker/), i.e.
obtained with

```
docker run                                          \
    -it                                             \
    -p 6650:6650                                    \
    -p 8080:8080                                    \
    --mount source=pulsardata,target=/pulsar/data   \
    --mount source=pulsarconf,target=/pulsar/conf   \
    apachepulsar/pulsar:2.9.1                       \
    bin/pulsar                                      \
    standalone
```

(note that ports 6650 and 8080 are made accessible from outside docker: we are going to take advantage of this fact.)

Spawn a shell on the Pulsar machine (here and in the following
we assume variable `CONTAINER_ID` contains the name of the Pulsar container):

    docker exec -it ${CONTAINER_ID} bash

and create the four required topics with
```
# this should output nothing
./bin/pulsar-admin topics list public/default

./bin/pulsar-admin topics create persistent://public/default/rr-raw-in
./bin/pulsar-admin topics create persistent://public/default/rr-hotel-reviews
./bin/pulsar-admin topics create persistent://public/default/rr-restaurant-reviews
./bin/pulsar-admin topics create persistent://public/default/rr-restaurant-anomalies

# this should list the four created topics
./bin/pulsar-admin topics list public/default
```

**Function:**

Create a directory in the Pulsar container to host the function file:
```
mkdir /root/functions
```

Next, carry the Python file (containing the Pulsar function) to the Docker instance
and install it as a Pulsar function:

    # IN YOUR LOCAL SHELL:
    docker cp pulsar_routing_function/review_router.py ${CONTAINER_ID}:/root/functions

```
# Back to the Pulsar machine shell
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

(You would delete it, should the need arise, with `./bin/pulsar-admin functions delete --tenant public --namespace default --name rrouter-function`).

The Pulsar setup is done.

### Local settings

Now that the Pulsar setup is done, let's turn to local configuration.

Copy the `.env.sample` file to `.env` and edit it:

`PULSAR_MODE` should match whether you use Astra Streaming or standard Pulsar.
In the former case, paste the values you obtained earlier for the streaming
connection/credentials in the `ASTRA_STREAMING_BROKER_URL` and
`ASTRA_STREAMING_TOKEN` variables.
In the latter case (standalone Pulsar, again assuming a simple local dockerized
installation) you are good with inserting the URL to your local Pulsar in
`PULSAR_CLIENT_URL` (probably `docker inspect ${CONTAINER_ID}` may help).

Make sure `TENANT` and `NAMESPACE` match your setup (the former is likely
`public` on a local Pulsar and is whatever tenant name you chose if you are
on Astra Streaming; the latter is most likely just `default`).

Unless you got creative with the topic names, those should be all
right as they are.

Next is the Astra DB part: take the token you created earlier for the DB
and paste it to `ASTRA_DB_APP_TOKEN`, while the values for
`ASTRA_DB_ID`, `ASTRA_DB_REGION` and `ASTRA_DB_KEYSPACE` are all to be found in the
main dashboard of your Astra UI.

### Python environment

Create a Python 3.6+ virtual environment, install the dependencies
in `requirements.txt` and also add the repo's root directory to the
`PYTHONPATH`. You should be in this virtual environment in all Python commands
you will soon start.



## Running the demo

Everything is now ready to run the demo.

Open three shells next to each other: one will run the review generator,
one will run the analyzer, and the third will consume and display entries
from the "review anomalies" topic.

> The third shell will run a simple utility able to subscribe to a generic
> Pulsar topic and display the items found therein. You can use it to peek
> into the other topics as well. But if you are using Astra Streaming you may
> as well want to explore the "Try Me!" feature available directly in the Web UI,
> which allows to read and write items by hand from/to Astra Streaming topics.

Now start in rapid succession these three commands in the three shells and
enjoy the show:
```
# first shell
./revGenerator/review_generator.py -r 10

# second shell
./revAnalyzer/review_analyzer.py -r -o -t -f 200

# third shell
./tools/reader.py -t rr-restaurant-anomalies
```

_Note_: you can customize the behaviour of those commands - try passing `-h`
to the scripts to see what is available.

### Querying the database

The only missing piece at this point are direct database queries. You can access
the tables in any way you want, for instance using the
provided [CQL shell on the Astra DB UI](https://github.com/datastaxdevs/awesome-astra/wiki/Cql-Shell):
just inspect the `trollsquad` keyspace and try to `SELECT` rows from the tables you find there.

> You will notice that the restaurant reviews are written in _two_ tables: one will simply
> contain the latest average score for each restaurant, the other is structured to offer
> historical data for e.g. a plotting client application (there is some built-in eviction
> of old results to avoid unbound growth of the table).

_Note:_ you just have to create the keyspace, since every time the analyzer starts
it checks for the tables and, if they do not exist, it creates them for you.

### Astra DB REST API

One of the nice things of Astra DB is that you effortlessly get various ways to interact
with your database through ordinary HTTP requests through
the [Stargate Data API](https://stargate.io/) on top of the underlying database.

The following examples are run with `cURL`, but of course they can be adapted
to any client able to issue simple HTTPS requests.

First source the `.env` file in a shell and construct the full base URL used in the subsequent requests:
```
. .env
ASTRA_URL_ROOT="https://${ASTRA_DB_ID}-${ASTRA_DB_REGION}.apps.astra.datastax.com/api/rest/v1/keyspaces/${ASTRA_DB_KEYSPACE}/tables"
```

then try to run the following commands one by one and wee what the result looks like:

```
# What restaurants can be queried?
curl -s -X GET \
    "${ASTRA_URL_ROOT}/known_ids_per_type/rows/restaurant" \
    -H "accept: application/json" \
    -H "X-Cassandra-Token: ${ASTRA_DB_APP_TOKEN}" | python -mjson.tool


# What reviewers can be queried?
curl -s -X GET \
    "${ASTRA_URL_ROOT}/known_ids_per_type/rows/reviewer" \
    -H "accept: application/json" \
    -H "X-Cassandra-Token: ${ASTRA_DB_APP_TOKEN}" | python -mjson.tool


# What's the current status of a restaurant?
curl -s -X GET \
    "${ASTRA_URL_ROOT}/restaurants_by_id/rows/vegg00" \
    -H "accept: application/json" \
    -H "X-Cassandra-Token: ${ASTRA_DB_APP_TOKEN}" | python -mjson.tool


# What's the current status of a reviewer?
curl -s -X GET \
    "${ASTRA_URL_ROOT}/reviewers_by_id/rows/geri" \
    -H "accept: application/json" \
    -H "X-Cassandra-Token: ${ASTRA_DB_APP_TOKEN}" | python -mjson.tool


# What is the timeline of reviews for a restaurant?
curl -s -X GET \
    "${ASTRA_URL_ROOT}/restaurants_by_id_time/rows/gold_f" \
    -H "accept: application/json" \
    -H "X-Cassandra-Token: ${ASTRA_DB_APP_TOKEN}" | python -mjson.tool
```
