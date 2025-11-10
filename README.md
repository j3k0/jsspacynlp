# jsspacynlp

Fast lemmatization microservice powered by spaCy with TypeScript/JavaScript client library.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

jsspacynlp provides a performant REST API for text lemmatization using spaCy models, along with a full-featured TypeScript/JavaScript client library. Designed for processing large corpora efficiently, it features:

- **High Performance**: FastAPI-based server with batch processing
- **Compact Format**: 50-70% smaller JSON responses than traditional formats
- **Multi-Language**: Support for transformer and large spaCy models
- **Docker Ready**: Easy deployment with docker-compose
- **Export Utilities**: NoSketchEngine vertical format, CSV, JSON
- **Batch Processing**: Handle millions of texts with progress tracking
- **TypeScript**: Full type safety for the client library
- **Well Tested**: >80% test coverage on both server and client

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/j3k0/jsspacynlp.git
cd jsspacynlp

# Start the server
docker-compose up -d

# Check health
curl http://localhost:8000/health

# Install client library
npm install jsspacynlp
```

### Basic Usage

```javascript
import { SpacyNLP } from 'jsspacynlp';

const nlp = new SpacyNLP({ apiUrl: 'http://localhost:8000' });

// Lemmatize text
const result = await nlp.lemmatize(
  'Les chats courent dans le jardin.',
  'fr_dep_news_trf'
);

// Access tokens
for (const doc of result.documents) {
  for (const token of doc.tokens) {
    console.log(`${token.text} -> ${token.lemma} (${token.pos})`);
  }
}
```

## Architecture

```
┌────────────────────────────────────────┐
│   Your Application (Node.js/Browser)   │
│                                        │
│  ┌───────────────────────────────────┐ │
│  │  jsspacynlp Client Library        │ │
│  │  - Batch processing               │ │
│  │  - Export utilities               │ │
│  │  - Progress tracking              │ │
│  └───────────────┬───────────────────┘ │
└──────────────────┼─────────────────────┘
                   │ HTTP/REST
                   ▼
┌────────────────────────────────────────┐
│   jsspacynlp Server (Docker)           │
│                                        │
│  ┌───────────────────────────────────┐ │
│  │  FastAPI REST API                 │ │
│  │  - /lemmatize (batch support)     │ │
│  │  - /health, /models, /info        │ │
│  └───────────────┬───────────────────┘ │
│                  │                     │
│  ┌───────────────▼───────────────────┐ │
│  │  spaCy Model Registry             │ │
│  │  - Pre-loaded models              │ │
│  │  - Transformer & large models     │ │
│  │  - Custom model support           │ │
│  └───────────────────────────────────┘ │
└────────────────────────────────────────┘
```

## Project Structure

```
jsspacynlp/
├── server/              # Python FastAPI service
│   ├── app/
│   │   ├── main.py     # FastAPI endpoints
│   │   ├── models.py   # Model management
│   │   ├── schemas.py  # Request/response schemas
│   │   └── config.py   # Configuration
│   ├── tests/          # Python tests (pytest)
│   ├── Dockerfile
│   └── requirements.txt
├── client/              # TypeScript client library
│   ├── src/
│   │   ├── client.ts   # API client
│   │   ├── batch.ts    # Batch processor
│   │   ├── result.ts   # Result utilities
│   │   └── types.ts    # TypeScript types
│   ├── __tests__/      # TypeScript tests (Jest)
│   └── package.json
├── models/              # Model configuration
│   ├── config.json     # Model definitions
│   └── README.md       # Model documentation
├── docker-compose.yml   # Development setup
├── docker-compose.prod.yml  # Production setup
└── README.md
```

## Features

### Compact JSON Format

Traditional spaCy JSON responses can be very large. jsspacynlp uses a compact column-based format:

**Traditional Format** (verbose):
```json
{
  "tokens": [
    {"text": "Hello", "lemma": "hello", "pos": "INTJ", "tag": "UH"},
    {"text": "world", "lemma": "world", "pos": "NOUN", "tag": "NN"}
  ]
}
```

**jsspacynlp Format** (compact):
```json
{
  "annotations": ["text", "lemma", "pos", "tag"],
  "tokens": [
    [["Hello", "hello", "INTJ", "UH"],
     ["world", "world", "NOUN", "NN"]]
  ]
}
```

**Result**: 50-70% smaller payloads, faster parsing, lower bandwidth.

### Batch Processing

Process large corpora efficiently:

```javascript
import { SpacyNLP, BatchProcessor } from 'jsspacynlp';

