/**
 * jsspacynlp - TypeScript/JavaScript client for spaCy lemmatization service
 */

export { SpacyNLP } from './client';
export { BatchProcessor } from './batch';
export { LemmatizationResultImpl } from './result';

export type {
  SpacyNLPConfig,
  LemmatizeRequest,
  LemmatizeResponse,
  Token,
  Document,
  LemmatizationResult,
  ModelInfo,
  ModelsResponse,
  HealthResponse,
  InfoResponse,
  ErrorResponse,
  BatchProcessorConfig,
} from './types';

export { SpacyNLPError } from './types';

// Default export for convenience
import { SpacyNLP } from './client';
export default SpacyNLP;

