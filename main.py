from dataclasses import dataclass
from drafter import *

START_HOURS = 8
START_MONEY = 5
START_ROOM = "Entrance"
START_MESSAGE = "You stand at the dungeon entrance."
VAULT_COST = 15
POWER_UP_VALUE = 20
POWER_UP_BONUS = 5
LOOT_GOAL = 40
ROOMS = ["Crystal Cave", "Goblin Den", "Flooded Tunnel", "Vault"]
IMAGE_WIDTH = 480
START_PICTURE = "dungeon escape starting page.jpg"
EXPLORE_PICTURE = "which way.jpg"


@dataclass
class Item:
    """A piece of loot the player can pick up.

    Attributes:
        name: The name of the item.
        description: What the item is like.
        value: How much the item is worth.
    """

    name: str
    description: str
    value: int


@dataclass
class State:
    """Everything the game remembers between pages.

    Attributes:
        player_name: The name the player typed on the start screen.
        hours_left: Time left before the dungeon collapses.
        dungeon_room: The room the player is currently in.
        money: Coins the player is carrying; they unlock the Vault.
        inventory: The Items the player has picked up.
        message: A line describing what happened most recently.
    """

    player_name: str
    hours_left: int
    dungeon_room: str
    money: int
    inventory: list[Item]
    message: str


def new_state() -> State:
    """Creates the starting State for a new game."""
    return State("", START_HOURS, START_ROOM, START_MONEY, [], START_MESSAGE)


def make_item(room: str) -> Item:
    """Creates the loot hidden in the given room."""
    if room == "Crystal Cave":
        return Item("Glowing Crystal", "Hums with soft light.", 25)
    elif room == "Goblin Den":
        return Item("Goblin Dagger", "Chipped but still sharp.", 10)
    elif room == "Flooded Tunnel":
        return Item("Soggy Map", "Shows a shortcut out.", 5)
    else:
        return Item("Dragon Egg", "Warm and heavy.", 40)


def room_cost(room: str) -> int:
    """Returns how many hours it takes to search the given room."""
    if room == "Crystal Cave":
        return 2
    elif room == "Goblin Den":
        return 3
    elif room == "Flooded Tunnel":
        return 1
    else:
        return 2


def room_coins(room: str) -> int:
    """Returns how many coins the player finds just by searching the room."""
    if room == "Crystal Cave":
        return 5
    elif room == "Goblin Den":
        return 10
    elif room == "Flooded Tunnel":
        return 2
    else:
        return 0


def room_description(room: str) -> str:
    """Returns the story text for the given room."""
    if room == "Crystal Cave":
        return "Glowing crystals hum along the walls. One of them is loose."
    elif room == "Goblin Den":
        return "Goblins snore around a fire. Their loot pile is right there."
    elif room == "Flooded Tunnel":
        return "Cold water rises to your knees. Something floats nearby."
    else:
        return "The guard steps aside. A dragon egg rests on an altar."


def room_picture(room: str) -> str:
    """Returns the filename of the picture for the given room."""
    if room == "Crystal Cave":
        return "crystal cave.jpg"
    elif room == "Goblin Den":
        return "goblin den.jpg"
    elif room == "Flooded Tunnel":
        return "flooded tunnel.jpg"
    else:
        return "the vault.jpg"


def ending_picture(ending: str) -> str:
    """Returns the filename of the picture for the given ending."""
    if ending == "victory":
        return "victory.jpg"
    else:
        return "fail page.jpg"


def picture(filename: str) -> Image:
    """Builds a picture component from an image file in the repository."""
    return Image(filename, width=IMAGE_WIDTH)


def has_item(items: list[Item], name: str) -> bool:
    """Returns True if an item with the given name is in the list."""
    for item in items:
        if item.name == name:
            return True
    return False


def total_loot_value(items: list[Item]) -> int:
    """Adds up the value of every item in the list."""
    total = 0
    for item in items:
        total = total + item.value
    return total


def count_power_ups(items: list[Item]) -> int:
    """Counts the items valuable enough to give a power-up."""
    power_ups = 0
    for item in items:
        if item.value > POWER_UP_VALUE:
            power_ups = power_ups + 1
    return power_ups


def final_score(items: list[Item]) -> int:
    """Loot value plus a bonus for every power-up item."""
    return total_loot_value(items) + POWER_UP_BONUS * count_power_ups(items)


def inventory_lines(items: list[Item]) -> list[str]:
    """Turns each item into a line of text for display."""
    lines = []
    for item in items:
        line = item.name + " (worth " + str(item.value) + "): "
        lines.append(line + item.description)
    return lines


def room_lines() -> list[str]:
    """Describes how long each room takes to search."""
    lines = []
    for room in ROOMS:
        lines.append(room + ": " + str(room_cost(room)) + " hours")
    return lines


def pick_ending(state: State) -> str:
    """Decides the ending: late, poor, or victory."""
    if state.hours_left <= 0:
        return "late"
    elif final_score(state.inventory) < LOOT_GOAL:
        return "poor"
    else:
        return "victory"


