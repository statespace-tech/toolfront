from urllib.parse import urljoin

import click
import duckdb

from toolfront.utils import clean_url


@click.group()
def document():
    """Document commands for full-text search and content navigation."""
    pass


@document.command()
@click.argument("url", type=click.STRING)
@click.option(
    "--stemmer",
    default="porter",
    type=click.Choice(
        [
            "arabic",
            "basque",
            "catalan",
            "danish",
            "dutch",
            "english",
            "finnish",
            "french",
            "german",
            "greek",
            "hindi",
            "hungarian",
            "indonesian",
            "irish",
            "italian",
            "lithuanian",
            "nepali",
            "norwegian",
            "porter",
            "portuguese",
            "romanian",
            "russian",
            "serbian",
            "spanish",
            "swedish",
            "tamil",
            "turkish",
            "none",
        ]
    ),
    help="The type of stemmer to be used. One of 'arabic', 'basque', 'catalan', 'danish', 'dutch', 'english', 'finnish', 'french', 'german', 'greek', 'hindi', 'hungarian', 'indonesian', 'irish', 'italian', 'lithuanian', 'nepali', 'norwegian', 'porter', 'portuguese', 'romanian', 'russian', 'serbian', 'spanish', 'swedish', 'tamil', 'turkish', or 'none' if no stemming is to be used. Defaults to 'porter'",
)
@click.option(
    "--stopwords",
    default="english",
    type=click.STRING,
    help="Qualified name of table containing a single VARCHAR column containing the desired stopwords, or 'none' if no stopwords are to be used. Defaults to 'english' for a pre-defined list of 571 English stopwords",
)
@click.option(
    "--ignore",
    default="(\\.|[^a-z])+",
    help="Regular expression of patterns to be ignored. Defaults to '(\\.|[^a-z])+', ignoring all escaped and non-alphabetic lowercase characters",
)
@click.option(
    "--strip-accents/--no-strip-accents", default=True, help="Whether to remove accents (e.g., convert 'á' to 'a')"
)
@click.option("--lower/--no-lower", default=True, help="Whether to convert all text to lowercase")
@click.option("--overwrite/--no-overwrite", default=False, help="Whether to overwrite an existing index on a table")
@click.option(
    "--attach", type=click.Path(exists=True), help="Attach a database file with authentication secrets and settings"
)
def index(url, stemmer, stopwords, ignore, strip_accents, lower, overwrite, attach):
    """Create a DuckDB full-text search index from all files in directory.

    Usage: `document index URL [OPTIONS]`

    Parameters
    ----------
    url : str
        Directory path or url containing files to index
    stemmer : str
        The type of stemmer to be used (defaults to 'porter')
    stopwords : str
        Qualified name of table containing stopwords (defaults to 'english')
    ignore : str
        Regular expression of patterns to be ignored
    strip_accents : bool
        Whether to remove accents (e.g., convert 'á' to 'a')
    lower : bool
        Whether to convert all text to lowercase
    overwrite : bool
        Whether to overwrite an existing index on a table
    attach : str
        Attach a database file with authentication secrets and settings

    LLM Instructions
    ----------------
    1. ALWAYS provide the url as the first argument - this is the directory containing files to index
    2. The index.duckdb file will be created in the same directory as the url
    3. ALL files in the directory (recursively) will be indexed
    4. Choose appropriate stemmer based on document language (default 'porter' works for English)
    5. Use --overwrite flag if you need to rebuild an existing index
    6. The resulting index.duckdb file can be searched using the 'search' command

    Example
    -------
    ```bash
    uvx toolfront document index ./docs --stemmer french --stopwords french
    ```
    """

    url = clean_url(url).rstrip("/") + "/"

    index_url = urljoin(url, "index.duckdb")
    with duckdb.connect(index_url) as conn:
        if attach:
            conn.execute(f"ATTACH '{attach}'")
        conn.execute("INSTALL fts")
        conn.execute("LOAD fts")

        # Create table with data from all files
        conn.execute(f"""
            CREATE OR REPLACE TABLE documents AS
            SELECT
                filename,
                content
            FROM read_blob('{url}/**/*')
            WHERE content IS NOT NULL;
        """)

        # Create lines table for line-level searching
        conn.execute("""
            CREATE OR REPLACE TABLE lines AS
            SELECT
                filename,
                unnest(string_split(content::VARCHAR, '\n')) AS line,
                ROW_NUMBER() OVER (PARTITION BY filename ORDER BY (SELECT NULL)) AS line_number
            FROM documents;
        """)

        conn.execute(f"""
            PRAGMA create_fts_index(
                'documents',
                'filename',
                'content',
                stemmer='{stemmer}',
                stopwords='{stopwords}',
                ignore='{ignore}',
                strip_accents={str(strip_accents).lower()},
                lower={str(lower).lower()},
                overwrite={overwrite}
            );
        """)

        result = conn.execute("SELECT COUNT(*) FROM documents;").fetchone()
        num_files = result[0] if result else 0

        click.echo(f"DuckDB index with {num_files} files created in {index_url}")
