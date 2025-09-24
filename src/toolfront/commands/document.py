from urllib.parse import urljoin

import click
import duckdb

from toolfront.utils import clean_url

DEFAULT_CHUNK_SIZE = 10000


@click.group()
def document():
    """Document commands"""
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

    This command builds a searchable index from text files in a directory, enabling fast full-text search capabilities.
    The index is stored as a DuckDB database file that can be queried using the search command.

    Instructions:
    1. ALWAYS provide the url as the first argument - this is the directory containing files to index
    2. The index.duckdb file will be created in the same directory as the url
    3. Use --files pattern to specify which files to include (supports glob patterns like "*.txt", "*.md", "**/*.py")
    4. Choose appropriate stemmer based on document language (default 'porter' works for English)
    5. Use --overwrite flag if you need to rebuild an existing index
    6. The resulting index.duckdb file can be searched using the 'search' command

    Args:
        url: Directory path or url containing files to index (e.g., "/path/to/docs", "s3://bucket/docs")
        params: Authentication parameters for the filesystem protocol (default: None)
        files: Glob pattern for files to include (default: "*.txt", "*.md")
        stemmer: Language-specific stemmer for better search (default: "porter" for English)
        stopwords: Language for common words to ignore (default: "english")
        ignore: Regex pattern for characters to ignore durlng indexing
        strip_accents: Remove accents from characters (default: True)
        lower: Convert text to lowercase (default: True)
        overwrite: Replace existing index if it exists (default: False)

    Examples:
        # Index all .txt and .md files in current directory
        toolfront document index ./

        # Index Python files with custom pattern
        toolfront document index ./src --files py

        # Index with French language settings
        toolfront document index ./docs --stemmer french --stopwords french
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

    This command searches through a previously created document index and returns ranked results based on relevance.
    Uses BM25 scoring algorithm to rank documents by how well they match the search terms.

    Instructions:
    1. ALWAYS ensure an index.duckdb file exists in the url directory (create with 'index' command first)
    2. Provide search terms as a single string - can include multiple words for phrase matching
    3. Use --limit to control how many results to return (default: 10)
    4. Results are automatically ranked by relevance score (highest first)
    5. Search is case-insensitive and handles stemming based on index configuration

    Args:
        url: Directory containing the index.duckdb file (default: current directory)
        terms: Search query string (e.g., "machine learning", "error handling python")
        limit: Maximum number of results to return (default: 10)

    Examples:
        # Basic search in current directory
        toolfront document search ./ "python functions"

        # Search with specific result limit
        toolfront document search file:///path/to/index "API documentation" --limit 5

        # Search in specific index location
        toolfront document search s3://bucket/path/to/index "error handling"
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

    This command provides efficient access to large documents by automatically breaking them into manageable chunks.
    Supports multiple file formats and offers flexible navigation options for targeted reading.

    Instructions:
    1. ALWAYS provide a valid file URL/path with supported extensions (.json, .md, .txt, .xml, .yaml, .rtf, .html)
    2. Use pagination strategically to avoid reading entire large documents unnecessarily
    3. For targeted information extraction, use percentile-based navigation first, then section-based for precision
    4. STOP reading once you find the information you need - don't continue through the entire document
    5. When analyzing document structure, start with small chunks to understand layout before deep diving

    Navigation Strategies:
    - Full document (pagination=-1): Use only for small files or when complete content is needed
    - Percentile navigation (0.0-0.99): Jump to approximate document positions (0.1=beginning, 0.5=middle, 0.9=end)
    - Section navigation (>=1): Read specific numbered chunks sequentially
    - Binary search approach: Start with educated percentile guess, then refine based on content

    Args:
        url: File path or url to the document (e.g., "/path/to/doc.txt", "s3://bucket/file.md")
        pagination: Navigation mode - -1 (full), 0.0-0.99 (percentile), >=1 (section number)
        chunk_size: Chunk size in characters for section-based reading (default: 10000)

    Examples:
        # Read full small document
        toolfront document read ./README.md

        # Read middle section of large document
        toolfront document read ./large_doc.txt --pagination 0.5 --chunk-size 5000

        # Read first chunk with custom chunk size
        toolfront document read ./data.json --pagination 1 --chunk-size 5000

        # Jump to conclusion section (typically near end)
        toolfront document read ./paper.pdf --pagination 0.8 --chunk-size 5000
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
