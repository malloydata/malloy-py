![Malloy Logo](https://raw.githubusercontent.com/malloydata/malloy-py/main/assets/malloy_square_centered.png)

## What is it?

Malloy is an experimental language for describing data relationships and transformations. It is both a semantic modeling language and a querying language that runs queries against a relational database. Malloy currently connects to BigQuery, and natively supports DuckDB. We've built a Visual Studio Code extension to facilitate building Malloy data models, querying and transforming data, and creating simple visualizations and dashboards.

*Note: These APIs are still in development and are subject to change.*

## How do I get it?

Binary installers for the latest released version are available at the Python Package Index (PyPI). (Currently only available through the test respository)

```sh
python3 -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ malloy==2022.1006a0
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

Run named query from malloy file:

```python
import asyncio

import malloy
from malloy.data.duckdb import DuckDbConnection


async def main():
    home_dir = "/path/to/samples/duckdb/names"
    with malloy.Runtime() as runtime:
        runtime.add_connection(DuckDbConnection(home_dir=home_dir))

        data = await runtime.load_file(home_dir + "/1_names.malloy").run("duckdb", named_query="j_names")

        dataframe = data.df()
        print(dataframe)


if __name__ == "__main__":
    asyncio.run(main())


```

Get SQL from inline query using malloy file as source:

```python
import asyncio

import malloy
from malloy.data.duckdb import DuckDbConnection


async def main():
    home_dir = "/path/to/samples/duckdb/faa"
    with malloy.Runtime() as runtime:
        runtime.add_connection(DuckDbConnection(home_dir=home_dir))

        sql = await runtime.load_file(home_dir +"/2_flights.malloy").get_sql(
                query="""
                  query: flights -> {
                    where: carrier ? 'WN' | 'DL', dep_time ? @2002-03-03 
                    group_by: 
                      flight_date is dep_time.day
                      carrier
                    aggregate: 
                      daily_flight_count is flight_count
                      aircraft.aircraft_count
                    nest: per_plane_data is {
                      top: 20
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

Write inline malloy model source and run query:

```python
import asyncio

import malloy
from malloy.data.duckdb import DuckDbConnection


async def main():
    home_dir = "/path/to/samples/duckdb/auto_recalls"
    with malloy.Runtime() as runtime:
        runtime.add_connection(DuckDbConnection(home_dir=home_dir))

        data = await runtime.load_source("""
        source: auto_recalls is table('duckdb:auto_recalls.csv') {
          declare:
            recall_count is count()
            percent_of_recalls is recall_count/all(recall_count)*100
        }
        """).run("duckdb", query="""
        query: auto_recalls -> {
          group_by: Manufacturer
          aggregate:
            recall_count
            percent_of_recalls
        }
        """)

        dataframe = data.df()
        print(dataframe)


if __name__ == "__main__":
    asyncio.run(main())

```
