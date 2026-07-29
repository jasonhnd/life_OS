---
id: monitor
status: optional-template
authoritative: false
runtime_authority: SKILL.md
purpose: Observe an explicit condition over a bounded period.
---

# Monitor

## Useful when

The user wants a change, deadline, result, or external state checked again over
a defined period and the host supports a suitable observation mechanism.

## Skip when

One immediate check is sufficient, no observation source exists, or the request
has no bounded duration or stopping condition.

## Suggested inputs

- observable condition and evidence source;
- cadence, deadline, or stopping condition;
- material-change threshold;
- notification or handoff expectation supported by the host.

## Useful questions

- What exact change counts?
- How often is checking useful and proportionate?
- When must monitoring stop?
- How will an unavailable or stale source be reported?

## Possible output

A bounded monitoring definition, current observation, change notification, or
honest statement that recurring monitoring is unavailable.

## Safety

Do not create an indefinite background process, daemon, or hidden notification
channel. Use only monitoring capabilities the current host actually provides.
