# Change requests (meeting 9.10.2026) – status

Source: `change-requests.pdf`. Commits are on branch `minor_adjustments` (not pushed).

Background: MONDEY works in 14-day observation rounds (answer sessions), not with a separate
dated answer per milestone. When a round starts, every age-relevant milestone is unanswered
(milestones already answered "Zuverlässig" are left out). Feedback is only calculated for
completed rounds, i.e. once every milestone in the round has been answered. After 14 days a
round expires and the next one starts from blank (`session_lifetime_days` in
`mondey_backend/src/mondey_backend/routers/utils.py`). Several requests assume answers
persist per milestone and go out of date after 3 weeks, which doesn't happen in this model.

## Done

| Request | Commit | Notes |
| --- | --- | --- |
| Beobachtungshinweise always expanded (p4) | `54c53ef` | Open by default on every milestone; opening other items doesn't collapse it |
| No blue border on unanswered milestones, ✓ on the chosen answer (p4) | `96391e0` | The ring was on "Später bewerten" because unanswered = -1 = that button's value. Also adds `aria-pressed` |
| Banner on the homepage (p7): neutral colour | `d9c6313` | Grey instead of red. **The text is not changed yet**, see below |

### Bugs found and fixed along the way

| Bug | Commit |
| --- | --- |
| Feedback rounds sorted as text, so an older round could be shown as "Aktuell" (relevant to p3) | `32cb17f` |
| "Später bewerten" button did nothing (backend rejects -1 since 0d95f01); now skips to the next milestone | `a898778` |
| Printing the report deleted the data of the feedback rounds still on screen (`in` vs `includes`) | `e640ae4` |
| Overall feedback: a single grey group overrode all other results. Now the worst result of the groups that could be evaluated wins; grey only if no group could be evaluated | `4a1ae90` |

## Not done

| Request | Status / how to implement |
| --- | --- |
| Fourth, grey status "Nicht genug Daten für Feedback" (p2) | **Mostly exists already**, but with a different meaning: grey (`-2`) means the *statistics* aren't enough to compare against (fewer than 5 comparison rounds for that group at that age, no spread, or no milestone in the group with a fitted curve). It never means the child's data is missing. Still to do: add a 4th legend entry, use a grey icon at group level (currently a white X), and maybe reword it, e.g. "Noch zu wenige Vergleichsdaten" |
| Rule: show traffic lights only if all milestones were answered within 3 weeks (p2) | **Already true.** Feedback only exists for completed rounds, where every milestone was answered within 14 days. If "3 weeks" matters, set the round length to 21 days |
| "Green although there's no data" (p3) | **Misread.** The screenshot shows the most recent completed round (14-5-2025), labelled "Aktuell". Ideas: show the date instead of "Aktuell", or add a note when the latest round is old. Possible real concern: if few milestones in a group were actually answered, the rest are filled in with the average for that age, which pushes the score towards green. Ask them whether that's what they mean |
| "Letzter Bewertungsstand: bearbeitet vor x Tagen", red if more than 3 weeks, "Noch nicht bewertet" (p4) | **Partly a misunderstanding.** "Noch nicht bewertet" is easy (answer = -1). "Vor x Tagen" needs a new `answered_at` column on `MilestoneAnswer` (with a migration). "Red if more than 3 weeks" can't happen, because answers are reset each round. Alternative: show the previous round's answer and date |
| Filter "Noch nicht bewertet / Nicht mehr aktuell / Noch aktuell" instead of "noch bearbeiten / schon bearbeitet" (p5) | **Partly a misunderstanding.** The current options are "unanswered only" and "show all"; "schon bearbeitet" is a misleading label for "show all". "Nicht mehr aktuell" can't exist in the round model. Possible now: "Noch nicht bewertet / Bewertet / Alle" in `GalleryDisplay.svelte` plus the hint text |
| Disclaimer for a new child (p6) | Text only: new translation key on the child registration page |
| Several observers per child with a shared code (p6) | New feature: a nullable `shared_code` on `Child` (with a migration), a question at registration, code generation, and a way for the second person to enter it. **Decide:** how the code gets to the second person, and how statistics and export treat children that share a code |
| New banner text "Achtung, das ist eine Pilot-Version → … Kontakt ✉" (p7) | Text: edit `frontpage.disclaimerPopup` in the admin translations (no deploy needed). The ✉ link to `/static/kontakt` needs a small change in `frontend/src/routes/+page.svelte` |

## Open questions for them

- Keep the 14-day round model and word the UI around it, possibly with 21-day rounds? Or switch to rolling per-milestone answers? Slides 2, 4 and 5 assume the rolling model, which is a large redesign (statistics, suspicious-round checks, feedback).
- The green overall text says "für sämtliche Meilensteine…". Since groups with not enough data are now left out of the overall result, maybe soften it, e.g. "…für alle auswertbaren Bereiche…".
