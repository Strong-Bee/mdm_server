# MDM Server Landing Page

Next.js landing page for the experimental Apple iOS/iPadOS MDM server project.

## Stack

- Next.js App Router
- React
- TypeScript (strict mode)
- Responsive CSS; no component library required

## Local development

From this directory:

```bash
npm install
npm run dev
```

Open http://localhost:3000.

## Vercel deployment

Import `Strong-Bee/mdm_server` from GitHub, then set **Root Directory** to `web`. Vercel will detect Next.js and use the scripts and dependencies in `web/package.json`.

This is a static marketing/documentation site. It does **not** deploy or expose the Python Flask MDM backend. The backend still requires a deployment environment with persistent storage, HTTPS, device identity validation, and proper enrollment security. Do not publish the experimental MDM endpoints publicly until those controls are implemented and tested.

## Links

- [Main repository](https://github.com/Strong-Bee/mdm_server)
- [Project README](https://github.com/Strong-Bee/mdm_server/blob/main/README.md)
- [Project security notes](https://github.com/Strong-Bee/mdm_server/blob/main/ABOUT.md)
