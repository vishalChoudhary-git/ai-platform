# Topic 26 — Lead / Manager & Behaviour Round

**Status:** Added interview questions

## Focus
Technical leadership, ownership, judgment, communication, prioritization, stakeholder management, conflict resolution, mentoring, handling ambiguity, production incidents and learning from difficult AI-system problems.

## Interview outcomes
Demonstrate that you can own difficult AI/engineering problems end-to-end, make sound trade-offs under pressure, communicate clearly with technical and non-technical stakeholders, and improve the system/process after an incident.

---

## 1. Most Difficult AI-System Problem You Faced ⭐

### Primary question
**Tell me about the most difficult problem or production issue you have faced while building an AI/LLM system.**

This is a **manager/behaviour question**, not a deep technical-design question. The interviewer is primarily looking for ownership, judgment, communication, prioritization, resilience and learning.

### Recommended answer structure
Use a concise STAR-style story, but make your **personal ownership** and decision-making explicit.

```text
Situation
  ↓
What made the AI-system problem difficult?
  ↓
Task / Ownership
  ↓
What were YOU responsible for?
  ↓
Actions
  ↓
How did you diagnose, prioritize, communicate and decide?
  ↓
Trade-off
  ↓
What did you choose and what did you intentionally not do?
  ↓
Result
  ↓
Business + technical impact
  ↓
Learning / Prevention
  ↓
What changed afterwards?
```

### What the interviewer is really testing
- Ownership under pressure
- Structured problem solving
- Ability to separate symptoms from root cause
- Prioritization during ambiguity
- Communication with stakeholders
- Ability to make and explain trade-offs
- Handling disagreement or incomplete information
- Accountability rather than blame
- Learning and prevention

### Manager / Behaviour follow-up questions

**Ownership**
1. Why did you take ownership of this problem?
2. What part did you personally own versus the team?
3. How did you make sure the issue did not fall between teams?
4. What would have happened if you had not stepped in?

**Prioritization & Judgment**
5. How did you decide what to fix first?
6. How did you balance immediate mitigation with finding the real root cause?
7. What trade-off did you make?
8. Was there anything you deliberately chose not to fix at that time? Why?
9. How did you make a decision when you did not have complete information?

**Communication & Stakeholders**
10. How did you communicate the problem to your manager or leadership?
11. How did you explain the impact to a non-technical stakeholder?
12. How did you handle pressure from stakeholders who wanted a faster fix?
13. How did you keep stakeholders updated while the issue was still unresolved?

**Conflict & Collaboration**
14. Did anyone disagree with your diagnosis or proposed solution?
15. How did you handle that disagreement?
16. Tell me about a time another team or person blocked your approach. What did you do?
17. How did you make sure the team stayed aligned during the incident?

**Failure & Self-Awareness**
18. Tell me about a time your initial diagnosis was wrong.
19. What mistake did you make during the incident?
20. What would you do differently today?
21. What did the experience teach you about your own working style?

**Prevention & Leadership**
22. What process or engineering change did you introduce afterwards?
23. How did you make sure the same problem would not happen again?
24. Did you document or share the learning with the wider team?
25. What did you change in monitoring, testing, release practices or ownership boundaries?

**Pressure & Ambiguity**
26. How do you handle a high-severity production issue when everyone wants an immediate answer?
27. How do you decide when to escalate?
28. How do you operate when the root cause is still unclear?
29. How do you keep the team productive when the system is unstable?

---

## 2. AI-Specific Difficult-Problem Variations

The primary story can come from areas such as:

- RAG quality unexpectedly degrading in production
- Retrieval returning irrelevant or unauthorized context
- LLM hallucinations despite seemingly correct RAG retrieval
- Sudden latency or token-cost increase
- Model/provider outage or unstable dependency
- Prompt/model change causing a regression
- Vector-search quality changing as the corpus scales
- Agent/tool workflow producing unreliable or unsafe behaviour
- Streaming/conversation-memory failures in production
- Evaluation metrics looking good offline but poor user feedback online

The **follow-up should remain manager/behaviour oriented** unless the interviewer explicitly asks for technical depth. Do not turn every follow-up into another architecture interview.

---

## 3. Strong Answer Signals

A strong answer should contain:

- A real, specific incident rather than a generic example
- Clear personal ownership
- A measurable or observable impact
- A logical sequence of decisions
- At least one meaningful trade-off
- Stakeholder communication
- A mistake, uncertainty or constraint where appropriate
- A concrete lesson and prevention step

Avoid answers that sound like:

> “We had a problem, so we fixed it.”

Instead make the story show **how you thought, communicated and led** through the problem.

---

## 4. One-Minute Practice Prompt

> **Tell me about the most difficult problem you faced in an AI system. What happened, what did you personally own, how did you handle the pressure and stakeholders, what trade-off did you make, and what did you change afterwards?**

Prepare a 60–90 second version first, then be ready for the manager-style follow-ups above.
