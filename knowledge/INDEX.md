# Knowledge index — allowed question classes

The agent answers from this knowledge base only when the question matches an allowed class.
Anything outside these classes goes to the normal gate path (answer / review / no action) —
never invented from the docs.

| Class | Example questions | Docs |
|---|---|---|
| plant-care | yellow leaves, spots after rain, pruning timing, light | `yellow-tomato-leaves`, `watering-schedule` |
| watering | how often, hard water, monsoon changes, succulents | `watering-schedule` |
| pests | mealybugs, aphids, fungus gnats, treatment | `neem-oil-buying`, `yellow-tomato-leaves` |
| buying-local | where to buy neem oil, fair prices, nurseries | `neem-oil-buying` |

How it works:
1. `classify` asks Jev whether the message is a genuine question (question_shape).
2. If yes, the agent retrieves the top passages from this base (FTS5).
3. A **nested Jev call** asks: is this an internal-knowledge question, and is it answerable from these passages?
4. Only if answerable: the `draft` state composes a reply using **only the cited passages**; otherwise it escalates.
