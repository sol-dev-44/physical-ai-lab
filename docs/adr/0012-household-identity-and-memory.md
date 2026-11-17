# 0012: Household identity and memory stay in the house

Status: Superseded by [0013](0013-owner-governs-personal-data.md) (2026-11-17). Previously accepted the same day.
Extends [0007](0007-child-privacy.md).

**Context.** exp003 is becoming a household robot: it recognizes each family member and the pets,
speaks to each differently, and remembers things about them and about the house. That needs face
and voice data and personal memories, a child's included. ADR 0007 keeps identifiable child data out
of the repo, the site, the database and public logs, and keeps raw recordings off synced storage.
Recognition and memory only work if the robot keeps some of this data, so where it lives and what
may leave the house has to be fixed before any code is written.

**Decision.**

- **One local store.** Profiles (name, role, style settings), face and voice embeddings, pet
  appearance features, household rules and memories live in one encrypted store on the lab machine
  and the robot, outside the repo. Never in git, the site, Supabase, the event log, cloud-synced
  backups, or any upload to a GPU provider. An encrypted backup to a local drive is allowed.
- **Enrollment.** A parent enrolls each person at home: adults with their own agreement, children
  with a parent's. Enrollment frames and voice clips are turned into embeddings in memory and
  discarded; no enrollment photo or recording is saved. Pets are enrolled the same way.
  Guests are never enrolled.
- **Recognition.** Runs on live frames and audio in memory, which are then dropped, as in exp001.
  Anyone not recognized with confidence is treated as a guest.
- **What reaches the Claude API.** Text only: the person's name and role, their style settings,
  and the few short memories relevant to the moment. Audio, images and embeddings never leave the
  house. Before this is switched on, the owner checks the API's current data-retention terms and
  records the check in exp003's notes. Sending a name to the API does not make it publishable:
  names stay out of everything public, as above and in ADR 0007.
- **Memories.** Short text notes the robot writes after an interaction: a fact, a preference, or a
  one-line summary of what happened. No transcripts, no audio. Each memory belongs to one person.
  - Parents can list, edit and delete any memory, and wipe a person completely, from a screen on the
    lab machine (not the website).
  - "Forget that" by voice deletes the last memory about the person who said it.
  - A child's memories of events expire after 90 days unless a parent pins them.
- **Sharing.** The robot never tells one person what it remembers about another, with one exception:
  parents can review a child's memories. Guests hear nothing personal about the household.
- **Event log.** May record that an interaction happened and the role involved (child, parent,
  pet, guest, unknown). Never a name, embedding or memory text. Published runs show aggregates only.
- **Household rules.** Zones, quiet hours and what each role may ask for are changed only by a parent
  on the lab machine's screen, never by voice alone, because a recording or a good imitation can fool
  voice recognition. The rules are enforced by the safety gate as interlocks, like `ArenaFence`.
- **Privacy mode.** A mic mute and a camera shutter on the robot; the gate sees both, and the robot
  does no recognition while either is engaged. A light shows whenever it is listening.

**Consequences.** Memories have no cloud backup, so losing the machine without a local backup loses
them. On-device recognition is less accurate than cloud services; that is accepted, and failures
fall back to treating the person as a guest. The Claude API is the one place household data leaves
the house, as text including names; if that becomes unacceptable, names can be swapped for role
labels before sending, or conversations with the child can move to a local model. If identity data is ever found in git, the site, the database or an upload,
recognition and memory stop until this ADR is reviewed.
