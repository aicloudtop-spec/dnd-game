# D&D 5e Text Adventure

A simple, terminal-based D&D-style text adventure game powered by the [Open5e API](https://open5e.com). Fight monsters, cast spells, and explore dungeon rooms in classic 5e style.

## Features

- **Character creation** – choose Fighter, Rogue, or Wizard
- **Real-time combat** with attack rolls, critical hits, and spellcasting
- **Open5e API integration** – fetches monsters and spells from the SRD
- **Progressive difficulty** – each floor features tougher monsters
- **Rest system** – heal between encounters

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
4. After each victory, take a short rest to heal.

## Requirements

- Python 3.6+
- `requests` library (`pip install requests`)

## License

Open-source, MIT. Fork it, mod it, enjoy it!
