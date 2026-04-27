# D&D 5e Text Adventure

A simple, terminal-based D&D-style text adventure game powered by the [Open5e API](https://open5e.com). Fight monsters, cast spells, and explore dungeon rooms in classic 5e style.

## Features

- **Character creation** – choose Fighter, Rogue, or Wizard
- **Real-time combat** with attack rolls, critical hits, and spellcasting
- **Open5e API integration** – fetches monsters and spells from the SRD
- **Progressive difficulty** – each floor features tougher monsters
- **Rest system** – heal between encounters
- **Randomized Boss Encounters** – bosses appear at random 4‑7 room intervals
- **Loot System** – bosses drop legendary items; regular rooms drop scaled gear
- **Save/Load Support** – save progress after each room and resume later

## Quick Start

```bash
# Clone the repo
git clone https://github.com/aicloudtop-spec/dnd-game.git
cd dnd-game

# Run the game (requires Python 3 + requests)
python3 dungeon_game.py
```

## How to Play

1. Enter your character's name.
2. Pick a class:
   - **Fighter** – High HP, strong melee attacks
   - **Rogue** – High damage, critical hits
   - **Wizard** – Spellcaster with fireball, magic missile, and shield
3. Enter rooms, fight monsters, and survive as long as you can!
4. After each victory:
   - **Boss fights** (every 4‑7 rooms) grant legendary loot via a d20 roll.
   - **Regular rooms** may drop minor or good items (no legendaries).
5. After each room you can:
   - Take a short rest to heal.
   - Save your progress (type `s`).
6. On next launch, the game will detect your save and offer to resume.

## Requirements

- Python 3.6+
- `requests` library (`pip install requests`)

## License

Open-source, MIT. Fork it, mod it, enjoy it!
