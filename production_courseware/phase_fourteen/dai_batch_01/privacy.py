def build(course, module):
    return course(85, 'Data Protection, Consent and Cyber Hygiene',
        'Data Protection,\nConsent and\nCyber Hygiene',
        'Review a fictional service data flow, explain consent choices, and apply protective work habits.', [
        module('Map purpose and minimise collection',
            'Justify each fictional intake field and identify a privacy review decision.',
            """
Start a privacy review with the service action the person wants. An appointment request may require a safe return channel and rough availability. A later eligibility assessment may need different evidence. Document each purpose separately, including optional analytics or training. Grouping unrelated purposes under one vague label obscures what the agency actually intends to do. The Nigerian Act sets expectations for specified purposes, relevance, limits on retention and accountability. [S73]

Trace a field through collection, access, sharing, retention and disposal. Identify who decides why the field is collected and who processes it on an agency's behalf. A contractor's access to a document still needs a defined function and review. If the team cannot say how a field changes a legitimate action, challenge its collection and check whether an existing less intrusive value would suffice. [S74]

Removing obvious names may leave a record identifiable through a rare combination of dates, location and circumstances. Replacing a name with a case code protects certain workflows while someone with the key or enough context may still link records. Consider the recipient and realistic linkability when proposing a transfer. Use invented records for the exercise, and specify who can review the purpose and safeguards of a real transfer. [S73]

Plan decisions about correction and retention while designing the intake. Identify what triggers review, who can act, what exceptions may need assessment and how the request is communicated. A retention note needs an owner and an operational action beyond a line in a policy. Flag sensitive fields, novel processing and consequential decisions for the appropriate privacy review before a real service uses the proposed workflow. [S73]
            """,
            'A booking form asks for a support date, a safe contact number, full case histories and optional research permission. Every staff member can open each record indefinitely.',
            'Categorise fields by purpose and necessity. Draw their access, retention and correction routes.',
            'Separate booking from optional research. Challenge full histories, limit access by function and assign retention and correction responsibility.',
            """
Define separate purposes.|How should the agency handle optional research in the booking flow?|Define the distinct purpose and route it for separate review.|Treat it as required for every appointment.|Store it under a generic service label.|Collect first and choose a purpose later.|Distinct purposes support a clear necessity and authority decision.
Minimise intake fields.|Which proposed booking field most directly supports a reply?|A safe contact method.|Full family history.|All past employment records.|An unrelated identity document.|The minimum follows from the immediate decision.
Map recipient functions.|What should a proposed contractor access entry contain?|Defined task, permitted information and responsible review.|Permanent access for any future request.|A label with the contractor name only.|The login details of a staff owner.|Access follows an identified role and purpose.
Consider linkability.|Why might a coded record still be personal data?|Other details or a lookup key can link it to a person.|The code is shorter than the name.|The file has a date format.|The document is read through a browser.|Pseudonymisation can leave realistic ways to identify people.
Assign lifecycle controls.|Which retention plan can be implemented?|Define a trigger, responsible role and disposal or review action.|Keep records until someone remembers them.|Remove the owner from the schedule.|Use the same period for every purpose by default.|A useful schedule guides decisions and review.
            """),
        module('Explain meaningful consent and choice',
            'Separate service agreement, recording choice and a verified processing basis.',
            """
An agency needs to explain what service it offers, what information it uses and who can answer questions. Agreement to receive a service concerns the service relationship. Consent to record the conversation concerns a different action. A processing basis is the justification the responsible organisation identifies for a specific purpose under applicable law. The Act sets out multiple lawful bases, and organisations need to assess the applicable basis rather than relying on a general acceptance screen. [S73] [S74]

Consider what happens when a person declines an optional recording. A choice may lose practical meaning if the ordinary service becomes inaccessible or slower without explanation. Describe the purpose, alternatives, possible recipients and what continuing without the optional feature looks like. Check understanding in plain language. Record the decision contemporaneously and provide a way to change it through an accessible service route. [S71]

Where consent is the basis, the agency needs a way to demonstrate it. Under the Nigerian Act, silence and inactivity cannot provide consent, and the request needs a clear accessible format. Withdrawal affects future reliance on that consent and does not retrospectively invalidate processing already lawfully carried out. Determine treatment of existing records and other obligations with the designated lead, and tell the person what can be done and when. [S73]

Avoid seeking a blanket yes to future uses. A second use may require its own assessment, information and safeguards. For the exercise, keep a decision record with the purpose, version of the explanation, decision, date, available service alternative and responsible role. Escalate unclear situations, including significant power imbalance or uncertainty around legal authority, to supervision and privacy review. [S74]
            """,
            'The team asks callers to agree to service, recording and later product development with one button. It treats silence as permission and has no manual appointment route.',
            'Draft a plain-language recording choice and indicate who verifies the processing basis and manages withdrawal.',
            'Explain the specific use and an ordinary appointment option. Capture the choice and give an accessible way to revisit it.',
            """
Separate service and recording choices.|What should happen when someone wants the appointment and declines optional recording?|Offer the ordinary approved appointment route.|Classify them as refusing the service.|Ask for a blanket yes again.|Treat delivery participation as automatic recording permission.|The two decisions involve different purposes.
Identify a basis for each purpose.|Who verifies a fictional agency's basis for a new transfer before real use?|The responsible privacy or qualified agency lead.|Any learner who completed this exercise.|The software vendor alone.|The receptionist on personal preference.|A basis depends on law, responsibilities and context.
Provide an active choice.|How should an unanswered recording request be recorded?|As no recorded agreement to the optional action.|As acceptance after two seconds.|As a verbal signature.|As consent to all future exports.|Silence does not establish consent under the Act.
Explain withdrawal practically.|What belongs in an explanation of consent withdrawal?|A usable contact route and how future consent-based use will be handled.|A claim that prior lawful processing automatically becomes unlawful.|A promise that every record will immediately disappear.|A requirement to finish the contract first.|Withdrawal arrangements need clarity about timing and other obligations.
Document what someone agreed to.|Which entry provides the best record of an optional decision?|Specific purpose, explanation version, decision and date.|A green check with no purpose.|A vendor report on total logins.|A staff guess about preferences.|The agency needs evidence of what was explained and chosen.
            """),
        module('Protect work accounts and report incidents',
            'Choose protective account habits and route a fictional information concern.',
            """
A workplace account connects the practitioner to sensitive agency activity. Use named authorised accounts, suitably strong unique passwords stored through an approved manager and multifactor authentication where provided. Follow the agency's device and update procedures. A shared account makes actions harder to attribute and can leave former team members with access. Review barriers to using the approved method with the responsible support team. [S77]

A message asking for urgent access changes should be checked independently using an established agency contact route. Stop before opening unfamiliar attachments or sending information, and report the suspicious message through the workplace process. Follow the service desk's instructions for preserving evidence and handling affected equipment. Staff support and well-practised reporting can reduce delay when someone is uncertain how serious an event is. [S77]

When an unintended recipient receives a fictional case file, identify the information, action, time and affected channel without broadcasting the file further. Promptly tell the responsible incident and privacy teams. Follow their directions on containment, records and practical protection of recipients and affected people. Statutory breach assessment and notification depend on the facts and the controller's duties. The learner's role is prompt accurate escalation. [S73]

Access also needs a lifecycle. When someone moves from intake to another role, verify the new tasks and request that unnecessary permissions are removed through the approved process. A review can check that approved people can still do their work and that test or former staff accounts no longer have access. Use the documented continuity route when access is interrupted, and leave credentials out of support tickets. [S71]
            """,
            'An invented team shares a login. A staff member receives an urgent request for a password reset through an unexpected channel and discovers a case attachment sent to the wrong inbox.',
            'Identify three preventive controls and draft an incident note with the minimum useful facts and recipients.',
            'Use named accounts and approved authentication. Verify the request independently and report exposure promptly through designated routes.',
            """
Use attributable accounts.|Which account arrangement helps trace staff actions?|Each authorised worker is assigned their own account.|Every team uses a common login.|The administrator enters all records on behalf of staff.|Workers swap passwords when off shift.|Distinct identities support accountability and access reviews.
Protect credentials.|Which routine protects approved workplace logins?|Unique passwords with an approved manager and MFA.|Repeat one strong password across services.|Share reset codes with colleagues.|Write passwords in the appointment calendar.|Separate protective factors reduce avoidable exposure.
Verify unexpected requests.|What should a staff member do with an unexpected urgent credential request?|Check independently through the established service desk route.|Reply with credentials to test authenticity.|Forward it widely to see who responds.|Click the message link to ask for proof.|Independent verification avoids reliance on the unexpected message.
Escalate accidental disclosure.|Which first note supports the incident team's work?|Relevant time, channel, information type and known actions.|A copy of the file sent to everyone.|An unverified public attribution.|A message deleting the event from the record.|Prompt minimal factual reporting enables assessment.
Review permissions after role changes.|What action follows an intake worker's transfer?|Review required access and remove prior permissions through the approved process.|Preserve every permission indefinitely.|Give their credentials to the replacement.|Switch the team to a shared account.|Role changes can leave access beyond current need.
            """),
    ])
