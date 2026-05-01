# Prerequisites Check

## Environment

- [ ] **FAL_KEY** — fal.ai API key must be set as an environment variable (`FAL_KEY=fak_...`). Get one at https://fal.ai/dashboard/keys
- [ ] **Node.js** — likely already installed. Verify with `node -v`
- [ ] **Python 3** — likely already installed. Verify with `python3 --version`

## CLI Tools

- [ ] **gltf-transform** — required for GLB compression (resize textures, convert to WebP, apply Draco)
  ```
  npm install -g @gltf-transform/cli
  ```
  Verify: `gltf-transform --version`

## Python Packages

- [ ] **fal-client** — Python client for fal.ai API calls
  ```
  pip install fal-client
  ```
  Verify: `python3 -c "import fal_client; print('ok')"`
