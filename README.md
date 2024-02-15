![Malloy Logo](https://raw.githubusercontent.com/malloydata/malloy-py/main/assets/malloy_square_centered.png)

## What is it?

Malloy is an experimental language for describing data relationships and transformations. It is both a semantic modeling language and a querying language that runs queries against a relational database. Malloy currently connects to BigQuery, and natively supports DuckDB. We've built a Visual Studio Code extension to facilitate building Malloy data models, querying and transforming data, and creating simple visualizations and dashboards.

_Note: These APIs are still in development and are subject to change._

## How do I get it?

Binary installers for the latest released version are available at the [Python Package Index](https://pypi.org/project/malloy/) (PyPI).

```sh
python3 -m pip install malloy
```

## Resources

- [Malloy Language GitHub](https://github.com/looker-open-source/malloy/) - Primary location for the malloy language source, documentation, and information
- [Malloy Language](https://looker-open-source.github.io/malloy/documentation/language/basic.html) - A quick introduction to the language
- [eCommerce Example Analysis](https://looker-open-source.github.io/malloy/documentation/examples/ecommerce.html) - A walkthrough of the basics on an ecommerce dataset (BigQuery public dataset)
- [Modeling Walkthrough](https://looker-open-source.github.io/malloy/documentation/examples/iowa/iowa.html) - An introduction to modeling via the Iowa liquor sales public data set (BigQuery public dataset)
- [Malloy on YouTube](https://www.youtube.com/channel/UCfN2td1dzf-fKmVtaDjacsg) - Watch demos / walkthroughs of Malloy

## Join The Community

- Join our [Malloy Slack Community!](https://join.slack.com/t/malloy-community/shared_invite/zt-upi18gic-W2saeFu~VfaVM1~HIerJ7w) Use this community to ask questions, meet other Malloy users, and share ideas with one another.
- Use [GitHub issues](https://github.com/looker-open-source/malloy/issues) to provide feedback, suggest improvements, report bugs, and start new discussions.

## Syntax Examples

### Run a named query from a Malloy file

```python
import asyncio

import malloy
from malloy.data.duckdb import DuckDbConnection

async def main():
  home_dir = "/path/to/samples/duckdb/imdb"
  with malloy.Runtime() as runtime:
    runtime.add_connection(DuckDbConnection(home_dir=home_dir))

    data = await runtime.load_file(home_dir + "/imdb.malloy").run(
        named_query="genre_movie_map")

    dataframe = data.to_dataframe()
    print(dataframe)

if __name__ == "__main__":
  asyncio.run(main())
```

### Get SQL from an in-line query, using a Malloy file as a source

```python
import asyncio

import malloy
from malloy.data.duckdb import DuckDbConnection

async def main():
  home_dir = "/path/to/samples/duckdb/faa"
  with malloy.Runtime() as runtime:
    runtime.add_connection(DuckDbConnection(home_dir=home_dir))

    [sql, connection
    ] = await runtime.load_file(home_dir + "/flights.malloy").get_sql(query="""
                  run: flights -> {
                    where: carrier ? 'WN' | 'DL', dep_time ? @2002-03-03
                    group_by:
                      flight_date is dep_time.day
                      carrier
                    aggregate:
                      daily_flight_count is flight_count
                      aircraft.aircraft_count
                    nest: per_plane_data is {
                      limit: 20
                      group_by: tail_num
                      aggregate: plane_flight_count is flight_count
                      nest: flight_legs is {
                        order_by: 2
                        group_by:
                          tail_num
                          dep_minute is dep_time.minute
                          origin_code
                          dest_code is destination_code
                          dep_delay
                          arr_delay
                      }
                    }
                }
            """)

    print(sql)

if __name__ == "__main__":
  asyncio.run(main())
```

### Write an in-line Malloy model, and run a query

```python
import asyncio

import malloy
from malloy.data.duckdb import DuckDbConnection


async def main():
  home_dir = "/path/to/samples/duckdb/imdb/data"
  with malloy.Runtime() as runtime:
    runtime.add_connection(DuckDbConnection(home_dir=home_dir))

    data = await runtime.load_source("""
        source:titles is duckdb.table('titles.parquet') extend {
          primary_key: tconst
          dimension:
            movie_url is concat('https://www.imdb.com/title/',tconst)
        }
        """).run(query="""
        run: titles -> {
          group_by: movie_url
          limit: 5
        }
        """)

    dataframe = data.to_dataframe()
    print(dataframe)


if __name__ == "__main__":
  asyncio.run(main())
  
```

### Querying BigQuary tables

BigQuery auth via OAuth using gcloud.
```
gcloud auth login --update-adc
gcloud config set project {my_project_id} --installation
```

Actual usage is similar to DuckDB.

```python
import asyncio
import malloy
from malloy.data.bigquery import BigQueryConnection

async def main():
  with malloy.Runtime() as runtime:
    runtime.add_connection(BigQueryConnection())

    data = await runtime.load_source("""
        source:ga_sessions is bigquery.table('bigquery-public-data.google_analytics_sample.ga_sessions_20170801') extend {
          measure:
            hits_count is hits.count()
        }
        """).run(query="""
        run: ga_sessions -> {
            where: trafficSource.`source` != '(direct)'
            group_by: trafficSource.`source`
            aggregate: hits_count
            limit: 10
          }
        """)

    dataframe = data.to_dataframe()
    print(dataframe)

if __name__ == "__main__":
  asyncio.run(main())

```

## Development

### Initial setup

```sh
git submodule init
git submodule update
python3 -m pip install -r requirements.dev.txt
scripts/gen-services.sh
```

### Regenerate Protobuf files

```sh
scripts/gen-protos.sh
```

### Tests

```sh
python3 -m pytest
```
