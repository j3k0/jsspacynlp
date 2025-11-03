/**
 * Tests for SpacyNLP client
 */

import { SpacyNLP, SpacyNLPError } from '../index';

// Mock node-fetch
jest.mock('node-fetch');
import fetch from 'node-fetch';
const { Response } = jest.requireActual('node-fetch');

const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

describe('SpacyNLP', () => {
  let client: SpacyNLP;

  beforeEach(() => {
    client = new SpacyNLP({ apiUrl: 'http://localhost:8000' });
    jest.clearAllMocks();
  });

  describe('constructor', () => {
    it('should use default config', () => {
      const defaultClient = new SpacyNLP();
      expect(defaultClient.getApiUrl()).toBe('http://localhost:8000');
    });

    it('should accept custom config', () => {
      const customClient = new SpacyNLP({ apiUrl: 'http://custom:9000' });
      expect(customClient.getApiUrl()).toBe('http://custom:9000');
    });
  });

  describe('lemmatize', () => {
    it('should lemmatize single text', async () => {
      const mockResponse = {
        annotations: ['text', 'lemma', 'pos'],
        tokens: [[['Hello', 'hello', 'INTJ'], ['world', 'world', 'NOUN']]],
        model: 'en_core_web_sm',
        processing_time_ms: 10.5,
      };

      mockFetch.mockResolvedValueOnce(
        new Response(JSON.stringify(mockResponse), { status: 200 })
      );

      const result = await client.lemmatize('Hello world', 'en_core_web_sm');

      expect(result).toEqual(mockResponse);
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/lemmatize',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            model: 'en_core_web_sm',
            texts: ['Hello world'],
          }),
        })
      );
    });

    it('should lemmatize multiple texts', async () => {
      const mockResponse = {
        annotations: ['text', 'lemma', 'pos'],
        tokens: [
          [['Hello', 'hello', 'INTJ']],
          [['world', 'world', 'NOUN']],
        ],
        model: 'en_core_web_sm',
        processing_time_ms: 15.0,
      };

      mockFetch.mockResolvedValueOnce(
        new Response(JSON.stringify(mockResponse), { status: 200 })
      );

      const result = await client.lemmatize(['Hello', 'world'], 'en_core_web_sm');

      expect(result).toEqual(mockResponse);
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/lemmatize',
        expect.objectContaining({
          body: JSON.stringify({
            model: 'en_core_web_sm',
            texts: ['Hello', 'world'],
          }),
        })
      );
    });

    it('should include custom fields', async () => {
      const mockResponse = {
        annotations: ['text', 'lemma'],
        tokens: [[['Hello', 'hello']]],
        model: 'en_core_web_sm',
        processing_time_ms: 8.0,
      };

      mockFetch.mockResolvedValueOnce(
        new Response(JSON.stringify(mockResponse), { status: 200 })
      );

      await client.lemmatize('Hello', 'en_core_web_sm', ['text', 'lemma']);

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/lemmatize',
        expect.objectContaining({
          body: JSON.stringify({
            model: 'en_core_web_sm',
            texts: ['Hello'],
            fields: ['text', 'lemma'],
          }),
        })
      );
    });

    it('should throw SpacyNLPError on 400', async () => {
      const errorResponse = {
        error: 'Model not found',
        available_models: ['en_core_web_sm'],
      };

      mockFetch.mockResolvedValueOnce(
        new Response(JSON.stringify(errorResponse), { status: 400 })
      );

      await expect(client.lemmatize('test', 'invalid_model')).rejects.toThrow(SpacyNLPError);
    });

    it('should retry on network error', async () => {
      const mockResponse = {
        annotations: ['text', 'lemma', 'pos'],
        tokens: [[['test', 'test', 'NOUN']]],
        model: 'en_core_web_sm',
        processing_time_ms: 10.0,
      };

      // Fail twice, then succeed
      mockFetch
        .mockRejectedValueOnce(new Error('Network error'))
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce(
          new Response(JSON.stringify(mockResponse), { status: 200 })
        );

      const result = await client.lemmatize('test', 'en_core_web_sm');

      expect(result).toEqual(mockResponse);
      expect(mockFetch).toHaveBeenCalledTimes(3);
    });

    it('should not retry on 400 error', async () => {
      const errorResponse = { error: 'Bad request' };

      mockFetch.mockResolvedValueOnce(
        new Response(JSON.stringify(errorResponse), { status: 400 })
      );

      await expect(client.lemmatize('test', 'invalid')).rejects.toThrow(SpacyNLPError);
      expect(mockFetch).toHaveBeenCalledTimes(1);
    });
  });

  describe('health', () => {
    it('should fetch health status', async () => {
      const mockResponse = {
        status: 'healthy',
        models_loaded: ['en_core_web_sm'],
        uptime_seconds: 3600,
      };

      mockFetch.mockResolvedValueOnce(
        new Response(JSON.stringify(mockResponse), { status: 200 })
      );

      const result = await client.health();

      expect(result).toEqual(mockResponse);
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/health',
        expect.objectContaining({ method: 'GET' })
      );
    });
  });

  describe('info', () => {
    it('should fetch server info', async () => {
      const mockResponse = {
        name: 'jsspacynlp',
        version: '0.1.0',
        spacy_version: '3.7.2',
        models_loaded: 1,
      };

      mockFetch.mockResolvedValueOnce(
        new Response(JSON.stringify(mockResponse), { status: 200 })
      );

      const result = await client.info();

      expect(result).toEqual(mockResponse);
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/info',
        expect.objectContaining({ method: 'GET' })
      );
    });
  });

  describe('models', () => {
    it('should fetch available models', async () => {
      const mockResponse = {
        available_models: [
          {
            name: 'en_core_web_sm',
            language: 'en',
            type: 'small',
            version: '3.7.0',
            components: ['tagger', 'lemmatizer'],
          },
        ],
      };

      mockFetch.mockResolvedValueOnce(
        new Response(JSON.stringify(mockResponse), { status: 200 })
      );

      const result = await client.models();

      expect(result).toEqual(mockResponse);
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/models',
        expect.objectContaining({ method: 'GET' })
      );
    });
  });
});

