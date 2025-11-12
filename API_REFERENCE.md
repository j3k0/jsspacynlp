# jsspacynlp API Reference

Fast lemmatization microservice with TypeScript client. spaCy-powered REST API with compact JSON format.

## Quick Start

```bash
docker-compose up -d
npm install jsspacynlp
```

```typescript
import { SpacyNLP } from 'jsspacynlp';
const nlp = new SpacyNLP({ apiUrl: 'http://localhost:8000' });
const result = await nlp.lemmatize('Hello world', 'en_core_web_sm');
```

## REST API

Base URL: `http://localhost:8000`

### POST /lemmatize

Lemmatize texts in batch.

**Request:**
```typescript
{
  model: string;              // Model name (required)
  texts: string | string[];   // Text(s) to process (required)
  fields?: string[];          // Fields to return (optional)
}
```

**Response:**
```typescript
{
  annotations: string[];      // Field names in order
  tokens: string[][][];       // Documents -> tokens -> field values
  model: string;              // Model used
  processing_time_ms: number; // Processing time
}
```

**Available fields:**
- `text` (always included) - Token text
- `lemma` (always included) - Lemmatized form
- `pos` - Part-of-speech tag
- `tag` - Fine-grained POS tag
- `dep` - Dependency relation
- `ent_type` - Named entity type
- `is_alpha` - Is alphabetic (boolean)
- `is_stop` - Is stop word (boolean)

**Default fields:** `['text', 'lemma', 'pos', 'tag', 'dep']`

**Example:**
```bash
curl -X POST http://localhost:8000/lemmatize \
  -H "Content-Type: application/json" \
  -d '{"model": "en_core_web_sm", "texts": "Hello world"}'
```

### GET /health

Health check.

**Response:**
```typescript
{
  status: "healthy";
  models_loaded: string[];
  uptime_seconds: number;
}
```

### GET /models

List available models.

**Response:**
```typescript
{
  available_models: Array<{
    name: string;
    language: string;
    type: string;
    version: string;
    components: string[];
  }>;
}
```

### GET /info

Service information.

**Response:**
```typescript
{
  name: "jsspacynlp";
  version: string;
  spacy_version: string;
  models_loaded: number;
}
```

## Client Library

### SpacyNLP

**Constructor:**
```typescript
new SpacyNLP(config?: {
  apiUrl?: string;      // Default: 'http://localhost:8000'
  timeout?: number;     // Default: 30000 (ms)
  retries?: number;     // Default: 3
  retryDelay?: number;  // Default: 1000 (ms)
})
```

**Methods:**

```typescript
// Lemmatize text(s)
lemmatize(
  texts: string | string[],
  model: string,
  fields?: string[]
): Promise<LemmatizationResult>

// Check health
health(): Promise<HealthResponse>

// List models
models(): Promise<ModelsResponse>

// Get info
info(): Promise<InfoResponse>
```

### BatchProcessor

Process large datasets efficiently.

**Constructor:**
```typescript
new BatchProcessor(client: SpacyNLP, config: {
  model: string;
  batchSize?: number;           // Default: 1000
  fields?: string[];
  onProgress?: (processed: number, total: number) => void;
})
```

**Methods:**
```typescript
// Process all texts
process(texts: string[]): Promise<LemmatizationResult>

// Stream processing
processStream(texts: string[]): AsyncGenerator<LemmatizationResult>
```

### LemmatizationResult

**Properties:**
```typescript
{
  documents: Document[];    // Parsed documents
  raw: LemmatizeResponse;   // Raw API response
}
```

**Methods:**
```typescript
allTokens(): Token[]                                  // All tokens from all docs
filterTokens(predicate: (t: Token) => boolean): Token[]  // Filter tokens
toVertical(): string                                  // NoSketchEngine format
toCSV(): string                                       // CSV format
toJSON(): object[][]                                  // JSON array
```

### Types

```typescript
interface Token {
  text: string;
  lemma: string;
  pos?: string;
  tag?: string;
  dep?: string;
  ent_type?: string;
  is_alpha?: boolean;
  is_stop?: boolean;
}

interface Document {
  text: string;
  tokens: Token[];
}
```

## Configuration

### Environment Variables

Prefix all with `JSSPACYNLP_`:

- `MODELS_CONFIG_DIR` - Model directory path (default: `/app/models`)
- `MODELS_CONFIG_FILE` - Config filename (default: `config.json`)
- `HOST` - Server host (default: `0.0.0.0`)
- `PORT` - Server port (default: `8000`)
- `LOG_LEVEL` - Logging level (default: `info`)
- `MAX_BATCH_SIZE` - Maximum batch size (default: `1000`)
- `MAX_TEXT_LENGTH` - Maximum text length (default: `1000000`)

### Model Configuration

`models/config.json`:
```json
{
  "models": [
    {
      "name": "model_name",
      "language": "en",
      "type": "transformer",
      "path": "model_path_or_name",
      "disable": ["parser", "ner"],
      "download_url": "https://...",
      "huggingface_repo": "org/repo"
    }
  ]
}
```

**Required fields:**
- `name` - Unique identifier
- `language` - Language code
- `type` - Model type
- `path` - Model path or spaCy name

**Optional fields:**
- `disable` - Pipeline components to disable
- `download_url` - Auto-download URL
- `huggingface_repo` - HuggingFace repository

## Error Handling

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad request (invalid model, invalid fields)
- `422` - Validation error
- `500` - Server error

**Error Response:**
```typescript
{
  error: string;
  available_models?: string[];  // When model not found
  details?: object;             // Additional context
}
```

**Client Errors:**
```typescript
try {
  await nlp.lemmatize('text', 'invalid_model');
} catch (error) {
  if (error instanceof SpacyNLPError) {
    console.error(error.message);
    console.error(error.statusCode);
    console.error(error.details);
  }
}
```

## Batch Processing Example

```typescript
import { SpacyNLP, BatchProcessor } from 'jsspacynlp';

const nlp = new SpacyNLP();
const processor = new BatchProcessor(nlp, {
  model: 'en_core_web_sm',
  batchSize: 1000,
  onProgress: (p, t) => console.log(`${p}/${t}`)
});

const result = await processor.process(texts);
console.log(result.toVertical());
```

## Export Formats

**NoSketchEngine Vertical:**
```
word1\tlemma1\tpos1\ttag1
word2\tlemma2\tpos2\ttag2

word3\tlemma3\tpos3\ttag3
```

**CSV:**
```
text,lemma,pos,tag
Hello,hello,INTJ,UH
world,world,NOUN,NN
```

**JSON:**
```json
[[{"text": "Hello", "lemma": "hello", "pos": "INTJ"}]]
```

## Performance

- Response time: <100ms per 1000 words
- Throughput: >10,000 words/second
- Optimal batch size: 500-2000 texts
- Memory: ~2GB per transformer model, ~500MB per large model

## Documentation

- [README.md](README.md) - Overview and getting started
- [QUICKSTART.md](QUICKSTART.md) - 5-minute tutorial
- [client/README.md](client/README.md) - Client library details
- [server/README.md](server/README.md) - Server details
- [models/README.md](models/README.md) - Model configuration
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guide

