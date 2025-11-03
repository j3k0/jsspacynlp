# jsspacynlp Client

TypeScript/JavaScript client library for jsspacynlp lemmatization service.

## Features

- 🚀 Promise-based async API
- 📦 TypeScript support with full type definitions
- 🔄 Automatic retry with exponential backoff
- 📊 Batch processing for large datasets
- 🌊 Streaming support for memory-efficient processing
- 🎯 NoSketchEngine vertical format export
- 📝 CSV and JSON export utilities
- 🌐 Works in Node.js and browsers

## Installation

```bash
npm install jsspacynlp
```

## Quick Start

```typescript
import { SpacyNLP } from 'jsspacynlp';

const nlp = new SpacyNLP({
  apiUrl: 'http://localhost:8000',
});

// Lemmatize a single text
const result = await nlp.lemmatize('The cats are running.', 'en_core_web_sm');
console.log(result);

// Lemmatize multiple texts
const results = await nlp.lemmatize(
  ['First text.', 'Second text.'],
  'fr_dep_news_trf'
);
```

## API Documentation

### SpacyNLP Client

#### Constructor

```typescript
const nlp = new SpacyNLP({
  apiUrl: 'http://localhost:8000',  // API server URL
  timeout: 30000,                    // Request timeout in ms
  retries: 3,                        // Number of retry attempts
  retryDelay: 1000,                  // Initial retry delay in ms
});
```

#### Methods

##### `lemmatize(texts, model, fields?)`

Lemmatize text(s) using specified model.

```typescript
const result = await nlp.lemmatize(
  'Hello world',
  'en_core_web_sm',
  ['text', 'lemma', 'pos']  // Optional: specify fields
);
```

**Parameters:**
- `texts`: `string | string[]` - Text or array of texts to process
- `model`: `string` - Name of the spaCy model
- `fields`: `string[]` (optional) - Fields to include in response

**Returns:** `Promise<LemmatizeResponse>`

##### `health()`

Check server health status.

```typescript
const health = await nlp.health();
console.log(health.status);           // "healthy"
console.log(health.models_loaded);    // ["en_core_web_sm", ...]
console.log(health.uptime_seconds);   // 3600
```

##### `models()`

List available models.

```typescript
const { available_models } = await nlp.models();
for (const model of available_models) {
  console.log(model.name, model.language, model.type);
}
```

##### `info()`

Get server information.

```typescript
const info = await nlp.info();
console.log(info.version);         // "0.1.0"
console.log(info.spacy_version);   // "3.7.2"
```

### Batch Processing

For processing large datasets efficiently:

```typescript
import { SpacyNLP, BatchProcessor } from 'jsspacynlp';

const nlp = new SpacyNLP();

// Create batch processor
const processor = new BatchProcessor(nlp, {
  model: 'fr_dep_news_trf',
  batchSize: 1000,               // Texts per batch
  fields: ['text', 'lemma', 'pos'],
  onProgress: (processed, total) => {
    console.log(`Progress: ${processed}/${total}`);
  }
});

// Process large array
const texts = [...]; // Array of 10,000+ texts
const result = await processor.process(texts);

// Access results
for (const doc of result.documents) {
  console.log(doc.text);
  for (const token of doc.tokens) {
    console.log(token.text, token.lemma, token.pos);
  }
}
```

### Streaming (Memory Efficient)

For extremely large datasets:

```typescript
const processor = new BatchProcessor(nlp, {
  model: 'en_core_web_sm',
  batchSize: 1000,
});

// Process as stream
for await (const batchResult of processor.processStream(hugeTextArray)) {
  // Process each batch as it arrives
  console.log(`Batch processed: ${batchResult.documents.length} documents`);
  
  // Export batch to file
  fs.appendFileSync('output.vertical', batchResult.toVertical() + '\n');
}
```

### Result Utilities

#### LemmatizationResult

The result object provides helper methods:

```typescript
const result = await nlp.lemmatize(['Hello world', 'Testing'], 'en_core_web_sm');

// Get all tokens from all documents
const allTokens = result.allTokens();

// Filter tokens
const nouns = result.filterTokens(token => token.pos === 'NOUN');
const stopWords = result.filterTokens(token => token.is_stop === true);

// Export formats
const vertical = result.toVertical();  // NoSketchEngine format
const csv = result.toCSV();            // CSV format
const json = result.toJSON();          // Array of token objects
```

#### NoSketchEngine Vertical Format

