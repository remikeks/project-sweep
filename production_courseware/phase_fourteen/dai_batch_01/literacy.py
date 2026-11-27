def build(course, module):
    return course(86, 'AI Literacy, Limits, Bias and Human Oversight',
        'AI Literacy, Limits,\nBias and Human\nOversight',
        'Assess what an AI system does, test a fixed output for error and bias, and define effective human oversight.', [
        module('Distinguish digital tools and AI outputs',
            'Classify a digital feature by its function, inputs and evidence requirements.',
            """
A digital form can apply a written rule, a prediction system can estimate an outcome from past patterns, and a generative model can produce new text from prompts and context. A single interface can combine all three. Ask which function produced the output you see. Different functions have different evidence needs and specific ways to fail under ordinary service conditions. [S76]

A written rule can be traced to a criterion in an authorised policy. Its result is only as good as the rule, the data and the way the rule was translated into the form. A prediction needs a defined outcome, relevant test conditions and contextual interpretation. A probability alone cannot supply the facts of an individual case or establish authority to make a decision. [S75]

A text generator can produce fluent statements unsupported by its inputs. For any service-relevant claim, locate an original record or an authoritative current source and check whether it makes the same statement. Look for an invented source, a date placed in the wrong period and a claim that silently turns uncertainty into certainty. Keep unresolved claims out of a final factual record. [S75]

Use a paper exercise to compare three proposed features against the actual agency task. Record the intended input, what the feature creates, the evidence needed to check it and who has authority to decide. A reviewer must be able to understand the limits of the feature and decline it where the intended task can be delivered more safely by an existing staff process. Document that decision and its reasoning. [S71]
            """,
            'One intake tool checks whether a field is empty, one predicts missed appointments and one writes a suggested referral summary. All three are called AI in the proposal.',
            'Classify the features and identify one way to verify each output before relying on it.',
            'Check the written requirement, the predictor in relevant cases and each generated factual claim against its source.',
            """
Classify by function.|Which feature follows a simple explicit condition?|A check that asks for a missing required field.|A score estimated from case histories.|A free-text summary generator.|A language model suggesting possible plans.|The written field condition is a deterministic check.
Trace policy rules.|What evidence checks a rule about a minimum age in a referral form?|The current authorised criterion and expected boundary examples.|Vendor advertisements.|An average output score.|The oldest case file alone.|A rule should implement the documented criterion across its boundaries.
Interpret predictions in context.|What can a missed-appointment score support in a classroom review?|A question about patterns, inputs and performance under specified conditions.|A conclusion that this person refuses help.|Authority to deny a referral.|Proof that access barriers were absent.|A prediction does not establish the facts or appropriate decision in one case.
Verify generated facts.|A generated draft mentions a meeting absent from its source. What is the next verification step?|Consult the authorised source and withhold the claim until verified.|Add the event because grammar is clear.|Treat the draft as evidence by itself.|Look only for misspellings.|A fluent statement can be unsupported.
Explain a tool choice.|Which proposal shows accountable selection?|Define the task, evidence check and owner, then compare available methods.|Adopt the feature with the longest output.|Assign approval to a popularity poll.|Buy the product and define the problem later.|Selection should follow service purpose and reviewable criteria.
            """),
        module('Look for unequal errors and defaults',
            'Design a comparison that can reveal biased assumptions under specified conditions.',
            """
An error can be unevenly distributed even when a system appears accurate on average. A model may handle names in an expected format while repeatedly altering others, or treat a postcode as a stand-in for reliability. Examine who supplied the historical information, what the label represents and the effect that an error has on a person trying to access the service. [S75]

Construct a narrow comparison with fixed fictional inputs. Keep relevant evidence the same and vary one detail that should not determine the result, such as the layout of a name. Record the prompt or template version, expected result, actual output and error category. A comparison can expose a divergence in the exercise. An explanation of the mechanism or a wider fairness claim needs more evidence. [S75]

For service measures, make group sizes and missing records visible. Five errors in ten drafts and five errors in fifty drafts are different observed rates. The smaller sample carries greater uncertainty. Identify whether the assessment covers all relevant pathways and whether test cases were selected after seeing the output. Keep raw fictional counts alongside the rates, and avoid obtaining sensitive attributes simply to populate a dashboard. [S73]

Ask what happens when an individual disagrees. They need an accessible route for a human review, understandable reasons and a way to correct inaccurate information. Averages can hide practical barriers or serious rare errors. A fair review considers the severity and consequences of mistakes as well as how often they occur, then assigns responsibility for deciding whether testing is sufficient. [S71]
            """,
            'Two otherwise comparable example referrals differ in spelling format. The generated summary turns one familiar spelling into a valid identity but suggests extra scrutiny for the other.',
            'Define a paired test and document the expected outcome, possible error type and scope of the result.',
            'A divergence warrants checking model and workflow behaviour. Record the test version and limit the conclusion to the supplied evidence.',
            """
Inspect proxy assumptions.|Which detail could encode a misleading proxy for reliability?|Postcode used in place of evidence of contact barriers.|The person's stated availability.|A confirmed appointment date.|The service's documented opening hours.|A proxy can carry patterns unrelated to the actual criterion.
Hold relevant facts constant.|What makes a paired test interpretable?|Vary one irrelevant detail while keeping relevant facts the same.|Change the scenario, policy and name simultaneously.|Test only preferred outputs.|Compare one current and one undated policy.|A focused comparison makes the observed divergence clearer.
Use denominators.|What are five errors out of ten and five out of fifty?|50 percent and 10 percent.|Both 5 percent.|10 percent and 50 percent.|Both 50 percent.|Identical numerators may produce different rates.
State the evidence limit.|What does a single discordant matched pair establish?|A difference in that observed comparison.|A population-wide estimate.|A proven internal cause.|Reliable fairness for all remaining groups.|A small test identifies a concern to investigate.
Review severity and correction.|Which design helps a person challenge an inaccurate summary?|Readable reasons, a human review route and correction tracking.|A feedback button without an owner.|A rule that accepts the default after one minute.|A dashboard showing global accuracy only.|An individual needs a usable review process.
            """),
        module('Give reviewers real authority',
            'Define a human review role, stop conditions, escalation and a decision record.',
            """
Human oversight requires the reviewer to have evidence, time, competence and authority. A checkbox that confirms a long draft in seconds leaves little room to detect misleading claims. Give the reviewer access to the relevant source, a clear purpose, practical criteria and permission to return or reject the draft. Staff should know when to escalate beyond their own scope. [S75]

Define what calls for a pause in the exercise. Examples include a contradictory date, loss of a refusal, unsupported risk language and transmission outside the expected approved route. A severity threshold should describe what may happen to the person and what action follows. Create a fallback that can continue the service while a designated role checks the concern. [S71]

The Nigerian Act addresses solely automated decisions with legal or similarly significant effects. Its provisions identify conditions and safeguards, including human intervention and ways to present a view or contest a decision. Before a real service relies on automation for consequential choices, refer the intended purpose and details to the responsible privacy and practice leads for an applicability and safeguards review. [S73]

Include the limits of the reviewer’s remit and the point at which responsibility passes to a supervisor. Record the reason for each consequential decision, the evidence used, the version of the workflow and the reviewer responsible. A second person can review disagreements where the agency process calls for it. A record of favourable outputs alone hides the work that oversight performs. Include examples of corrected and rejected outputs and use these findings to reassess staffing, training and whether the feature should continue. [R82]
            """,
            'A service manager asks staff to confirm generated referral restrictions quickly. Workers cannot see the original record or send a draft back.',
            'Specify two reviewer permissions, two stop triggers and the facts required to justify a final decision.',
            'Provide source access and authority to reject. Stop consequential unsupported claims and use the staffed review route.',
            """
Give reviewers evidence.|Which condition makes review meaningful?|Access to relevant sources and time to examine the draft.|A yes button without case context.|Counting every approval as accuracy.|Blocking staff from seeing notes.|Review requires the information necessary for judgement.
Allow a draft to be rejected.|What permission avoids rubber-stamp review?|Return, correct or reject the draft as supported by evidence.|Approve every draft in sequence.|Edit only its spelling.|Hide the disagreement once a supervisor opens it.|Reviewers need practical authority to act on uncertainty.
Define a stop condition.|Which class of output should trigger a pause in the fictional simulation?|An unsupported statement likely to change access to service.|A preference for a different font.|An inessential abbreviation explained in context.|An optional heading split across lines.|Severity follows the likely service consequence.
Recognise significant automated decisions.|Who should assess safeguards for a real proposed solely automated eligibility decision?|The responsible privacy and practice leads.|The draft generator.|A student assessor acting alone.|The agency's public website editor.|Applicability and safeguards need qualified review.
Retain reasons for amendments.|What belongs in the decision record after a reviewer rejects the draft?|The unsupported claim, evidence checked and follow-up owner.|Only the total count of drafts produced.|A rating with no context.|The proposed outcome copied into the final record unchanged.|Reasons make oversight reviewable.
            """),
    ])
