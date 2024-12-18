# MONDEY frontend

The svelte frontend for the MONDEY project.

## Local development

Initial setup to edit the frontend locally:

- install [pnpm](https://pnpm.io/installation), e.g. `curl -fsSL https://get.pnpm.io/install.sh | sh -`
- clone the repo, e.g. `git clone https://github.com/ssciwr/mondey.git`
- go to the frontend folder of the repository, e.g. `cd mondey/frontend`
- install the node dependencies, e.g. `pnpm install`
- (optional) install playwright browsers for testing: `pnpm exec playwright install --with-deps`
- (optional) install pre-commit for code formatting and linting: `pip install pre-commit && pre-commit install`

To start a development server:

- `pnpm run dev`

This will serve the website at [http://localhost:5173](http://localhost:5173)

## Tests

To run the unit tests:

- `pnpm test:unit`

To run the ui tests interactively:

- `pnpm test:ui:dev`
