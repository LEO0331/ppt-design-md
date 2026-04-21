# DESIGN.md

## Design Intent
Use this guide to create new slides that preserve the source deck's visual language. Favor consistency in hierarchy, spacing, and composition over exact pixel replication.

## Canvas
- Slide size: 10.0in x 7.5in
- Aspect ratio: 1.333
- Coordinate strategy: place major blocks on inferred anchors and preserve margin rhythm.

## Color System
- Candidate palette (ranked): Not enough evidence
- Theme-declared colors: Not enough evidence
- Neutrals: Not enough evidence
- Primary colors: Not enough evidence
- Accent colors: Not enough evidence
- Guidance: use neutrals for backgrounds/body text, primary for structural emphasis, accents sparingly for highlights.

## Typography
- Candidate font families: Not enough evidence
- Theme-declared fonts: Not enough evidence
- Common font sizes (pt): Not enough evidence
- Inferred text roles:
- No strong role evidence found.

## Spacing
- Left margins (in): 0.5, 1.25
- Right margins (in): 0.5, 3.75
- Top offsets (in): 0.3, 0.94
- Vertical gaps (in): Not enough evidence
- Column gaps (in): Not enough evidence
- Alignment anchors (in): 0.5, 1.25

## Shapes and Components
- No repeated component signatures crossed threshold.
- Charts/SmartArt/grouped objects: treat as visual blocks in MVP; preserve container placement and proportion.

## Layout Archetypes
- Dominant layouts: cover slide (slides: 1)
- Common alignments: Not enough evidence

## Composition Rules
- Preserve top-level structure first: title zone, content zone, support zone.
- Keep repeated components at consistent dimensions and anchors.
- Maintain margin and gap rhythm before adjusting decorative shape details.
- Use no more than 1-2 accent colors per slide.

## AI Generation Guidance
- Generate slides by selecting one inferred archetype, then fill with content while preserving spacing and typographic hierarchy.
- If uncertain about theme-inherited values, prefer explicitly observed fonts/colors from this file.
- Avoid introducing new component styles unless required by content.
- When chart details are unknown, emulate chart-like block style and relative placement only.

## Confidence and Gaps
- Font inference is limited because few explicit run-level font declarations were found.
- Color extraction confidence is limited due to sparse explicit color values.
- Layout/archetype confidence is limited because the deck has fewer than 3 slides.
- Low slide count reduces archetype confidence.
- Limited explicit colors found; theme inheritance may be partial.
- No repeating component signatures crossed threshold.
- Diagnostic scores: {'typography': 0.0, 'layout': 1.0, 'components': 0.0, 'color': 0.0, 'coverage': 0.5, 'overall': 0.33}
- Evidence counts: {'slides': 1, 'elements': 2, 'text_elements': 2, 'color_tokens': 0, 'layout_clusters': 1, 'component_candidates': 0}