def ending_text(ending: str, name: str) -> str:
    """Returns the story text for the given ending."""
    if ending == "late":
        return name + ", the tunnel collapses behind you. You are trapped."
    elif ending == "poor":
        return name + ", you escaped, but with too little loot to matter."
    else:
        return name + ", you stagger into the sunlight with a fortune!"


def ending_page(state: State, ending: str) -> Page:
    """Builds the victory or fail page for the given ending."""
    if ending == "victory":
        title = "Victory!"
    else:
        title = "Game Over"
    return Page(state, [
        Header(title),
        picture(ending_picture(ending)),
        ending_text(ending, state.player_name),
        "Final score: " + str(final_score(state.inventory))
        + " (goal: " + str(LOOT_GOAL) + ")",
        "Power-ups earned: " + str(count_power_ups(state.inventory)),
        Button("Play again", "restart"),
    ])


@route
def index(state: State) -> Page:
    """The start screen, where the player enters their name."""
    return Page(state, [
        Header("Dungeon Escape"),
        picture(START_PICTURE),
        "The dungeon is collapsing. Grab " + str(LOOT_GOAL)
        + " points of loot and get out alive!",
        "What is your name?",
        TextBox("name", state.player_name),
        Button("Enter the dungeon", "start_game"),
    ])


@route
def start_game(state: State, name: str) -> Page:
    """Saves the player's name and starts the adventure."""
    if name.strip() == "":
        return Page(state, [
            Header("Wait!"),
            "Please enter a name.",
            Button("Back", "index"),
        ])
    state.player_name = name
    state.message = "Welcome, " + name + ". The ceiling groans above you."
    return time_left(state)


@route
def time_left(state: State) -> Page:
    """The crossroads page. Shows the time left, or game over at 0 hours."""
    if state.hours_left <= 0:
        return ending_page(state, "late")
    return Page(state, [
        Header("Dungeon Crossroads"),
        state.message,
        "Hours left: " + str(state.hours_left),
        "Coins: " + str(state.money),
        "Items carried: " + str(len(state.inventory)),
        Button("Explore a room", "explore"),
        Button("View items", "view_items"),
        Button("Leave the dungeon", "leave_dungeon"),
    ])


@route
def explore(state: State) -> Page:
    """Lets the player pick which room to enter."""
    return Page(state, [
        Header("Which way?"),
        picture(EXPLORE_PICTURE),
        BulletedList(room_lines()),
        "The Vault guard wants " + str(VAULT_COST) + " coins to open the door.",
        SelectBox("cave", ROOMS, ROOMS[0]),
        Button("Go", "choose_room"),
    ])


@route
def choose_room(state: State, cave: str) -> Page:
    """Moves the player into the chosen room, if they are allowed in."""
    if cave == "Vault" and state.money < VAULT_COST:
        return Page(state, [
            Header("Locked!"),
            picture(room_picture(cave)),
            "The guard blocks the door. You need " + str(VAULT_COST)
            + " coins.",
            Button("Back", "time_left"),
        ])
    state.dungeon_room = cave
    item = make_item(cave)
    return Page(state, [
        Header(cave),
        picture(room_picture(cave)),
        room_description(cave),
        CheckBox("take_item", False),
        "Pick up the " + item.name + " (worth " + str(item.value) + ")",
        Button("Continue", "loot_room"),
    ])


@route
def loot_room(state: State, take_item: bool) -> Page:
    """Spends time and coins in the room and maybe takes its loot."""
    room = state.dungeon_room
    state.hours_left = state.hours_left - room_cost(room)
    state.money = state.money + room_coins(room)
    if room == "Vault":
        state.money = state.money - VAULT_COST
    item = make_item(room)
    if take_item and not has_item(state.inventory, item.name):
        state.inventory.append(item)
        state.message = ("You took the " + item.name + " (worth "
                         + str(item.value) + ").")
    else:
        state.message = "You leave the " + room + " with nothing new."
    return time_left(state)


@route
def view_items(state: State) -> Page:
    """Shows the inventory and the total value of the loot."""
    lines = inventory_lines(state.inventory)
    if len(lines) == 0:
        lines = ["Your pack is empty."]
    return Page(state, [
        Header("Your Items"),
        BulletedList(lines),
        "Total loot value: " + str(total_loot_value(state.inventory)),
        "Coins: " + str(state.money),
        Button("Back", "time_left"),
    ])


@route
def leave_dungeon(state: State) -> Page:
    """Asks the player to confirm before escaping."""
    warning = ""
    if len(state.inventory) == 0:
        warning = "Your pack is empty. You will not impress anyone."
    return Page(state, [
        Header("The Exit"),
        warning,
        "Your score so far: " + str(final_score(state.inventory))
        + " (goal: " + str(LOOT_GOAL) + ")",
        Button("Escape now", "finale"),
        Button("Keep exploring", "time_left"),
    ])


@route
def finale(state: State) -> Page:
    """Scores the loot and shows the final screen."""
    return ending_page(state, pick_ending(state))


