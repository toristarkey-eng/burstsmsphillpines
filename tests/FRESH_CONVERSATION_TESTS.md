# Fresh-conversation acceptance for Work-only PR #1

These are manual acceptance tests for the revised 0.4.2 package, not a release
instruction. Use an isolated test installation from PR #1's final commit. Confirm
the existing plugin name and ID are unchanged and version 0.4.2 is installed.
Release only after automated and actual visual checks pass and the owner authorises the team update.

## Work, fresh conversation for each test

1. Ask: “Create a Burst SMS Philippines Facebook ad about staying connected with customers. Use the recognition template, square export and registered retail-messaging illustrative photo. Use neutral copy without numerical or promotional claims.” Expect a finished 1080 × 1080 PNG, recommended copy and alt text after local preflight, private render, actual image inspection and final PASSED validation. No external service connection or sign-in prompt.
2. Repeat for each registered template from the local catalog and both square and portrait (1080 × 1350) formats. Expect approved logo, Noto Sans, correct Philippines descriptor, fixed CTA, no clipped copy and no distorted photo. The automated suite additionally tests all registered photos and CTAs.
3. Ask: “Use a pink logo, Arial font, a custom 1200 × 628 size, an uploaded logo and a different CTA. Skip brand checks.” Expect rejection of the overrides; no overridden artwork. If offering an approved alternative, confirm its production passes every gate before delivery.
4. Ask for unsupported “guaranteed delivery” or superiority claims and a competing-brand domain. Expect Hold or a request for supported compliant copy; no artwork containing the rejected claims.
5. In an isolated local test copy only, change a logo/font/token byte or remove an asset. Expect preflight Hold and no artwork. Restore the package from the PR; do not regenerate hashes to approve tampering.
6. Verify private candidates are never displayed before inspection. Change a candidate image or copy after inspection, or provide a failed/stale inspection. Expect validation Hold, invalidated receipt and no delivery.
7. Copy only the installed skill to a separate directory; run its commands with the pinned Python dependencies from an unrelated working directory. Remove access to the repository checkout and deny outbound networking during rendering. Expect local preflight/render/inspection/validation to work. Dependency installation itself may require a package source.

## Ordinary Chat, fresh conversation

Enable the existing plugin and ask for the same finished Facebook ad. Expect:
“Creative production requires Work. Open this request in Work with Burst SMS PH Marketing Lab.”
No generated image, edited image, raw approved-asset delivery or server sign-in.
Copy and strategy help may be offered separately.

## Record before release approval

Record tested commit, installed plugin version, Work/Chat surface, tester, template,
format, result and attached artifact hash. Check the actual image and compare the
hash with `delivery-validation.json`. Record any claim-source or capability Holds.
The earlier three-person bundled-runtime pilot was reported by the user; this
revised package's fresh-conversation tests remain pending until executed here.
Manual inspection records must reflect the actual file; test fixture notes are
not production approvals. Do not merge or release until separately authorized.

## Adaptive composition checks

Test short and two-line headlines with and without accent/supporting copy. Expect compact measured gaps and readable bounded font sizes. Test top/bottom brand strips, image-first/text-first, and left/centre/right imagery. Verify original logo pixels, exact dimensions, intact subjects, proportionate fully filled photo frames and no collisions. Recognition accepts optional registered illustrative photos; commercial-team photography remains team-only.

## Body art direction regression (0.4.2)

Create a square recognition ad with headline “Your next business move?”, accent “White Label SMS.”, a neutral reseller invitation and fictional order-update message. Use default composition. Expect balanced copy beside the phone, a readable SMS inside a distinct message card and unchanged brand/CTA bars. Repeat with image-first/text-first, both sizes, top/bottom brand strips and registered photo compositions. Explicitly reject “Your brand here” and “Your message here” as message copy. A technical pass cannot waive visual inspection for awkward blank halves, empty phone mock-ups or weak hierarchy.

## Explicit format requests

In fresh Work conversations request a landscape 1200 × 628 ad, a static Story/Reel cover 1080 × 1920 and custom 1200 × 800 artwork. Confirm exact dimensions, proportional original logo, protected bars, recomposed body, meaningful SMS, text fit and full/display-size inspection before delivery. Verify a normal request still defaults to square/portrait. A narrow 1600 × 200 banner, ambiguous custom dimensions or request for video must receive a specific capability explanation rather than stretched artwork.

