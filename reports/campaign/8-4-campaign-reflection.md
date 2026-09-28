# 8-4 campaign reflection

The first three live attempts had identical 537-decision failures at x2391. Against the historical r82 winner, the first differing action was decision396 at x2191, feet154, rising: winner waited, campaign jumped. The original request carried second-section-plant timer2 and said to wait below90, but selected jump with probability0.533.

A broad timer-only projection candidate (8-4-r01) correctly answered all20 boundary/motion probes across four replicas, but was never installed in the live override. Closer inspection showed the historical winning trajectory did not obey the full wait90 rule: several later low-confidence choices jumped or ran before90. Changing the whole timer behavior therefore would not preserve the historical path.

Candidate8-4-r02 adds a narrow x2190..2193 note in the castle room, projecting only motion. It asks DJev to release buttons while rising, otherwise run. A live API-only probe selectedwait for rising (0.714) andrun for falling (0.991). This candidate was installed for the next natural retry only. At installation, attempt5 was already atx3277 using the untouched historical profile, so any success in that attempt must not be attributed to r02. No worker restart or action override was used.

Probe outputs are reports/campaign/8-4-r01-request-probe.json and8-4-r02-request-probe.json. These API probes are not gameplay trials and receive no campaign clear credit.

Final result: attempt 5 cleared at x4805 after 1262 decisions using the original r82 profile. r01 and r02 were not used for the winning attempt. No further attempts were launched after the final axe flag.
