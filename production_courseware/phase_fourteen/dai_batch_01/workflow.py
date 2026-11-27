def build(course, module):
    return course(88, 'Digital Case Management and Workflow Design',
        'Digital Case\nManagement and\nWorkflow Design',
        'Design and test an invented referral workflow with named decisions, acknowledgements and continuity arrangements.', [
        module('Define case states and accountable handoffs',
            'Specify state changes, accountable roles and a check for lost referrals.',
            """
Describe the real service action behind each proposed status. Received means information has arrived. Accepted means a receiving role has taken responsibility under its process. Scheduled means an appointment is agreed or assigned as specified. Closed needs a reason and an authorised decision. A label with different meanings across offices makes it hard to see who is accountable for the next stage. [S71]

Draw a line for each role from intake to follow-up. At the point where responsibility passes, show what minimum information moves, how the recipient acknowledges it and which worker handles a failure to acknowledge. The sender may need to follow up if a receiving queue is unavailable. Give the person a usable confirmation and avoid promising an outcome the service has yet to deliver. [S71]

Define what happens when there are duplicates, an incomplete referral or a case sent to the wrong team. A worker checks the source records and follows the authorised correction process. A role should be able to return an incomplete record with a reason and next action. Keep enough history to understand the decisions without replicating sensitive information into every handover channel. [S73]

Test the workflow using a small fictional timeline. At 09:00 intake sends a request, at 10:00 the team has not acknowledged it and at 11:00 it is found in the wrong queue. Walk through ownership at each point. Do the same for a confirmed referral and a request that needs clarification. Record observable outcomes that can be compared after a repair. [S76]
            """,
            'The dashboard marks referrals complete as soon as intake sends them. The receiving team never acknowledges one request and the person receives a message implying a booked appointment.',
            'Draw states with a trigger and responsible role for each. Add a timeout, follow-up and accurate confirmation.',
            'A send event belongs before acceptance. Provide accountable follow-up and match the message to the actual service status.',
            """
Define status in terms of action.|Which event supports a status of accepted referral?|An authorised receiving worker acknowledges taking responsibility.|Intake opens a blank form.|The sending screen shows a spinner.|A staff member reads an unrelated message.|Acceptance concerns responsibility at the receiving end.
Assign a handoff owner.|Who should respond to a missing acknowledgement?|The role specified by the handoff procedure.|The service user alone by default.|An unrelated administrator.|A vendor selected from the dashboard.|The process needs a named role before a handoff fails.
Match contact to state.|What should the fictional confirmation say after receipt but before scheduling?|The request arrived, and the next response is pending.|A visit has been booked.|Treatment is completed.|No further checks are required.|A contact should give an accurate understanding of progress.
Handle duplicate records carefully.|What should workers verify before reconciling duplicate referrals?|Identity within authorised records, evidence and the appropriate correction route.|The file with the newest logo.|The shortest record only.|The version most convenient to delete.|Reconciliation needs evidence and reviewable history.
Test a failure path.|Which scenario tests the acknowledgement deadline?|A request reaches a wrong queue and remains unacknowledged.|A worker opens the correct page.|The logo loads successfully.|Two team members share a desk.|A timeout test follows the missing event and its consequences.
            """),
        module('Manage minimum access and version history',
            'Design task-based access, a correction history and an exception route.',
            """
Begin with tasks rather than broad job labels. The person scheduling a meeting needs the safe contact option and availability. A practitioner handling the case may need more context. A service evaluator may need grouped counts and definitions. Document actions each role must complete and which information makes them possible. Challenge convenience requests that expose case narratives beyond a defined function. [S73]

Separate view and change permissions in the workflow design. An intake worker may be authorised to create a request without editing a signed assessment later. A supervisor may approve reassignment while a service desk handles permission requests. Review exceptions through a named process with an expiry or reassessment point when relevant. In your classroom map, simulate who requests access and who reviews it. [S71]

Keep a reliable correction history for meaningful changes. For example, repairing a wrong appointment location should preserve when it was changed, who changed it and whether the person was updated. The new status needs to point staff to the current location. A history is useful where it answers an accountability question, and sensitive text should be limited to what that question requires. [S73]

Test the design using a paper permissions matrix and task cards. Ask whether each role can execute its ordinary tasks, whether a role can see more than required and how staff receive continuity support during an absence. Record one situations-based exception, the responsible approval role and how the exception ends. Revisit permissions when staff transfer or a workflow changes. Check permissions against the actual tasks again. [S71]
            """,
            'An intake assistant can change signed assessments. A temporary covering worker has indefinite access and the calendar silently overwrites appointment locations.',
            'Prepare a three-role access matrix and a correction record for the changed location.',
            'Limit permissions by function, review temporary access and preserve a dated correction with a safe notification.',
            """
Start from the task.|Which information is most directly needed to schedule a fictional follow-up?|Safe contact and availability.|Every historic assessment narrative.|A full export of all closed referrals.|All team financial records.|The purpose guides access scope.
Separate view and edit.|Why might a role view a signed assessment but lack permission to edit it?|Its task requires reference while correction follows a different authorised process.|Read access always confers ownership.|Every viewer should be able to rewrite history.|Signatures determine display colours only.|Viewing and changing records are distinct actions.
End temporary access.|What should accompany an approved temporary coverage grant?|An owner, purpose and expiry or review date.|Unrestricted access until the next software upgrade.|A transferred colleague's password.|No record of the grant.|Temporary need should lead to a reviewable permission decision.
Retain correction provenance.|Which facts help verify the address correction?|Current location, time, responsible worker and notice status.|Only the original wrong location.|Only a screenshot of the home page.|A count of all changed fields with no context.|Relevant change history supports staff and person follow-up.
Test ordinary and exception paths.|How should learners validate a paper permissions matrix?|Run legitimate tasks and an exception through the mapped roles.|Ask the vendor if its template is attractive.|Check only whether supervisors can see all fields.|Avoid testing coverage arrangements.|Both everyday and unusual authorised tasks need a usable route.
            """),
        module('Plan outages and safe reconciliation',
            'Describe continuity, controlled recovery and indicators for follow-up failure.',
            """
Even a well-designed referral system can become unavailable. Decide how staff identify an outage, who coordinates the temporary route and which high-priority services require continuity first. Use the agency's approved fallback and arrange a safe response channel for the person. A continuity procedure helps practitioners explain what is known about delay and how the next update will arrive. [S71]

A fictional outage card can include a unique temporary reference, time, necessary information and the role responsible. Track whether the delayed request received a response and which service actions can safely wait. Give staff an approved way to check the latest outage instruction and agree a review time for requests that cannot wait. The procedure should avoid collecting more information merely because a usual validation step is unavailable. Any real temporary record uses the organisation's authorised storage and handling arrangements. [S73]

Reconciliation brings temporary records and actions into the restored workflow while identifying duplicate arrivals. Compare each temporary reference against the recovered queue and distinguish actions already taken from items still awaiting a response. Record who confirms reconciliation and how a mismatch is escalated. Do not assume that a restored login means every referral was accounted for. [S71]

Measure service continuity using examples of elapsed time, missed acknowledgement and unresolved mismatch. If eighteen of twenty fictional temporary cases reconcile, the remaining two need an owner and review. Record their state separately from the total instead of describing the exercise as complete. Rehearse the sequence and identify what would change after a different kind of interruption. [S76]
            """,
            'Connectivity fails after two intake workers send forms. Twenty temporary records are created. The portal returns, eighteen records reconcile and two have uncertain follow-up.',
            'Describe the temporary route and its return to the normal workflow. Assign responsibility for the unresolved cases.',
            'Trace every temporary reference against the restored queue. Keep the two unresolved records visible with assigned follow-up.',
            """
Activate documented continuity.|Which first choice supports an outage response?|Use the authorised fallback under the named coordinator.|Ask every person to wait without an update.|Spread files across personal accounts.|Create a new permanent route during the outage.|A prepared fallback protects service continuity.
Capture minimum temporary facts.|What belongs on a fictional temporary referral record?|Unique reference, time, essential details and responsible role.|The full case history for every inquiry.|An anonymous count with no way to reconcile.|A personal credential for future access.|A limited record still needs enough information for follow-up.
Check recovery beyond login.|After the portal reopens, what workflow step is required?|Match temporary referrals and actions to restored records.|Assume all cases transferred automatically.|Mark every record closed.|Discard the temporary list before review.|A working interface does not prove that all cases are accounted for.
Keep unresolved cases visible.|What should the team report when eighteen of twenty reconcile?|Eighteen reconciled and two assigned for review.|Twenty confirmed without checks.|The exercise was unusable and has no result.|Two fictional referrals had definitely never arrived.|Accurate status preserves both progress and uncertainty.
Evaluate the continuity route.|Which indicator can reveal a weak fallback?|Elapsed acknowledgement time and unmatched temporary referrals.|Average logo image size.|The number of options in the settings menu.|Count of staff without review tasks.|Timing and reconciliation relate to the continuity objective.
            """),
    ])
