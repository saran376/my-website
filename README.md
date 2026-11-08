# CartPal AI — Vercel upload

This folder is the complete deployable CartPal project. It serves the storefront and its live Channel3 product-search endpoints from one Vercel project. It contains no API keys.

## Deploy with Vercel CLI

1. Download and extract `cartpal-vercel-upload.zip`.
2. In Terminal, change into the extracted `cartpal-vercel` folder.
3. Run `npx vercel`, sign in, and follow the prompts to create or link the project.
4. In the Vercel project, open **Settings → Environment Variables**. Add `CHANNEL3_API_KEY` and paste your Channel3 key as its value. Select the environments you plan to use, then save.
5. Run `npx vercel --prod` from the project folder.

To deploy from the Vercel website instead, put this folder in a Git repository, import that repository, and set `cartpal-vercel` as the project root if it is inside a larger repository. Add `CHANNEL3_API_KEY` under the Vercel project's Environment Variables before deploying.

## After deployment

The home page is `/`. Vercel maps the Python files in `api/` to `/api/search`, `/api/product`, and `/api/health`. The storefront calls these endpoints on the same domain. The API key stays in Vercel's server-side environment and is never exposed to the browser.

On the first visit, the catalog status should show as connected. If you change the environment variable, redeploy the project for the change to take effect. Use `https://<your-deployment>/api/health` to inspect the connection status without revealing the key.

The shared cart and shopper preferences are saved in each visitor's browser. Each product link opens the seller's real product page; the retailer confirms final price, shipping, and tax. This package does not charge through PayPal or share carts between different devices.
