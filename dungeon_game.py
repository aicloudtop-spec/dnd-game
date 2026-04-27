#!/usr/bin/env python3
"""
Open5e Text Adventure
A simple D&D-style text adventure using the Open5e API for monsters and spells.
"""

import requests
import random
import json
import os

# ----------------- Save / Load system -----------------
SAVE_FILE = "dnd_save.json"

def save_game(state):
    """Persist the current game state to disk.
    The state dict contains player info, current room, monsters list and any other needed data."""
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        print_color("Game saved to " + SAVE_FILE, Colors.YELLOW)
    except Exception as e:
        print_color("Failed to save game: {}".format(e), Colors.RED)

def load_game():
    """Load a saved state if one exists. Returns None if nothing was found."""
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        print_color("Loaded saved game from " + SAVE_FILE, Colors.YELLOW)
        return state
    except Exception as e:
        print_color("Failed to load save: {}".format(e), Colors.RED)
        return None

# ----------------------------------------------------------

API_BASE = "https://api.open5e.com"

# Colors for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_color(text, color=Colors.RESET):
    print(f"{color}{text}{Colors.RESET}")

# Character creation
def create_character():
    print_color("\n=== Create Your Character ===", Colors.BOLD)
    name = input("Name: ").strip() or "Hero"

    print("\nChoose your class:")
    print("1. Fighter - Strong warrior, high HP")
    print("2. Rogue - Sneaky, high damage")
    print("3. Wizard - Spellcaster, low HP but powerful")

    classes = {
        "1": {"name": "Fighter", "hp": 12, "ac": 16, "str": 16, "dex": 12, "int": 10, "damage": 8, "spells": []},
        "2": {"name": "Rogue", "hp": 8, "ac": 14, "str": 10, "dex": 16, "int": 12, "damage": 6, "spells": []},
        "3": {"name": "Wizard", "hp": 6, "ac": 12, "str": 8, "dex": 12, "int": 16, "damage": 4, "spells": ["fireball", "magic missile", "shield"]}
    }

    choice = input("Choice (1-3): ").strip() or "1"
    char_class = classes.get(choice, classes["1"])

    char = {
        "name": name,
        "class": char_class["name"],
        "hp": char_class["hp"],
        "max_hp": char_class["hp"],
        "ac": char_class["ac"],
        "str": char_class["str"],
        "dex": char_class["dex"],
        "int": char_class["int"],
        "damage": char_class["damage"],
        "spells": char_class["spells"]
    }

    print_color(f"\n{char['name']} the {char['class']} enters the dungeon!", Colors.GREEN)
    return char

# Fetch monsters from Open5e API
# Global boss list – you can expand as you like
BOSS_MONSTERS = [
    {"name": "Ancient Red Dragon", "hp": 200, "ac": 22,
     "desc": "A massive dragon breathing scorching fire.",
     "actions": [{"name": "Fire Breath", "damage": "30"}]},
    {"name": "Lich", "hp": 150, "ac": 18,
     "desc": "Undead sorcerer wielding forbidden magic.",
     "actions": [{"name": "Necrotic Blast", "damage": "25"}]},
    {"name": "Beholder", "hp": 180, "ac": 20,
     "desc": "A floating eye monster with many deadly rays.",
     "actions": [{"name": "Eye Ray", "damage": "22"}]},
]

# -------- Boss‑loot system --------

def apply_item(player, item):
    """Apply an item's effect to the player."""
    eff = item.get("effect")
    val = item.get("value", 0)
    if eff == "heal":
        player["hp"] = min(player["max_hp"], player["hp"] + val)
        print_color(f"  You heal {val} HP! (Now {player['hp']}/{player['max_hp']})", Colors.GREEN)
    elif eff == "damage":
        player["damage"] += val
        print_color(f"  Your damage increased by {val}! (Now {player['damage']})", Colors.GREEN)
    elif eff == "ac":
        player["ac"] += val
        print_color(f"  Your AC increased by {val}! (Now {player['ac']})", Colors.GREEN)
    elif eff == "max_hp":
        player["max_hp"] += val
        player["hp"] = min(player["max_hp"], player["hp"] + val)
        print_color(f"  Your max HP increased by {val}! (Now {player['max_hp']})", Colors.GREEN)
    elif eff == "spell":
        if item.get("spell") not in player["spells"]:
            player["spells"].append(item["spell"])
            print_color(f"  You learned a new spell: {item['spell']}!", Colors.PURPLE)
    else:
        # dud – no effect or a small penalty
        if eff == "none":
            print_color("  It's just a worthless trinket...", Colors.RED)
        else:
            # small penalty
            player["hp"] = max(1, player["hp"] - 5)
            print_color("  The item is cursed! You lose 5 HP.", Colors.RED)


