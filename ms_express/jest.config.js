module.exports = {
  testEnvironment: 'node',
  testTimeout: 10000,
  forceExit: true,
  detectOpenHandles: true,
  collectCoverageFrom: [
    'index.js',
    '!node_modules/**',
  ]
};
