import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const [catalogueArg, outputArg, backgroundArg] = process.argv.slice(2);
if (!catalogueArg || !outputArg || !backgroundArg) {
  throw new Error("Usage: build_production_decks.mjs <catalogue.json> <output-root> <background.png>");
}
const cataloguePath = path.resolve(catalogueArg);
const outputRoot = path.resolve(outputArg);
const backgroundPath = path.resolve(backgroundArg);

const skillDir = "C:\\Users\\PARAKLETUS HUB\\.codex\\plugins\\cache\\openai-primary-runtime\\presentations\\26.904.11930\\skills\\presentations";
const runtimePython = "C:\\Users\\PARAKLETUS HUB\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe";
const { resolvePresentationFont, finalizePresentation } = await import(
  pathToFileURL(path.join(skillDir, "container_tools", "artifact_tool_utils.mjs")).href,
);

const courses = JSON.parse(await fs.readFile(cataloguePath, "utf8"));
const backgroundBytes = await fs.readFile(backgroundPath);
const outputDir = path.join(outputRoot, "pptx");
const previewDir = path.join(outputRoot, "qa", "deck-montages");
const stagingDir = path.join(outputRoot, ".deck-build");
await fs.mkdir(outputDir, { recursive: true });
await fs.mkdir(previewDir, { recursive: true });
await fs.mkdir(stagingDir, { recursive: true });

const family = resolvePresentationFont();
const colors = {
  navy: "#0B2C7A",
  dark: "#071D52",
  blue: "#1E9BE0",
  green: "#4C8B1D",
  gold: "#F5A400",
  body: "#17223B",
  muted: "#52617D",
  white: "#FFFFFF",
  cream: "#FAF8F2",
};

function addText(slide, text, position, style = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position,
    fill: "none",
    line: { fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    typeface: family,
    fontSize: 20,
    color: colors.body,
    autoFit: "shrinkText",
    ...style,
  };
  return shape;
}

function addFooter(slide, course, index) {
  addText(slide, `${course.code}   SWEEP Academy`, { left: 70, top: 674, width: 600, height: 22 }, {
    fontSize: 12,
    color: colors.muted,
  });
  addText(slide, String(index).padStart(2, "0"), { left: 1160, top: 674, width: 50, height: 22 }, {
    fontSize: 12,
    color: colors.muted,
    alignment: "right",
  });
}

function addNotes(slide, course, purpose) {
  slide.speakerNotes.textFrame.setText(
    `Source: SWEEP Academy Course Content Outlines, approved catalogue. ${purpose} ` +
    "The deck uses a SWEEP Academy generated illustration as the cover background. " +
    "Facilitators must confirm local law, policy, and referral routes before delivery.",
  );
}

function moduleText(module) {
  return `This module covers ${module.focus}. Work from the learner guide to separate observed information from assumptions, involve the person or community appropriately, and use supervision or local policy when the decision falls outside your authority.`;
}

function slugify(value) {
  return value.toLowerCase().replaceAll("&", "and").replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
}