def grant_boss_reward(player):
    """Roll a d20 to determine the boss loot quality."""
    print_color("\n*** Boss Defeated! Rolling for loot... ***", Colors.YELLOW)
    roll = roll_d20()
    print_color(f"Loot roll: {roll}", Colors.YELLOW)

    if roll <= 4:
        # Dud or minor penalty
        pool = [
            {"name": "Cursed Trinket", "effect": "none", "desc": "A worthless, slightly creepy bauble."},
            {"name": "Moldy Scroll", "effect": "minor_damage", "desc": "It crumbles and gives you a headache."},
        ]
        chosen = random.choice(pool)
        print_color(f"You found: {chosen['name']}!", Colors.RED)
        print_color(f"  {chosen['desc']}", Colors.RED)
        apply_item(player, chosen)

    elif roll <= 12:
        # Minor item
        pool = [
            {"name": "Healing Potion", "effect": "heal", "value": 10, "desc": "A small vial of healing fluid."},
            {"name": "Sharpening Stone", "effect": "damage", "value": 2, "desc": "+2 damage."},
            {"name": "Minor Shield Ring", "effect": "ac", "value": 1, "desc": "+1 AC."},
        ]
        chosen = random.choice(pool)
        print_color(f"You found: {chosen['name']}!", Colors.GREEN)
        print_color(f"  {chosen['desc']}", Colors.GREEN)
        apply_item(player, chosen)

    elif roll <= 18:
        # Good item
        pool = [
            {"name": "Enchanted Sword", "effect": "damage", "value": 4, "desc": "+4 damage."},
            {"name": "Reinforced Shield", "effect": "ac", "value": 2, "desc": "+2 AC."},
            {"name": "Ring of Vigor", "effect": "max_hp", "value": 10, "desc": "+10 max HP."},
            {"name": "Spell Scroll (Fireball)", "effect": "spell", "spell": "fireball", "desc": "You learn a new spell!"},
        ]
        chosen = random.choice(pool)
        print_color(f"You found: {chosen['name']}!", Colors.BLUE)
        print_color(f"  {chosen['desc']}", Colors.BLUE)
        apply_item(player, chosen)

    else:
        # Epic / 19‑20
        pool = [
            {"name": "Dragon Scale Armor", "effect": "ac", "value": 4, "desc": "+4 AC."},
            {"name": "Staff of Power", "effect": "damage", "value": 6, "desc": "+6 damage."},
            {"name": "Amulet of Health", "effect": "max_hp", "value": 20, "desc": "+20 max HP."},
            {"name": "Ring of Three Wishes", "effect": "heal", "value": 50, "desc": "Massive heal!"},
        ]
        chosen = random.choice(pool)
        print_color(f"You found: {chosen['name']}!", Colors.PURPLE)
        print_color(f"  {chosen['desc']}", Colors.PURPLE)
        apply_item(player, chosen)

    print_color("="*40, Colors.YELLOW)


