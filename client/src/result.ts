/**
 * Result wrapper with helper methods
 */

import { LemmatizeResponse, LemmatizationResult, Document, Token } from './types';

/**
 * Parse compact API response into structured documents
 */
function parseResponse(response: LemmatizeResponse): Document[] {
  const documents: Document[] = [];

  for (const docTokens of response.tokens) {
    const tokens: Token[] = [];

    for (const tokenValues of docTokens) {
      const token: Token = { text: '', lemma: '', pos: '' };

      response.annotations.forEach((fieldName, index) => {
        const value = tokenValues[index];

        // Parse boolean fields
        if (fieldName.startsWith('is_')) {
          token[fieldName] = value === 'true' || value === 'True';
        } else {
          token[fieldName] = value;
        }
      });

      tokens.push(token);
    }

    // Reconstruct text from tokens
    const text = tokens.map((t) => t.text).join(' ');
    documents.push({ tokens, text });
  }

  return documents;
}

/**
 * Implementation of LemmatizationResult
 */
export class LemmatizationResultImpl implements LemmatizationResult {
  public readonly raw: LemmatizeResponse;
  public readonly documents: Document[];

  constructor(response: LemmatizeResponse) {
    this.raw = response;
    this.documents = parseResponse(response);
  }

  allTokens(): Token[] {
    return this.documents.flatMap((doc) => doc.tokens);
  }

  filterTokens(predicate: (token: Token) => boolean): Token[] {
    return this.allTokens().filter(predicate);
  }

  toVertical(): string {
    const lines: string[] = [];

    for (let i = 0; i < this.documents.length; i++) {
      if (i > 0) {
        lines.push(''); // Empty line between documents
      }

      for (const token of this.documents[i].tokens) {
        const fields = [
          token.text,
          token.lemma,
          token.pos || '',
          token.tag || '',
        ];
        lines.push(fields.join('\t'));
      }
    }

    return lines.join('\n');
  }

  toCSV(): string {
    const tokens = this.allTokens();
    if (tokens.length === 0) return '';

    // Get all unique keys from first token
    const headers = Object.keys(tokens[0]);
    const lines = [headers.join(',')];

    for (const token of tokens) {
      const values = headers.map((key) => {
        const value = token[key];
        const str = String(value ?? '');
        // Escape CSV values
        if (str.includes(',') || str.includes('"') || str.includes('\n')) {
          return `"${str.replace(/"/g, '""')}"`;
        }
        return str;
      });
      lines.push(values.join(','));
    }

    return lines.join('\n');
  }

  toJSON(): Token[][] {
    return this.documents.map((doc) => doc.tokens);
  }
}

