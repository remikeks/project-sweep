/** Render each slide of a PowerPoint file for local visual quality assurance. */

import fs from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

const [inputArg, outputArg] = process.argv.slice(2);
const runtimeNodeModules = process.env.RUNTIME_NODE_MODULES;
if (!inputArg || !outputArg || !runtimeNodeModules) {
  throw new Error("Usage: RUNTIME_NODE_MODULES=<path> node render_presentation_preview.mjs <input.pptx> <output-dir>");
}

const runtimeRequire = createRequire(path.join(runtimeNodeModules, "package.json"));
const artifactToolPath = runtimeRequire.resolve("@oai/artifact-tool");
const { FileBlob, PresentationFile } = await import(pathToFileURL(artifactToolPath).href);
const inputPath = path.resolve(inputArg);
const outputDir = path.resolve(outputArg);
const presentation = await PresentationFile.importPptx(await FileBlob.load(inputPath));

await fs.mkdir(outputDir, { recursive: true });
for (const [index, slide] of presentation.slides.items.entries()) {
  const image = await presentation.export({ slide, format: "png", scale: 1.5 });
  const filename = `slide-${String(index + 1).padStart(2, "0")}.png`;
  await fs.writeFile(path.join(outputDir, filename), new Uint8Array(await image.arrayBuffer()));
}
console.log(`Rendered ${presentation.slides.items.length} slides to ${outputDir}`);