def get_monsters(challenge="0-4"):
    """Fetch monsters from Open5e API (fallback list if needed)."""
    try:
        url = f"{API_BASE}/monsters/?challenge_rating={challenge}&limit=20"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("results", [])
    except Exception as e:
        print_color(f"API error: {e}", Colors.RED)

    # Fallback monsters if API fails – keep them low‑level for early play
    return [
        {"name": "Goblin", "hp": 7, "ac": 15, "challenge_rating": "1/4", "actions": [{"name": "Scimitar", "damage": "5"}], "desc": "A small, wicked creature"},
        {"name": "Kobold", "hp": 5, "ac": 12, "challenge_rating": "1/8", "actions": [{"name": "Dagger", "damage": "4"}], "desc": "A reptilian humanoid"},
        {"name": "Skeleton", "hp": 13, "ac": 13, "challenge_rating": "1/4", "actions": [{"name": "Shortbow", "damage": "6"}], "desc": "Undead remains"},
        {"name": "Zombie", "hp": 22, "ac": 8, "challenge_rating": "1/4", "actions": [{"name": "Slam", "damage": "4"}], "desc": "A rotting undead"},
        {"name": "Giant Spider", "hp": 26, "ac": 14, "challenge_rating": "1", "actions": [{"name": "Bite", "damage": "7"}], "desc": "A massive arachnid"},
    ]

def get_spell(spell_name):
    """Fetch spell from Open5e API"""
    try:
        url = f"{API_BASE}/spells/?search={spell_name}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            if results:
                return results[0]
    except:
        pass
    return None

# Combat system
def roll_d20():
    return random.randint(1, 20)

def player_attack(player, monster):
    roll = roll_d20() + (player["dex"] if player["class"] == "Rogue" else player["str"]) // 3
    print_color(f"\nYou attack the {monster['name']}! (Roll: {roll})", Colors.YELLOW)

    if roll >= 10:
        dmg = random.randint(1, player["damage"]) + (player["dex"] if player["class"] == "Rogue" else player["str"]) // 3
        if player["class"] == "Rogue" and roll >= 15:
            dmg *= 2
            print_color("CRITICAL HIT!", Colors.GREEN)
        print_color(f"You hit for {dmg} damage!", Colors.GREEN)
        return dmg
    else:
        print_color("You miss!", Colors.RED)
        return 0

def monster_attack(monster, player):
    cr = float(monster.get("challenge_rating", "1").split("/")[-1] or "1")
    roll = roll_d20() + int(cr) * 2
    ac = player["ac"]
    print_color(f"\nThe {monster['name']} attacks you! (Roll: {roll} vs AC:{ac})", Colors.RED)

    if roll >= ac - 5:
        action = monster.get("actions", [{"name": "Attack", "damage": "3"}])[0]
        dmg_str = action.get("damage", "3")
        dmg = int(dmg_str.split("d")[-1].split()[0] or "3")
        dmg = max(1, dmg + random.randint(0, 3))
        print_color(f"It hits for {dmg} damage!", Colors.RED)
        return dmg
    else:
        print_color("It misses!", Colors.GREEN)
        return 0

def cast_spell(player, spell_name, monster):
    spell = get_spell(spell_name)
    if not spell:
        print_color(f"You cast {spell_name} but nothing happens...", Colors.YELLOW)
        return 0

    print_color(f"\nYou cast {spell['name']}!", Colors.PURPLE)
    if spell.get("desc"):
        print(f"  {spell['desc'][:100]}...")

    dmg = random.randint(3, 8) + player["int"] // 3
    print_color(f"The spell deals {dmg} damage!", Colors.GREEN)
    return dmg

def combat(player, monster, is_boss=False):
    # Return a tuple (won, is_boss) so we can grant rewards after boss fights
    print_color(f"\n=== COMBAT: {player['name']} vs {monster['name']} ===", Colors.BOLD)
    desc = monster.get("desc", "A dangerous foe")
    print(f"Monster: {desc} (HP:?, AC:{monster['ac']})")

    monster_hp = monster.get("hp", 10)

    while player["hp"] > 0 and monster_hp > 0:
        print_color(f"\n--- Your HP: {player['hp']}/{player['max_hp']} | Monster HP: {monster_hp} ---", Colors.BLUE)
        print("1. Attack")
        if player["spells"]:
            print("2. Cast Spell")
        print("3. Run!")

        choice = input("\nAction: ").strip()

        if choice == "1":
            dmg = player_attack(player, monster)
            monster_hp -= dmg
        elif choice == "2" and player["spells"]:
            # Show spells with numbers for quick selection
            print("Spells:")
            for idx, sp in enumerate(player["spells"], start=1):
                print(f"  {idx}. {sp}")
            spell_choice = input("Choose spell number: ").strip()
            if spell_choice.isdigit():
                idx = int(spell_choice) - 1
                if 0 <= idx < len(player["spells"]):
                    spell_name = player["spells"][idx]
                    dmg = cast_spell(player, spell_name, monster)
                    monster_hp -= dmg
                else:
                    print_color("Invalid spell number!", Colors.RED)
            else:
                print_color("Please enter a number!", Colors.RED)
        elif choice == "3":
            if roll_d20() + player["dex"] // 3 > 10:
                print_color("You escape!", Colors.GREEN)
                return False
            else:
                print_color("You can't escape!", Colors.RED)
        else:
            print_color("Invalid choice!", Colors.RED)
            continue

        if monster_hp <= 0:
            break

        dmg = monster_attack(monster, player)
        player["hp"] -= dmg

    if player["hp"] > 0:
        print_color(f"\n*** You defeated the {monster['name']}! ***", Colors.GREEN)
        return True
    else:
        print_color("\n*** You have been defeated... ***", Colors.RED)
        return False

