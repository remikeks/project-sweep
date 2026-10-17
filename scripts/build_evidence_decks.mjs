import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const [outputArg] = process.argv.slice(2);
if (!outputArg) throw new Error('Usage: build_evidence_decks.mjs <new-candidate-directory>');
const output = path.resolve(outputArg);
const runtimeRequire = createRequire(path.join(process.env.CODEX_RUNTIME_NODE_MODULES, 'package.json'));
const { Presentation, PresentationFile } = await import(pathToFileURL(runtimeRequire.resolve('@oai/artifact-tool')).href);
const skill = process.env.CODEX_PRESENTATIONS_SKILL_DIR;
const { finalizePresentation, resolvePresentationFont } = await import(pathToFileURL(path.join(skill, 'container_tools/artifact_tool_utils.mjs')).href);
const source = JSON.parse(await fs.readFile('production_courseware/expansion_review/teaching_source.json', 'utf8'));
const banks = JSON.parse(await fs.readFile('production_courseware/expansion_review/assessment_source.json', 'utf8'));
const catalogue = JSON.parse(await fs.readFile(path.join(output, 'course_catalogue.json'), 'utf8'));
const family = resolvePresentationFont();
for (const dir of ['pptx', '.deck-build', 'qa/decks']) await fs.mkdir(path.join(output, dir), {recursive:true});

function text(slide, content, left, top, width, height, size=24, bold=false, color='#17223B') {
  const shape = slide.shapes.add({geometry:'textbox',position:{left,top,width,height},fill:'none',line:{fill:'none',width:0}});
  shape.text = content;
  shape.text.style = {typeface:family, fontSize:size, bold, color, autoFit:'shrinkText'};
}

for (const course of source.courses) {
  const meta = catalogue.find(c => c.code === course.code);
  const bank = banks.courses.find(c => c.code === course.code);
  const prefix = `${String(meta.number).padStart(2,'0')}-${meta.slug}`;
  const finalPath = path.join(output, 'pptx', `${prefix}-course-deck.pptx`);
  try { await fs.access(finalPath); throw new Error(`Refusing to overwrite ${finalPath}`); }
  catch (error) { if (error.code !== 'ENOENT') throw error; }
  const presentation = Presentation.create({slideSize:{width:1280,height:720}});
  function slide(title, label, notes='') {
    const item = presentation.slides.add();
    item.background.fill = '#FFFFFF';
    text(item, label, 64, 35, 1140, 34, 17, true, '#35634B');
    text(item, title, 64, 92, 1140, 105, 35, true, '#0B2C7A');
    text(item, `${course.code}  |  SWEEP Academy  |  1.1.0`, 64, 674, 1000, 25, 12);
    text(item, String(presentation.slides.items.length), 1170, 674, 50, 25, 12);
    item.speakerNotes.textFrame.setText(notes);
    return item;
  }
  const cover = slide(meta.title, 'RESEARCH INFORMED LEARNING');
  text(cover, meta.outcome, 64, 230, 1080, 130, 29);
  text(cover, 'Read the learner guide, apply each lesson, then complete the worksheet.', 64, 410, 1080, 65, 24);
  text(cover, 'Educational material. Use applicable local procedures. Cases are fictional. Index inclusion is not expert endorsement.', 64, 535, 1080, 80, 21);
  for (const module of course.modules) {
    const assessed = bank.modules.find(m => m.order === module.order);
    const references = course.references.map(id => source.references.find(r => r.id === id));
    const notes = [...module.explanation, ...assessed.items.map(i=>i[0]), ...references.map(r=>`${r.citation} ${r.url} ${r.limit}`)].join('\n\n');
    const core = slide(module.heading, `MODULE ${module.order}  |  REASONING`, notes);
    text(core, module.slide, 64, 225, 1100, 185, 30);
    text(core, assessed.outcome, 64, 465, 1100, 110, 23);
    const practice = slide('Apply the lesson', `MODULE ${module.order}  |  FICTIONAL WORKED EXAMPLE`, `${module.example}\n\n${module.feedback}\n\n${notes}`);
    text(practice, module.example, 64, 205, 1110, 160, 25);
    text(practice, 'YOUR TASK', 64, 405, 1100, 35, 17, true, '#35634B');
    text(practice, module.activity, 64, 460, 1110, 140, 25);
  }
  const refs = course.references.map(id => source.references.find(r=>r.id===id));
  for (let i=0; i<refs.length; i+=2) {
    const page = slide('Sources and limits', 'EVIDENCE CHECK');
    refs.slice(i,i+2).forEach((r,index) => {
      text(page, `[${r.id}] ${r.citation}`, 64, 200+index*210, 1110, 105, 21, true);
      text(page, `${r.url}\n${r.limit}`, 64, 305+index*210, 1110, 100, 18);
    });
    page.speakerNotes.textFrame.setText(refs.slice(i,i+2).map(r=>`${r.access}\n${r.summary}\n${r.limit}`).join('\n\n'));
  }
  const candidatePath = path.join(output, '.deck-build', `${prefix}.pptx`);
  await (await PresentationFile.exportPptx(presentation)).save(candidatePath);
  await finalizePresentation({explicitTotalSlideCount:presentation.slides.items.length,workspaceDir:output,candidatePath,finalPath,
    pythonExecutable:process.env.CODEX_RUNTIME_PYTHON,
    integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
    layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
    layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],
    requiredNativeTableOwnerSlides:[],fontPolicy:{basis:'design',families:[family]},verifyArtifactToolImport:true,
    receiptPath:path.join(output,'.deck-build',`${prefix}-validation.json`)});
  const qa = path.join(output, 'qa/decks', course.code);
  await fs.mkdir(qa,{recursive:true});
  for (const [index,item] of presentation.slides.items.entries()) {
    const png = await presentation.export({slide:item,format:'png',scale:1});
    await fs.writeFile(path.join(qa,`${index+1}.png`),new Uint8Array(await png.arrayBuffer()));
  }
  console.log(`${course.code}: ${presentation.slides.items.length} slides built and structurally validated.`);
}
