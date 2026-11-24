"""
Lock In - a daily task tracker built with Drafter.

Add tasks for the day, check them off, rate your day (1-10), and get a day score.
"""
from dataclasses import dataclass
import random
from typing import Any
from drafter import *
from bakery import assert_equal as bakery_assert_equal

hide_debug_information()
set_website_title("Lock IN Tracker")
set_website_framed(False)


set_site_information(
    author="Tyler Giouzelis",
    description="Lock In: a daily task tracker with a day score.",
    sources=["Drafter documentation: https://drafter-edu.github.io/drafter/"],
    planning="Week 10 and Week 11 worksheets are in this repository.",
    links=["https://github.com/"],
)

# ------------------------------- theme ----------------------------------
# A simple dark "lock in" look: black background, light text, neon green accents.
# "!important" makes sure these win over Drafter's built-in styles.
add_website_css("html, body", "background-color: #0d0d0d !important; "
                              "color: #f2f2f2 !important; "
                              "font-family: Arial, sans-serif;")
add_website_css("div, p, span, label, li, td, th, pre",
                "background-color: transparent !important; "
                "color: #f2f2f2 !important;")
add_website_css("h1, h2, h3, h4", "color: #39ff14 !important; "
                                  "letter-spacing: 2px; "
                                  "text-transform: uppercase;")
add_website_css("button, input[type=submit]",
                "background-color: #39ff14 !important; "
                "color: #0d0d0d !important; font-weight: bold; "
                "border: none; border-radius: 4px; padding: 6px 14px; "
                "margin: 3px; cursor: pointer;")
add_website_css("input, textarea, select",
                "background-color: #1c1c1c !important; "
                "color: #f2f2f2 !important; "
                "border: 1px solid #39ff14; border-radius: 4px; padding: 4px;")
add_website_css("hr", "border-color: #39ff14;")

RATINGS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
NOT_RATED = 0
NO_TASK = "(No task - just rate my day)"
QUOTES = [
    "Discipline is choosing what you want most over what you want now.",
    "Small steps every day beat big plans someday.",
    "You do not have to feel ready. You just have to start.",
    "Lock in now, rest later.",
    "Your future self is watching what you do today.",
    "Done is better than perfect.",
    "Motivation gets you going. Habit keeps you going.",
    "One finished task is worth ten good intentions.",
    "Focus on the next right thing, not everything at once.",
    "Progress is progress, no matter how small.",
    "Show up even when it is boring. Especially when it is boring.",
    "Hard work is quiet. Results are loud.",
    "Today's effort is tomorrow's momentum.",
    "Make your goals so clear that excuses have nowhere to hide.",
    "Win the day, and the weeks will take care of themselves.",
]
SCORE_EXPLANATION = ("Day score = half your tasks done (%) + half your "
                     "day rating (1-10 scaled to 100).")


@dataclass
class Goal:
    name: str
    done: bool
    note: str


@dataclass
class State:
    goals: list[Goal]
    user_name: str
    day_rating: int
    daily_note: str
    message: str
    quote_number: int
    open_task: str



def count_done(goals: list[Goal]) -> int:
    """Count how many goals are marked done."""
    total = 0
    for goal in goals:
        if goal.done:
            total = total + 1
    return total


def percent_done(goals: list[Goal]) -> int:
    """Return the percent (0-100) of goals done; an empty list gives 0."""
    if len(goals) == 0:
        return 0
    return round(count_done(goals) / len(goals) * 100)


def day_score(percent: int, rating: int) -> int:
    """Combine percent done (0-100) and the day rating (1-10) into a score.

    A rating of 0 (NOT_RATED) means the user has not rated the day yet.
    """
    if rating == NOT_RATED:
        return percent
    return round((percent + rating * 10) / 2)


def status_label(score: int) -> str:
    """Turn a day score into a status message."""
    if score >= 80:
        return "Locked in"
    elif score >= 50:
        return "On track"
    else:
        return "Need a push"


def goal_exists(goals: list[Goal], name: str) -> bool:
    """Return True if a goal with this name (ignoring case) already exists."""
    for goal in goals:
        if goal.name.lower() == name.lower():
            return True
    return False


