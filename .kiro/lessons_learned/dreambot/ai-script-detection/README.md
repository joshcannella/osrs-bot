# Lessons Learned: AI-Generated DreamBot Scripts & Ban Avoidance

Source: DreamBot forum discussion (Nov 2025) between gnittobs and Decrypted (experienced scripter).

## Key Takeaways

### 1. LLMs hallucinate DreamBot API methods
LLMs don't have access to the full DreamBot API and will invent methods that don't exist or use long-winded workarounds when a simple API call exists (e.g., writing custom price fetching instead of `LivePrices.get()`).

**Our mitigation:** Javadocs scraper (`scripts/refresh-javadocs.py`) provides 438 classes and 4,571 verified method signatures as local knowledge. Agent loads these on demand.

### 2. DreamBot already randomizes low-level input
`interact()` handles click position, left/right click decisions, mouse paths, and timing internally. Adding manual randomization on top creates detectable double-randomization patterns.

**Our mitigation:** Anti-ban focuses on high-level behavioral variation only. See `knowledge/osrs/dreambot-builtin-randomization.md`.

### 3. Identical timing between actions is a detection signal
AI-generated scripts tend to use the same sleep values everywhere — `return 600` after every action. Even with random ranges, the distribution is uniform and predictable. Real players have variable reaction times with occasional long pauses.

**Our mitigation:** Fatigue system scales delays over session. `reactionDelay()` uses gaussian distribution with 5% "wasn't paying attention" spikes. But scripts still need to vary their own return values — don't always return 600.

### 4. Vary HOW you do things, not just WHEN
Real players don't always interact the same way:
- Sometimes deposit all, sometimes right-click → "Bank all"
- Sometimes left-click a tree, sometimes right-click → "Chop down"
- Sometimes click game world to walk, sometimes click minimap
- Sometimes use keyboard shortcuts for tabs, sometimes click

**Status:** Partially addressed. `shouldUseMinimap()` exists. `interactForceLeft()`/`interactForceRight()` available in DreamBot API. Scripts should use these to vary interaction style. Could add more helpers.

### 5. Don't spam-open interfaces
Opening the same window multiple times in a row (bank, inventory, stats) is a bot tell. Real players open it once and use it.

**Status:** Not explicitly guarded against. Scripts should check `Bank.isOpen()` / `Tabs.getOpen()` before opening. AntiBanNode already checks current tab before switching.

### 6. AFK timers and extended breaks matter
Real players step away from the computer. Short idle pauses aren't enough — need occasional 1-5 minute breaks where the character does nothing.

**Status:** AntiBanNode has extended idle (8-25s every 5+ minutes). Could be longer. Break scheduling is still deferred — noted as future work.

### 7. Proxies/VPNs reduce ban rates
Forum consensus is that proxies help, though hard to confirm definitively.

**Status:** Outside scope of scripting — infrastructure concern.

### 8. AI is good for scaffolding, bad for interaction code
The forum poster's final approach: let AI write the script structure, state management, and logic flow, but write the DreamBot interaction code (clicks, sleeps, banking) manually.

**Our approach:** We use AI for everything but mitigate the interaction problem with verified API references and anti-ban patterns. The agent has the full API and knows the patterns — it shouldn't need to hallucinate.

## Action Items

- [x] Full API reference via javadocs scraper
- [x] Anti-ban uses DreamBot's built-in randomization, not manual mouse jitter
- [x] Fatigue system for delays and mouse speed
- [x] Gaussian reaction delays with outlier spikes
- [x] Interaction variation helpers (`shouldForceRightClick()`)
- [x] Break scheduler for 1-5 minute AFK breaks (`maybeBreak()`)
- [x] Return value convention updated — no uniform `return 600`
- [x] Interface spam guard — critical rule #15: check state before opening
- [ ] Audit existing scripts once they exist
