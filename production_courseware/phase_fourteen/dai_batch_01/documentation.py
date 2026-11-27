def build(course, module):
    return course(87, 'Responsible AI for Casework Documentation',
        'Responsible AI\nfor Casework\nDocumentation',
        'Reconcile a fixed example draft with fictional source notes and produce a reviewable case record.', [
        module('Preserve voice and source distinctions',
            'Separate a person’s account, worker observation, interpretation and agreed action.',
            """
Case documentation helps the person and the team understand what happened and what comes next. Record who supplied a factual claim, when the interaction occurred and what the person actually agreed to. Distinguish reported experiences from directly observed behaviour. The worker's interpretation belongs in a recognisable place and should identify its evidence and uncertainty. [S71]

Consider this invented source. The person says they could not take the call because other people were nearby. The worker observed that the person asked for a different time. Recasting that record as refusal of support changes the meaning and may affect future decisions. Preserve the stated privacy barrier, the preferred timing and responsibility for making contact. Include relevant observations without making a diagnostic inference. [R82]

A generated summary may compress disagreement, flatten emotion or replace local language with generic service labels. Ingram's baseline work identifies tensions about observation, presence and reflection. Most respondents had yet to use the tool with service users, which makes the findings useful for educational discussion about expectations. Treat the concerns as prompts for careful examination in your setting. [R82]

Read a fixed classroom draft against the original notes line by line. Mark whether each claim is supported, uncertain, absent or contradicted. Check whether a crucial preference or refusal was omitted. Then produce a short record with a dated source, appropriate attribution and the named role responsible for action. The actual date of the interaction and the date the note is written can be distinct. Label both explicitly when the distinction affects interpretation or later follow-up. [S75]
            """,
            'The source records that a person requested a private time to call. The draft says the person was uncooperative, declined help and refused to explain the absence.',
            'Write a revised four-line note separating reported account, observation, interpretation and next step.',
            'Record the person’s privacy reason and request. Attribute what was observed and mark any interpretation as provisional.',
            """
Attribute the account.|Which wording preserves the fictional source accurately?|The person reported they lacked privacy for the call.|The person refused all assistance.|The worker verified persistent noncompliance.|The person declined to state a reason.|Attribution distinguishes reported circumstances from inference.
Separate observation from interpretation.|Which statement is directly observable in this case?|The person asked for a different call time.|They intended to disrupt intake.|They lacked motivation to engage.|They disliked the worker personally.|Direct observation concerns what occurred or was said.
Preserve a material preference.|What omission would matter when scheduling follow-up?|The request for a private time.|The colour of the office wall.|The formatting of the template.|The staff calendar’s font.|Contact preferences can affect safety and practical access.
Apply baseline evidence appropriately.|What did the Scottish baseline specifically help explore?|Expectations and concerns when practitioners first encountered the tool.|Measured national action times.|Causal service outcomes after several years.|Accuracy on every local language.|A baseline primarily shows early conditions and perceptions.
Record verifiable next steps.|Which entry will support follow-up?|The assigned worker will call at the agreed private time.|Someone should do something soon.|Next action automatically completed.|No contact is needed because a draft exists.|Ownership and a clear action make the record usable.
            """),
        module('Reconcile drafts before signing',
            'Detect additions, omissions, substitutions and misleading conclusions in a draft.',
            """
Begin with the intended audience and decision. An appointment update can be brief, while a formal case note may need provenance and enough context to review the action. Check names or fictional identifiers, dates, negation, who said what, uncertainty and agreed actions. Label an unsupported addition separately from a missing source detail. An altered detail can produce both types of error at once. [S75]

A fictional source might say an application arrived Thursday and the team has yet to confirm a meeting. A draft that says the team promised a meeting on Thursday combines an incorrect event with an omitted uncertainty. Correct the date's meaning and retain the outstanding decision. Do not infer that a neat chronological paragraph is reliable simply because all the dates sound plausible. [S75]

Reconciliation also checks how the text represents agency and relationships. A phrase such as refused service can conceal a limited choice about recording or timing. Restore the person's wording and agency where relevant. If a literal quotation is important, verify it with a reliable source rather than inventing quotation marks around a paraphrase. Seek clarification through the responsible route if the source contains conflicting accounts. [R82]

Include time to review, correct and sign when judging whether a documentation change is worthwhile. The Finnish social welfare pilot gathered facilitated workshop feedback and described perceived efficiencies, but it did not time documentation or use structured questionnaires. In a classroom comparison, note which error types people corrected and which would require a different workflow. A saved draft becomes a final record only after the defined review. [R84]
            """,
            'The source lists an application received Thursday, a provisional meeting date and a refusal of recording. The draft announces a Thursday meeting and omits the recording choice.',
            'Mark both changes and rewrite the action status and recording decision. Specify what a signer should verify.',
            'Thursday refers to receipt. Keep the meeting provisional and preserve the decision about recording before signing.',
            """
Check event and date together.|What should Thursday label in the revised record?|Receipt of the application.|The confirmed meeting.|The date consent was granted.|A final case closure.|Correct date attribution preserves chronology.
Recognise a material omission.|What was omitted from the generated draft?|The refusal of recording.|The case status label used in the software.|A proposed invoice.|A claim that the meeting occurred.|A recording decision can affect how later work proceeds.
Verify direct quotes.|When should supplied words appear as an attributed quotation?|When the authorised source supports the wording accurately.|Whenever the generator uses quotation marks.|When the worker remembers the subject only.|Whenever the quote sounds helpful.|Verbatim claims need a suitable source.
Count review labour.|Which comparison captures documentation effort?|Drafting plus checking, corrections and approval time.|Generation time alone.|The number of words only.|Number of notes opened by managers.|Review labour is part of the workflow cost.
Put ambiguous facts on hold.|What should a signer do when authorised sources conflict about the next action?|Flag the uncertainty and seek clarification through the responsible route.|Choose the more fluent version.|Apply the earliest date as a rule.|Remove all evidence of disagreement.|A signed record should represent uncertainty and the action needed to resolve it.
            """),
        module('Record consent and handle corrections',
            'Design traceable recording choices, review history and a correction route.',
            """
An approved recording workflow needs a specific purpose and an accessible explanation. Describe what would be captured, who can use it, how recording affects the meeting, how retention is handled and what happens if someone declines. For the classroom scenario, practise explaining a manual note option and checking that the person understands the choice before marking any recording decision. [S71]

Keep decisions about audio, a transcript, draft text and the final case record distinct. Different records serve different functions and may have different retention and access decisions. A real organisation assesses those conditions with its qualified lead. In the exercise, document source, draft version, review date and sign-off role without including real identifiers or copying a questionable draft into unrelated notes. [S73]

If an inaccuracy reaches the final record, record what was corrected, the reason, the authorised role and which subsequent uses may require review. Stop continuing use of the inaccurate version where the process allows and inform the responsible team. The agency process needs to handle the person's request to correct an account, retain required history and explain the outcome in a usable way. [S73]

Reflect on how digital recording affects attention. A worker may spend less time writing in the room, or focus too much on what the tool captures. The observed difference depends on task and context. In a simulation, compare a manual note and a reviewed assisted draft for the quality of the record, staff reflection and whether the person's own account remains recognisable. Allow time for the worker to consider what the record may have missed. [R82]
            """,
            'The fictional team keeps audio, draft and signed note in one folder. A person later challenges a quote that caused an unnecessary referral restriction.',
            'Propose a correction record, identify downstream recipients and give the person a clear response route.',
            'Assess the affected decision, track the correction and review recipients through the approved process. Maintain usable feedback and ownership.',
            """
Explain the recording choice early.|What information does a person need before deciding about optional recording?|Purpose, recipients, ordinary alternative and how to ask questions.|Only the product’s marketing name.|The internal file naming convention.|A promise that every case must be recorded.|A useful decision requires understandable information and a real choice.
Distinguish record types.|Which records can require different access and retention decisions?|Audio, transcript, draft and signed case note.|Only text with a spelling mistake.|Only calendar records.|All files are interchangeable.|Different artefacts support different purposes.
Track a correction.|Which correction entry supports accountability?|Amended fact, reason, date and authorised reviewer.|A silent replacement with no history.|An unrelated duplicate note.|Deletion of the person’s challenge from every record.|A reviewable history supports explanation and subsequent checks.
Review downstream effects.|A wrong quote informed a referral restriction. What needs review?|The restriction and relevant recipients of the earlier version.|Only the quote’s punctuation.|Whether the file opens quickly.|The total number of staff logins.|The effect of an inaccuracy may extend beyond the note.
Compare relational effects.|Which classroom observation helps assess role of technology during a discussion?|Whether the person’s account and choices are reflected after review.|Only how polished the draft looks.|Number of menus on screen.|How often the generator shows a spinner.|Relational quality is expressed in listening, accurate representation and understandable choices.
            """),
    ])
