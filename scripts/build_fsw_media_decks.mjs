/** Build aligned, editable course decks. Render with render_fsw_media.py. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';

const root=process.cwd();
const output=path.resolve(process.argv[2] || 'production_courseware/phase_three/fsw_media_01');
const sourcePath=process.argv[4] || 'production_courseware/phase_two/fsw_batch_01/review_package.json';
const source=JSON.parse(await fs.readFile(sourcePath,'utf8'));
const approved=process.env.SWEEP_MATERIAL_RELEASE==='approved';
const skill=process.env.CODEX_PRESENTATIONS_SKILL_DIR;
process.env.RUNTIME_NODE_MODULES ||= process.env.CODEX_RUNTIME_NODE_MODULES;
const require=createRequire(path.join(process.env.CODEX_RUNTIME_NODE_MODULES,'package.json'));
const {Presentation,PresentationFile,FileBlob}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const {finalizePresentation,resolvePresentationFont}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const font=resolvePresentationFont();
const background=await fs.readFile('static/img/courseware-deck-background.png');
for(const dir of ['pptx','pdf','.deck-build','qa/decks']) await fs.mkdir(path.join(output,dir),{recursive:true});

function text(slide,value,x,y,w,h,size=28,bold=false,color='#17223B'){
  const shape=slide.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  shape.text=value;
  shape.text.style={typeface:font,fontSize:size,bold,color,autoFit:'none'};
  return shape;
}

for(const c of source.courses){
  if(process.argv[3] && c.code!==process.argv[3]) continue;
  const presentation=Presentation.create({slideSize:{width:1280,height:720}});
  const prefix=`${c.code}-${c.slug}`;
  const used=new Set(c.modules.flatMap(m=>m.sources));
  const refs=source.references.filter(r=>used.has(r.id));
  function slide(title,label,notes=''){
    const s=presentation.slides.add();s.background.fill='#FFFFFF';
    text(s,label,64,34,1150,32,18,true,'#35634B');
    text(s,title,64,89,1150,104,43,true,'#0B2C7A');
    text(s,`${c.code}   SWEEP Academy   ${approved?'Learning edition':'Draft'} 0.1.0`,64,674,1050,24,15,false,'#52617D');
    text(s,String(presentation.slides.items.length),1170,674,50,24,15,false,'#52617D');
    s.speakerNotes.textFrame.setText(notes);
    return s;
  }
  const cover=presentation.slides.add();cover.background.fill='#071D52';
  cover.images.add({blob:background,contentType:'image/png',alt:'SWEEP Academy illustration of a diverse community learning together',fit:'cover',position:{left:0,top:0,width:1280,height:720}});
  const coverTitle=c.cover_title || (c.code==='SWP-035'?'Social Work Values\nand Ethical\nDecision Making':'Generalist Assessment\nand Case Management');
  text(cover,coverTitle,68,145,620,245,52,true,'#FFFFFF');
  text(cover,c.school_display || 'Foundational Social Work\nPractice and Ethics',70,438,480,88,26,false,'#FFFFFF');
  text(cover,`${c.code}   ${approved?'Approved learning materials':'Draft for academic review'}\nVersion 0.1.0`,70,558,550,68,22,false,'#FFFFFF');
  text(cover,'SWEEP Academy',70,659,350,28,18,true,'#FFFFFF');
  cover.speakerNotes.textFrame.setText(`${c.title}\n${c.outcome}\nCover image: existing SWEEP Academy generated courseware background, static/img/courseware-deck-background.png. Original teaching source: ${sourcePath}. ${approved?'Owner-authorised learning materials. Assessment configuration and certification remain separate. No recorded video.':'This is a teaching draft, not a published course or a recorded video.'}`);
  let s=slide('Learning outcome and study route','COURSE OVERVIEW',c.outcome);
  text(s,c.outcome,64,212,1135,112,30);
  c.modules.forEach((m,i)=>text(s,`${m.order}. ${m.title}`,64,366+i*76,1140,62,28));
  for(const m of c.modules){
    const localRefs=source.references.filter(r=>m.sources.includes(r.id));
    const notes=[m.outcome,...m.paragraphs,...localRefs.map(r=>`[${r.id}] ${r.author} (${r.year}). ${r.title}. ${r.url}\nUse: ${r.use}\nLimit: ${r.appraisal}`)].join('\n\n');
    s=slide(m.title,`MODULE ${m.order} CONCEPTS`,notes);
    const points=c.assessment.modules.find(row=>row.order===m.order).teaching_points;
    points.forEach((point,i)=>text(s,`${i+1}. ${point.text}`,64,210+i*82,1135,76,28));
    s=slide('Worked case and practice',`MODULE ${m.order} APPLICATION`,`${m.example}\n\nActivity: ${m.activity}\n\n${notes}`);
    text(s,m.example,64,210,1135,204,29);
    text(s,'Practice task',64,441,1100,39,22,true,'#35634B');
    text(s,m.activity,64,496,1135,151,27);
    s=slide('Feedback and reflection',`MODULE ${m.order} REVIEW`,`${m.feedback}\n\n${notes}`);
    text(s,m.feedback,64,215,1135,205,31);
    text(s,'Reflection',64,457,1100,35,22,true,'#35634B');
    text(s,'Which part of your response needs more evidence, consultation or a clearer action owner?',64,513,1120,105,28);
  }
  s=slide('Course recap','LEARNING REVIEW',c.modules.map(m=>m.outcome).join('\n\n'));
  c.modules.forEach((m,i)=>text(s,m.outcome,64,215+i*139,1135,117,29));
  s=slide('Assessment and recognition','LEARNING PATHWAY');
  text(s,'The proposed course CBT contains 15 MCQs. A 70 percent pass mark requires at least 11 correct answers.',64,215,1135,104,30);
  text(s,'Course badges require an approved course and a verified ParaLearn CBT pass.',64,362,1135,85,29);
  text(s,approved?'School certification requires all curriculum courses, a final mixed ParaLearn exam, human written marking, independent moderation and authorised signatures.':'School certification also requires all curriculum courses and a final ParaLearn exam with MCQs, short answers and essays.',64,496,1135,117,29);
  for(let i=0;i<refs.length;i+=2){
    const page=refs.slice(i,i+2);
    s=slide('References and evidence limits','COURSE SOURCES',page.map(r=>`[${r.id}] ${r.author} (${r.year}). ${r.title}. ${r.url}\n${r.appraisal}\n${r.licence}\n${r.quartile || ''}`).join('\n\n'));
    page.forEach((r,j)=>{
      const y=202+j*220;
      text(s,`[${r.id}] ${r.slide_author || r.author} (${r.year})`,64,y,1135,36,24,true);
      text(s,r.slide_title || r.title,64,y+43,1135,92,24);
      const short=r.link_label || (r.doi?`doi.org/${r.doi}`:(r.id==='S1'?'ifsw.org Ethical principles':'socialworkers.org Case management standards'));
      const link=text(s,short,64,y+139,1135,36,21,false,'#0B2C7A');
      link.hyperlink={uri:r.url,isExternal:true};
      const limits={S1:'Professional framework. Confirm local law and policy.',S2:'US practice benchmark. Confirm Nigerian requirements.',
        R1:'Qualitative evidence from settings outside Nigeria.',R2:'Ten German rehabilitation facilities. Context matters.',
        R3:'Review quality and navigation roles vary.',R5:'Desk review and conceptual framework. No new participant data.'};
      text(s,r.slide_limit || limits[r.id] || 'Read the full source and context limits in the learner guide.',64,y+178,1135,39,22);
    });
  }
  const count=presentation.slides.items.length;
  const candidate=path.join(output,'.deck-build',prefix+'.pptx');
  const final=path.join(output,'pptx',prefix+'-course-slides.pptx');
  await (await PresentationFile.exportPptx(presentation)).save(candidate);
  await finalizePresentation({workspaceDir:output,candidatePath:candidate,finalPath:final,
    explicitTotalSlideCount:count,requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[],
    pythonExecutable:process.env.CODEX_RUNTIME_PYTHON,
    integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
    layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
    layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],
    fontPolicy:{basis:'design',families:[font]},verifyArtifactToolImport:true,
    receiptPath:path.join(output,'.deck-build',prefix+'-validation.json')});
  console.log(`${c.code}: ${count} editable slides exported and structurally validated.`);
}
