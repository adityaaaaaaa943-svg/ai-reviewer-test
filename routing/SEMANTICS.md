# Routing engine semantics

Route planning, delivery time windows, service level measurement and driver
payout for the codzee.io logistics platform.

## Units

These are the contract. A function that returns a different unit than the one
listed here is a bug even if its arithmetic is internally consistent.

| Quantity | Unit | Where |
| --- | --- | --- |
| Distance | metres | every function in `geo` and `planner` |
| Distance, driver-facing | miles | `payout` only, converted at the boundary |
| Duration | minutes | `windows`, `metrics`, `sla` |
| Money | integer pence | `payout` |
| Angles | degrees for inputs and outputs, radians internally | `geo` |

## Conventions

1. **Time windows are half-open.** The start instant is included, the end
   instant is not. Two windows that merely touch do not overlap.
2. **The SLA promise is inclusive.** A delivery arriving exactly on the
   promised minute is on time.
3. **Distance tiers are marginal.** A driver covering 60 miles is paid the
   first 40 at the first rate and the remaining 20 at the second, in the same
   way income tax bands work.
4. **Surge applies to drop pay only.** It does not multiply distance pay or
   bonuses.
5. **The weekly cap applies to the week.** It is not a per-shift limit.
6. **Excluded deliveries leave the denominator.** When a status is excluded
   from an SLA calculation it is removed from both the numerator and the
   denominator, not just the numerator.
7. **Every route returns to the depot.** Route cost includes the final leg
   home.
8. **The planner never silently drops a stop.** A stop that cannot be served
   is returned in `unserved` so it can be assigned to another vehicle or
   deferred.
9. **Money is never lost to rounding.** Amounts that are split must sum back
   to the original.
10. **Statistics are computed on sorted input where the definition requires
    it.** Percentiles in particular are meaningless on unsorted data.

## Known gaps

Traffic and road networks are not modelled; distances are great-circle. Driver
break scheduling is handled upstream. There is no persistence layer yet.
