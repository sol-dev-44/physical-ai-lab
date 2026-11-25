---
name: spend-research
description: Compare prices across vendors before proposing any purchase or reorder (filament, parts, tools, hardware). Use whenever a recommendation would spend the owner's money - an order list, a reorder, "should I buy", cart links for the UI agent - before naming a store or a product.
---

# Research before spending

The owner asked (2026-11-25) for prices to be researched across companies and sites before any
spending advice. A recommendation that names one store without checking the others is not done.

## Before proposing a purchase

1. **Define the need first:** quantity (from `docs/inventory.md` usage rate and reorder rules),
   the specs that matter (for example 1.75 mm, colour, AMS-safe spool, M3 x 12 button head,
   a datasheet value), and when it must arrive (the build it unblocks).
2. **Compare at least 3 to 5 sources**, including:
   - the maker's own store (bulk or mix-and-match tiers, free-shipping thresholds),
   - Amazon (watch for reseller listings and title mismatches such as "Matte"),
   - competing brands of equal quality, and a budget option, flagged as such.
   For a big or recurring spend (over about $100, or anything reordered monthly), delegate a
   research subagent with a tight brief and run it in the background.
3. **Compare like for like:** price per unit (per kg, per piece) at the quantity actually
   needed, shipping included, plus lead time. Note anything that changes the real cost:
   spool type (cardboard spools shed dust in the AMS), tolerance and reputation, RFID or
   presets, return policy.
4. **Use store pages, not memory.** Prices move; forum and deal posts are leads only. Date
   every price ("on 2026-11-25").

## How to present it

- One table: option, unit price at the real quantity, shipping, lead time, catch.
- A ranked pick in a few lines: the cheapest good option, and the reason to pay more if
  there is one (colour match, fit, time).
- Exact product URLs and the variant (colour code, size) for the owner or their UI agent.
- Record the chosen order and the comparison's headline in `docs/inventory.md`.

## Never

- Never place an order, check out, or add to a cart: the owner does that.
- Never put the owner's personal details into a search or a site.
- Never skip the comparison because a vendor was used before. Last time's store is one row in
  the table, not the answer.