@route
def restart(state: State) -> Page:
    """Resets the game and returns to the start screen."""
    state.player_name = ""
    state.hours_left = START_HOURS
    state.dungeon_room = START_ROOM
    state.money = START_MONEY
    state.inventory = []
    state.message = START_MESSAGE
    return index(state)


def run_tests() -> None:
    """Unit tests for the helper functions and the routes."""
    crystal = Item("Glowing Crystal", "Hums with soft light.", 25)
    dagger = Item("Goblin Dagger", "Chipped but still sharp.", 10)
    soggy = Item("Soggy Map", "Shows a shortcut out.", 5)
    egg = Item("Dragon Egg", "Warm and heavy.", 40)

    assert_equal(make_item("Crystal Cave"), crystal)
    assert_equal(make_item("Goblin Den"), dagger)
    assert_equal(make_item("Flooded Tunnel"), soggy)
    assert_equal(make_item("Vault"), egg)
    assert_equal(room_cost("Goblin Den"), 3)
    assert_equal(room_cost("Flooded Tunnel"), 1)
    assert_equal(room_coins("Goblin Den"), 10)
    assert_equal(room_coins("Vault"), 0)
    assert_equal(room_picture("Crystal Cave"), "crystal cave.jpg")
    assert_equal(room_picture("Goblin Den"), "goblin den.jpg")
    assert_equal(room_picture("Flooded Tunnel"), "flooded tunnel.jpg")
    assert_equal(room_picture("Vault"), "the vault.jpg")
    assert_equal(ending_picture("victory"), "victory.jpg")
    assert_equal(ending_picture("late"), "fail page.jpg")
    assert_equal(ending_picture("poor"), "fail page.jpg")
    assert_equal(has_item([crystal, dagger], "Goblin Dagger"), True)
    assert_equal(has_item([crystal], "Goblin Dagger"), False)
    assert_equal(has_item([], "Goblin Dagger"), False)
    assert_equal(total_loot_value([]), 0)
    assert_equal(total_loot_value([crystal, dagger]), 35)
    assert_equal(count_power_ups([crystal, dagger, egg]), 2)
    assert_equal(count_power_ups([dagger, soggy]), 0)
    assert_equal(final_score([crystal, dagger]), 40)
    assert_equal(inventory_lines([]), [])
    assert_equal(inventory_lines([soggy]),
                 ["Soggy Map (worth 5): Shows a shortcut out."])
    assert_equal(pick_ending(State("A", 0, "Vault", 0, [egg], "")), "late")
    assert_equal(pick_ending(State("A", 3, "Vault", 0, [soggy], "")), "poor")
    assert_equal(pick_ending(State("A", 3, "Vault", 0, [crystal, dagger], "")),
                 "victory")
    assert_equal(ending_text("late", "Ada"),
                 "Ada, the tunnel collapses behind you. You are trapped.")

    s = new_state()
    start_game(s, "  ")
    assert_equal(s.player_name, "")
    start_game(s, "Ada")
    assert_equal(s.player_name, "Ada")

    s = new_state()
    choose_room(s, "Vault")
    assert_equal(s.dungeon_room, START_ROOM)
    choose_room(s, "Goblin Den")
    assert_equal(s.dungeon_room, "Goblin Den")

    s = new_state()
    choose_room(s, "Crystal Cave")
    loot_room(s, True)
    assert_equal(s.hours_left, START_HOURS - 2)
    assert_equal(s.money, START_MONEY + 5)
    assert_equal(s.inventory, [crystal])
    loot_room(s, True)
    assert_equal(s.inventory, [crystal])
    assert_equal(s.hours_left, START_HOURS - 4)

    s = new_state()
    choose_room(s, "Flooded Tunnel")
    loot_room(s, False)
    assert_equal(s.inventory, [])
    assert_equal(s.money, START_MONEY + 2)
    assert_equal(s.hours_left, START_HOURS - 1)

    s = new_state()
    s.money = VAULT_COST
    choose_room(s, "Vault")
    assert_equal(s.dungeon_room, "Vault")
    loot_room(s, True)
    assert_equal(s.money, 0)
    assert_equal(s.inventory, [egg])

    s = State("Ada", 3, "Vault", 9, [egg], "Hi")
    restart(s)
    assert_equal(s, new_state())

    s = new_state()
    index(s)
    explore(s)
    time_left(s)
    view_items(s)
    leave_dungeon(s)
    finale(s)
    assert_equal(s, new_state())
    s.hours_left = 0
    time_left(s)
    assert_equal(s.hours_left, 0)


run_tests()

set_website_title("Dungeon Escape")
set_site_information(
    author="Jayden Pajanel (jaypaj@udel.edu)",
    description="A story game where you collect coins and get items "
                "to escape a dungeon.",
    sources="Drafter documentation and an AI assistant (see the LLM "
            "conversation file in the repository).",
    planning=["Copy of CS1 Final Project 0_ Pick a Problem.pdf",
              "Copy of CS1 Final Project 1_ Design.pdf"],
    links=["https://github.com/jaydenpaj/Dungeon_escape"],
)
hide_debug_information()
set_website_framed(False)
start_server(new_state())