const nlp = new SpacyNLP();
const processor = new BatchProcessor(nlp, {
  model: 'fr_dep_news_trf',
  batchSize: 1000,
  onProgress: (processed, total) => {
    console.log(`${processed}/${total} texts processed`);
  }
});

// Process 50,000+ texts
const texts = loadCorpus();
const result = await processor.process(texts);
```

### NoSketchEngine Export

Export directly to NoSketchEngine vertical format:

```javascript
const result = await processor.process(texts);
const vertical = result.toVertical();

// Output format:
// word1\tlemma1\tpos1\ttag1
// word2\tlemma2\tpos2\ttag2
// 
// word3\tlemma3\tpos3\ttag3

fs.writeFileSync('corpus.vertical', vertical);
```

### Multi-Language Support

Configure multiple spaCy models:

```json
{
  "models": [
    {
      "name": "fr_dep_news_trf",
      "language": "fr",
      "type": "transformer",
      "path": "fr_dep_news_trf"
    },
    {
      "name": "en_core_web_trf",
      "language": "en",
      "type": "transformer",
      "path": "en_core_web_trf"
    },
    {
      "name": "custom_occitan",
      "language": "oc",
      "type": "custom",
      "path": "/app/models/custom/oc_model"
    }
  ]
}
```

## Installation

### Server Setup

#### Using Docker (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/j3k0/jsspacynlp.git
cd jsspacynlp

# 2. Configure models
cp models/config.example.json models/config.json
# Edit models/config.json to add your models

# 3. Start server
docker-compose up -d

# 4. Check health
curl http://localhost:8000/health
```

#### Manual Installation

```bash
# 1. Install Python dependencies
cd server
pip install -r requirements.txt

# 2. Install spaCy models
python -m spacy download en_core_web_sm

# 3. Configure models
cd ../models
cp config.example.json config.json
# Edit config.json

# 4. Run server
cd ../server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Client Installation

```bash
npm install jsspacynlp
```

## Configuration

### Server Configuration

Environment variables (prefix: `JSSPACYNLP_`):

- `MODELS_CONFIG_DIR`: Model directory path (default: `/app/models`)
- `MODELS_CONFIG_FILE`: Config filename (default: `config.json`)
- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `8000`)
- `LOG_LEVEL`: Logging level (default: `info`)
- `MAX_BATCH_SIZE`: Maximum batch size (default: `1000`)
- `MAX_TEXT_LENGTH`: Maximum text length (default: `1000000`)

### Model Configuration

Create `models/config.json`:

```json
{
  "models": [
    {
      "name": "fr_dep_news_trf",
      "language": "fr",
      "type": "transformer",
      "path": "fr_dep_news_trf",
      "disable": ["parser", "ner"]
    }
  ]
}
```

See [models/README.md](models/README.md) for detailed configuration options.

## API Documentation

### REST API Endpoints

Interactive documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

#### POST /lemmatize

Lemmatize texts in batch.

**Request:**
```json
{
  "model": "fr_dep_news_trf",
  "texts": ["L'avion vole.", "Le chat dort."],
  "fields": ["text", "lemma", "pos"]
}
```

**Response:**
```json
{
  "annotations": ["text", "lemma", "pos"],
  "tokens": [
    [["L'", "le", "DET"], ["avion", "avion", "NOUN"], ["vole", "voler", "VERB"]],
    [["Le", "le", "DET"], ["chat", "chat", "NOUN"], ["dort", "dormir", "VERB"]]
  ],
  "model": "fr_dep_news_trf",
  "processing_time_ms": 42.5
}
```

#### GET /health

Health check.

#### GET /models

List available models.

#### GET /info

Service information.

### Client Library API

See [client/README.md](client/README.md) for full client documentation.

```typescript
import { SpacyNLP, BatchProcessor } from 'jsspacynlp';

// Create client
const nlp = new SpacyNLP({
  apiUrl: 'http://localhost:8000',
  timeout: 30000,
  retries: 3
});

// Lemmatize
const result = await nlp.lemmatize(texts, 'fr_dep_news_trf');

// Batch processing
const processor = new BatchProcessor(nlp, {
  model: 'fr_dep_news_trf',
  batchSize: 1000
});
const result = await processor.process(largeTextArray);

