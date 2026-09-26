# Knowledge index — allowed question classes

The agent answers from this knowledge base only when the question matches an allowed class.
Anything outside these classes goes to the normal gate path (answer / review / no action) —
never invented from the docs.

| Class | Example questions | Docs |
|---|---|---|
| community-info | what is GDG, GDG Cloud New Delhi, who runs it | `gdg-what-is`, `gdg-cloud-new-delhi` |
| events | how to join, find events, RSVP, event formats, DevFest | `gdg-how-to-join`, `gdg-events`, `gdg-cloud-new-delhi` |
| volunteering | volunteer, speak, propose a talk, organize, GDE | `gdg-volunteer-speaking` |
| conduct | code of conduct, community guidelines, reporting | `gdg-code-of-conduct` |

How it works:
1. `classify` asks Jev whether the message is a genuine question (question_shape).
2. If yes, the agent retrieves the top passages from this base (FTS5).
3. A **nested Jev call** asks: is this an internal-knowledge question, and is it answerable from these passages?
4. Only if answerable: the `draft` state composes a reply using **only the cited passages**; otherwise it escalates.
