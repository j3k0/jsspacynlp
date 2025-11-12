# jsspacynlp

Fast lemmatization microservice powered by spaCy with TypeScript/JavaScript client library.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

jsspacynlp provides a performant REST API for text lemmatization using spaCy models, along with a full-featured TypeScript/JavaScript client library. Designed for processing large corpora efficiently.

**Key Features:**
- High-performance FastAPI server with batch processing
- Compact JSON format (50-70% smaller than traditional)
- Multi-language support (transformer and large spaCy models)
- Docker-ready deployment
- NoSketchEngine vertical format export
- Batch processing with progress tracking
- Full TypeScript support
- >80% test coverage

**Architecture:** Client library → REST API → spaCy model registry with pre-loaded models.

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone and start
git clone https://github.com/j3k0/jsspacynlp.git
cd jsspacynlp
docker-compose up -d

# Check health
curl http://localhost:8000/health

# Install client
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

## Features

### Compact JSON Format

Traditional spaCy JSON responses can be very large. jsspacynlp uses a compact column-based format:

**Traditional:**
```json
{"tokens": [{"text": "Hello", "lemma": "hello", "pos": "INTJ"}]}
```

**jsspacynlp:**
```json
{
  "annotations": ["text", "lemma", "pos"],
  "tokens": [[["Hello", "hello", "INTJ"]]]
}
```

**Result:** 50-70% smaller payloads.

### Batch Processing

```javascript
import { BatchProcessor } from 'jsspacynlp';

const processor = new BatchProcessor(nlp, {
  model: 'fr_dep_news_trf',
  batchSize: 1000,
  onProgress: (processed, total) => {
    console.log(`${processed}/${total} texts processed`);
  }
});

const result = await processor.process(texts);
```

### NoSketchEngine Export

```javascript
const vertical = result.toVertical();
// word1\tlemma1\tpos1\ttag1
// word2\tlemma2\tpos2\ttag2

fs.writeFileSync('corpus.vertical', vertical);
```

## Installation

### Server Setup

#### Docker (Recommended)

```bash
# 1. Configure models
cp models/config.example.json models/config.json
# Edit models/config.json to add your models

# 2. Start server
docker-compose up -d
```

#### Manual

```bash
cd server
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Client Installation

```bash
npm install jsspacynlp
```

## Configuration

### Server Configuration

Environment variables (prefix: `JSSPACYNLP_`):

- `MODELS_CONFIG_DIR` - Model directory path (default: `/app/models`)
- `MODELS_CONFIG_FILE` - Config filename (default: `config.json`)
- `MAX_BATCH_SIZE` - Maximum batch size (default: `1000`)
- `MAX_TEXT_LENGTH` - Maximum text length (default: `1000000`)

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

See [models/README.md](models/README.md) for detailed configuration.

## API Documentation

### REST API

- **POST /lemmatize** - Lemmatize texts in batch
- **GET /health** - Health check
- **GET /models** - List available models
- **GET /info** - Service information

Interactive docs: `http://localhost:8000/docs`

### Client Library

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

**For complete API reference, see [API_REFERENCE.md](API_REFERENCE.md)**

## Supported Languages & Models

### Recommended Models

**Transformer Models** (best quality):
- French: `fr_dep_news_trf`
- English: `en_core_web_trf`
- Spanish: `es_dep_news_trf`
- German: `de_dep_news_trf`

**Large Models** (good quality, faster):
- Italian: `it_core_news_lg`
- Portuguese: `pt_core_news_lg`
- Russian: `ru_core_news_lg`

**Custom Models:** Supported via model configuration

### Installing Models

```bash
# Via spaCy CLI
python -m spacy download fr_dep_news_trf

# Via pip
pip install https://github.com/explosion/spacy-models/releases/download/fr_dep_news_trf-3.7.0/fr_dep_news_trf-3.7.0-py3-none-any.whl

# Auto-download (add download_url in config.json)
```

## Performance

- Response time: <100ms per 1000 words
- Throughput: >10,000 words/second
- Memory: ~2GB per transformer model, ~500MB per large model
- Optimal batch size: 500-2000 texts

## Testing

```bash
# Server tests
cd server && pytest

# Client tests
cd client && npm test

# Integration tests
docker-compose up -d
cd server && pytest tests/test_integration.py
```

## Development

### Server

```bash
cd server
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
black app/ tests/        # Format
ruff check app/ tests/   # Lint
```

### Client

```bash
cd client
npm install
npm run dev              # Build with watch
npm run test:watch       # Tests with watch
npm run lint             # Lint
```

## Deployment

```bash
# Production
docker-compose -f docker-compose.prod.yml up -d

# With resource limits
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/models:/app/models:ro \
  --memory=8g \
  --cpus=4 \
  jsspacynlp-server
```

## Troubleshooting

**Server won't start:**
- Check `models/config.json` syntax
- Verify models are accessible: `docker-compose logs jsspacynlp-server`

**Out of memory:**
- Reduce number of loaded models
- Use smaller models (large instead of transformer)
- Increase Docker memory limit

**Slow processing:**
- Check batch size (optimal: 500-2000)
- Disable unnecessary pipeline components in config

## Documentation

- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API reference
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute tutorial
- **[client/README.md](client/README.md)** - Client library details
- **[server/README.md](server/README.md)** - Server details
- **[models/README.md](models/README.md)** - Model configuration
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development guide

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Support

- GitHub Issues: https://github.com/j3k0/jsspacynlp/issues
- Documentation: See README files in subdirectories

## Acknowledgments

Built with [spaCy](https://spacy.io/), [FastAPI](https://fastapi.tiangolo.com/), and [TypeScript](https://www.typescriptlang.org/).

Inspired by [spacy-js](https://github.com/ines/spacy-js) (MIT License).