def goal_line(goal: Goal) -> str:
    """Build one text row for a goal, like '[x] Read'."""
    if goal.done:
        return "[x] " + goal.name
    return "[ ] " + goal.name


def goal_names(goals: list[Goal]) -> list[str]:
    """Return just the names of the goals (for the check-in SelectBox)."""
    names = []
    for goal in goals:
        names.append(goal.name)
    return names


def goal_options(goals: list[Goal]) -> list[str]:
    """Return each goal as '[x] name' or '[ ] name' (for the check-in SelectBox)."""
    options = []
    for goal in goals:
        options.append(goal_line(goal))
    return options


def name_from_option(option: str) -> str:
    """Remove the 4-character '[x] ' or '[ ] ' marker from a goal_line string."""
    return option[4:]


def nav_buttons() -> list:
    """Navigation buttons shown at the bottom of every page."""
    return [
        HorizontalRule(),
        Button("Home", index),
        Button("Tasks", tasks_page),
        Button("Check-in", checkin_page),
        Button("Progress", progress_page),
        Button("Profile", profile_page),
    ]


# -------------------------------- routes --------------------------------
@route
def index(state: State) -> Page:
    """Home page: greeting, tasks done, and a progress bar."""
    if state.user_name == "":
        greeting = "Welcome to Lock In! Set your name on the Profile page."
    else:
        greeting = "Welcome back, " + state.user_name + ". Time to lock in."
    quote = QUOTES[state.quote_number % len(QUOTES)]
    state.quote_number = (state.quote_number + 1) % len(QUOTES)
    content: list[Any] = [
        Header("LOCK IN", 1),
        greeting,
        '"' + quote + '"',
        str(count_done(state.goals)) + " of " + str(len(state.goals)) + " tasks done",
        ProgressBar(percent_done(state.goals) / 100),
    ]
    content.extend(nav_buttons())
    return Page(state, content)


@route
def profile_page(state: State) -> Page:
    """Profile page: set your name."""
    content: list[Any] = [
        Header("Profile", 1),
        "Your name:",
        TextBox("new_name", state.user_name),
        Button("Save profile", save_profile),
    ]
    content.extend(nav_buttons())
    return Page(state, content)


@route
def save_profile(state: State, new_name: str) -> Page:
    """Save the user's name, then go home."""
    state.user_name = new_name.strip()
    return index(state)


@route
def tasks_page(state: State) -> Page:
    """Tasks page: each task has its own button to mark it done or undo it."""
    content: list[Any] = [Header("Tasks", 1)]
    if state.message != "":
        content.append(state.message)
        state.message = ""
    if len(state.goals) == 0:
        content.append("No tasks yet. Add your first one below.")
    else:
        content.append("Tap a task to see its note. Use Finish / Undo to change its status.")
    for goal in state.goals:
        label = goal_line(goal)
        if goal.note != "":
            label = label + "  (has note)"
        content.append(Button(label, toggle_note,
                              [Argument("note_name", goal.name)]))
        if goal.done:
            content.append(Button("Undo", toggle_goal,
                                  [Argument("toggle_name", goal.name)]))
        else:
            content.append(Button("Finish", toggle_goal,
                                  [Argument("toggle_name", goal.name)]))
        if state.open_task == goal.name:
            if goal.note == "":
                content.append("No note yet. Add one on the Check-in page.")
            else:
                content.append("Note: " + goal.note)
    content.append(HorizontalRule())
    content.append("New task:")
    content.append(TextBox("goal_name", ""))
    content.append(Button("Add task", add_goal))
    content.extend(nav_buttons())
    return Page(state, content)


@route
def toggle_note(state: State, note_name: str) -> Page:
    """Open the note under a task, or close it if it is already open."""
    if state.open_task == note_name:
        state.open_task = ""
    else:
        state.open_task = note_name
    return tasks_page(state)


@route
def toggle_goal(state: State, toggle_name: str) -> Page:
    """Flip one goal between done and not done, then show the tasks again."""
    for goal in state.goals:
        if goal.name == toggle_name:
            goal.done = not goal.done
    return tasks_page(state)


