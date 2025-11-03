# jsspacynlp Quick Start Guide

Get up and running with jsspacynlp in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- Node.js 14+ (for client usage)

## Step 1: Clone and Setup (1 minute)

```bash
# Clone the repository
git clone https://github.com/j3k0/jsspacynlp.git
cd jsspacynlp

# Copy example config
cp models/config.example.json models/config.json
```

## Step 2: Configure Models (2 minutes)

Edit `models/config.json` to specify which spaCy models to load:

```json
{
  "models": [
    {
      "name": "en_core_web_sm",
      "language": "en",
      "type": "small",
      "path": "en_core_web_sm",
      "disable": ["parser", "ner"]
    }
  ]
}
```

**Note**: For the first run, use a small model like `en_core_web_sm` which will be downloaded automatically.

## Step 3: Start the Server (1 minute)

```bash
# Build and start
docker-compose up -d

# Check server is running
curl http://localhost:8000/health
```

Expected output:
```json
{
  "status": "healthy",
  "models_loaded": ["en_core_web_sm"],
  "uptime_seconds": 5.2
}
```

## Step 4: Use the Client (1 minute)

### Install Client

```bash
npm install jsspacynlp
```

### Basic Example

Create `test.js`:

```javascript
const { SpacyNLP } = require('jsspacynlp');

async function main() {
  const nlp = new SpacyNLP({ apiUrl: 'http://localhost:8000' });

  // Lemmatize text
  const result = await nlp.lemmatize(
    'The cats are running in the garden.',
    'en_core_web_sm'
  );

  // Print tokens
  for (const doc of result.documents) {
    for (const token of doc.tokens) {
      console.log(`${token.text} -> ${token.lemma} (${token.pos})`);
    }
  }
}

main();
```

Run it:
```bash
node test.js
```

Output:
```
The -> the (DET)
cats -> cat (NOUN)
are -> be (AUX)
running -> run (VERB)
in -> in (ADP)
the -> the (DET)
garden -> garden (NOUN)
. -> . (PUNCT)
```

## Step 5: Test Batch Processing (Bonus)

Create `batch-test.js`:

```javascript
const { SpacyNLP, BatchProcessor } = require('jsspacynlp');
const fs = require('fs');

async function main() {
  const nlp = new SpacyNLP();

  // Create batch processor
  const processor = new BatchProcessor(nlp, {
    model: 'en_core_web_sm',
    batchSize: 100,
    onProgress: (processed, total) => {
      console.log(`Progress: ${processed}/${total}`);
    }
  });

  // Process 1000 texts
  const texts = [];
  for (let i = 0; i < 1000; i++) {
    texts.push(`This is test sentence number ${i}.`);
  }

  const result = await processor.process(texts);

  // Export to NoSketchEngine format
  const vertical = result.toVertical();
  fs.writeFileSync('output.vertical', vertical);

  console.log(`Processed ${result.documents.length} documents`);
  console.log(`Total tokens: ${result.allTokens().length}`);
  console.log(`Processing time: ${result.raw.processing_time_ms}ms`);
}

main();
```

Run it:
```bash
node batch-test.js
```

## Next Steps

### Add More Languages

Edit `models/config.json`:

```json
{
  "models": [
    {
      "name": "fr_dep_news_trf",
      "language": "fr",
      "type": "transformer",
      "path": "fr_dep_news_trf",
      "disable": ["parser", "ner"]
    },
    {
      "name": "es_dep_news_trf",
      "language": "es",
      "type": "transformer",
      "path": "es_dep_news_trf",
      "disable": ["parser", "ner"]
    }
  ]
}
```

Restart the server:
```bash
docker-compose restart
```

### Explore the API

Open the interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Production Deployment

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d
```

## Common Issues

### Server won't start

Check logs:
```bash
docker-compose logs jsspacynlp-server
```

### Model download fails

Pre-download models:
```bash
# Inside Docker container
docker-compose exec jsspacynlp-server python -m spacy download en_core_web_sm
```

### Out of memory

Use smaller models or increase Docker memory:
```bash
# In docker-compose.yml, add:
deploy:
  resources:
    limits:
      memory: 4G
```

## Useful Commands

```bash
# View logs
docker-compose logs -f

# Restart server
docker-compose restart

# Stop server
docker-compose down

# Rebuild after changes
docker-compose build

# Check server status
curl http://localhost:8000/health

# List available models
curl http://localhost:8000/models

# Run tests
cd client && npm test
cd server && pytest
```

## Learn More

- Full Documentation: [README.md](README.md)
- Client API: [client/README.md](client/README.md)
- Server API: [server/README.md](server/README.md)
- Model Configuration: [models/README.md](models/README.md)
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)

## Support

- GitHub Issues: https://github.com/j3k0/jsspacynlp/issues
- Documentation: https://github.com/j3k0/jsspacynlp

Happy lemmatizing! 🚀

