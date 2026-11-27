def build(course, module):
    return course(84, 'Digital Inclusion, Accessibility and Service Design',
        'Digital Inclusion,\nAccessibility and\nService Design',
        'Map who can complete a digital service journey and design a usable alternative with comparable access.', [
        module('Map barriers through a service journey',
            'Identify two interacting access barriers and propose an observable service requirement.',
            """
A digital service journey begins when someone first tries to find help. Map discovery, initial contact, completion, confirmation and follow-up. At every stage ask what the person needs and what the agency supplies. A successful web form measures only one point in the journey. People who give up while looking for the form may be absent from its records. [S71]

Consider device control, connection reliability, cost, language, time, physical access and support. A shared phone may be usable for browsing but unsuitable for a notification about a sensitive appointment. An intermittent connection can turn a twenty-minute application into repeated work. Describe each restriction in terms of the task it affects and avoid assuming that age or location can stand in for individual preferences. [R81]

Guo and Ogbodo studied experiences in six rural locations across Nigeria and China through focus groups with adults aged 50 or above. Participants raised different material and social barriers. Use the study to suggest what to investigate in a fictional pathway. The recruitment and specific sites limit how far the observations can be generalised, including to other Nigerian communities. [R81]

Turn the barrier into a requirement that a reviewer could observe. If a connection often drops at submission, a practical test could check whether someone can recover a short interrupted application without entering every field again. Also compare what the agency can collect through an assisted route and how the person receives a safe confirmation. State which claim the test supports and what you would still need to learn. [S76]
            """,
            'A referral service uses a long online form and sends a detailed text confirmation. One person borrows a phone, another loses connection at submission and a third never finds the form.',
            'Map the three different points of exclusion. Write two observable improvements and identify people missing from the form counts.',
            'Discovery, completion and follow-up each have separate barriers. Test recovery and a safe confirmation while keeping a staffed route available.',
            """
Map stages beyond submission.|Which stage is missing when the team counts submitted forms only?|Discovery and unsuccessful attempts.|Only completed referrals.|Only staff processing.|Only the confirmation screen.|Submission records begin after some people have already been excluded.
Shared devices affect privacy.|What should staff ask before sending a detailed update to a borrowed phone?|Which channel and timing are safe for the person.|Whether the phone is expensive.|Which handset the agency prefers.|How frequently messages are opened.|Access and confidentiality depend on who can see the communication.
Combine barriers at task level.|What makes an intermittent connection an access barrier during intake?|It may interrupt submission and require re-entry.|It reveals a preference for paper.|It proves low literacy.|It makes referral needs less urgent.|Connectivity becomes relevant through its effect on a service task.
Use qualitative findings in context.|What can the rural focus groups contribute to a local service review?|Questions about affordability, power and preferred contact.|A national exclusion rate.|A causal estimate for all rural sites.|A universal channel rule.|Focus groups illuminate situated experiences.
Requirements can be observed.|Which requirement can be checked in a fictional intake test?|Resume the form after an interrupted submission.|Make the internet fairer.|Increase general awareness.|Improve service culture.|An observable requirement specifies the task and successful behavior.
            """),
        module('Test accessibility in everyday tasks',
            'Apply keyboard, focus, error and authentication checks to a sample service flow.',
            """
Define a short end-to-end task, such as a person finding the referral form, choosing a safe contact channel, correcting an error and receiving confirmation. Record the version, device, assistive setup, expected behaviour and observed result. A blocker can exist after the home page, so run the task through the confirmation stage and include an unsuccessful attempt. [S72]

Use a keyboard to move through controls and confirm that the sequence follows the task. Observe whether the current control is visible, whether a banner covers it and whether buttons have understandable names when read aloud. A visible label helps everyone interpret a field, and the programmatically associated name helps an assistive device identify it. Test without assuming that one browser represents every setup. [S72]

When a person leaves a date blank, a clear error identifies the field, explains the next action and lets the person keep other answers wherever appropriate. Check that the explanation can be discovered through the keyboard and a screen reader. Authentication also needs attention. An accessible method can support a password manager or an equivalent option rather than requiring everyone to solve a memory puzzle. [S72]

Automated checks can flag certain patterns, while a human walkthrough can reveal confusing instructions, dead ends and burden across steps. Review whether contrast, zoom, narrow screen use and readable language let someone complete the whole task. A list of checks is a starting point. Explain the test coverage and remaining uncertainty, especially where involvement of disabled users and expert review would add evidence. [S76]
            """,
            'A fixed banner covers the active field when a keyboard user tabs down. The form highlights an error in red without naming it, and login prevents a password manager from filling fields.',
            'Describe one reproducible acceptance test for each problem. Include an expected result and one scope limit.',
            'Check focus visibility, a clear discoverable error and a usable authentication route. Record the version and environment for any retest.',
            """
Follow the entire service task.|What should an accessibility walkthrough include after choosing the contact channel?|Submission, corrections and confirmation.|Only colour on the home page.|Only page load speed.|A staff dashboard screenshot.|The relevant unit is the complete task.
Keep focused controls visible.|What should a reviewer record when a fixed banner entirely covers the active control?|A keyboard focus obstruction and the step where it occurs.|An authentication mismatch.|A referral authority issue.|A duplicate case record.|A keyboard user needs to identify the active control.
Give usable error feedback.|Which response helps someone correct a blank date?|Name the date field and explain how to correct it.|Make the field border red alone.|Reset the entire form automatically.|Show the error code in the footer only.|People need the location and a recovery path.
Check accessible authentication.|Which change improves a login that requires users to remember a code they already possess in their password manager?|Allow compatible autofill or a usable alternative.|Expand the memory puzzle.|Require the code to be read aloud publicly.|Lock past clipboard users out.|Accessible authentication reduces unnecessary recall barriers.
Report test scope.|What conclusion fits a pass on selected keyboard tests?|The listed tasks passed in the tested configuration.|The service conforms to all WCAG requirements.|All devices give the same result.|Every user can complete the route.|A scoped result describes what was actually tested.
            """),
        module('Design a staffed service alternative',
            'Specify an alternative route, handoff and monitoring plan for comparable access.',
            """
An assisted or in-person option needs a real decision purpose, an owner and enough time to act. A phone number without staffing or a callback commitment can create a second queue with a lower chance of reaching service. Compare the practical conditions and service outcomes of each route. Include hours, language support, privacy, transport and how urgent information is routed. [S71]

Ask how the person wants to be contacted, within the agency's safe options. Provide a choice the person can understand before committing to the route. If a contact may reveal the nature of the referral, agree on a neutral confirmation or another safe approach. Offer approved language and communication support without making a family member the default interpreter for confidential decisions. [S71]

An effective change preserves the person's place in the process when the route changes. Agree what the first worker can pass to the next, who acknowledges the handoff and how the person learns the next step. For example, someone who begins a request by phone should receive an accessible confirmation and know when the receiving team will respond. A route is only as usable as its weakest required step. [S71]

Start evaluation with a small classroom walkthrough using invented profiles. Compare who can start, complete and receive a timely response by route. Record reasons for abandoning or changing channel where the simulation supplies them. Volume and convenience may improve for one group while another loses access. Consider that a preference for face-to-face support may reflect trust and culture as well as material access, and use that insight when interpreting the exercise. [R81]
            """,
            'A portal adds a help number, but nobody answers after midday and callers must make a new online account to keep their place. A confirmation message exposes the referral subject.',
            'Design a staffed fallback. Define an acknowledgement time, safe confirmation and measures that compare routes.',
            'A usable fallback needs staff, continuity of place and a safe channel. Compare completion and response using similar service stages and disclose missing attempts.',
            """
Staff the fallback.|What makes an assisted route operational in this example?|Named staff, hours and monitored response expectations.|A number printed on the form.|A second landing page.|An unassigned inbox.|Availability requires someone to respond.
Provide understandable choices.|Which offer supports a person who prefers an in-person route?|Explain the location, hours and achievable next step.|Require internet registration first in every case.|Assume declining online service means declining help.|Close the alternative after a single call.|People need a practical route to an equivalent service step.
Plan safe confirmation.|The user shares a phone and prefers neutral messages. What response fits?|Agree wording and timing within authorised channels.|Mention the referral category to reduce confusion.|Send the entire application again.|Ask a neighbour to relay the message.|Limited confirmation protects privacy and supports follow-up.
Preserve handoff responsibility.|What makes a channel switch traceable?|A responsible receiving role and recorded acknowledgement.|An automatic status of completed as soon as the case is sent.|A shared spreadsheet link for everyone.|Leaving the person to repeat intake unaided.|The sending and receiving stages have distinct obligations.
Count barriers in each route.|Which comparison helps assess equivalent access?|Completions among comparable attempts with missing attempts described.|The largest raw traffic total.|Number of help links alone.|Average page load across all channels.|The denominator and missing experiences shape interpretation.
            """),
    ])
