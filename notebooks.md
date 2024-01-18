## Using Malloy in IPython notebooks

Install Malloy if it isn't installed already.

```sh
python3 -m pip install malloy
```

Load the Malloy package.

```sh
%reload_ext malloy
```


## Malloy Cell Magics

Malloy uses 2 kinds of cell magics for using models and queries.
To declare or import a model, use `%%malloy_model` magic:

```sh
%%malloy_model imdb

source: titles is duckdb.table('./titles.parquet') extend {
  primary_key: tconst
  dimension:
    movie_url is concat('https://www.imdb.com/title/',tconst)
}
```

It should be noted that each model cell must be given a unique name and models have to be declared before using them in query cells.

To create a query cell, use `%%malloy_query` magic:

```sh
%%malloy_query imdb
run: titles -> {
  # link
  group_by: movie_url
  limit: 2
}
```

Here, the query cell is referring to a model that is declared as `imdb` in the model cell above.
If you would like to save the query results to a variable (for ex: `result_var`), mention the variable name next to the model name:

```sh
%%malloy_query imdb result_var
run: titles -> {
  # link
  group_by: movie_url
  limit: 2
}
```

## Malloy Service path

By default, Malloy-Py spins up it's own instance of Malloy Service gRPC server locally. If you would like to use your own instance of Malloy-Service (for ex: docker), use the below config:

```sh
MALLOY_SERVICE='127.0.0.1:14310'
```