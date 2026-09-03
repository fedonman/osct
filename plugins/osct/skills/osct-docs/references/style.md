# House writing style

These rules apply to every prose surface in the repo: the documentation site,
the README, and docstrings. They exist so that the documentation reads as one
voice and so that a reader can trust what it says.

The project's own vocabulary, surfaces, and checklist live in
`.osct/docs/project.md`. This file is the part that does not change between
repos.

## Voice

Write as an experienced engineer explaining something to a colleague who is
competent but new to this codebase. Professional, direct, grounded. Accuracy and
readability come before personality and polish.

Say what a thing does, why it exists, and when to use it. Resist the urge to say
that it is good. If a design has a real advantage, name the alternative and the
trade-off; a reader can judge from that. If it has a limitation, say so in the
same paragraph rather than hiding it in a later section.

Assume the reader is reading in order and does not need to be sold on continuing.
No introductions that restate the title, no conclusions that restate the body, no
transitions that announce what the next paragraph will do.

## Punctuation

Do not use em dashes or en dashes as sentence punctuation. Use a comma for an
aside, parentheses for a genuine parenthetical, a colon to introduce, a semicolon
to join two related clauses, or two sentences. Hyphens in compound adjectives
(`real-time`, `host-side`, `bus-scoped`) are unaffected.

Use contractions only where the surrounding text already does. Documentation
sites mostly avoid them; READMEs use them more freely.

## Sentences and paragraphs

Vary sentence length, but keep every sentence easy to follow on one pass. Prefer
plain words to formal ones: "use" rather than "utilise", "many" rather than "a
plethora of", "look at" rather than "delve into".

Prefer connected paragraphs to fragmented sections. A paragraph can hold a chain
of reasoning; a bullet list cannot, because it strips the connective tissue that
explains why one point follows from another.

Use a bulleted list when the content is a genuine enumeration: parameters,
options, requirements, independent items that have no order. Use a numbered list
only when the order of the steps matters. A run of more than a dozen bullets is
almost always a paragraph that was chopped up, or a table.

## Headings

Sentence case, not Title Case. "Adding a new operation", not "Adding A New
Operation". Identifiers keep their own casing, and a heading may be nothing but
an identifier: `## sweep(variable, source)` is fine.

Headings are functional labels for navigation, not titles. Keep them short and
descriptive. Do not skip levels. Do not add a heading for four sentences of text,
and do not stack a section heading directly on top of a subsection heading with
nothing in between.

## Claims

Do not write that something is better, easier, faster, or more efficient unless
the sentence also says what it is being compared with. "Faster than resolving the
waveform at each call site" is a claim a reader can check. "Faster" alone is not.

Do not describe the library's own design with praise words. The reader is looking
at it; they will form their own view.

## Vocabulary to avoid

These read as generated text. The checker flags them.

| Avoid | Instead |
|---|---|
| honestly, simply, just works | say the thing directly, or say what makes it simple |
| powerful, robust, seamless, effortless | say what it does or what it tolerates |
| unlock, supercharge, revolutionise, game-changing | say what becomes possible |
| leverage, utilise | use |
| delve into, dive into, let's explore, embark | start explaining |
| at its core, it is worth noting, a testament to | delete the phrase, keep the fact |
| in today's world, whether you are a beginner or an expert | delete the sentence |
| crucial, vital, cutting-edge, state-of-the-art | say why it matters, concretely |
| plethora, myriad | many |
| in conclusion, to sum up, that's all there is to it | stop writing |

The list is not exhaustive. The test is whether a sentence carries information or
only enthusiasm.

## Terminology

Use the codebase's own words, exactly, and do not invent synonyms for them. The
vocabulary is load-bearing: the docs, the error messages, and the diagnostics all
have to agree, or a reader cannot connect a message to the page that explains it.

Which words those are is per project, and the ones that matter are written down
in `.osct/docs/project.md`. Read that section before writing prose, and add to it
when a rename lands.

## Mechanics

Wrap prose near 80 columns and let the checker warn above 88. Tables and long
links are exempt, since breaking them hurts more than it helps.

Fence every code block with its language: `python` for Python, `bash` for shell,
`toml` for configuration. Leave the fence bare for terminal output and for the
project's own DSL, which the checker parses with the real parser when the fence
opens with the header named in `.osct/docs/config.toml`.

Link between pages with relative paths that include the `.md` extension. Anchors
are slugified headings; anchors generated by an API renderer are produced at
build time and the checker knows not to chase them.

Prose spelling is US English throughout (`behavior`, `flavor`, `serialize`),
matching the identifiers the code already uses. Do not introduce British forms.

## The revision pass

Reread what you wrote before handing it over, and cut:

- sentences that could appear in any project's documentation
- adjectives that describe quality rather than behavior
- repetition across the introduction, the body, and the summary
- headings introducing sections too short to need one
- bullets that were sentences in a paragraph before they were chopped up

This pass is part of writing, not an optional polish step. The result should read
as though a human engineer wrote it and a second one reviewed it.