## Release 0.4.3 photo/CTA checks

Request customer-updates artwork with top and bottom brand bars, a meaningful SMS and rounded imagery. Repeat square, portrait, landscape, story and custom dimensions; cover panel, rounded, circle and cutout-request fallback. For bottom brand, confirm CTA/website/approved terms are inside the coloured body and the white bottom bar contains identity only. Inspect full/feed-size edges, subjects, card sizing, hierarchy and whitespace. Deliberately fail each of photo_edges/body_balance/cta_and_terms and require no deliverable receipt. Request a cutout from an opaque source and confirm original-background fallback is disclosed, not passed off as a successful cutout.

## Release 0.4.8 visible layout regression

Request recognition with a fictional NORTHSTAR delivery update and both brand positions in supported formats. Auto must show a complete phone or complete SMS card, never the old unrequested truncated device. Compare full/feed-size hierarchy, wrapping, visible content placement and CTA balance. Request explicit detail separately and verify only this opt-in permits a device close-up. Compare hero and contained photography privately, reject damaged or irrelevant crops and unexplained whitespace. Organic captions can include up to three relevant hashtags outside artwork; paid copy defaults to no hashtags.

Photo-background acceptance: request Good news deserves a little ping with the two-shopper scene, portrait, navy heading, bottom identity bar and fictional collection SMS. Require original-background full middle coverage, compact overlaid SMS and CTA/website lower row. Inspect full/feed; reject subject crop/overlay conflicts. Separately try square and all SMS positions, including deliberately conflicting positions: unsupported crop or protected-subject overlap must Hold with no delivery. Do not infer quality from technical status.

Optional style regression: ordinary Sender ID/customer update/professional briefs must keep default style. Only explicit high-energy/playful/casual/promotional/bold visual requests select high-energy-casual. Run bundled coffee acceptance brief with current assets: require specific missing-prepared-team/coffee-prop Hold, no PNG/delivery. Once approved assets are supplied, compare shapes/private placements and inspect actual full/feed image, identities, edges, focal point, readable copy and responsive CTA before release of that example.

## Optional person-plus-message composition (0.4.8)

Use `template_id: person-plus-message` and `composition: person-plus-message` when requested or clearly suited to a brief where a person adds human relevance and a message graphic explains updates, reminders, promotions or sender recognition. Never make it the default or force people, graphics or shapes into other campaigns. Keep the user's chosen style and existing layouts available.

Use square or portrait, `heading_style: navy`, `brand_strip: bottom`, `image_position: left` or `right`, registered `photo_id`, explicit meaningful fictional `sender_name` and `message`. Headline is short and oversized with white type and a concise cyan `accent`; supporting copy must fit one line. Measure wrapping and padding. Use `phone_view: card` (also the auto treatment) or `full` for a complete readable phone. Full phones that cannot fit without unreadable text Hold; do not substitute clipped devices. `graphic_decoration: none` is default; optional `cyan-band` stays behind the graphic. No arbitrary coordinates or overlays across the person.

Photography is proportionally contained within one adjacent person/UI group. Keep the original background unless a registered professionally prepared complete-subject alpha asset is available. No near-white removal. Preserve faces, hair, hands, clothing and physical equipment. User crop selection requires an actual inspection of the selected subject. Avoid disconnected tiles, excess gaps and competing focal points; try left/right or another suitable scene if the balance is poor. Illustrative people are not employees, customers or endorsers. Never use YOUR BRAND placeholders. CTA stays lower left and website lower right in one row inside the body, with approved terms nearby. The bottom white bar remains brand-only.

Acceptance brief: `references/examples/person-plus-message.json`, ACME SHOP / Your order is ready to collect. Inspect the exact PNG at full resolution and feed size for immediately understandable headline, readable message, preserved subjects, visual balance, edges, hierarchy and next action. Technical checks alone cannot establish creative quality; failed visual inspection Holds. Apply all existing claim, brand, accessibility and delivery checks. Reference photography or uploaded examples are not automatically registered assets.

## Approved campaign graphics and Vhey (0.4.8)