// Export
const vertical = result.toVertical();
const csv = result.toCSV();
const json = result.toJSON();
```

## Supported Languages & Models

### Recommended Models

**Transformer Models** (best quality, slower):
- French: `fr_dep_news_trf`
- English: `en_core_web_trf`
- Spanish: `es_dep_news_trf`
- German: `de_dep_news_trf`

**Large Models** (good quality, faster):
- Italian: `it_core_news_lg`
- Portuguese: `pt_core_news_lg`
- Russian: `ru_core_news_lg`

**Custom Models**:
- Serbian: (to be provided)
- Occitan: (to be provided)

### Installing Models

```bash
# Via pip
pip install https://github.com/explosion/spacy-models/releases/download/fr_dep_news_trf-3.7.0/fr_dep_news_trf-3.7.0-py3-none-any.whl

# Via spaCy CLI
python -m spacy download fr_dep_news_trf

# In Dockerfile (automatic)
RUN python -m spacy download fr_dep_news_trf
```

## Performance

- **API Response Time**: <100ms per 1000 words
- **Throughput**: >10,000 words per second
- **Memory**: ~2GB per transformer model, ~500MB per large model
- **Batch Size**: Optimal at 500-2000 texts per request

### Optimization Tips

1. **Disable Unnecessary Components**: Only keep tokenizer, tagger, lemmatizer
2. **Use Appropriate Batch Sizes**: 500-2000 texts per batch
3. **Pre-load Models**: Models are loaded at startup (not per-request)
4. **Resource Limits**: Allocate sufficient RAM (4-8GB for transformers)

## Testing

### Server Tests

```bash
cd server
pytest
pytest --cov=app --cov-report=html
```

### Client Tests

```bash
cd client
npm test
npm run test:coverage
```

### Integration Tests

```bash
# Start server
docker-compose up -d

# Run integration tests
cd server
pytest tests/test_integration.py

# Or run all tests
npm run test:all
```

## Development

### Server Development

```bash
cd server

# Install dev dependencies
pip install -r requirements-dev.txt

# Run with auto-reload
uvicorn app.main:app --reload

# Format code
black app/ tests/

# Lint
ruff check app/ tests/
```

### Client Development

```bash
cd client

# Install dependencies
npm install

# Build with watch
npm run dev

# Run tests in watch mode
npm run test:watch

# Lint
npm run lint

# Format
npm run format
```

## Deployment

### Production with Docker

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# Or with resource limits
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/models:/app/models:ro \
  --memory=8g \
  --cpus=4 \
  jsspacynlp-server
```

### Deployment Checklist

- [ ] Configure models in `models/config.json`
- [ ] Install required spaCy models
- [ ] Set production environment variables
- [ ] Configure resource limits (RAM, CPU)
- [ ] Set up monitoring (health checks)
- [ ] Configure logging
- [ ] Set up backup for custom models
- [ ] Test with production-scale data

## Troubleshooting

### Server won't start

- Check model configuration: `cat models/config.json`
- Verify models are installed: `python -m spacy info`
- Check logs: `docker-compose logs jsspacynlp-server`

### Out of memory

- Reduce number of loaded models
- Use smaller models (large instead of transformer)
- Increase Docker memory limit
- Reduce batch size

### Slow processing

- Check batch size (optimal: 500-2000)
- Disable unnecessary pipeline components
- Use CPU-optimized models for production
- Monitor resource usage: `docker stats`

### Connection errors

- Verify server is running: `curl http://localhost:8000/health`
- Check firewall settings
- Verify client API URL configuration

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## Related Projects

- [spaCy](https://spacy.io/) - Industrial-strength NLP library
- [spacy-js](https://github.com/ines/spacy-js) - Original JavaScript wrapper (inspiration)
- [NoSketchEngine](https://www.sketchengine.eu/) - Corpus analysis tool

## Support

For issues and questions:
- GitHub Issues: https://github.com/j3k0/jsspacynlp/issues
- Documentation: See README files in subdirectories

## Acknowledgments

Built with:
- [spaCy](https://spacy.io/) - NLP processing
- [FastAPI](https://fastapi.tiangolo.com/) - REST API framework
- [TypeScript](https://www.typescriptlang.org/) - Type-safe client library

Inspired by [spacy-js](https://github.com/ines/spacy-js) (MIT License).