async function buildDeck(course) {
  const prefix = `${String(course.number).padStart(2, "0")}-${slugify(course.title)}`;
  const finalPath = path.join(outputDir, `${prefix}-course-deck.pptx`);
  const candidatePath = path.join(stagingDir, `${prefix}-candidate.pptx`);
  const receiptPath = path.join(stagingDir, `${prefix}-validation.json`);
  const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });

  const cover = presentation.slides.add();
  cover.background.fill = colors.dark;
  cover.images.add({
    blob: backgroundBytes,
    contentType: "image/png",
    alt: "Illustrated community learning background",
    fit: "cover",
    position: { left: 0, top: 0, width: 1280, height: 720 },
  });
  addText(cover, course.title, { left: 72, top: 130, width: 620, height: 180 }, {
    fontSize: 52,
    bold: true,
    color: colors.white,
    autoFit: "shrinkText",
  });
  addText(cover, `${course.school}\n${course.code}`, { left: 74, top: 350, width: 480, height: 70 }, {
    fontSize: 20,
    color: colors.white,
  });
  addText(cover, "SWEEP Academy", { left: 74, top: 625, width: 300, height: 32 }, {
    fontSize: 17,
    bold: true,
    color: colors.white,
  });
  addNotes(cover, course, "Cover slide.");

  const outcome = presentation.slides.add();
  outcome.background.fill = colors.cream;
  addText(outcome, "Course outcome", { left: 72, top: 68, width: 860, height: 55 }, {
    fontSize: 38,
    bold: true,
    color: colors.navy,
  });
  addText(outcome, course.outcome, { left: 72, top: 176, width: 1000, height: 150 }, {
    fontSize: 32,
    bold: true,
    color: colors.body,
  });
  addText(outcome, "Practice notice", { left: 72, top: 400, width: 240, height: 34 }, {
    fontSize: 20,
    bold: true,
    color: colors.green,
  });
  addText(outcome, "Apply the law, organisational policy, supervision requirements, and approved referral pathways that govern your setting. This course supports learning and does not replace urgent safeguarding, clinical, or legal procedures.", { left: 72, top: 450, width: 1040, height: 120 }, {
    fontSize: 21,
    color: colors.body,
  });
  addFooter(outcome, course, 2);
  addNotes(outcome, course, "Course outcome and delivery safeguard.");

  for (const module of course.modules) {
    const slide = presentation.slides.add();
    slide.background.fill = colors.white;
    addText(slide, `Module ${module.order}`, { left: 72, top: 62, width: 300, height: 36 }, {
      fontSize: 20,
      bold: true,
      color: colors.green,
    });
    addText(slide, module.title, { left: 72, top: 110, width: 980, height: 90 }, {
      fontSize: 40,
      bold: true,
      color: colors.navy,
    });
    addText(slide, module.focus, { left: 72, top: 245, width: 1060, height: 90 }, {
      fontSize: 25,
      bold: true,
      color: colors.body,
    });
    addText(slide, moduleText(module), { left: 72, top: 390, width: 1050, height: 145 }, {
      fontSize: 22,
      color: colors.body,
    });
    addText(slide, "Reflection: What information do you need to verify, and where would your local procedure set a limit or escalation point?", { left: 72, top: 565, width: 1030, height: 55 }, {
      fontSize: 18,
      color: colors.muted,
    });
    addFooter(slide, course, module.order + 2);
    addNotes(slide, course, `Module ${module.order} teaching slide.`);
  }

  const activity = presentation.slides.add();
  activity.background.fill = colors.cream;
  addText(activity, "Practice activity and assessment preparation", { left: 72, top: 68, width: 1050, height: 65 }, {
    fontSize: 36,
    bold: true,
    color: colors.navy,
  });
  addText(activity, "Use the course worksheet to apply the three modules to a de-identified case. Describe what you notice, the action that sits within your role, and what needs consultation, referral, or verification.", { left: 72, top: 178, width: 1040, height: 108 }, {
    fontSize: 24,
    color: colors.body,
  });
  addText(activity, "Assessment focus", { left: 72, top: 370, width: 260, height: 34 }, {
    fontSize: 22,
    bold: true,
    color: colors.green,
  });
  addText(activity, course.cbt_focus.map((item, idx) => `${idx + 1}. ${item}`).join("\n"), { left: 72, top: 425, width: 920, height: 120 }, {
    fontSize: 22,
    color: colors.body,
  });
  addText(activity, "Pass mark: 70%", { left: 72, top: 592, width: 270, height: 34 }, {
    fontSize: 18,
    bold: true,
    color: colors.gold,
  });
  addFooter(activity, course, 6);
  addNotes(activity, course, "Practice activity and assessment preparation.");

  await (await PresentationFile.exportPptx(presentation)).save(candidatePath);
  const result = await finalizePresentation({
    explicitTotalSlideCount: 6,
    workspaceDir: outputRoot,
    candidatePath,
    finalPath,
    pythonExecutable: runtimePython,
    integrityValidatorPath: path.join(skillDir, "container_tools", "inspect_presentation_package_integrity.py"),
    layoutValidatorPath: path.join(skillDir, "container_tools", "inspect_presentation_layout_geometry.py"),
    layoutArgs: ["--expected-slide-size-emu", "12192000,6858000", "--validate-bullet-geometry", "--validate-heading-fit"],
    requiredNativeTableOwnerSlides: [],
    fontPolicy: { basis: "design", families: [family] },
    verifyArtifactToolImport: true,
    receiptPath,
  });
  if (result?.errors?.length) {
    throw new Error(`Deck validation failed for ${course.title}: ${JSON.stringify(result.errors)}`);
  }
  const montage = await presentation.export({ format: "webp", montage: true, scale: 1 });
  await fs.writeFile(path.join(previewDir, `${prefix}.webp`), new Uint8Array(await montage.arrayBuffer()));
}

for (const course of courses) {
  await buildDeck(course);
  process.stdout.write(`Built deck ${course.number}/30: ${course.title}\n`);
}
