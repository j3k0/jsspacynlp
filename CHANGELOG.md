# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-05-19

### Added

- On-demand model downloading from HuggingFace Hub (`huggingface_repo` config field)
- On-demand model downloading from pip URLs (`download_url` config field)
- Models cache directory with persistent Docker volume for downloaded models
- Fallback from `config.json` to `config.default.json` when user config is missing
- `spacy-transformers` dependency for transformer-based models (fr_dep_news_trf, es_dep_news_trf)
- `spacy-curated-transformers` dependency for English transformer model (en_core_web_trf)
- `JSSPACYNLP_MODELS_CACHE_DIR` environment variable for cache directory configuration
- `JSSPACYNLP_CORS_ORIGINS` environment variable for CORS origin configuration

### Changed

- Upgraded spaCy from 3.7.x to 3.8.11
- Updated all spaCy model versions to 3.8.0 in config examples
- Docker Compose now mounts a persistent `models-cache` volume for downloaded models

### Fixed

- TypeScript type for `BatchProcessor` configuration
- Dockerfile compatibility with restricted systems

## [Unreleased]

### Planned

- GPU acceleration support
- WebSocket support for real-time processing
- Multi-document context processing
- Additional export formats (CONLL, TEI XML)
- Authentication and rate limiting
- Metrics and monitoring dashboards
- Model hot-reloading without restart

## [0.1.0] - 2024-11-03

### Added

#### Server
- FastAPI-based REST API for lemmatization
- Compact JSON response format (50-70% smaller than traditional)
- Batch processing support (up to 1000 texts per request)
- Multi-language spaCy model support
- Custom model loading from mounted volumes
- Health check endpoint (`/health`)
- Model listing endpoint (`/models`)
- Service info endpoint (`/info`)
- Comprehensive error handling with detailed messages
- Docker support with optimized multi-stage build
- Model configuration via JSON file
- Environment-based configuration
- Request validation with Pydantic
- Automatic API documentation (OpenAPI/Swagger)
- Python tests with >80% coverage

#### Client
- TypeScript client library with full type definitions
- Promise-based async API
- Automatic retry with exponential backoff
- Batch processor for large datasets
- Streaming support for memory-efficient processing
- Progress tracking callbacks
- NoSketchEngine vertical format export
- CSV export utility
- JSON export utility
- Token filtering and manipulation
- Result parsing and formatting
- Configurable timeouts and retries
- Custom error types with detailed information
- Jest tests with >80% coverage

#### Infrastructure
- Docker Compose setup for development
- Production Docker Compose configuration
- Resource limits and health checks
- Volume mounting for models
- Network isolation

#### Documentation
- Comprehensive README with examples
- Server-specific documentation
- Client library API documentation
- Model configuration guide
- Contributing guidelines
- Troubleshooting guide
- Deployment instructions

### Features

- **Performance**: <100ms response time for 1000 words
- **Scalability**: Process millions of texts with batch processing
- **Flexibility**: Support for transformer, large, and custom models
- **Type Safety**: Full TypeScript support in client library
- **Developer Experience**: Auto-generated API docs, comprehensive tests
- **Production Ready**: Docker deployment, health checks, monitoring

### Supported Models

#### Transformer Models (Recommended)
- French: `fr_dep_news_trf`
- English: `en_core_web_trf`
- Spanish: `es_dep_news_trf`
- German: `de_dep_news_trf`

#### Large Models
- Italian: `it_core_news_lg`
- Portuguese: `pt_core_news_lg`
- Russian: `ru_core_news_lg`

#### Custom Models
- Support for user-provided spaCy models
- Serbian and Occitan (to be provided by users)



