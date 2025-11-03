/**
 * Tests for LemmatizationResult
 */

import { LemmatizationResultImpl } from '../result';
import { LemmatizeResponse } from '../types';

describe('LemmatizationResultImpl', () => {
  const mockResponse: LemmatizeResponse = {
    annotations: ['text', 'lemma', 'pos', 'tag'],
    tokens: [
      [
        ['Hello', 'hello', 'INTJ', 'UH'],
        ['world', 'world', 'NOUN', 'NN'],
      ],
      [
        ['Testing', 'test', 'VERB', 'VBG'],
        ['lemmatization', 'lemmatization', 'NOUN', 'NN'],
      ],
    ],
    model: 'en_core_web_sm',
    processing_time_ms: 10.5,
  };

  let result: LemmatizationResultImpl;

  beforeEach(() => {
    result = new LemmatizationResultImpl(mockResponse);
  });

  describe('constructor', () => {
    it('should parse response into documents', () => {
      expect(result.documents).toHaveLength(2);
      expect(result.documents[0].tokens).toHaveLength(2);
      expect(result.documents[1].tokens).toHaveLength(2);
    });

    it('should correctly parse token fields', () => {
      const firstToken = result.documents[0].tokens[0];
      expect(firstToken.text).toBe('Hello');
      expect(firstToken.lemma).toBe('hello');
      expect(firstToken.pos).toBe('INTJ');
      expect(firstToken.tag).toBe('UH');
    });

    it('should reconstruct document text', () => {
      expect(result.documents[0].text).toBe('Hello world');
      expect(result.documents[1].text).toBe('Testing lemmatization');
    });
  });

  describe('allTokens', () => {
    it('should return all tokens from all documents', () => {
      const tokens = result.allTokens();
      expect(tokens).toHaveLength(4);
      expect(tokens[0].text).toBe('Hello');
      expect(tokens[3].text).toBe('lemmatization');
    });
  });

  describe('filterTokens', () => {
    it('should filter tokens by predicate', () => {
      const nouns = result.filterTokens((token) => token.pos === 'NOUN');
      expect(nouns).toHaveLength(2);
      expect(nouns[0].text).toBe('world');
      expect(nouns[1].text).toBe('lemmatization');
    });

    it('should return empty array if no matches', () => {
      const adjectives = result.filterTokens((token) => token.pos === 'ADJ');
      expect(adjectives).toHaveLength(0);
    });
  });

  describe('toVertical', () => {
    it('should export to NoSketchEngine vertical format', () => {
      const vertical = result.toVertical();
      const lines = vertical.split('\n');

      expect(lines[0]).toBe('Hello\thello\tINTJ\tUH');
      expect(lines[1]).toBe('world\tworld\tNOUN\tNN');
      expect(lines[2]).toBe(''); // Empty line between documents
      expect(lines[3]).toBe('Testing\ttest\tVERB\tVBG');
      expect(lines[4]).toBe('lemmatization\tlemmatization\tNOUN\tNN');
    });
  });

  describe('toCSV', () => {
    it('should export to CSV format', () => {
      const csv = result.toCSV();
      const lines = csv.split('\n');

      expect(lines[0]).toBe('text,lemma,pos,tag');
      expect(lines[1]).toBe('Hello,hello,INTJ,UH');
      expect(lines[2]).toBe('world,world,NOUN,NN');
      expect(lines.length).toBe(5); // Header + 4 tokens
    });

    it('should handle empty result', () => {
      const emptyResult = new LemmatizationResultImpl({
        annotations: [],
        tokens: [],
        model: 'test',
        processing_time_ms: 0,
      });
      expect(emptyResult.toCSV()).toBe('');
    });

    it('should escape CSV values', () => {
      const responseWithComma: LemmatizeResponse = {
        annotations: ['text', 'lemma'],
        tokens: [[['Hello, world', 'hello']]],
        model: 'test',
        processing_time_ms: 0,
      };

      const result = new LemmatizationResultImpl(responseWithComma);
      const csv = result.toCSV();
      expect(csv).toContain('"Hello, world"');
    });
  });

  describe('toJSON', () => {
    it('should export to JSON array', () => {
      const json = result.toJSON();
      expect(json).toHaveLength(2);
      expect(json[0]).toHaveLength(2);
      expect(json[0][0]).toEqual({
        text: 'Hello',
        lemma: 'hello',
        pos: 'INTJ',
        tag: 'UH',
      });
    });
  });

  describe('boolean fields', () => {
    it('should parse boolean fields correctly', () => {
      const responseWithBooleans: LemmatizeResponse = {
        annotations: ['text', 'lemma', 'is_alpha', 'is_stop'],
        tokens: [[['Hello', 'hello', 'true', 'false']]],
        model: 'test',
        processing_time_ms: 0,
      };

      const result = new LemmatizationResultImpl(responseWithBooleans);
      const token = result.documents[0].tokens[0];

      expect(token.is_alpha).toBe(true);
      expect(token.is_stop).toBe(false);
    });
  });
});

