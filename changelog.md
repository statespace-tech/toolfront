# 🚀 Release v0.1.10

## Document Library Support
Added document library functionality to ToolFront, enabling AI agents to search and read documents alongside database and API operations.

**Supported Document Types:**
- **PDF** (`.pdf`) - with smart pagination
- **Microsoft Office** - Word (`.docx`), PowerPoint (`.pptx`), Excel (`.xlsx`, `.xls`)
- **Text formats** - JSON, Markdown, TXT, XML, YAML/YML, RTF

**Key Features:**
- **Intelligent Pagination**: Percentile-based navigation for large documents
- **Performance Optimized**: Caching layer for improved response times
- **No External Dependencies**: BM25 implementation without embeddings

## 🔧 Technical Improvements

- **Modular Architecture**: Separated tools into API, database, and library modules
- **Improved Caching**: Improved performance for schema discovery and document operations

## 📦 Installation

Document support is available as an optional dependency:

```bash
# Install with document support
uv pip install -e ".[document]"
```

## 🔧 Usage

Add a document library to your ToolFront configuration:

```bash
# Point to any directory containing documents
file:///path/to/your/documents

# Example: Documents in your Downloads folder
file:///Users/username/Downloads
```

## 🐛 Bug Fixes

- Fixed various edge cases in search algorithms
- Improved error handling for malformed documents
- Better connection management for large file operations

This release expands ToolFront's capabilities, allowing AI agents to work with both structured data (databases) and unstructured data (documents) in a unified interface.

---

**Full Changelog**: https://github.com/kruskal-labs/toolfront/compare/v0.1.9...v0.1.10
