import { BaseExtractor } from './base-extractor.js';

const INLINE = /\[[^\]]*\]\(([^)\s]+)[^)]*\)/g;
const AUTOLINK = /<((?:https?|mailto):[^>\s]+)>/g;

export class MarkdownExtractor extends BaseExtractor {
  extract(text) {
    const found = [];
    for (const pattern of [INLINE, AUTOLINK]) {
      for (const match of text.matchAll(pattern)) {
        if (!found.includes(match[1])) {
          found.push(match[1]);
        }
      }
    }
    return found;
  }
}
