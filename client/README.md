# jsspacynlp Client

TypeScript/JavaScript client library for jsspacynlp lemmatization service.

## Features

- Promise-based async API with automatic retry
- TypeScript support with full type definitions
- Batch processing for large datasets
- Streaming support for memory efficiency
- NoSketchEngine vertical format export
- CSV and JSON export utilities
- Works in Node.js and browsers

## Installation

```bash
npm install jsspacynlp
```

## Quick Start

```typescript
import { SpacyNLP } from 'jsspacynlp';

const nlp = new SpacyNLP({ apiUrl: 'http://localhost:8000' });
const result = await nlp.lemmatize('The cats are running.', 'en_core_web_sm');

for (const doc of result.documents) {
  for (const token of doc.tokens) {
    console.log(`${token.text} -> ${token.lemma} (${token.pos})`);
  }
}
```

## API

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
- `lemmatize(texts: string | string[], model: string, fields?: string[]): Promise<LemmatizationResult>`
- `health(): Promise<HealthResponse>`
- `models(): Promise<ModelsResponse>`
- `info(): Promise<InfoResponse>`

### BatchProcessor

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
- `process(texts: string[]): Promise<LemmatizationResult>`
- `processStream(texts: string[]): AsyncGenerator<LemmatizationResult>`

### LemmatizationResult

**Properties:**
- `documents: Document[]` - Parsed documents
- `raw: LemmatizeResponse` - Raw API response

**Methods:**
- `allTokens(): Token[]` - All tokens from all documents
- `filterTokens(predicate: (t: Token) => boolean): Token[]` - Filter tokens
- `toVertical(): string` - NoSketchEngine vertical format
- `toCSV(): string` - CSV format
- `toJSON(): object[][]` - JSON array

## Types

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

**Available fields:**
- `text`, `lemma` (always included)
- `pos`, `tag`, `dep` (optional)
- `ent_type`, `is_alpha`, `is_stop` (optional)

**Default fields:** `['text', 'lemma', 'pos', 'tag', 'dep']`

## Usage Examples

### Batch Processing

```typescript
import { SpacyNLP, BatchProcessor } from 'jsspacynlp';

const processor = new BatchProcessor(new SpacyNLP(), {
  model: 'en_core_web_sm',
  batchSize: 1000,
  onProgress: (p, t) => console.log(`${p}/${t}`)
});

const result = await processor.process(texts);
```

### Streaming (Memory Efficient)

```typescript
for await (const batch of processor.processStream(hugeTextArray)) {
  fs.appendFileSync('output.vertical', batch.toVertical() + '\n');
}
```

### Export Formats

```typescript
const result = await nlp.lemmatize(texts, 'en_core_web_sm');

// NoSketchEngine vertical: word\tlemma\tpos\ttag
const vertical = result.toVertical();

// CSV: text,lemma,pos,tag
const csv = result.toCSV();

// JSON: [{"text": "...", "lemma": "...", "pos": "..."}]
const json = result.toJSON();
```

### Filter Tokens

```typescript
const result = await nlp.lemmatize(texts, 'en_core_web_sm');

// Get all nouns
const nouns = result.filterTokens(t => t.pos === 'NOUN');

// Get unique lemmas
const lemmas = new Set(result.allTokens().map(t => t.lemma));

// Count frequencies
const freq = new Map<string, number>();
for (const token of result.allTokens()) {
  freq.set(token.lemma, (freq.get(token.lemma) || 0) + 1);
}
```

### Error Handling

```typescript
import { SpacyNLPError } from 'jsspacynlp';

try {
  await nlp.lemmatize('text', 'invalid_model');
} catch (error) {
  if (error instanceof SpacyNLPError) {
    console.error(error.message, error.statusCode);
    console.log(error.details?.available_models);
  }
}
```

## TypeScript Imports

```typescript
import {
  SpacyNLP,
  SpacyNLPConfig,
  BatchProcessor,
  BatchProcessorConfig,
  LemmatizationResult,
  LemmatizeResponse,
  Token,
  Document,
  ModelInfo,
  SpacyNLPError,
} from 'jsspacynlp';
```

## Testing

```bash
npm test                # Run tests
npm run test:coverage   # With coverage
npm run test:watch      # Watch mode
```

## Building

```bash
npm run build           # Build to dist/
```

## Documentation

- [API_REFERENCE.md](../API_REFERENCE.md) - Complete API reference
- [README.md](../README.md) - Overview and getting started
- [server/README.md](../server/README.md) - Server details
- [models/README.md](../models/README.md) - Model configuration

## License

MIT License - See LICENSE file for details.
