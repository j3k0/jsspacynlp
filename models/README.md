# Models Directory

This directory contains the configuration and (optionally) custom spaCy models for jsspacynlp.

## Configuration Files

### config.json (User Configuration)

Create `config.json` to specify which models to load at startup. This file is **not tracked in git** - it's your personal configuration.

If `config.json` doesn't exist, the server will use `config.default.json` (which has no models by default).

### Creating Your Configuration

Copy the example and customize it:
```bash
cp config.example.json config.json
# Edit config.json with your desired models
```

Each model entry requires:

- **name**: Unique identifier for the model (used in API requests)
- **language**: Language code (e.g., "fr", "en", "es")
- **type**: Model type (e.g., "transformer", "large", "custom")
- **path**: Model path or spaCy model name
- **disable**: Optional list of pipeline components to disable for performance

### Example Configuration

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
      "name": "custom_occitan",
      "language": "oc",
      "type": "custom",
      "path": "/app/models/custom/oc_model",
      "disable": ["parser", "ner"]
    }
  ]
}
```

## Model Paths

Models can be specified as:

1. **spaCy model names**: The server will load them from the installed spaCy models
   - Example: `"fr_dep_news_trf"`
   - Requires the model to be installed via `pip install` or `spacy download`

2. **Absolute paths**: For custom models
   - Example: `"/app/models/custom/oc_model"`
   - Mount custom models to `/app/models/custom/` in Docker

3. **Relative paths**: Relative to the models directory
   - Example: `"custom/oc_model"`
   - Will look in `/app/models/custom/oc_model`

## Installing Standard Models

To install standard spaCy models, use pip:

```bash
pip install https://github.com/explosion/spacy-models/releases/download/fr_dep_news_trf-3.7.0/fr_dep_news_trf-3.7.0-py3-none-any.whl
```

Or with spaCy CLI:

```bash
python -m spacy download fr_dep_news_trf
```

## Custom Models

Place custom spaCy models in the `custom/` subdirectory and reference them in `config.json`.

Custom models should be valid spaCy model packages with:
- `config.cfg`
- `tokenizer`
- `vocab/`
- Other pipeline components

## Disabling Components

For lemmatization-focused usage, disable unnecessary components:

```json
"disable": ["parser", "ner"]
```

This significantly improves performance. Essential components for lemmatization:
- **tokenizer**: Required
- **tagger**: Required (for POS tags)
- **lemmatizer**: Required
- **attribute_ruler**: Recommended

## Docker Volume Mounting

When running in Docker, mount this directory as a volume:

```bash
docker run -v $(pwd)/models:/app/models jsspacynlp-server
```

Or with docker-compose:

```yaml
volumes:
  - ./models:/app/models:ro
```

