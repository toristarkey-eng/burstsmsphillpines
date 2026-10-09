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