@route
def add_goal(state: State, goal_name: str) -> Page:
    """Add a new goal, rejecting blank and repeated names."""
    name = goal_name.strip()
    if name == "":
        state.message = "A task needs a name."
    elif goal_exists(state.goals, name):
        state.message = "You already have a task called '" + name + "'."
    else:
        state.goals.append(Goal(name, False, ""))
        state.message = "Added '" + name + "'."
    return tasks_page(state)


@route
def checkin_page(state: State) -> Page:
    """Check-in page: rate the day, optionally mark a task, and write a note."""
    content: list[Any] = [Header("Check-in", 1)]
    if state.day_rating == NOT_RATED:
        default_rating = "5"
    else:
        default_rating = str(state.day_rating)
    content.append("Step 1: How is your day going? (1 = rough, 10 = great)")
    content.append(SelectBox("rating", RATINGS, default_rating))
    content.append("Step 2 (optional): Update a task ([x] = done, [ ] = not done)")
    content.append(SelectBox("task_name", [NO_TASK] + goal_options(state.goals),
                             NO_TASK))
    content.append("Mark the chosen task as done (uncheck it to mark it not done):")
    content.append(CheckBox("is_done", True))
    content.append("Step 3 (optional): Note for the chosen task (or for the day if no task is chosen)")
    content.append(TextArea("note", ""))
    content.append(Button("Save check-in", save_checkin))
    content.extend(nav_buttons())
    return Page(state, content)


@route
def save_checkin(state: State, task_name: str, is_done: bool,
                 rating: str, note: str) -> Page:
    """Save the rating, then save the note on the chosen task (or the day)."""
    clean_note = note.strip()
    if task_name == NO_TASK:
        if clean_note != "":
            state.daily_note = clean_note
    else:
        chosen_name = name_from_option(task_name)
        for goal in state.goals:
            if goal.name == chosen_name:
                goal.done = is_done
                if clean_note != "":
                    goal.note = clean_note
    state.day_rating = int(rating)
    return progress_page(state)


@route
def progress_page(state: State) -> Page:
    """Progress page: percent, day score, status, explanation, and the note."""
    content: list[Any] = [Header("Progress", 1)]
    if len(state.goals) == 0:
        content.append("No tasks yet, so there is no progress to show.")
    else:
        percent = percent_done(state.goals)
        score = day_score(percent, state.day_rating)
        content.append(str(percent) + "% of tasks done")
        content.append(ProgressBar(percent / 100))
        content.append("Day score: " + str(score) + " / 100")
        content.append(SCORE_EXPLANATION)
        content.append("Status: " + status_label(score))
        if state.daily_note != "":
            content.append("Note: " + state.daily_note)
    content.extend(nav_buttons())
    return Page(state, content)


# ------------------------------ unit tests ------------------------------
def make_state() -> State:
    """Build a fresh State with two goals for the tests."""
    return State([Goal("Read", True, ""), Goal("Run", False, "")], "Tyler", 0, "", "", 0, "")


def test_helpers() -> None:
    """Unit tests for the helper functions."""
    goals = make_state().goals
    bakery_assert_equal(count_done(goals), 1)
    bakery_assert_equal(count_done([]), 0)
    bakery_assert_equal(percent_done(goals), 50)
    bakery_assert_equal(percent_done([]), 0)
    bakery_assert_equal(day_score(50, 0), 50)
    bakery_assert_equal(day_score(50, 8), 65)
    bakery_assert_equal(day_score(100, 10), 100)
    bakery_assert_equal(status_label(80), "Locked in")
    bakery_assert_equal(status_label(50), "On track")
    bakery_assert_equal(status_label(49), "Need a push")
    bakery_assert_equal(goal_exists(goals, "read"), True)
    bakery_assert_equal(goal_exists(goals, "Swim"), False)
    bakery_assert_equal(goal_line(goals[0]), "[x] Read")
    bakery_assert_equal(goal_line(goals[1]), "[ ] Run")
    bakery_assert_equal(goal_names(goals), ["Read", "Run"])
    bakery_assert_equal(goal_options(goals), ["[x] Read", "[ ] Run"])
    bakery_assert_equal(name_from_option("[x] Read"), "Read")
    bakery_assert_equal(name_from_option("[ ] Run"), "Run")
    bakery_assert_equal(len(QUOTES), 15)


