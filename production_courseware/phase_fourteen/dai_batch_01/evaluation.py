def build(course, module):
    return course(89, 'Evaluating Digital and AI-Enabled Services',
        'Evaluating Digital\nand AI-Enabled\nServices',
        'Design an evaluation that measures service access, quality, effort and harm and supports a bounded decision.', [
        module('Connect indicators to the service purpose',
            'Define process, outcome and balancing measures for a fictional digital service.',
            """
Begin with the decision the service is trying to improve. A referral team may want eligible requests to receive a timely human response. The number of templates opened measures activity. Referral acknowledgements within a defined period measure a service process. Whether people received useful support is an outcome requiring separate evidence. Define when the clock starts and stops before collecting a count. [S71]

Specify which records belong in the denominator. Suppose forty of fifty acknowledged referrals received a first response, and another twenty attempts were never acknowledged. Forty of fifty describes a later stage. Forty of seventy would describe a broader stage only if the seventy attempts are comparable and completely accounted for. Explain exclusions and use comparable denominators across periods. [S76]

Balance speed with quality, access and workload. In a fictional drafting trial, count the time to review and correct, whether material choices survived editing and how many records triggered escalation. Service users may value clarity and reduced repetition even when staff time is similar. Define what bad outcomes would warrant stopping and who checks for them. [S75]

The English FOI study describes reports of adoption by authorities. Read that as organisational behaviour in a defined setting. An organisation can adopt a tool and still have little evidence about accessibility, quality or outcomes. Use that difference to avoid interpreting dashboards of logins as successful service. Describe what new evidence would answer your actual outcome question and how to obtain it proportionately. An outcome indicator should reflect what people needed from the service. [R83]
            """,
            'A service claims better access after template openings doubled. It reports 40 timely responses among 50 acknowledged referrals and ignores 20 earlier attempts without acknowledgement.',
            'Define activity, timely response, missing attempts and two balancing measures. Give each measure a denominator or observation rule.',
            'Keep the stages distinct. Document the earlier lost attempts, review burden, and the quality and usability of the response.',
            """
Match measures to outcomes.|Which measure most directly captures a timely service process?|First responses within a defined period among eligible attempts.|Total template openings.|Number of staff accounts created.|Total characters generated.|Measures should reflect the defined service step.
Name the denominator.|What does 40 timely responses out of 50 acknowledged referrals describe?|80 percent among acknowledged referrals.|80 percent of all people needing the service.|40 percent of all residents.|A causal effect of AI.|The denominator determines the population the figure describes.
Count the cost of quality.|What would complement a measure of draft production time?|Time to review, correct and approve a usable draft.|Number of draft title formats.|Page background size.|Total device purchases alone.|Preparation and review together determine real work.
Distinguish adoption from outcome.|What question can FOI adoption counts help answer?|How many responding authorities report using the technology.|How many people got better support.|What software caused better equity.|Whether a specific output is accurate.|Reported adoption is a measure of organisational use.
Set a balancing measure.|Which measure could reveal harm hidden by a speed gain?|Material inaccuracies remaining at sign-off.|Number of accounts with a profile photo.|Total folders created.|Number of headings exported.|Balancing measures capture costs or harms elsewhere in the workflow.
            """),
        module('Compare options and explain uncertainty',
            'Interpret a fictional before-and-after comparison and propose a stronger design.',
            """
Decide whether the immediate question is feasibility, user experience, workflow performance or effect on outcomes. A small simulation can show whether staff can operate a prototype and find a named error. It cannot establish that a real service improved. A comparison under similar conditions can estimate differences on the chosen task, with caveats for the sample, timing, conditions and selection of cases. Capture departures from the task protocol. [S75]

Imagine a manual route with thirty timely outcomes among forty attempts and an assisted route with forty-eight among eighty. The counts rise, but the proportions are seventy-five and sixty percent. Compare definitions, complexity and staffing. If the new route started alongside longer opening hours and a new intake policy, a change in rates alone cannot isolate the effect of the drafting feature. [S76]

Try a stronger classroom comparison. Use the same task definitions for both routes, use predetermined sample cases, retain every outcome and ask reviewers to apply clear criteria. If the same worker completes both routes, changing the order across workers can reduce an obvious practice effect. Record when timing starts and stops and define how unresolved cases enter the results. [S75]

The Finnish pilot illustrates why a finding needs its method beside it. Facilitated workshop feedback can help identify usability problems and perceived benefits. The paper describes variation in use, with no structured survey or measured task times at that stage. A classroom plan can build on those questions while specifying consistent observation and capturing service-user experiences through an appropriately reviewed route. [R84]
            """,
            'A manual route has 30 timely responses in 40 attempts. A new route has 48 in 80 after hours and eligibility changed. The report credits AI for the higher number.',
            'Compute the rates and identify confounding changes. Propose a comparable fictional exercise with two predeclared measures.',
            'The rates fall from 75 to 60 percent. Define comparable tasks and account for concurrent changes before making an attribution claim.',
            """
Match design to question.|What can a paper simulation establish most directly?|Whether a defined team can execute the supplied workflow tasks.|The service's population effect over a year.|The prevalence of need across the region.|A universal outcome improvement.|A simulation tests performance within its designed conditions.
Compute comparable rates.|Which timely-response rates match the supplied counts?|75 percent and 60 percent.|40 percent and 80 percent.|60 percent and 75 percent.|Both 75 percent.|Divide the timely responses by all specified attempts in each period.
Identify concurrent influences.|Why does the comparison fail to isolate AI's effect?|Eligibility and opening hours changed in the same period.|Both rates contain percent signs.|The numerator increased.|The comparison used two periods.|Other changes could explain part of the observed difference.
Reduce order effects.|How can the classroom comparison address practice from repeated tasks?|Vary route order with comparable cases and common scoring criteria.|Always run one route second after coaching.|Exclude all corrections from timing.|Change scoring after seeing the results.|Task order can alter performance independently of the route.
Read evidence by design.|Which result fits a facilitated workshop pilot without measured task times?|Reported experiences and issues to test further.|A measured 30 percent saving.|A validated cutoff for all users.|A causal improvement in waiting time.|The feedback method supports perceptions and design questions.
            """),
        module('Monitor incidents and decide what changes',
            'Write a decision supported by defined measures, adverse findings and accountable review.',
            """
Draft a brief monitoring plan before a change begins. Describe the feature version, target task, acceptable performance and what would trigger review. Include an accessible way for staff and people using services to raise concerns. A manager needs an account of beneficial changes and possible harms before deciding whether to continue, modify or pause a feature. [S75]

Distinguish a near miss from a confirmed consequence. If a reviewer corrects a fabricated appointment before signing, the event still offers evidence about the workload and safety of the process. If a person relied on the wrong date, record the actual consequence and response. Use the agency's incident process in real service settings and keep details within the authorised route. [S71]

Summarise counts, denominators and what the test omitted. Check whether one group experienced more failures and whether the pattern is consistent across examples. A serious failure can deserve action even if only one case appears. Consider who participates in a review, who has authority to pause or restore an alternative and where disputed findings will be examined. [S75]

Make a decision that someone can test later. A fictional team might keep a manual route available and revise the draft feature before a follow-up comparison. Tell the receiving team and the people affected how to reach the temporary route. Record the unmet criterion, restoration condition, date and role that will decide whether the evidence is sufficient. Describe any effect on service access and staffing during the pause. Treat adaptation as a documented change to evaluate. [S71]
            """,
            'A trial reports faster drafts. One generated record omitted a refusal that staff caught before sign-off. Another sent an incorrect date that a person relied on.',
            'Classify the events, explain the review action and state a specific decision and return condition.',
            'Both events matter. Record the caught error and the actual consequence. Assign a reviewer and restore the affected route only after agreed checks.',
            """
Define monitoring before release.|What belongs in a plan for the fictional pilot?|Version, measure, stop trigger, reporting route and owner.|A promise that every benefit will appear quickly.|A dashboard with hidden definitions.|A fixed expectation that all drafts pass.|A monitoring plan connects observations to decisions.
Record near misses.|Which event is a documentation near miss in this case?|An omitted refusal corrected before sign-off.|The inaccurate date already used by a person.|A successfully confirmed appointment.|A planned manual route walkthrough.|The error was caught before it had the potential recorded consequence.
Respond to actual effects.|Which response fits the incorrect date a person relied on?|Restore accurate follow-up and route the incident through the authorised process.|Correct the dashboard only.|Ignore the event because average speed improved.|Treat it as a formatting suggestion.|Actual consequences require a service and accountability response.
Consider severity.|Why review a single consequential failure despite a low aggregate rate?|Its impact may be serious and expose a preventable weakness.|Counts are meaningless in every evaluation.|One event establishes the national rate.|It proves every future draft will fail.|Frequency and consequences inform different parts of a decision.
Name restoration conditions.|Which decision can a reviewer reassess later?|Pause the affected feature until a named owner verifies the date and refusal checks.|Make it faster at some stage.|Restart after enough time passes.|Move the incident log away from the team.|Clear criteria and responsibility make a decision actionable.
            """),
    ])
