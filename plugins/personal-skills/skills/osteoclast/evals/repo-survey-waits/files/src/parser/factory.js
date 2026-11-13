import { MarkdownExtractor } from './markdown-extractor.js';

const EXTRACTORS = {
  markdown: MarkdownExtractor,
};

export class ExtractorFactory {
  static create(type) {
    const Extractor = EXTRACTORS[type];
    if (!Extractor) {
      throw new Error(`no extractor for ${type}`);
    }
    return new Extractor();
  }

  static supported() {
    return Object.keys(EXTRACTORS);
  }
}