```typescript
const result = await processor.process(texts);
const vertical = result.toVertical();

// Output format:
// word1\tlemma1\tpos1\ttag1
// word2\tlemma2\tpos2\ttag2
// 
// word3\tlemma3\tpos3\ttag3  (new document)

fs.writeFileSync('corpus.vertical', vertical);
```

#### CSV Export

```typescript
const csv = result.toCSV();
// text,lemma,pos,tag
// Hello,hello,INTJ,UH
// world,world,NOUN,NN
```

#### JSON Export

```typescript
const json = result.toJSON();
// [
//   [
//     { text: "Hello", lemma: "hello", pos: "INTJ", tag: "UH" },
//     { text: "world", lemma: "world", pos: "NOUN", tag: "NN" }
//   ]
// ]
```

### Error Handling

```typescript
import { SpacyNLP, SpacyNLPError } from 'jsspacynlp';

try {
  const result = await nlp.lemmatize('test', 'invalid_model');
} catch (error) {
  if (error instanceof SpacyNLPError) {
    console.error('API Error:', error.message);
    console.error('Status Code:', error.statusCode);
    
    if (error.details?.available_models) {
      console.log('Available models:', error.details.available_models);
    }
  } else {
    console.error('Unexpected error:', error);
  }
}
```

### TypeScript Types

The library includes full TypeScript definitions:

```typescript
import {
  SpacyNLP,
  SpacyNLPConfig,
  LemmatizeResponse,
  Token,
  Document,
  LemmatizationResult,
  ModelInfo,
  BatchProcessorConfig,
  SpacyNLPError,
} from 'jsspacynlp';
```

## Available Fields

When calling `lemmatize()`, you can specify which fields to include:

- `text` - Token text (always included)
- `lemma` - Lemmatized form (always included)
- `pos` - Part-of-speech tag
- `tag` - Fine-grained POS tag
- `dep` - Dependency relation
- `ent_type` - Named entity type
- `is_alpha` - Is alphabetic (boolean)
- `is_stop` - Is stop word (boolean)

**Default fields:** `['text', 'lemma', 'pos', 'tag', 'dep']`

## Examples

### Basic Usage

```typescript
import { SpacyNLP } from 'jsspacynlp';

const nlp = new SpacyNLP({ apiUrl: 'http://localhost:8000' });

const result = await nlp.lemmatize(
  'Les chats courent dans le jardin.',
  'fr_dep_news_trf'
);

// Access parsed documents
for (const doc of result.documents) {
  for (const token of doc.tokens) {
    console.log(`${token.text} -> ${token.lemma} (${token.pos})`);
  }
}
```

### Batch Processing with Progress

```typescript
import { SpacyNLP, BatchProcessor } from 'jsspacynlp';

const nlp = new SpacyNLP();
const texts = loadTexts(); // Load 50,000 texts

const processor = new BatchProcessor(nlp, {
  model: 'fr_dep_news_trf',
  batchSize: 1000,
  onProgress: (processed, total) => {
    const percent = ((processed / total) * 100).toFixed(1);
    console.log(`Processing: ${percent}% (${processed}/${total})`);
  },
});

const result = await processor.process(texts);
console.log(`Processed ${result.documents.length} documents`);
```

### Export to NoSketchEngine

```typescript
import fs from 'fs';
import { SpacyNLP, BatchProcessor } from 'jsspacynlp';

const nlp = new SpacyNLP();
const processor = new BatchProcessor(nlp, {
  model: 'en_core_web_trf',
  batchSize: 1000,
});

const texts = loadCorpus();
const result = await processor.process(texts);

// Export to vertical format
const vertical = result.toVertical();
fs.writeFileSync('corpus.vertical', vertical, 'utf-8');
```

### Filter and Analyze Tokens

```typescript
const result = await nlp.lemmatize(texts, 'en_core_web_sm');

// Get all nouns
const nouns = result.filterTokens(t => t.pos === 'NOUN');

// Get unique lemmas
const uniqueLemmas = new Set(nouns.map(t => t.lemma));

// Count token frequencies
const frequencies = new Map<string, number>();
for (const token of result.allTokens()) {
  frequencies.set(token.lemma, (frequencies.get(token.lemma) || 0) + 1);
}
```

## Testing

```bash
# Run tests
npm test

# Run with coverage
npm run test:coverage

# Watch mode
npm run test:watch
```

## Building

```bash
# Build TypeScript to JavaScript
npm run build

# Output in dist/ directory
```

## License

MIT License - See LICENSE file for details.

