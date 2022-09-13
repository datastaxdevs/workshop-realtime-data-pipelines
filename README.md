## 🎓 Real-Time data pipelines with Apache Pulsar™ and Apache Cassandra™

<img src="images/badge.png?raw=true" width="150" align="right" />

[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/datastaxdevs/workshop-realtime-data-pipelines)
[![License Apache2](https://img.shields.io/hexpm/l/plug.svg)](http://www.apache.org/licenses/LICENSE-2.0)
[![Discord](https://img.shields.io/discord/685554030159593522)](https://discord.com/widget?id=685554030159593522&theme=dark)

Welcome to the *RealTime data pipeline with Apache Pulsar and Apache Cassandra** workshop! In this two-hour workshop, we will show you a sample architecture making use of Apache Pulsar™ and Pulsar Functions for real-time, event-streaming-based data ingestion, cleaning and processing.

⏲️ **Duration :** 2 hours

🎓 **Level** Beginner to Intermediate

![](images/splash.png)

> [🔖 Accessing HANDS-ON](#-start-hands-on)

## 📋 Table of contents

- **HouseKeeping**
  - [Objectives](#objectives)
  - [Frequently asked questions](#frequently-asked-questions)
  - [Materials for the Session](#materials-for-the-session)
- **Architecture Design**
  - [Architecture overview](#architecture-overview)
  - [Injector Component](#injector-component)
  - [Analyzer Component](#analyzer-component)
- [**Setup - Initialize your environment**](#setup---initialize-your-environment)
- [**LAB1 - Producer and Consumer**](#)
  - [1.1 Start your tenant](#)
  - [1.2 Create topics](#)
  - [1.3 Start injector (producer)](#)
  - [1.4 Visualize messages (consumer)](#)
- [**LAB2 - Pulsar functions**](#)  
  - [2.1 Create function](#)
  - [2.2 Deploy function](#)
  - [2.3 Run Analyzer](#)
  - [2.4 Access Database](#)
- [**LAB3 - Pulsar I/O**](#)  
  - [3.1 Setup sink](#)
  - [3.2 Access Database](#)
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

#### `✅.001`- Open Gitpod

Gitpod is an IDE based on VSCode deployed in the cloud.


> ↗️ _Right Click and select open as a new Tab..._

<a href="https://gitpod.io/#https://github.com/datastaxdevs/workshop-realtime-data-pipelines"><img src="https://dabuttonfactory.com/button.png?t=Open+Gitpod&f=Open+Sans-Bold&ts=16&tc=fff&hp=20&vp=10&c=11&bgt=unicolored&bgc=0b5394" /></a>

#### `✅.002`- Create your Astra Account: Following web page opened by gitpod or follow this link

_**`ASTRA`** is the simplest way to run both Cassandra and Pulsat with zero operations at all - just push the button and get your clusters. No credit card required_

Leveraging [Database creation guide](https://awesome-astra.github.io/docs/pages/astra/create-instance/#c-procedure) create a database. *Right-Click the button* with *Open in a new TAB.*

The Astra registration page should have opened with Gitpod, if not use [this link](https://astra.dev/yt-9-14).

#### `✅.003`- reate Astra Credentials (token): Create an application token by following <a href="https://awesome-astra.github.io/docs/pages/astra/create-token/" target="_blank">these instructions</a>. 

Skip this step is you already have a token. You can reuse the same token in our other workshops, too.

> Your token should look like: `AstraCS:....`

#### `✅.004`- Setup Astra CLI

Go back to your gitpod terminal waiting for your token. Provide the value where it is asked

![pic](images/pic-astratoken.png)

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

- List your existing Users.

```
astra user list
```

> 🖥️ Output
>
> ```
> +--------------------------------------+-----------------------------+---------------------+
> | User Id                              | User Email                  | Status              |
> +--------------------------------------+-----------------------------+---------------------+
> | b665658a-ae6a-4f30-a740-2342a7fb469c | cedrick.lunven@datastax.com | active              |
> +--------------------------------------+-----------------------------+---------------------+
> ```

#### ✅ S.5 Create your database

- Create database `workshops` and keyspace `trollsquad` if they do not exist:

```
astra db create workshops -k trollsquad --if-not-exist --wait
```

Let's analyze the command:
| Chunk         | Description     |
|--------------|-----------|
| `db create` | Operation executed `create` in group `db`  |
| `workshops` | Name of the database, our argument |
|`-k trollsquad` | Name of the keyspace, a db can contains multiple keyspaces |
| `--if-not-exist` | Flag for itempotency creating only what if needed |
| `--wait` | Make the command blocking until all expected operations are executed (timeout is 180s) |

> **Note**: If the database already exist but has not been used for while the status will be `HIBERNATED`. The previous command will resume the db an create the new keyspace but it can take about a minute to execute.

> 🖥️ Output
>
> ```
> [ INFO ] - Database 'workshops' already exist. Connecting to database.
> [ INFO ] - Database 'workshops' has status 'MAINTENANCE' waiting to be 'ACTIVE' ...
>[ INFO ] - Database 'workshops' has status 'ACTIVE' (took 7983 millis)
> ```

- ✅ Check the status of database `workshops`

```
astra db status workshops
```

> 🖥️ Output
>
> ```
> [ INFO ] - Database 'workshops' has status 'ACTIVE'
> ```

- ✅ Get the informations for your database including the keyspace list

```
astra db get workshops
```

> 🖥️ Output
>
> ```
> +------------------------+-----------------------------------------+
> | Attribute              | Value                                   |
> +------------------------+-----------------------------------------+
> | Name                   | workshops                               |
> | id                     | bb61cfd6-2702-4b19-97b6-3b89a04c9be7    |
> | Status                 | ACTIVE                                  |
> | Default Cloud Provider | AWS                                     |
> | Default Region         | us-east-1                               |
> | Default Keyspace       | trollsquad                              |
> | Creation Time          | 2022-08-29T06:13:06Z                    |
> |                        |                                         |
> | Keyspaces              | [0] trollsquad                          |
> |                        |                                         |
> |                        |                                         |
> | Regions                | [0] us-east-1                           |
> |                        |                                         |
> +------------------------+-----------------------------------------+
> ```

## LAB1 - Producer and Consumer

#### 1.1 Create tenant

> **Note**: Your tenant name must start with a lowercase alphabetic character. It can only contain lowercase alphanumeric characters, and hyphens (kebab-case), and the maximum length is 25.

- ✅ Generate an unique tenant name

A tenant name should also BE UNIQUE IN ALL CLUSTER. So to get a unique name let's generate one randomly.

```
export TENANT="trollsquad-$(tr -dc a-z0-9 </dev/urandom | head -c 9 ; echo '')"
echo $TENANT
```

> 🖥️ Output (*faked, I am not that lucky*)
>
> ```
> trollsquad-abcdefghi
>```

- ✅ Create the tenant using the generated name

You can create a tenant from the user interface using [this tutorial](https://docs.datastax.com/en/astra-streaming/docs/astream-quick-start.html#create-a-tenant) but we will not use this today.

We will use the CLI for everyone to share the same values for regions and cloud provider. We will default all values for simplicity and because they are harcoded in the configuration file.

```
astra streaming create ${TENANT}
```

```
[ INFO ] - Tenant 'trollsquad-abcdefghi' has being created.
```

- ✅ List your tenants

```
astra streaming list
```

- ✅ Start `Pulsar-shell`

> **Note** Pulsar shell is a fast and flexible shell for Pulsar cluster management, messaging, and more. It's great for quickly switching between different clusters, and can modify cluster or tenant configurations in an instant.

Astra CLI will download and install the software if needed. Then it will generate a `client.conf` based on the tenant name you provide.

```
astra streaming pulsar-shell ${TENANT}
```

> 🖥️ Output
> ```
> [ INFO ] - pulsar-shell first launch, downloading (~ 60MB), please wait...
> [ INFO ] - pulsar-shell has been installed
> /home/gitpod/.astra/lunastreaming-shell-2.10.1.1/conf/client-aws-useast2-trollsquad-pk6oztya8.conf
> Pulsar-shell is starting please wait for connection establishment...
> Using directory: /home/gitpod/.pulsar-shell
> Welcome to Pulsar shell!
>   Service URL: pulsar+ssl://pulsar-aws-useast2.streaming.datastax.com:6651
>   Admin URL: https://pulsar-aws-useast2.api.streaming.datastax.com
> 
> Type help to get started or try the autocompletion (TAB button).
> Type exit or quit to end the shell session.
> 
> default(pulsar-aws-useast2.streaming.datastax.com)> 
> ```

#### 1.2 Create topics

- ✅ Show namespaces in `pulsar-shell`

```
admin namespaces list ${TENANT}
```

> 🖥️ Output
>
> ```
> trollsquad-abcdefghijkl/default
>```

- ✅ Show topics in `pulsar-shell` (empty)

```bash
admin topics list ${TENANT}/default
```

- ✅ Create topics `rr-raw-in`, `rr-hotel-reviews` `rr-restaurant-reviews` `rr-restaurant-anomalies`.

You can create topics through the user interface following this [official documentation](https://docs.datastax.com/en/astra-streaming/docs/astream-quick-start.html#create-a-topic) and [awesome-astra](https://awesome-astra.github.io/docs/pages/astra/create-topic/). 

But here we will keep leveraging on `pulsar-shell`.

```
admin topics create persistent://${TENANT}/default/rr-raw-in
admin topics create persistent://${TENANT}/default/rr-hotel-reviews
admin topics create persistent://${TENANT}/default/rr-restaurant-reviews
admin topics create persistent://${TENANT}/default/rr-restaurant-anomalies
```

- ✅ Show topics

```
admin topics list ${TENANT}/default
```

> 🖥️ Output
>
> ```
> persistent://trollsquad-pk6oztya8/default/rr-raw-in
> persistent://trollsquad-pk6oztya8/default/rr-restaurant-anomalies
> persistent://trollsquad-pk6oztya8/default/rr-hotel-reviews
> persistent://trollsquad-pk6oztya8/default/rr-restaurant-reviews
> ```

- ✅ Exit

```
exit
```

- ✅ Show your topic `rr-raw-in` in Astra User Interface:

```
ORGID=`astra org id`
gp preview --external https://astra.datastax.com/org/${ORGID}/streaming/pulsar-aws-useast2/tenants/${TENANT}/topics/namespaces/default/topics/rr-raw-in/1/0/overview
```

#### 1.3 Start injector (producer)

- Create `.env` as configuration file

```
cp .env.sample .env
ASTRA_DB_ID=`astra db get workshops --key id`
echo "ASTRA_DB_ID=\"${ASTRA_DB_ID}\"" >> .env
ASTRA_DB_APP_TOKEN=`astra config get default --key ASTRA_DB_APPLICATION_TOKEN`
echo "ASTRA_DB_APP_TOKEN=\"${ASTRA_DB_APP_TOKEN}\"" >> .env
echo "TENANT=\"${TENANT}\"" >> .env
PULSAR_TOKEN=`astra streaming pulsar-token ${TENANT}`
echo "PULSAR_TOKEN=\"${PULSAR_TOKEN}\"" >> .env
ORGID=`astra org id`
echo "ORGID=\"${ORGID}\"" >> .env

tail -5 .env
```

- Start the generator

```
/workspace/workshop-realtime-data-pipelines/revGenerator/review_generator.py -r 10
```

- Show producer on the UI

```
set -a
source .env
set +a
gp preview --external https://astra.datastax.com/org/${ORGID}/streaming/pulsar-aws-useast2/tenants/${TENANT}/topics/namespaces/default/topics/rr-raw-in/1/0/producers
```

#### 1.4 Visualize messages (consumer)

Locate terminal `consumer` or open a new one with shorcut `CONTROL^ + SHIFT + ``.

- Load environment variables and start pulsar shell

```
set -a
source .env
set +a
astra streaming ${TENANT} pulsar-shell
```

- Launch a consumer in the console

```
client consume persistent://${TENANT}/default/rr-raw-in -s consume_log -n 0
```

- Show Consumers in the Astra User Interface

```
gp preview --external https://astra.datastax.com/org/${ORGID}/streaming/pulsar-aws-useast2/tenants/${TENANT}/topics/namespaces/default/topics/rr-raw-in/1/0/consumers
```

### LAB2 - Pulsar functions

#### 2.1 Create function

```
gp open /workspace/workshop-realtime-data-pipelines/pulsar_routing_function/review_router.py
sed -i "s/___TENANT___/${TENANT}/" /workspace/workshop-realtime-data-pipelines/pulsar_routing_function/review_router.py
```

#### 2.2 Deploy function

When creating the function through the Astra Streaming UI:

- Name = `rrouter-function`, namespace = `default`;
- upload the `pulsar_routing_function/review_router.py` and pick the `ReviewRouter` function name;
- input topic: `default` and `rr-raw-in`;
- leave output/log topics empty;
- do not touch Advanced Configuration;
- no need for any further option configuration. Hit "Create".

The function will display as "Initializing" in the listing for some time
(20 s perhaps), then "Running". You're all set now.

- Access Pulsar-shell

```
astra streaming pulsar-shell ${TENANT}
```

- List functions
```
admin functions list --tenant=${TENANT} --namespace=default
```

```bash
admin functions create \
  --py /workspace/workshop-realtime-data-pipelines/pulsar_routing_function/review_router.py \
  --classname review_router.ReviewRouter \
  --tenant ${TENANT} \
  --namespace default \
  --name rrouter-function \
  --inputs persistent://${TENANT}/default/rr-raw-in
```

```bash
admin functions list --tenant=${TENANT} --namespace=default
```

- You should have items in `rr-hotel-reviews` and `rr-restaurant-reviews` now. 

```
gp preview --external https://astra.datastax.com/org/${ORGID}/streaming/pulsar-aws-useast2/tenants/${TENANT}/topics/namespaces/default/topics/rr-hotel-reviews/1/0
```

```
gp preview --external https://astra.datastax.com/org/${ORGID}/streaming/pulsar-aws-useast2/tenants/${TENANT}/topics/namespaces/default/topics/rr-restaurant-reviews/1/0
```

- Check content with consumer

```
client consume persistent://${TENANT}/default/rr-restaurant-reviews -s consume_log -n 0
```

#### 2.3 Run Analyzer

- Start Analyzer in shell `analyzer`

```
/workspace/workshop-realtime-data-pipelines/revAnalyzer/review_analyzer.py -r -o -t -f 200
```

- Start reader to log anomalies in shell `reader`

```
/workspace/workshop-realtime-data-pipelines/tools/reader.py -t rr-restaurant-anomalies
```

_Note_: you can customize the behaviour of those commands - try passing `-h`
to the scripts to see what is available.

#### 2.4 Query the Database

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

- ✅ What restaurants can be queried?

```
astra db cqlsh workshops \
   -e "select * from trollsquad.known_ids_per_type where id_type='restaurant'"
```

- ✅ What reviewers can be queried?

```
astra db cqlsh workshops \
   -e "select * from trollsquad.known_ids_per_type where id_type='reviewer'"
```

- ✅ What's the current status of a restaurant?

```
astra db cqlsh workshops \
   -e "select * from trollsquad.restaurants_by_id where id='vegg00'"
```

- ✅ What's the current status of a reviewer?

```
astra db cqlsh workshops \
   -e "select * from trollsquad.reviewers_by_id where id='geri'"
```

- ✅ What is the timeline of reviews for a restaurant?

```
astra db cqlsh workshops \
   -e "select * from trollsquad.restaurants_by_id_time where id='gold_f'"
```

```

Cqlsh is starting please wait for connection establishment...

 id     | time                            | average | name
--------+---------------------------------+---------+-------------
 gold_f | 2022-09-13 00:48:51.481000+0000 | 5.14027 | Golden Fork
 gold_f | 2022-09-13 00:48:52.782000+0000 | 4.02716 | Golden Fork
 gold_f | 2022-09-13 00:48:59.465000+0000 |  2.9716 | Golden Fork
 gold_f | 2022-09-13 00:49:01.645000+0000 | 4.91724 | Golden Fork
 gold_f | 2022-09-13 00:49:03.377000+0000 | 4.09476 | Golden Fork
 gold_f | 2022-09-13 00:49:05.156000+0000 | 3.31554 | Golden Fork
 gold_f | 2022-09-13 00:49:06.902000+0000 | 4.79082 | Golden Fork
 gold_f | 2022-09-13 00:49:08.588000+0000 | 3.13101 | Golden Fork
 gold_f | 2022-09-13 00:49:10.141000+0000 | 4.96983 | Golden Fork
 gold_f | 2022-09-13 00:49:12.284000+0000 | 4.87864 | Golden Fork
 gold_f | 2022-09-13 00:49:13.722000+0000 | 4.18713 | Golden Fork
 gold_f | 2022-09-13 00:49:15.501000+0000 |  2.9564 | Golden Fork
 ```

 ### LAB3 - Pulsar I/O

 We used a standalone analyzer to create the tables and populate values.

 What is, each time a data is inserted in a topic is ti copy in the db

#### 3.1 Setup sink

https://docs.datastax.com/en/astra-streaming/docs/astream-astradb-sink.html

https://pulsar.apache.org/docs/io-cli#sinks

```
admin sinks create \

```

#### 3.2 Access Database

