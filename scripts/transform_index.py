"""Transform fal-roster reference HTML into our 12-game-character version.

Input:  index.html.tmp  (already path-remapped via sed)
Output: index.html
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "index.html.tmp"
DST = ROOT / "index.html"

# 12 game characters: id, display, role, franchise, tier, palette[c1,c2,c3]
CHARS = [
    {"id": "master-chief", "disp": "MASTER-CHIEF", "role": "SPARTAN-117", "game": "Halo",                  "tier": "S",
     "pal": ["#5B8C5A", "#3D5A3D", "#C4A84D"], "world": "REQUIEM",          "mission": "OPERATION FIRSTSTRIKE",  "district": "INSTALLATION 04"},
    {"id": "kratos",       "disp": "KRATOS",       "role": "GOD SLAYER",  "game": "God of War",            "tier": "S",
     "pal": ["#C0392B", "#7D7D7D", "#F5D76E"], "world": "MIDGARD",          "mission": "GHOST OF SPARTA",        "district": "LAKE OF NINE"},
    {"id": "link",         "disp": "LINK",         "role": "HERO OF TIME","game": "Legend of Zelda",       "tier": "S",
     "pal": ["#27AE60", "#8B7355", "#3498DB"], "world": "HYRULE",           "mission": "MASTER SWORD",           "district": "KOKIRI FOREST"},
    {"id": "mario",        "disp": "MARIO",        "role": "SUPER PLUMBER","game": "Super Mario",          "tier": "S",
     "pal": ["#E74C3C", "#3498DB", "#F1C40F"], "world": "MUSHROOM KINGDOM", "mission": "RESCUE PEACH",           "district": "WORLD 1-1"},
    {"id": "samus",        "disp": "SAMUS",        "role": "BOUNTY HUNTER","game": "Metroid",              "tier": "A",
     "pal": ["#E67E22", "#C0392B", "#27AE60"], "world": "ZEBES",            "mission": "MOTHER BRAIN",           "district": "BRINSTAR"},
    {"id": "cloud",        "disp": "CLOUD",        "role": "SOLDIER 1ST", "game": "Final Fantasy VII",     "tier": "A",
     "pal": ["#2C3E50", "#8E44AD", "#F39C12"], "world": "MIDGAR",           "mission": "REACTOR No. 1",          "district": "SECTOR 7 SLUMS"},
    {"id": "snake",        "disp": "SNAKE",        "role": "FOXHOUND",    "game": "Metal Gear Solid",      "tier": "A",
     "pal": ["#2C3E50", "#5D6D7E", "#95A5A6"], "world": "SHADOW MOSES",     "mission": "TACTICAL ESPIONAGE",     "district": "ALASKAN BLACK SITE"},
    {"id": "geralt",       "disp": "GERALT",       "role": "WITCHER",     "game": "The Witcher 3",         "tier": "A",
     "pal": ["#7F8C8D", "#C0392B", "#2C3E50"], "world": "VELEN",            "mission": "WILD HUNT",              "district": "WHITE ORCHARD"},
    {"id": "aloy",         "disp": "ALOY",         "role": "SEEKER",      "game": "Horizon Zero Dawn",     "tier": "A",
     "pal": ["#E74C3C", "#D4A76A", "#2ECC71"], "world": "FORBIDDEN WEST",   "mission": "MOTHER'S HEART",         "district": "NORA SACRED LAND"},
    {"id": "lara",         "disp": "LARA",         "role": "TOMB RAIDER", "game": "Tomb Raider",           "tier": "B",
     "pal": ["#5D4E37", "#2ECC71", "#95A5A6"], "world": "YAMATAI",          "mission": "ENDURANCE",              "district": "DRAGON'S TRIANGLE"},
    {"id": "arthur",       "disp": "ARTHUR",       "role": "OUTLAW",      "game": "Red Dead Redemption 2", "tier": "B",
     "pal": ["#8B4513", "#D4A76A", "#4A6741"], "world": "WEST ELIZABETH",   "mission": "BLACKWATER JOB",         "district": "VAN DER LINDE CAMP"},
    {"id": "joel",         "disp": "JOEL",         "role": "SURVIVOR",    "game": "The Last of Us",        "tier": "B",
     "pal": ["#5D4E37", "#2ECC71", "#8B7355"], "world": "QUARANTINE ZONE",  "mission": "SMUGGLE THE CARGO",      "district": "BOSTON Q.Z."},
]

# Generate stats per character — varied but deterministic
def make_stats(c, idx):
    seed = sum(ord(x) for x in c["id"])
    return {
        "hp": 400 + (seed % 9) * 40,
        "cyber": 12 + (seed % 13),
        "qh": [(seed + i * 7) % 16 for i in range(6)],
        "yoff": 0.0,
        "eddy": 100000 + (seed * 7919) % 700000,
        "carry": [60 + (seed % 80), 80 + (seed % 100) + 50],
        "tasks": 1 + (seed % 12),
        "sysver": f"{1 + (idx % 4)}.{(seed % 10)}.{(seed * 3 % 10)}.{(seed * 7 % 10)}",
        "map": c["world"],
        "gig": c["mission"],
        "district": c["district"],
        "temp": 8 + (seed % 30),
        "role": c["role"],
        "level": 30 + (seed % 25),
        "tier": c["tier"],
    }


def make_card_html(c, idx):
    stats = make_stats(c, idx)
    # JSON-encode then quote-escape for HTML attribute (mimics reference's &quot;)
    stats_attr = json.dumps(stats, ensure_ascii=False).replace('"', '&quot;')
    accent = c["pal"][0]
    dot_color = "var(--c1)" if idx % 2 == 0 else "var(--c2)"
    return (
        f'        <div class="char" data-id="{c["disp"]}" data-guild="{c["disp"]}" '
        f'data-stats="{stats_attr}" data-accent="{accent}" '
        f'data-glb="./assets/glb/{c["id"]}.glb" data-bgsrc="./assets/video/{c["id"]}.mp4">\n'
        f'          <img class="char-portrait" src="./assets/characters/{c["id"]}.png" alt="{c["disp"]}" '
        f'style="width:48px;height:48px;border-radius:12px;object-fit:cover;flex-shrink:0;border:1px solid rgba(56,189,248,.2)"/>\n'
        f'          <div class="flex-1">\n'
        f'            <div class="text-[13px] font-semibold" style="color:var(--c1)">{c["disp"]}</div>\n'
        f'            <div class="mono text-[9.5px]" style="color:var(--c1);letter-spacing:.12em;font-weight:500">'
        f'{c["role"]} · {c["game"].upper()}<span class="dot ml-1" style="background:{dot_color}"></span></div>\n'
        f'          </div>\n'
        f'          <div class="text-right flex flex-col items-end gap-1"><span class="tier {c["tier"]}">TIER {c["tier"]}</span></div>\n'
        f'        </div>'
    )


def main():
    src = SRC.read_text(encoding="utf-8")

    # ---- 1) Replace roster cards block ----
    cards_html = "\n\n".join(make_card_html(c, i) for i, c in enumerate(CHARS))
    cards_html = "\n" + cards_html + "\n\n      </div>"
    pattern = re.compile(
        r'\n        <div class="char" data-id="VEXA-3".*?\n      </div>',
        re.DOTALL,
    )
    new_src, n = pattern.subn(cards_html, src, count=1)
    if n != 1:
        print("ERROR: roster cards block not replaced", file=sys.stderr)
        sys.exit(1)
    src = new_src

    # ---- 2) Replace CHAR_PALETTES ----
    pal_lines = ",\n".join(
        f'  "{c["disp"]}":{ " " * (12 - len(c["disp"]))}["{c["pal"][0]}", "{c["pal"][1]}", "{c["pal"][2]}"], // {c["game"]}'
        for c in CHARS
    )
    pal_block = "const CHAR_PALETTES = {\n" + pal_lines + "\n};"
    src, n = re.subn(
        r'const CHAR_PALETTES = \{[^}]*\};',
        pal_block,
        src,
        count=1,
        flags=re.DOTALL,
    )
    if n != 1:
        print("ERROR: CHAR_PALETTES not replaced", file=sys.stderr)
        sys.exit(1)

    # ---- 3) Replace BAKED_SETUP ----
    def baked_entry(c, idx):
        yoff = -0.10 - 0.01 * (idx % 8)
        comp_yoff = round(0.02 * ((idx % 5) - 2), 2)
        rough = 0.18 + 0.04 * (idx % 4)
        metal = 0.05 + 0.06 * (idx % 3)
        disp = round(0.05 * (idx % 4), 2)
        refl = round(0.02 * ((idx % 6) - 2), 2)
        pal = c["pal"]
        return (
            f'  "{c["disp"]}":{ " " * (12 - len(c["disp"]))}{{ '
            f'yoff:{yoff:.2f}, companionYoff:{comp_yoff:.2f}, idle:0, '
            f'palette:["{pal[0]}","{pal[1]}","{pal[2]}"], '
            f'floor:{{roughness:{rough:.2f},metalness:{metal:.2f},normalScale:0.6,repeat:1.8,opacity:0.55,displacement:{disp:.2f}}}, '
            f'reflYoff:{refl:.2f} }}'
        )

    baked_lines = ",\n".join(baked_entry(c, i) for i, c in enumerate(CHARS))
    baked_block = "const BAKED_SETUP = {\n" + baked_lines + "\n};"
    src, n = re.subn(
        r'const BAKED_SETUP = \{.*?\n\};',
        baked_block,
        src,
        count=1,
        flags=re.DOTALL,
    )
    if n != 1:
        print("ERROR: BAKED_SETUP not replaced", file=sys.stderr)
        sys.exit(1)

    # ---- 4) Replace COMPANIONS map ----
    comp_lines = ",\n".join(
        f"  '{c['id']}':{ ' ' * (14 - len(c['id']))}'./assets/companions/{c['id']}.glb'"
        for c in CHARS
    )
    comp_block = "const COMPANIONS = {\n" + comp_lines + ",\n};"
    src, n = re.subn(
        r'const COMPANIONS = \{[^}]*\};',
        comp_block,
        src,
        count=1,
        flags=re.DOTALL,
    )
    if n != 1:
        print("ERROR: COMPANIONS not replaced", file=sys.stderr)
        sys.exit(1)

    # ---- 5) Repoint intro CHAR_GLB to first character (master-chief) ----
    src = src.replace(
        "const CHAR_GLB = './assets/glb/fal-08.glb';",
        "const CHAR_GLB = './assets/glb/master-chief.glb';",
    )
    # The intro-only fallback companion id 'fal-08' → 'master-chief'
    src = src.replace("setActiveCompanion('fal-08');", "setActiveCompanion('master-chief');")
    src = src.replace('__activeId = "FAL-08";', '__activeId = "MASTER-CHIEF";')
    # The intro bg video reference
    src = src.replace("./assets/video/fal-08.mp4", "./assets/video/master-chief.mp4")

    # ---- 6) Replace __FAL_JOBS__ with game-character lore ----
    LORE = {
        "MASTER-CHIEF": [
            ("Defend Reach",          "REQUIEM",          "Spartan-II augment", ["MJOLNIR", "Energy Sword", "Cortana", "UNSCDF", "Spartan-II", "Forerunner"], "Hold the line on Reach against the Covenant glassing fleet."),
            ("Halo Installation 04",  "INSTALLATION 04",  "Activation halt",    ["Pillar of Autumn", "Flood", "Halo Ring", "343 Guilty Spark", "Plasma Pistol", "Warthog"], "Prevent activation of the Halo array. Detonate the reactor."),
            ("Reclaim Earth",         "NEW MOMBASA",      "Tip of the Spear",   ["ODST", "Scarab", "Brute Chieftain", "Battle Rifle", "Spartan Laser", "Mongoose"], "Push back the Prophet of Regret's invasion fleet."),
        ],
        "KRATOS": [
            ("Slay Ares",            "GREECE",            "Origin sin",          ["Blades of Chaos", "Olympus", "Spartan Rage", "Pandora's Box", "Hades", "Athena"], "Avenge your family. End the God of War."),
            ("Father of Atreus",     "MIDGARD · LAKE OF NINE", "Norse arc",      ["Leviathan Axe", "Atreus", "Mimir", "Jörmungandr", "Spartan Rage", "Brok"], "Carry your wife's ashes to the highest peak of all the realms."),
            ("Ragnarök",             "ASGARD",            "End of all things",   ["Draupnir Spear", "Tyr", "Freya", "Odin", "Thor", "Bifröst"], "Stop Odin. Free the realms. Embrace the prophecy."),
        ],
        "LINK": [
            ("Awaken in Hyrule",     "HYRULE FIELD",      "Calamity Ganon",      ["Master Sword", "Hylian Shield", "Sheikah Slate", "Paraglider", "Champions", "Divine Beasts"], "Reclaim the Master Sword. Free the four Divine Beasts."),
            ("Tears of the Kingdom", "SKY ISLANDS",       "Ultrahand",           ["Recall", "Fuse", "Ascend", "Zelda", "Demon King", "Sky Islands"], "Reach the Demon King's seal beneath Hyrule Castle."),
            ("Ocarina of Time",      "KOKIRI FOREST",     "Hero awakens",        ["Master Sword", "Navi", "Ocarina", "Triforce", "Ganondorf", "Temple of Time"], "Pull the Master Sword. Become the Hero of Time."),
        ],
        "MARIO": [
            ("Rescue Peach",         "WORLD 1-1",         "Bowser's Castle",     ["Fire Flower", "Super Mushroom", "Cape Feather", "Yoshi", "Goomba Stomp", "Star Power"], "Cross 8 worlds. Save the Princess from Bowser."),
            ("Galactic Hop",         "GALAXY OBSERVATORY", "Starbits",           ["Star Bits", "Luma", "Power Star", "Spin Attack", "Wall Jump", "Triple Jump"], "Collect 121 Power Stars across the cosmos."),
            ("Mushroom Kart Cup",    "RAINBOW ROAD",      "Lap 3 / Final",       ["Banana Peel", "Blue Shell", "Star", "Lightning", "Bullet Bill", "Drift Boost"], "Take gold on the Special Cup against Bowser, Wario, DK."),
        ],
        "SAMUS": [
            ("Mother Brain",         "BRINSTAR · ZEBES",  "Original mission",    ["Power Suit", "Morph Ball", "Screw Attack", "Charge Beam", "Missiles", "Varia Suit"], "Infiltrate the space pirate base. End Mother Brain."),
            ("Phazon Outbreak",      "TALLON IV",         "Prime contagion",     ["Wave Beam", "Plasma Beam", "Power Bombs", "Grapple Beam", "Boost Ball", "Dark Suit"], "Quarantine the Phazon. Destroy Metroid Prime."),
            ("Dread Protocol",       "PLANET ZDR",        "EMMI sweeper",        ["Phantom Cloak", "Flash Shift", "Storm Missile", "Cross Bombs", "Speed Booster", "Hyper Beam"], "Survive ZDR. Eliminate the EMMI units."),
        ],
        "CLOUD": [
            ("Reactor 1 Bombing",    "MIDGAR · SECTOR 7", "AVALANCHE op",        ["Buster Sword", "Materia", "Limit Break", "Tifa", "Barrett", "Mako Energy"], "Plant the bomb. Destroy Mako Reactor No. 1. Escape Sector 7."),
            ("Hunt Sephiroth",       "NIBELHEIM",         "One-Winged Angel",    ["Omnislash", "Holy Materia", "Aerith", "Jenova", "Black Materia", "Lifestream"], "Pursue Sephiroth across the world. Stop Meteor."),
            ("Northern Crater",      "NORTHERN CRATER",   "Final descent",       ["Knights of Round", "Mime", "Ribbon", "Final Attack", "Cloud", "Vincent"], "Descend to the planet's core. End the Calamity."),
        ],
        "SNAKE": [
            ("Shadow Moses",         "ALASKAN BLACK SITE", "Tactical espionage", ["SOCOM", "FAMAS", "Stealth Camo", "Stinger", "C4", "Claymore"], "Infiltrate the nuclear weapons facility. Stop FOXHOUND."),
            ("Tanker Incident",      "HUDSON RIVER",      "Sons of Liberty",     ["M9 Tranq", "CQC", "Octocamo", "Codec", "Cardboard Box", "Gas Mask"], "Recover the photographs of Metal Gear RAY."),
            ("Big Shell Op",         "BIG SHELL FACILITY", "Patriot trigger",    ["Codec", "Sneaking Suit", "Sniper Rifle", "Raiden", "Otacon", "Solidus"], "Disarm Arsenal Gear. Expose the Patriots."),
        ],
        "GERALT": [
            ("Find Ciri",            "WHITE ORCHARD",     "Wild Hunt arc",       ["Silver Sword", "Steel Sword", "Igni Sign", "Quen Sign", "Witcher Senses", "Roach"], "Track Cirilla across the Continent. Outpace the Wild Hunt."),
            ("Bloody Baron",         "VELEN",             "Family curse",        ["Axii Sign", "Botchling", "Ladies of the Wood", "Crones", "Whispering Hillock", "Anna"], "Solve the Baron's missing wife. Confront the crones of Crookback Bog."),
            ("Battle of Kaer Morhen", "KAER MORHEN",      "Last stand",          ["Yennefer", "Triss", "Vesemir", "Eredin", "Mutagens", "Witcher School"], "Hold the Witcher fortress against the Wild Hunt's general Eredin."),
        ],
        "ALOY": [
            ("All-Mother Mountain",  "NORA SACRED LAND",  "Proving day",         ["Bow", "Tripcaster", "Rope Caster", "Focus", "Tearblaster", "Sharpshot Bow"], "Pass the Proving. Earn your name. Find your origin."),
            ("Forbidden West",       "LAS VEGAS RUINS",   "Far Zenith",          ["Spike Thrower", "Shredder Gauntlet", "Sylens", "Far Zenith", "Tenakth", "Hephaestus"], "Stabilize GAIA. Push west to find the missing subordinate functions."),
            ("Burning Shores",       "LOS ANGELES",       "Horus reactivates",   ["Specter Gauntlet", "Sylens-Lite", "Quen", "Londra", "Tideripper", "Stormbird"], "Stop Walter Londra from reactivating the Horus."),
        ],
        "LARA": [
            ("Yamatai",              "DRAGON'S TRIANGLE", "Survivor born",       ["Bow", "Climbing Axe", "Pry Axe", "Endurance", "Solarii", "Sun Queen"], "Survive the storm. Escape the island. Save your crew."),
            ("Croft Manor",          "ENGLAND",           "Father's legacy",     ["Akimbo Pistols", "Twin Pistols", "Manor", "Croft Family", "Trinity", "Atlas"], "Inherit Lord Richard Croft's research. Continue the work."),
            ("Shadow of the Tomb",   "PERU · COZUMEL",    "Apocalypse path",     ["Pickaxe", "Rope Ascender", "Yaaxil", "Trinity", "Dr. Dominguez", "Sun Eclipse"], "Stop the Mayan apocalypse you triggered. Find Paititi."),
        ],
        "ARTHUR": [
            ("Blackwater Job",       "BLACKWATER",        "First-act gone-wrong", ["Cattleman Revolver", "Lancaster Repeater", "Dead Eye", "Boadicea", "Dutch", "Hosea"], "Recover from the Blackwater ferry job. Lay low in the Grizzlies."),
            ("Camp Defense",         "VAN DER LINDE CAMP", "Loyalty kept",       ["Schofield", "Bow", "Lasso", "Charles", "Sadie", "Karen"], "Defend the camp against O'Driscolls and Pinkertons."),
            ("Final Ride",           "MOUNT HAGEN",       "TB diagnosis",        ["Mauser", "Bolt Action", "John Marston", "Micah", "Tuberculosis", "Last Honor"], "Get John out alive. Make peace with the man you became."),
        ],
        "JOEL": [
            ("Boston Q.Z.",          "BOSTON Q.Z.",       "Smuggler run",        ["Revolver", "Shiv", "9mm Pistol", "Tess", "FEDRA", "Fireflies"], "Smuggle the cargo across the wall to the Fireflies."),
            ("Cross-Country",        "WESTERN U.S.",      "Find the Fireflies",  ["Hunting Rifle", "Bow", "Molotov", "Bill", "Henry", "Sam"], "Escort Ellie across the infected ruins of America."),
            ("Salt Lake Hospital",   "ST. MARY'S HOSPITAL","Father's choice",    ["Shotgun", "Flamethrower", "Marlene", "Surgeons", "Ellie", "Jackson"], "Make the choice no one else could. Live with it."),
        ],
    }
    guilds = {}
    for c in CHARS:
        missions = LORE.get(c["disp"], [])
        jobs = []
        for (title, loc, hook, skills, _full, _mission) in [
            (m[0], m[1], m[2], m[3], m[4], m[4]) for m in missions
        ]:
            jobs.append({
                "title": title,
                "loc": loc,
                "salary": hook,
                "skills": skills,
                "mission": _full,
                "url": f"https://en.wikipedia.org/wiki/{c['game'].replace(' ', '_')}",
            })
        guilds[c["disp"]] = {
            "name": f"{c['game'].upper()} · {c['role']}",
            "label": c["game"].upper(),
            "jobs": jobs,
        }
    jobs_payload = {"guilds": guilds}
    jobs_json = json.dumps(jobs_payload, ensure_ascii=False)
    src, n = re.subn(
        r'<script>window\.__FAL_JOBS__ = \{.*?\};</script>',
        f'<script>window.__FAL_JOBS__ = {jobs_json};</script>',
        src,
        count=1,
        flags=re.DOTALL,
    )
    if n != 1:
        print("ERROR: __FAL_JOBS__ not replaced", file=sys.stderr)
        sys.exit(1)

    # ---- 7) Branding (title + meta + favicon) ----
    src = src.replace(
        "<title>fal — operator select</title>",
        "<title>Gaming Legends | 3D Character Showcase</title>",
    )
    src = src.replace(
        '<meta property="og:title" content="fal — operator select"/>',
        '<meta property="og:title" content="Gaming Legends | 3D Character Showcase"/>',
    )
    src = src.replace(
        '<meta property="og:description" content="Built for inference. Pick your operator."/>',
        '<meta property="og:description" content="12 iconic video-game protagonists rendered in 3D. Built by Allen Schiffman, powered by fal.ai × Claude."/>',
    )
    # Custom controller-shield favicon (replace fal-icon.svg link to dedicated favicon)
    src = src.replace(
        '<link rel="icon" type="image/svg+xml" href="./assets/fal-icon.svg"/>\n<link rel="apple-touch-icon" href="./assets/fal-icon.svg"/>',
        '<link rel="icon" type="image/svg+xml" href="./assets/favicon.svg"/>\n<link rel="apple-touch-icon" href="./assets/favicon.svg"/>',
    )
    # Left panel title
    src = src.replace(
        '<div class="mono text-[10px]" style="color:var(--c3);letter-spacing:.16em">BUILT FOR</div>\n        <div class="display text-2xl font-light leading-none" style="color:var(--c1)">INFERENCE</div>',
        '<div class="mono text-[10px]" style="color:var(--c3);letter-spacing:.16em">GAMING</div>\n        <div class="display text-2xl font-light leading-none" style="color:var(--c1)">LEGENDS</div>',
    )
    # Mobile header note
    src = src.replace(
        "/* On mobile, hide the BUILT FOR INFERENCE left panel entirely — keep things minimal */",
        "/* On mobile, hide the GAMING LEGENDS left panel entirely — keep things minimal */",
    )
    # Bottom-notice line — full Allen branding
    src = src.replace(
        '<div>ⓘ illustrative interface — metrics decorative, not live fal.ai telemetry</div>\n      <div>prototype by <a href="https://x.com/lovisodin" target="_blank" rel="noopener">lovis odin</a> · skill <a href="https://github.com/fal-ai-community/skills/blob/main/skills/claude.ai/fal-regenerate-3d/SKILL.md" target="_blank" rel="noopener">fal-regenerate-3d →</a></div>',
        '<div>ⓘ illustrative interface — stats are decorative, not real game telemetry</div>\n      <div><b>GAMING LEGENDS</b> · built by <a href="https://allenschiffman.com" target="_blank" rel="noopener">Allen Schiffman</a> · powered by <a href="https://fal.ai" target="_blank" rel="noopener">fal.ai</a> × <a href="https://claude.ai" target="_blank" rel="noopener">Claude</a></div>',
    )

    # ---- 8) Gaming-heritage stat labels (rename only display text, JS keys preserved) ----
    label_renames = [
        # Top bar
        ("STREET CRED", "BOSS KILLS"),
        ("CYBERWARE CAPACITY", "INVENTORY SLOTS"),
        # Left BUILT FOR INFERENCE / now GAMING LEGENDS panel
        ("SPEED · SCALE · ACCURACY", "SPEED · SCALE · LEGACY"),
        ("TOKENS / SEC · LIVE", "DEEDS / SEC · LIVE"),
        ("REQ / 24H", "BATTLES / 24H"),
        ("GPU FLEET", "LOOT CACHE"),
        ("EDGE NETWORK", "KINGDOM REGIONS"),
        ("ALL HEALTHY", "ALL ALIVE"),
        ("LATENCY · P50", "RESPONSE · P50"),
        ("ACTIVE MODELS · 7", "SIGNATURE MOVES · 7"),
        # Right roster header
        ("OPERATOR —", "CHARACTER —"),
        # Bottom bar
        ("EDDY BALANCE", "LEGACY SCORE"),
        (">TASKS<", ">QUESTS<"),  # only the standalone label (avoid matching tasks: in JSON)
        ("ACTIVE</span>", "COMPLETED</span>"),
        ("SYS VER", "GAME VER"),
        # Comments / left-panel internal label
        ("<!-- LEFT — BUILT FOR INFERENCE -->", "<!-- LEFT — GAMING LEGENDS -->"),
        ("<!-- EDDY BALANCE BAR -->", "<!-- LEGACY SCORE BAR -->"),
        ("<!-- RIGHT — OPERATOR SELECT (vertical roster) -->", "<!-- RIGHT — CHARACTER SELECT (vertical roster) -->"),
    ]
    for old, new in label_renames:
        if old not in src:
            print(f"WARNING: rename target not found: {old!r}", file=sys.stderr)
        src = src.replace(old, new)

    # Replace the bottom-bar Indian-rupee currency with a star (legacy theme)
    src = src.replace(
        '<div id="eddyVal" class="tabular-nums" style="color:#fff;font-weight:500;text-shadow:0 1px 4px rgba(15,23,42,.4)">₹ 427,893</div>',
        '<div id="eddyVal" class="tabular-nums" style="color:#fff;font-weight:500;text-shadow:0 1px 4px rgba(15,23,42,.4)">★ 427,893</div>',
    )

    # ---- 9) Show CREATE YOUR OWN tile by default ----
    src = src.replace(
        '<div id="createOwn" class="char" style="display:none;border:1px dashed var(--c2);background:linear-gradient(135deg,rgba(224,242,254,.5),rgba(186,230,253,.4))">',
        '<div id="createOwn" class="char" style="border:1px dashed var(--c2);background:linear-gradient(135deg,rgba(224,242,254,.5),rgba(186,230,253,.4))">',
    )

    # ---- 10) Boot loader resilience: skip cleanly if GLB/video assets missing ----
    src = src.replace(
        "  // 2) Load + add new sliding in from __slideDir side\n"
        "  const gltf = await loader.loadAsync(glbUrl);\n"
        "  window.__bootMark?.('char-glb');\n",
        "  // 2) Load + add new sliding in from __slideDir side\n"
        "  let gltf;\n"
        "  try {\n"
        "    gltf = await loader.loadAsync(glbUrl);\n"
        "  } catch (e) {\n"
        "    console.warn('[swapCharacter] GLB missing, skipping 3D render:', glbUrl);\n"
        "    window.__bootMark?.('char-glb');\n"
        "    window.__bootMark?.('bg-video');\n"
        "    return;\n"
        "  }\n"
        "  window.__bootMark?.('char-glb');\n",
    )
    # Layout comment
    src = src.replace(
        "// Layout: BUILT FOR INFERENCE (3 cols left) + 3D (5 cols center) + ROSTER (4 cols right).",
        "// Layout: GAMING LEGENDS (3 cols left) + 3D (5 cols center) + ROSTER (4 cols right).",
    )
    # Various FAL-08-as-intro comments
    src = src.replace(
        "// FAL-08 is the intro-only character (not in JOB SELECTION). Initial scene loads it directly.",
        "// MASTER-CHIEF is the default first character; the scene loads it on boot.",
    )
    src = src.replace(
        "// FAL-08 is the intro-only model and is not part of the selectable roster.",
        "// MASTER-CHIEF is the default opening character.",
    )

    DST.write_text(src, encoding="utf-8")
    print(f"Wrote {DST} ({len(src):,} bytes)")


if __name__ == "__main__":
    main()
