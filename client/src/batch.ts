/**
 * Batch processing for large datasets
 */

import { SpacyNLP } from './client';
import { BatchProcessorConfig, LemmatizationResult } from './types';
import { LemmatizationResultImpl } from './result';

const DEFAULT_BATCH_SIZE = 1000;

/**
 * Batch processor for handling large text arrays
 */
export class BatchProcessor {
  private client: SpacyNLP;
  private config: Required<Omit<BatchProcessorConfig, 'onProgress'>> & {
    onProgress?: (processed: number, total: number) => void;
  };

  constructor(client: SpacyNLP, config: BatchProcessorConfig) {
    this.client = client;
    this.config = {
      model: config.model,
      batchSize: config.batchSize || DEFAULT_BATCH_SIZE,
      fields: config.fields,
      onProgress: config.onProgress,
    };
  }

  /**
   * Process texts in batches
   */
  async process(texts: string[]): Promise<LemmatizationResult> {
    if (texts.length === 0) {
      throw new Error('Cannot process empty text array');
    }

    const totalBatches = Math.ceil(texts.length / this.config.batchSize);
    const allAnnotations: string[] = [];
    const allTokens: string[][][] = [];
    let totalProcessingTime = 0;

    for (let i = 0; i < totalBatches; i++) {
      const start = i * this.config.batchSize;
      const end = Math.min(start + this.config.batchSize, texts.length);
      const batch = texts.slice(start, end);

      const response = await this.client.lemmatize(batch, this.config.model, this.config.fields);

      // Store annotations from first batch
      if (i === 0) {
        allAnnotations.push(...response.annotations);
      }

      // Accumulate tokens
      allTokens.push(...response.tokens);
      totalProcessingTime += response.processing_time_ms;

      // Report progress
      if (this.config.onProgress) {
        this.config.onProgress(end, texts.length);
      }
    }

    // Combine results
    const combinedResponse = {
      annotations: allAnnotations,
      tokens: allTokens,
      model: this.config.model,
      processing_time_ms: totalProcessingTime,
    };

    return new LemmatizationResultImpl(combinedResponse);
  }

  /**
   * Process texts as async generator (memory efficient for huge datasets)
   */
  async *processStream(texts: string[]): AsyncGenerator<LemmatizationResult, void, unknown> {
    if (texts.length === 0) {
      throw new Error('Cannot process empty text array');
    }

    const totalBatches = Math.ceil(texts.length / this.config.batchSize);

    for (let i = 0; i < totalBatches; i++) {
      const start = i * this.config.batchSize;
      const end = Math.min(start + this.config.batchSize, texts.length);
      const batch = texts.slice(start, end);

      const response = await this.client.lemmatize(batch, this.config.model, this.config.fields);

      // Report progress
      if (this.config.onProgress) {
        this.config.onProgress(end, texts.length);
      }

      yield new LemmatizationResultImpl(response);
    }
  }
}