def test_page_routes() -> None:
    """Unit tests for the routes that only show a page."""
    state = make_state()
    bakery_assert_equal(index(state).state, state)
    bakery_assert_equal(profile_page(state).state, state)
    bakery_assert_equal(tasks_page(state).state, state)
    bakery_assert_equal(checkin_page(state).state, state)
    bakery_assert_equal(progress_page(state).state, state)
    empty = State([], "", 0, "", "", 0, "")
    bakery_assert_equal(len(checkin_page(empty).state.goals), 0)
    bakery_assert_equal(len(progress_page(empty).state.goals), 0)


def test_quotes() -> None:
    """Unit test: the home page shows a quote and moves to the next one."""
    state = make_state()
    index(state)
    bakery_assert_equal(state.quote_number, 1)
    state.quote_number = len(QUOTES) - 1
    index(state)
    bakery_assert_equal(state.quote_number, 0)


def test_save_profile() -> None:
    """Unit test for save_profile."""
    state = make_state()
    save_profile(state, "  Sam ")
    bakery_assert_equal(state.user_name, "Sam")


def test_add_goal() -> None:
    """Unit tests for add_goal, including blank and repeated names."""
    state = make_state()
    add_goal(state, "Study")
    bakery_assert_equal(len(state.goals), 3)
    add_goal(state, "   ")
    bakery_assert_equal(len(state.goals), 3)
    add_goal(state, "study")
    bakery_assert_equal(len(state.goals), 3)


def test_toggle_goal() -> None:
    """Unit tests for toggle_goal: flips done both ways, ignores unknown names."""
    state = make_state()
    toggle_goal(state, "Run")
    bakery_assert_equal(state.goals[1].done, True)
    toggle_goal(state, "Run")
    bakery_assert_equal(state.goals[1].done, False)
    toggle_goal(state, "Nope")
    bakery_assert_equal(count_done(state.goals), 1)


def test_save_checkin() -> None:
    """Unit tests for save_checkin, with and without a chosen task."""
    state = make_state()
    save_checkin(state, "[ ] Run", True, "4", "Good day")
    bakery_assert_equal(state.goals[1].done, True)
    bakery_assert_equal(state.day_rating, 4)
    bakery_assert_equal(state.goals[1].note, "Good day")
    bakery_assert_equal(state.daily_note, "")
    # rating only, no task chosen: tasks stay the same
    state2 = make_state()
    save_checkin(state2, NO_TASK, True, "9", "")
    bakery_assert_equal(state2.day_rating, 9)
    bakery_assert_equal(count_done(state2.goals), 1)
    # no task chosen but a note: it becomes the day note
    save_checkin(state2, NO_TASK, True, "9", "Long day")
    bakery_assert_equal(state2.daily_note, "Long day")
    # each task keeps its own note; a blank note does not erase an old one
    state3 = make_state()
    save_checkin(state3, "[x] Read", True, "5", "Chapter 3")
    save_checkin(state3, "[ ] Run", False, "5", "3 miles")
    bakery_assert_equal(state3.goals[0].note, "Chapter 3")
    bakery_assert_equal(state3.goals[1].note, "3 miles")
    save_checkin(state3, "[x] Read", True, "5", "   ")
    bakery_assert_equal(state3.goals[0].note, "Chapter 3")


def test_toggle_note() -> None:
    """Unit tests for toggle_note: open a task's note, switch, then close it."""
    state = make_state()
    toggle_note(state, "Run")
    bakery_assert_equal(state.open_task, "Run")
    toggle_note(state, "Read")
    bakery_assert_equal(state.open_task, "Read")
    toggle_note(state, "Read")
    bakery_assert_equal(state.open_task, "")


def run_tests() -> None:
    """Run every unit test."""
    test_helpers()
    test_page_routes()
    test_quotes()
    test_save_profile()
    test_add_goal()
    test_toggle_goal()
    test_toggle_note()
    test_save_checkin()


run_tests()

start_server(State([], "", 0, "", "", random.randrange(len(QUOTES)), ""))
