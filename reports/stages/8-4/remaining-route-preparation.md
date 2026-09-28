# Remaining 8-4 route: read-only preparation

No fresh gameplay, state patches, or new action probes were used for this route preparation. Source: saved primary disassembly `reports/stages/reference/SMBDIS.ASM`, especially `L_CastleArea6`, `E_CastleArea6`, `L_WaterArea3`, `E_WaterArea3`, `ParseRow0e`, and `ExecGameLoopback`. Area-data headers were byte-matched against the installed unmodified ROM to derive room IDs. Coordinates below are static decoded object positions, not guaranteed exact live collision thresholds.

## Observed vs inferred

- Observed in recorded gameplay: current castle area-data room ID 41980. First correct internal pipe returns to this same ID at x1848. The second correct elevated pipe at2432 has been entered in replay-only diagnostics and returns to x3128, feet176. These diagnostic transitions are not fresh model clears.
- Static decoded destination: second correct pipe leads to castle entrance page12. Thus x3128 in the same room is normal forward progress.
- Static decoded third-section pipes:3120 top176 decorative;3264 top128 decorative;3392 top112 enterable but returns to castle page1;3648 top128 enterable and targets AreaPointer0x02 entrancepage0 (underwater). Use the3648 pipe, not3392.
- Underwater area ID44738 derives from ROM header address0xaec0+2. Castle41980 derives from0xa3fa+2. These are current area-data addresses; pending AreaPointer is not the current-room identifier.
- Underwater normal exit destination: AreaPointer0x65, entrancepage16. Expected castle reentry x4152 (page16*256+56) is inferred from earlier entrance conventions; verify actual live spawn.

## Coordinate loop interpretation

World8 loop checkpoints use parser pages6,11,16, with required origin y0xf0 grounded. Failing those checks invokes `ExecGameLoopback`, which subtracts four pages (1024 pixels) from player, camera and parser page coordinates. A same-room x decrease of1024 is therefore a normal internal loop mechanism, not death or external warp. Trigger position depends on the forward parser; do not equate parserpage*256 directly to Mario x. The recorded first correct pipe originally1296 was reached after subtraction at272. If the third section loops, apply the same coordinate shift to static landmarks; do not assume pipe3648 remains3648 after loop.

## Underwater geometry and hazards, statically decoded

- Decorative entrance pipe x48 top176.
- Firebar bases at static x320,496,640,896,1024 (runtime origins can have a small offset such as+4).
- Squid objects at448,816,848.
- Normal horizontal water-exit object atx1088, rows5–6: metatiles0x6b/0x6c at y112/128. The mouth spans y112–144; feet near144 is the inferred entry height. The collision routine requires facing right and normal/grounded player state for side entry. Continue right into the mouth rather than pressing down on top.
- Destination record atx1056 selects castlepage16 before the exit. x1248 is the scroll-lock object, not the pipe.

## Final castle, statically decoded

- Expected entrance pipe4144 top176; avoid entering pipe4256, which points back to castlepage1.
- Hammer brother object at4368; lava bubble at4464; final enemy/Bowser-fire control at4688.
- Bowser base spawn4720; castle bridge begins4608, chain4800, axe4816. Enemy positions move after spawning and object origins differ from collision boxes.
- Final castle shares room41980 with all earlier castle sections; underwater44738 is the actual distinct room transition.

Original source URL retained by the team: https://gist.github.com/WillSams/678a2d8a49d3f01e1d6e0362f83d1fbc . This preparation used the saved source, not a new web retrieval.
