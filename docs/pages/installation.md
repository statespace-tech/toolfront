# Installation

Toolfront is available on PyPI as `toolfront` so installation is as simple as:

=== ":fontawesome-brands-python:{ .middle } &nbsp; pip"

    ```bash
    pip install toolfront
    ```

=== ":simple-uv:{ .middle } &nbsp; uv"

    ```bash
    uv add toolfront
    ```

=== ":fontawesome-brands-python:{ .middle } &nbsp; poetry"

    ```bash
    poetry add toolfront
    ```
<!-- 
To use ToolFront's database CLI tools with a specific database, install the corresponding extra:

- `bigquery`
- `clickhouse`
- `databricks`
- `druid`
- `duckdb`
- `flink`
- `mssql`
- `mysql`
- `oracle`
- `postgres`
- `pyspark`
- `risingwave`
- `snowflake`
- `sqlite`
- `trino`

You can also install dependencies for multiple databases, for example:

=== ":fontawesome-brands-python:{ .middle } &nbsp; pip"

    ```bash
    pip install "toolfront[postgres,bigquery,snowflake]"
    ```

=== ":simple-uv:{ .middle } &nbsp; uv"

    ```bash
    uv add "toolfront[postgres,bigquery,snowflake]"
    ```

=== ":fontawesome-brands-python:{ .middle } &nbsp; poetry"

    ```bash
    poetry add "toolfront[postgres,bigquery,snowflake]"
    ``` -->
