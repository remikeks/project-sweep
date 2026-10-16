// Convert the generated illustrations into lightweight, deployment-owned assets.
import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const sharp = require(path.join(process.env.RUNTIME_NODE_MODULES, 'sharp'));
const sources = JSON.parse(await fs.readFile(new URL('./catalogue_thumbnail_sources.json', import.meta.url), 'utf8'));
const output = path.resolve('static/img/catalogue');
await fs.mkdir(output, { recursive: true });
for (const { key, source } of sources) {
  for (const width of [480, 960]) {
    const result = await sharp(source).resize({ width, withoutEnlargement: true })
      .webp({ quality: 82, effort: 6 }).toFile(path.join(output, `${key}-${width}.webp`));
    console.log(`${key}-${width}.webp: ${result.width}x${result.height}, ${result.size} bytes`);
  }
}
