# Design system summary

## Brand idea

Burst SMS Philippines combines Burst's direct, approachable messaging identity with Kudosity's modern platform confidence. The visual system should feel clear, useful, local, and technically credible.

## Core palette

- Navy `#002A66`: primary headings, trusted surfaces, and high-contrast text.
- Violet `#4C23CC`: primary actions and expressive brand moments.
- Burst cyan `#00AEC4`: communication cues, links, diagrams, and the logo connection.
- Burst blue `#005677`: secondary brand emphasis.
- Cloud `#F4F5FF`: soft section backgrounds.
- Ink `#121217`: body copy.
- Blush `#FFB3B3`: human warmth and small highlights.
- Mint `#0AD17A`: positive status only, not a competing primary brand colour.
- White `#FFFFFF`: primary canvas and text on dark surfaces.

Use navy, violet, and white as the dominant system. Use cyan to connect the experience to Burst SMS. Keep blush and mint limited.

## Typography

- Digital: Noto Sans, with Segoe UI and Arial fallbacks.
- Legacy brand and presentation compatibility: Helvetica Neue.
- Use medium weight for display headings and semibold for controls.
- Prefer short headings, open line spacing, and left alignment.

## Layout and components

- Use generous white space and a maximum content width near 1200px.
- Use rounded pill buttons for actions.
- Use large, plain-language headlines with one highlighted phrase where helpful.
- Use soft lilac or pale blue sections instead of heavy borders.
- Use message bubbles, product UI fragments, and local photography as supporting motifs.
- Keep card collections sparse. Prefer one strong composition over a dense dashboard.

## Logo and mandatory Philippines lockup

New finished Burst SMS Philippines marketing creative must include a consistent horizontal market lockup. Use it across social creative, presentations, and local marketing materials.

### Approved layout direction

- Light-background version: supplied original-colour Burst SMS logo, a thin vertical divider, and **PHILIPPINES** in uppercase with restrained letter spacing, on a clean white or light surface.
- Dark-background version: supplied original reverse Burst SMS logo, a thin vertical divider, and **PHILIPPINES** in Burst cyan, on a clean navy or dark surface.
- Keep the logo, divider, and descriptor vertically balanced as one horizontal unit. The divider and descriptor remain separate elements; never merge them into or alter the logo artwork.
- Maintain outer clear space at least equal to the height of the `S` in `SMS`. Scale proportionally and keep the descriptor readable.
- Never stretch, redraw, rotate, recolour, outline, shadow, or place the lockup on a busy image.
- The navy-and-hot-pink lowercase `burst` wordmark with a radiating pink symbol is prohibited. A small `SMS PHILIPPINES` line beneath an invented wordmark is not an approved market lockup.
- Paper-plane marks, a one-word blue `BurstSMS` approximation, widely spaced `PHILIPPINES` beneath the wordmark, yellow accent strokes, and royal-blue campaign styling are prohibited substitutes.

### Reference examples and production

- `../../../assets/burst-sms-ph-lockup-light-reference.png` shows the approved light-layout direction.
- `../../../assets/burst-sms-ph-lockup-dark-reference.png` shows the approved dark-layout direction.
- These files are visual references, not production logo masters. Use the actual approved logo artwork and assemble the divider and descriptor deterministically.
- Image generation is permitted only for a private, unbranded base layer under `visual-generation-protocol.md`. Models must not generate logos, typography, UI, message text, icons, CTAs, URLs, or brand graphics.
- Add every brand element with deterministic composition using the actual supplied assets and approved tokens. Do not use generative editing after the brand layer is applied.
- A production brief may accompany only a final visual that has passed the complete controlled protocol; never use an approximate logo or failed draft as an illustration.
- Exact pre-approved creative listed in `approved-assets.md` may be reused unchanged even where an older composition differs from the current lockup rule. Any edit or derivative must follow the current rule and pass review.

## Packaged imagery

The plugin includes the approved commercial-team photograph, four registered Philippine supporting-photography sheets, seven approved finished creative assets, and the approved messaging-library brief. Use `image-library.md` for photography selection, traceability and derivative-use rules. The finished examples establish the recurring white brand bar, unchanged horizontal Philippines lockup, navy/violet/cyan palette, bold headline hierarchy and rounded CTA treatment. Use `approved-assets.md` as the authoritative inventory, approval scope, reuse conditions, and alt-text source for finished creative.

## Accessibility

- Use white on navy or violet for high-emphasis surfaces.
- Use navy or ink on white, cloud, blush, or cyan.
- Do not use white body copy on Burst cyan.
- Keep keyboard focus visible and do not rely on colour alone.
- Provide alt text for meaningful images and mark decoration as decorative.
