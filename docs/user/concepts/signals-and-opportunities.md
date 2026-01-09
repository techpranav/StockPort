# Signals & Opportunities

Stockport surfaces candidates in two related forms:

- **Opportunity**: a detected market setup produced by a scanner/strategy.
- **Signal**: an opportunity presented in a user-facing “trade candidate” shape.

In the current UI, the **signal stream is derived from opportunities**.

## Common fields you’ll see

- **Symbol**: instrument identifier
- **Score**: strength ranking (0–100)
- **Confidence**: normalized confidence (0–1 or 0–100 depending on the feed)
- **Source / Strategy**: which strategy produced the candidate
- **Timestamp**: when it was detected
- **Price**: last/entry reference price if provided

## How to interpret the score

Score is a prioritization mechanism:

- Higher score → higher urgency/quality relative to other candidates
- Score is not a guarantee; use **Decide** to validate risk–reward

## Flow through the UI

1. **Discover** visualizes opportunities (radar) and signals (stream)
2. **Decide** focuses on one candidate and shows risk–reward + rationale
3. **Execute** monitors order lifecycle and execution quality
4. **Review** assesses outcomes and learning/decay over time


