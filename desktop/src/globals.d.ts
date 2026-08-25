// App version injected at build time by Vite (define), sourced from package.json.
declare const __APP_VERSION__: string;

// Vite's `?raw` suffix hands a module's own source back as a string. Studio uses
// it in one place: a test that reads a route's source to prove a piece of wording
// has not been quietly shortened. A test that imported a mock could not catch that.
declare module "*?raw" {
  const content: string;
  export default content;
}
