# Merging duplicates

Applies when several portable diagrams go into one model. Each diagram declares its own copies of shared elements; the
model must hold each once.

## Ask once, before merging

Ask the user to pick one mode, then follow it for the whole migration:

1. **Confirm each**: ask about every suspected match before merging it.
2. **Decide and report**: merge on your own judgment, list every merge and every kept-separate decision in the final
   report.

## Identify matches

Treat two elements as the same entity when they share the same kind level (system, container, component) and one of:

- identical `alias`;
- identical label (case-insensitive, trimmed);
- same label and same technology.

Same label at different levels (a system and a container named alike) is not a match. Elements inside differently named
boundaries are not matches unless the user says so.

## Differing attributes

When matched elements differ in description, technology or properties:

- *Confirm each*: show both and ask which value wins, or whether they are different elements.
- *Decide and report*: keep the fuller description, union the properties, keep the more specific technology, and record
  the choice in the report.

Merged relationships with the same ends and label become one; with different labels, keep both.
