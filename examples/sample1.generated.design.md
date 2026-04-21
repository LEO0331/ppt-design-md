# DESIGN.md

## Design Intent
Use this guide to create new slides that preserve the source deck's visual language. Favor consistency in hierarchy, spacing, and composition over exact pixel replication.

## Canvas
- Slide size: 13.333in x 7.5in
- Aspect ratio: 1.778
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
- Left margins (in): 0.79, 12.65, 8.14, 0.42, 4.32, 5.47
- Right margins (in): 0.0, 0.78, 5.99, 0.44, 1.46, 4.33
- Top offsets (in): 6.81, 1.11, 0.54, 2.56, 3.26, 2.01
- Vertical gaps (in): 0.94, 0.11, 1.47
- Column gaps (in): 0.8, 0.23, 3.65
- Alignment anchors (in): 0.79, 12.65, 8.14, 0.42, 4.32, 5.47

## Shapes and Components
- footer note: signature `text:10x10`, occurrences=11, confidence=0.84
- footer note: signature `text:90x10`, occurrences=4, confidence=0.57
- title block: signature `text:40x40`, occurrences=3, confidence=0.54
- title block: signature `text:30x40`, occurrences=3, confidence=0.54
- Charts/SmartArt/grouped objects: treat as visual blocks in MVP; preserve container placement and proportion.

## Layout Archetypes
- Dominant layouts: section divider (slides: 2,4,5,9,10), cover slide (slides: 1,3,6,12), title + body (slides: 7,11), title + two-column (slides: 8)
- Common alignments: flush-right, centered, flush-left

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
- Limited explicit colors found; theme inheritance may be partial.
- Diagnostic scores: {'typography': 0.0, 'layout': 0.62, 'components': 1.0, 'color': 0.0, 'coverage': 0.81, 'overall': 0.48}
- Evidence counts: {'slides': 13, 'elements': 42, 'text_elements': 37, 'color_tokens': 0, 'layout_clusters': 4, 'component_candidates': 4}
