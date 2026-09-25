# ProjectOrchid Apple Watch Series 3 Companion

Target: Apple Watch Series 3 only, watchOS 8.x.

Controls:
- Dialogue mirrors the active Ren'Py line.
- Choices appear as tappable watch buttons and are sent to the iPhone.
- Digital Crown forward requests story advance/roll-forward.
- Digital Crown backward requests Ren'Py rollback.

Transport uses WatchConnectivity. The iPhone remains authoritative for game state; the watch is a remote UI, not a second Ren'Py runtime.

This target intentionally optimizes for the 38 mm and 42 mm Series 3 displays. No effort is made yet for newer watch families.
