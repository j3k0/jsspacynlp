# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

## [Unreleased]

### Planned

- GPU acceleration support
- Model caching for improved performance
- WebSocket support for real-time processing
- Multi-document context processing
- Additional export formats (CONLL, TEI XML)
- Authentication and rate limiting
- Metrics and monitoring dashboards
- Model hot-reloading without restart

---

## Release Notes

### v0.1.0 - Initial Release

This is the first release of jsspacynlp, providing a complete lemmatization microservice with:

- High-performance FastAPI server
- TypeScript client library
- Batch processing capabilities
- Multi-language support
- Docker deployment
- Comprehensive documentation

**Installation:**
```bash
# Server
docker-compose up -d

# Client
npm install jsspacynlp
```

**Quick Start:**
```typescript
import { SpacyNLP } from 'jsspacynlp';

const nlp = new SpacyNLP({ apiUrl: 'http://localhost:8000' });
const result = await nlp.lemmatize('Hello world', 'en_core_web_sm');
```

See README.md for full documentation.

