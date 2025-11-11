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
- **download_url**: Optional URL to download model via pip (for official spaCy models)
- **huggingface_repo**: Optional HuggingFace repository ID (for custom models on HuggingFace Hub)

### Example Configuration

```json
{
  "models": [
    {
      "name": "en_core_web_sm",
      "language": "en",
      "type": "small",
      "path": "en_core_web_sm",
      "download_url": "https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl",
      "disable": ["parser", "ner"]
    },
    {
      "name": "fr_dep_news_trf",
      "language": "fr",
      "type": "transformer",
      "path": "fr_dep_news_trf",
      "download_url": "https://github.com/explosion/spacy-models/releases/download/fr_dep_news_trf-3.7.0/fr_dep_news_trf-3.7.0-py3-none-any.whl",
      "disable": ["parser", "ner"]
    },
    {
      "name": "custom_from_huggingface",
      "language": "en",
      "type": "custom",
      "path": "custom_from_huggingface",
      "huggingface_repo": "your-org/your-custom-spacy-model",
      "disable": ["parser", "ner"]
    },
    {
      "name": "custom_local",
      "language": "oc",
      "type": "custom",
      "path": "/app/models/custom/oc_model",
      "disable": ["parser", "ner"]
    }
  ]
}
```

## Model Loading Methods

The service supports three ways to load models:

### 1. Auto-Download from URL (Recommended for Official spaCy Models)

Add `download_url` to automatically download and install models at startup:

```json
{
  "name": "en_core_web_sm",
  "path": "en_core_web_sm",
  "download_url": "https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl"
}
```

**Benefits:**
- ✅ No need to pre-install models in Docker image
- ✅ Smaller Docker image size
- ✅ Easy to change models by updating config.json
- ✅ Models downloaded once and cached persistently

Find official spaCy model URLs at: https://github.com/explosion/spacy-models/releases

### 2. Auto-Download from HuggingFace Hub (For Custom Models)

Add `huggingface_repo` to download custom models from HuggingFace:

```json
{
  "name": "custom_model",
  "path": "custom_model",
  "huggingface_repo": "your-organization/your-spacy-model"
}
```

**Benefits:**
- ✅ Host custom trained spaCy models on HuggingFace
- ✅ Easy sharing and versioning
- ✅ Automatic download at startup
- ✅ Models cached in `/app/models/downloads/`

**Requirements for HuggingFace models:**
- Must be valid spaCy model directories (with config.cfg, vocab/, etc.)
- Upload your spaCy model directory to HuggingFace Hub
- Use the repository ID (e.g., "username/model-name")

### 3. Pre-Installed or Local Models

Use `path` without download URLs for:
- Already installed models (via pip before startup)
- Models mounted as volumes
- Custom models in the models directory

```json
{
  "name": "local_model",
  "path": "/app/models/custom/my_model"
}
```

**Model paths can be:**
- **spaCy model names**: `"en_core_web_sm"` (if already pip-installed)
- **Absolute paths**: `"/app/models/custom/oc_model"`
- **Relative paths**: `"custom/oc_model"` (relative to `/app/models/`)

## How It Works

1. Service starts and reads `config.json`
2. For each model:
   - **First**: Try loading from `path`
   - **If not found + has `download_url`**: Download via pip and load
   - **If still not found + has `huggingface_repo`**: Download from HuggingFace and load
   - **If all fail**: Log error and skip model
3. Downloaded models are cached persistently in `/app/models/downloads/`
4. On restart: Models already downloaded load instantly

## Manual Model Installation (Alternative)

You can still manually install models if preferred:

```bash
pip install https://github.com/explosion/spacy-models/releases/download/fr_dep_news_trf-3.7.0/fr_dep_news_trf-3.7.0-py3-none-any.whl
```

Or with spaCy CLI:

```bash
python -m spacy download fr_dep_news_trf
```

## Custom Models

You have three options for custom models:

### Option 1: HuggingFace Hub (Recommended)

Upload your trained spaCy model to HuggingFace Hub and reference it:

```json
{
  "name": "my_custom_model",
  "path": "my_custom_model",
  "huggingface_repo": "your-username/your-model-name"
}
```

The model will be automatically downloaded on first startup.

### Option 2: Volume Mounting

Place custom spaCy models in the `custom/` subdirectory and mount as volume:

```json
{
  "name": "local_custom",
  "path": "/app/models/custom/my_model"
}
```

### Option 3: Include in Docker Build

Copy models into the Docker image during build (not recommended, increases image size).

**All custom models must be valid spaCy model packages with:**
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

