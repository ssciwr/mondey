# MONDEY frontend

The svelte frontend for the MONDEY project.

## Local development

See [DEVELOPMENT.md](../DEVELOPMENT.md) for the full local development setup, including how to run the backend.

Initial setup to edit the frontend locally:

- install Node.js 24 and enable its bundled Corepack, e.g. `corepack enable`; Corepack uses the pnpm version pinned in `package.json`
- clone the repo, e.g. `git clone https://github.com/ssciwr/mondey.git`
- go to the frontend folder of the repository, e.g. `cd mondey/frontend`
- copy `.env.dev.sample` to `.env`
- install the node dependencies, e.g. `pnpm install`
- (optional) install playwright browsers for testing: `pnpm exec playwright install --with-deps`
- (optional) install [prek](https://github.com/j178/prek) for code formatting and linting: `pip install prek && prek install`

To start a development server:

- `pnpm run dev`

This will serve the website at [http://localhost:5173](http://localhost:5173).
API requests are proxied to the backend at `VITE_API_PROXY_URL`, which needs to be running separately.

## Tests

To run the unit tests:

- `pnpm test:unit`

To run the ui tests interactively:

- `pnpm test:ui:dev`

To run the end-to-end tests, a backend with the test data needs to be running
(`mondey-backend` started from the `e2e` directory), then:

- `pnpm build && pnpm test:e2e`

To type check the code:

- `pnpm run check`

## Generated API client

`src/lib/client` is generated from the backend OpenAPI schema and should not be edited by hand -
see [DEVELOPMENT.md](../DEVELOPMENT.md) for how to regenerate it.
