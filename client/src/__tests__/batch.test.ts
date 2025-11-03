/**
 * Tests for BatchProcessor
 */

import { SpacyNLP } from '../client';
import { BatchProcessor } from '../batch';
import { LemmatizeResponse } from '../types';

// Mock the client
jest.mock('../client');

describe('BatchProcessor', () => {
  let mockClient: jest.Mocked<SpacyNLP>;
  let processor: BatchProcessor;

  const mockResponse: LemmatizeResponse = {
    annotations: ['text', 'lemma', 'pos'],
    tokens: [[['test', 'test', 'NOUN']]],
    model: 'en_core_web_sm',
    processing_time_ms: 10.0,
  };

  beforeEach(() => {
    mockClient = new SpacyNLP() as jest.Mocked<SpacyNLP>;
    mockClient.lemmatize = jest.fn().mockResolvedValue(mockResponse);

    processor = new BatchProcessor(mockClient, {
      model: 'en_core_web_sm',
      batchSize: 2,
    });
  });

  describe('process', () => {
    it('should process texts in batches', async () => {
      const texts = ['text1', 'text2', 'text3', 'text4'];

      const result = await processor.process(texts);

      expect(mockClient.lemmatize).toHaveBeenCalledTimes(2);
      expect(mockClient.lemmatize).toHaveBeenCalledWith(
        ['text1', 'text2'],
        'en_core_web_sm',
        undefined
      );
      expect(mockClient.lemmatize).toHaveBeenCalledWith(
        ['text3', 'text4'],
        'en_core_web_sm',
        undefined
      );

      expect(result.documents).toBeDefined();
    });

    it('should handle non-even batch sizes', async () => {
      const texts = ['text1', 'text2', 'text3'];

      await processor.process(texts);

      expect(mockClient.lemmatize).toHaveBeenCalledTimes(2);
      expect(mockClient.lemmatize).toHaveBeenNthCalledWith(
        1,
        ['text1', 'text2'],
        'en_core_web_sm',
        undefined
      );
      expect(mockClient.lemmatize).toHaveBeenNthCalledWith(
        2,
        ['text3'],
        'en_core_web_sm',
        undefined
      );
    });

    it('should call progress callback', async () => {
      const onProgress = jest.fn();
      const processorWithProgress = new BatchProcessor(mockClient, {
        model: 'en_core_web_sm',
        batchSize: 2,
        onProgress,
      });

      const texts = ['text1', 'text2', 'text3', 'text4'];
      await processorWithProgress.process(texts);

      expect(onProgress).toHaveBeenCalledTimes(2);
      expect(onProgress).toHaveBeenNthCalledWith(1, 2, 4);
      expect(onProgress).toHaveBeenNthCalledWith(2, 4, 4);
    });

    it('should include custom fields', async () => {
      const processorWithFields = new BatchProcessor(mockClient, {
        model: 'en_core_web_sm',
        batchSize: 2,
        fields: ['text', 'lemma'],
      });

      await processorWithFields.process(['text1', 'text2']);

      expect(mockClient.lemmatize).toHaveBeenCalledWith(
        ['text1', 'text2'],
        'en_core_web_sm',
        ['text', 'lemma']
      );
    });

    it('should throw on empty text array', async () => {
      await expect(processor.process([])).rejects.toThrow('Cannot process empty text array');
    });

    it('should accumulate processing times', async () => {
      const texts = ['text1', 'text2', 'text3'];

      const result = await processor.process(texts);

      // Should be sum of all batch processing times
      expect(result.raw.processing_time_ms).toBeGreaterThan(0);
    });
  });

  describe('processStream', () => {
    it('should yield results for each batch', async () => {
      const texts = ['text1', 'text2', 'text3', 'text4'];
      const results = [];

      for await (const result of processor.processStream(texts)) {
        results.push(result);
      }

      expect(results).toHaveLength(2);
      expect(mockClient.lemmatize).toHaveBeenCalledTimes(2);
    });

    it('should call progress callback in stream', async () => {
      const onProgress = jest.fn();
      const processorWithProgress = new BatchProcessor(mockClient, {
        model: 'en_core_web_sm',
        batchSize: 2,
        onProgress,
      });

      const texts = ['text1', 'text2', 'text3'];
      
      // Consume the generator
      for await (const _ of processorWithProgress.processStream(texts)) {
        // Just consume
      }

      expect(onProgress).toHaveBeenCalledTimes(2);
    });

    it('should throw on empty text array', async () => {
      const gen = processor.processStream([]);
      await expect(gen.next()).rejects.toThrow('Cannot process empty text array');
    });
  });
});

