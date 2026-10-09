# Controlled creative service

The repository includes `creative_service/`, a deterministic compositor and MCP
service. New creative on ChatGPT may use this service only after its actual
registered app is connected. The existence of repository code is not proof that
the tools are available. Never invent a tool, endpoint, app ID or pass result.

## Required sequence when tools are connected

1. Use `list_creative_templates` to retrieve the locked templates, CTA choices,
   registered imagery and formats.
2. Develop a campaign concept and proposed wording using the current messaging
   library. Pass only the permitted copy and selection fields to
   `prepare_creative`. Do not include logo files, font names, styles, colours,
   dimensions, positioning, URLs or arbitrary image sources.
3. The service runs the live brand preflight and private composition. A
   `technical_status: PASSED` candidate is still withheld for human review.
   Report its ID and pending review status. Never attach a private candidate,
   reproduce it using an image model or call a review endpoint on the user's behalf.
4. The publication owner reviews through the separately authenticated review
   site. Approval checks cover copy/claims, exact visual composition, local fit,
   imagery, accessibility and publication authority. The model has no review tool
   and must not ask for, retrieve or use review credentials.
5. Use `get_reviewed_creative` after the owner has reviewed the candidate. Display
   only the PNG returned with `technical_status: PASSED` and
   `publication_status: APPROVED`. Use its exact `channel_copy`, destination,
   alt text and approval record. Do not modify the released image or apply
   generative editing. Changed copy or assets require a new candidate and review.
6. A Hold, pending review, rejected creative or integrity failure never permits
   a replacement render, a generated concept or delivery of a private image.

## While the service is not connected

Use the existing exact-approved-asset workflow. If no approved finished asset
fits, report `Hold: controlled creative service not connected`. Do not claim
that syncing the marketplace deployed the renderer or connected the tools.

## What is enforced

The service restricts production inputs, validates source/font/template hashes,
locks the original logo and brand styles, rejects copy overflow, validates text
contrast and PNG dimensions, and releases only independently signed approvals
bound to the exact campaign, renderer and image hashes. The underlying model can
still ignore instructions outside this service. Do not claim that the host
prevents all unapproved images globally. Test the intended workflow across users.
