/**
 * jsspacynlp API client
 */

import fetch, { Response } from 'node-fetch';
import {
  SpacyNLPConfig,
  LemmatizeRequest,
  LemmatizeResponse,
  ModelsResponse,
  HealthResponse,
  InfoResponse,
  ErrorResponse,
  SpacyNLPError,
} from './types';

const DEFAULT_CONFIG: Required<SpacyNLPConfig> = {
  apiUrl: 'http://localhost:8000',
  timeout: 30000,
  retries: 3,
  retryDelay: 1000,
};

/**
 * Main client class for jsspacynlp API
 */
export class SpacyNLP {
  private config: Required<SpacyNLPConfig>;

  constructor(config: SpacyNLPConfig = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  /**
   * Make HTTP request with retry logic
   */
  private async request<T>(
    endpoint: string,
    options: {
      method?: string;
      body?: unknown;
      attempt?: number;
    } = {}
  ): Promise<T> {
    const { method = 'GET', body, attempt = 1 } = options;
    const url = `${this.config.apiUrl}${endpoint}`;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

    try {
      const response: Response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = (await response.json()) as ErrorResponse;
        throw new SpacyNLPError(
          errorData.error || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          errorData
        );
      }

      return (await response.json()) as T;
    } catch (error) {
      clearTimeout(timeoutId);

      // Don't retry on client errors (4xx)
      if (error instanceof SpacyNLPError && error.statusCode && error.statusCode < 500) {
        throw error;
      }

      // Retry on network errors or server errors (5xx)
      if (attempt < this.config.retries) {
        const delay = this.config.retryDelay * Math.pow(2, attempt - 1);
        await new Promise((resolve) => setTimeout(resolve, delay));
        return this.request<T>(endpoint, { method, body, attempt: attempt + 1 });
      }

      // Max retries reached
      if (error instanceof SpacyNLPError) {
        throw error;
      }

      throw new SpacyNLPError(
        `Request failed after ${attempt} attempts: ${(error as Error).message}`
      );
    }
  }

  /**
   * Lemmatize texts using specified model
   */
  async lemmatize(
    texts: string | string[],
    model: string,
    fields?: string[]
  ): Promise<LemmatizeResponse> {
    const textsArray = Array.isArray(texts) ? texts : [texts];

    const request: LemmatizeRequest = {
      model,
      texts: textsArray,
      fields,
    };

    return this.request<LemmatizeResponse>('/lemmatize', {
      method: 'POST',
      body: request,
    });
  }

  /**
   * Get server health status
   */
  async health(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/health');
  }

  /**
   * Get server information
   */
  async info(): Promise<InfoResponse> {
    return this.request<InfoResponse>('/info');
  }

  /**
   * List available models
   */
  async models(): Promise<ModelsResponse> {
    return this.request<ModelsResponse>('/models');
  }

  /**
   * Get the API URL
   */
  getApiUrl(): string {
    return this.config.apiUrl;
  }
}