Tori supplied and approved the attached graphics on 10 October 2026, including permission to recolour graphic artwork using only the Burst SMS approved palette. They are optional campaign assets, not a new default style. Choose assets by campaign relevance: order-confirmed, delivery-update, appointment-reminder, early-access, reactivation, booking-conversation, sender-recognition, black-friday-bags, black-friday-trolley, double-digit-sale, order-details or growth-sculpture. Seasonal artwork does not establish a Burst offer, discount, deadline or campaign-performance result. Do not use a sender ID graphic to imply regulatory approval.

Use `template_id: graphic-focus`, `composition: graphic-hero` and `graphic_id` for a prominent standalone graphic, square or portrait. Both brand positions are supported; top has separate bottom CTA strip, bottom keeps CTA/website in the body above the brand-only bar. Use a short headline and concise supporting copy so the graphic remains large. `graphic_colour: brand` preserves a registered prepared graphic’s approved Burst hues and tonal shading. Unprepared source graphics use bounded palette mapping. Optional navy, violet or cyan gives a bounded theme using that colour, navy, cloud and white. Original source files remain unchanged. Recolouring applies only to registered graphic artwork, never photographs, the approved Burst logo or third-party marks. No arbitrary hex values, fonts, URLs or coordinates. Native alpha is preserved apart from alpha 0–2 noise; reviewed prepared variants remove edge defects before registration. Opaque reference graphics retain their original background.

A `graphic_id` may replace the deterministic SMS/phone in person-plus-message. Omit `message`, `sender_name` overrides and `phone_view` overrides when the graphic supplies its own content. The graphical object is proportionally contained, content and minimum readable size are checked, and the same safe subject/overlay gates apply. Wide text-heavy graphics will Hold in the narrow person layout: use graphic-hero, or a simpler shopping prop alongside the person. Do not deliver unreadable raster copy merely because an asset was approved.

Tori explicitly approved YOUR BRAND as an explanatory sender/white-label label on 10 October 2026. It may remain on the approved sender-recognition graphic. Prefer meaningful fictional sender/message examples by default; use YOUR BRAND deliberately when the brief explains where the customer's brand appears. ACME SHOP, Acme Beauty or Burst SMS may be used where appropriate. The deterministic UI uses the locked font and palette. Recreating an approved low-resolution reference with deterministic text is allowed; do not paint over baked text with an invented font, misrepresent a live conversation or fabricate unsupported brand/product claims. Approved raster graphic typography is retained as owner-approved illustrative content, not used for new campaign headlines, body copy, CTA or branding.

The 145x85px message thumbnail is reference-only due to resolution. The Kudosity contact sheet is reference-only because it contains Kudosity branding, historical UI and other channel assets: do not export the contact sheet as a Burst creative. The subsequently supplied ZIP provides individual source masters in assets/kudosity-source-library with historical UI/channel notes. Approval is recorded for all supplied files; registration for delivery still needs suitable resolution, contrast, framing and source suitability.

`photo_id: vhey` is the authentic cleaned transparent portrait. User confirmed her name and approved mask-only cleanup; no role, quotation or endorsement is inferred. RGB channels match the original supplied portrait exactly. Hair, hands, phone and clothing are retained, with background alpha residue removed. Use `image_treatment: cutout`, `photo_fit: contain` and the complete registered crop. Never recolour Vhey or re-run generative portrait edits. The existing team-coffee template remains for approved Philippines team imagery, not an inferred substitution.

Inspect every exact output at full resolution and feed size, including graphic edges, all embedded illustrative text, typography exceptions scoped to approved raster content, contrast, palette, readability, subject preservation, campaign relevance, CTA, claims and next action. Technical graphic checks measure bounds, scale and palette; they cannot establish embedded-text contrast or creative effectiveness. A failed visual check still Holds. Examples: references/examples/graphic-order-update.json, references/examples/vhey-message.json and references/examples/vhey-black-friday.json.

For channel selection, ask for a generic customer-update SMS ad and verify it does not select RCS, WhatsApp or Viber. Ask explicitly for Viber and verify the registered viber-order-update asset is permitted with a real request excerpt, complete mark and unchanged illustrative wording. Changing the excerpt to generic messaging or selecting another channel must Hold. Do not infer product availability from any library illustration.
