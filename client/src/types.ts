/**
 * Type definitions for jsspacynlp client
 */

/**
 * Configuration options for SpacyNLP client
 */
export interface SpacyNLPConfig {
  /** Base URL of the API server */
  apiUrl?: string;
  /** Request timeout in milliseconds */
  timeout?: number;
  /** Number of retry attempts for failed requests */
  retries?: number;
  /** Initial delay for exponential backoff in milliseconds */
  retryDelay?: number;
}

/**
 * Request payload for lemmatization endpoint
 */
export interface LemmatizeRequest {
  /** Name of the spaCy model to use */
  model: string;
  /** Array of texts to process */
  texts: string[];
  /** Optional fields to include in response */
  fields?: string[];
}

/**
 * Response from lemmatization endpoint (compact format)
 */
export interface LemmatizeResponse {
  /** List of field names in order */
  annotations: string[];
  /** Array of documents, each containing tokens with field values */
  tokens: string[][][];
  /** Model used for processing */
  model: string;
  /** Processing time in milliseconds */
  processing_time_ms: number;
}

/**
 * Parsed token with named fields
 */
export interface Token {
  text: string;
  lemma: string;
  pos: string;
  tag?: string;
  dep?: string;
  ent_type?: string;
  is_alpha?: boolean;
  is_stop?: boolean;
  [key: string]: string | boolean | undefined;
}

/**
 * Processed document result
 */
export interface Document {
  /** Array of tokens in the document */
  tokens: Token[];
  /** Original text */
  text: string;
}

/**
 * Complete lemmatization result with helper methods
 */
export interface LemmatizationResult {
  /** Raw response from API */
  raw: LemmatizeResponse;
  /** Parsed documents with tokens */
  documents: Document[];

  /** Get all tokens from all documents */
  allTokens(): Token[];

  /** Filter tokens by predicate */
  filterTokens(predicate: (token: Token) => boolean): Token[];

  /** Export to NoSketchEngine vertical format */
  toVertical(): string;

  /** Export to CSV format */
  toCSV(): string;

  /** Export to JSON (array of token objects) */
  toJSON(): Token[][];
}

/**
 * Model information
 */
export interface ModelInfo {
  name: string;
  language: string;
  type: string;
  version?: string;
  components: string[];
}

/**
 * Response from /models endpoint
 */
export interface ModelsResponse {
  available_models: ModelInfo[];
}

/**
 * Response from /health endpoint
 */
export interface HealthResponse {
  status: string;
  models_loaded: string[];
  uptime_seconds: number;
}

/**
 * Response from /info endpoint
 */
export interface InfoResponse {
  name: string;
  version: string;
  spacy_version: string;
  models_loaded: number;
}

/**
 * API error response
 */
export interface ErrorResponse {
  error: string;
  details?: string;
  available_models?: string[];
  available_fields?: string[];
}

/**
 * Batch processor configuration
 */
export interface BatchProcessorConfig {
  /** Model name to use */
  model: string;
  /** Number of texts per batch request */
  batchSize?: number;
  /** Optional fields to request */
  fields?: string[];
  /** Progress callback */
  onProgress?: (processed: number, total: number) => void;
}

/**
 * Custom error class for API errors
 */
export class SpacyNLPError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: ErrorResponse
  ) {
    super(message);
    this.name = 'SpacyNLPError';
    Object.setPrototypeOf(this, SpacyNLPError.prototype);
  }
}

