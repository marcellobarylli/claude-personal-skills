export class BaseReporter {
  // eslint-disable-next-line no-unused-vars
  render(results) {
    throw new Error('render() must be implemented by subclasses');
  }

  summary(results) {
    const broken = results.filter((result) => !result.ok).length;
    return { total: results.length, broken };
  }
}