# Main game loop
def main():
    print_color("=" * 50, Colors.BOLD)
    print_color("   DUNGEON OF THE OPEN5E", Colors.PURPLE)
    print_color("=" * 50, Colors.BOLD)

    # Check for saved game
    state = load_game()
    if state:
        ans = input("Load saved game? (y/n): ").strip().lower()
        if ans == "y":
            player = state["player"]
            rooms = state["rooms"]
            monsters = state.get("monsters", get_monsters())
            print_color(f"Resuming game at room {rooms}...", Colors.GREEN)
        else:
            # Remove outdated save and start fresh
            try:
                os.remove(SAVE_FILE)
            except:
                pass
            player = create_character()
            monsters = get_monsters()
            rooms = 1
    else:
        player = create_character()
        monsters = get_monsters()
        rooms = 1

    while player["hp"] > 0:
        print_color(f"\n=== Room {rooms} ===", Colors.BOLD)
        input("Press Enter to enter the next room...")

        # Boss every 5 rooms
        is_boss = (rooms % 5 == 0)

        if is_boss:
            monster = random.choice(BOSS_MONSTERS)
            print_color(f"\n*** BOSS FIGHT: {monster['name']} appears! ***", Colors.RED)
        else:
            monster = random.choice(monsters)
            print_color(f"\nA {monster['name']} appears!", Colors.RED)

        print(f"  {monster.get('desc', 'It looks dangerous')}")

        # Scale normal monsters based on current floor (every 5 rooms)
        if not is_boss:
            floor = (rooms - 1) // 5
            scale = 1 + floor * 0.2  # 20% HP increase per floor
            monster = monster.copy()  # avoid modifying the original list item
            monster["hp"] = int(monster.get("hp", 10) * scale)
            # Slightly scale damage too
            for action in monster.get("actions", []):
                dmg_str = action.get("damage", "3")
                try:
                    base = int(dmg_str.split("d")[-1].split()[0])
                    action["damage"] = str(int(base * scale))
                except ValueError:
                    pass

        success = combat(player, monster, is_boss)

        if not success:
            break
        if success and is_boss:
            grant_boss_reward(player)

        if input("\nTake a short rest? (y/n): ").strip().lower() == "y":
            heal = random.randint(1, player["max_hp"] // 2)
            player["hp"] = min(player["max_hp"], player["hp"] + heal)
            print_color(f"You heal {heal} HP!", Colors.GREEN)

        rooms += 1
        # Prompt to save after each room
        save_choice = input("Save progress? (s) or continue: ").strip().lower()
        if save_choice == 's':
            save_game({"player": player, "rooms": rooms, "monsters": monsters})

        # Refresh normal monster list every 3 rooms with higher challenge rating
        if rooms % 3 == 0:
            print_color("\n*** NEW FLOOR ***", Colors.PURPLE)
            floor = rooms // 3
            monsters = get_monsters(challenge=f"{floor}-{floor+3}")

    print_color(f"\n=== GAME OVER ===", Colors.RED)
    print_color(f"You survived {rooms} rooms!", Colors.YELLOW)
    print_color(f"R.I.P. {player['name']}", Colors.PURPLE)

if __name__ == "__main__":
    main()
