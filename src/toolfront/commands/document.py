from urllib.parse import urljoin

import click
import duckdb

from toolfront.utils import clean_url

DEFAULT_CHUNK_SIZE = 10000


@click.group()
def document():
    """Document commands for full-text search and content navigation."""
    pass


@document.command()
@click.argument("url", type=click.STRING)
@click.option("--files", "-f", multiple=True, default=["md"], help="File extensions to index. Defaults to 'md'.")
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
def index(url, files, stemmer, stopwords, ignore, strip_accents, lower, overwrite, attach):
    """Create a DuckDB full-text search index from files.

    Usage: `document index URL [OPTIONS]`

    Parameters
    ----------
    url : str
        Directory path or url containing files to index
    files : tuple[str, ...]
        File extensions to index. Defaults to 'md'
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
    3. Use --files pattern to specify which files to include (supports glob patterns like "*.txt", "*.md", "**/*.py")
    4. Choose appropriate stemmer based on document language (default 'porter' works for English)
    5. Use --overwrite flag if you need to rebuild an existing index
    6. The resulting index.duckdb file can be searched using the 'search' command

    Example
    -------
    ```bash
    uvx toolfront document index ./docs --files md --stemmer french --stopwords french
    ```
    """

    url = clean_url(url).rstrip("/") + "/"

    index_url = urljoin(url, "index.duckdb")
    with duckdb.connect(index_url) as conn:
        if attach:
            conn.execute(f"ATTACH '{attach}'")

        conn.execute("INSTALL fts")
        conn.execute("LOAD fts")

        # Create table with data from all matching file patterns
        conn.execute("""
            CREATE OR REPLACE TABLE documents (
                filename VARCHAR PRIMARY KEY,
                content TEXT
            );
        """)

        # Insert data for each file pattern
        for file in files:
            file = file.lstrip(".")
            conn.execute(f"""
                INSERT INTO documents (filename, content)
                SELECT
                    filename,
                    content
                FROM read_text('{url}/**/*.{file}')
                WHERE content IS NOT NULL AND trim(content) != '';
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


@document.command()
@click.argument("url", type=click.STRING)
@click.argument("terms", type=click.STRING)
@click.option("--limit", type=click.INT, default=10, help="Number of results to return")
@click.option(
    "--attach", type=click.Path(exists=True), help="Attach a database file with authentication secrets and settings"
)
def search(url, terms, limit, attach) -> None:
    """Search for documents in a DuckDB full-text search index.

    Usage: `document search URL TERMS [OPTIONS]`

    Parameters
    ----------
    url : str
        Directory containing the index.duckdb file
    terms : str
        Search query string
    limit : int
        Number of results to return
    attach : str
        Attach a database file with authentication secrets and settings

    LLM Instructions
    ----------------
    1. ALWAYS ensure an index.duckdb file exists in the url directory (create with 'index' command first)
    2. Provide search terms as a single string - can include multiple words for phrase matching
    3. Use --limit to control how many results to return (default: 10)
    4. Results are automatically ranked by relevance score (highest first)
    5. Search is case-insensitive and handles stemming based on index configuration

    Example
    -------
    ```bash
    uvx toolfront document search ./docs "python functions" --limit 5
    ```
    """

    url = clean_url(url).rstrip("/") + "/"
    index_url = urljoin(url, "./index.duckdb")

    with duckdb.connect(index_url) as conn:
        if attach:
            conn.execute(f"ATTACH '{attach}'")

        query = f"""
            SELECT filename, fts_main_documents.match_bm25(filename, '{terms}'::string) AS score
            FROM documents
            WHERE score IS NOT NULL
            ORDER BY score DESC
            LIMIT {limit}
        """
        data = conn.execute(query).fetchdf()["filename"]
    click.echo(data.to_list())


@document.command()
@click.argument("url", type=click.STRING)
@click.option(
    "--pagination",
    "-p",
    type=click.FLOAT,
    default=-1,
    help="Section navigation: 0.0-0.99 for percentile, >=1 for section number. -1 for full document.",
)
@click.option("--chunk-size", type=click.INT, default=DEFAULT_CHUNK_SIZE, help="Document chunk size in characters.")
@click.option(
    "--attach", type=click.Path(exists=True), help="Attach a database file with authentication secrets and settings"
)
def read(url, pagination, chunk_size, attach):
    """Read and navigate through document contents with intelligent chunking and pagination.

    Usage: `document read URL [OPTIONS]`

    Parameters
    ----------
    url : str
        File path or url to the document
    pagination : float
        Section navigation: 0.0-0.99 for percentile, >=1 for section number. -1 for full document
    chunk_size : int
        Document chunk size in characters
    attach : str
        Attach a database file with authentication secrets and settings

    LLM Instructions
    ----------------
    1. ALWAYS provide a valid file URL/path with supported extensions (.json, .md, .txt, .xml, .yaml, .rtf, .html)
    2. Use pagination strategically to avoid reading entire large documents unnecessarily
    3. For targeted information extraction, use percentile-based navigation first, then section-based for precision
    4. STOP reading once you find the information you need - don't continue through the entire document
    5. When analyzing document structure, start with small chunks to understand layout before deep diving
    6. Navigation Strategies: Full document (pagination=-1) for small files, Percentile navigation (0.0-0.99) for approximate positions, Section navigation (>=1) for numbered chunks, Binary search approach for precision

    Example
    -------
    ```bash
    uvx toolfront document read ./large_doc.txt --pagination 0.5 --chunk-size 5000
    ```
    """
    url = clean_url(url)

    with duckdb.connect(":memory:") as conn:
        if attach:
            conn.execute(f"ATTACH '{attach}'")

        conn.execute(f"""
        CREATE TABLE document AS
        SELECT content
        FROM read_text('{url}')
        """)

        # Get document length for pagination calculations
        content_length = conn.execute("SELECT length(content) FROM document;").fetchone()

        if not content_length:
            raise FileNotFoundError("Document is empty")

        content_length = content_length[0]

        if 0.0 <= pagination < 1.0:
            # Percentile-based pagination
            start_pos = int(pagination * content_length) + 1
            chunk_num = int(pagination * ((content_length + chunk_size - 1) // chunk_size)) + 1
            total_chunks = (content_length + chunk_size - 1) // chunk_size

            query = f"""
            SELECT substr(
                content,
                {start_pos},
                {chunk_size}
            ) AS chunk
            FROM document
            """
        elif pagination >= 1:
            # Section-based pagination (1-indexed)
            chunk_num = int(pagination)
            total_chunks = (content_length + chunk_size - 1) // chunk_size
            start_pos = (chunk_num - 1) * chunk_size + 1

            query = f"""
            SELECT substr(
                content,
                {start_pos},
                {chunk_size}
            ) AS chunk
            FROM document
            """
        else:
            # Full document
            chunk_num = 1
            total_chunks = 1
            query = "SELECT content AS chunk FROM document"

        data = conn.execute(query).fetchdf()
        chunk_content = data["chunk"].item()

    click.echo(f"<chunk={chunk_num}_of_{total_chunks}>\n{chunk_content}\n</chunk>")
