# [mondey-frontend-prototype](https://ssciwr.github.io/mondey-frontend-prototype)

Initial frontend prototyping for the MONDEY project.

The static website is automatically built and deployed to
[ssciwr.github.io/mondey-frontend-prototype](https://ssciwr.github.io/mondey-frontend-prototype)
on every push to the main branch using this [Github Action](.github/workflows/deploy.yml).

## Component demos

- [Milestone](https://ssciwr.github.io/mondey-frontend-prototype/milestone)

## Local development

Initial setup to edit the website locally:

- install [pnpm](https://pnpm.io/installation), e.g. `curl -fsSL https://get.pnpm.io/install.sh | sh -`
- clone the repo
- install node dependencies, e.g. `pnpm install`

To start a dev server:

- `pnpm run dev`

## Notes

Commands used to generate most of the initial empty app:

```bash
pnpm create svelte@latest
pnpm i -D @sveltejs/adapter-static
npx svelte-add@latest tailwindcss
pnpm i -D flowbite-svelte flowbite
pnpm i -D flowbite-svelte-icons
```
