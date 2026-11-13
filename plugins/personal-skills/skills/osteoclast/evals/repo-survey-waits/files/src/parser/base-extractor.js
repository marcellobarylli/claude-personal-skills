export class BaseExtractor {
  // eslint-disable-next-line no-unused-vars
  extract(text) {
    throw new Error('extract() must be implemented by subclasses');
  }
}
