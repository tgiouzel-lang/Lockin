"""
Lock In - a daily task tracker built with Drafter.

Add tasks for the day, check them off, rate your day, and get a day score.
"""
from dataclasses import dataclass
from drafter import *
from bakery import assert_equal

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

RATINGS = ["1", "2", "3", "4", "5"]


@dataclass
class Goal:
    name: str
    done: bool


@dataclass
class State:
    goals: list[Goal]
    user_name: str
    day_rating: int
    daily_note: str
    message: str



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
    """Combine percent done (0-100) and the day rating (1-5) into a score.

    A rating of 0 means the user has not rated the day yet.
    """
    if rating == 0:
        return percent
    return round((percent + rating * 20) / 2)


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
    content = [
        "Lock In",
        greeting,
        str(count_done(state.goals)) + " of " + str(len(state.goals)) + " tasks done",
        ProgressBar(percent_done(state.goals) / 100),
    ]
    content.extend(nav_buttons())
    return Page(state, content)


@route
def profile_page(state: State) -> Page:
    """Profile page: set your name."""
    content = [
        "Profile",
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
    """Tasks page: shows every task and a form to add a new one."""
    content = ["Tasks"]
    if state.message != "":
        content.append(state.message)
        state.message = ""
    if len(state.goals) == 0:
        content.append("No tasks yet. Add your first one below.")
    for goal in state.goals:
        content.append(goal_line(goal))
    content.append(HorizontalRule())
    content.append("New task:")
    content.append(TextBox("goal_name", ""))
    content.append(Button("Add task", add_goal))
    content.extend(nav_buttons())
    return Page(state, content)


@route
def add_goal(state: State, goal_name: str) -> Page:
    """Add a new goal, rejecting blank and repeated names."""
    name = goal_name.strip()
    if name == "":
        state.message = "A task needs a name."
    elif goal_exists(state.goals, name):
        state.message = "You already have a task called '" + name + "'."
    else:
        state.goals.append(Goal(name, False))
        state.message = "Added '" + name + "'."
    return tasks_page(state)


@route
def checkin_page(state: State) -> Page:
    """Check-in page: mark a task, rate the day, and write a note."""
    content = ["Check-in"]
    if len(state.goals) == 0:
        content.append("No tasks yet. Add a task first, then come back.")
    else:
        content.append("Which task?")
        content.append(SelectBox("task_name", goal_names(state.goals)))
        content.append(CheckBox("is_done", True))
        content.append("Mark as done")
        content.append("How is your day going? (1 = rough, 5 = great)")
        content.append(SelectBox("rating", RATINGS, "3"))
        content.append("Note for the day:")
        content.append(TextArea("note", state.daily_note))
        content.append(Button("Save check-in", save_checkin))
    content.extend(nav_buttons())
    return Page(state, content)


@route
def save_checkin(state: State, task_name: str, is_done: bool,
                 rating: str, note: str) -> Page:
    """Update the chosen goal, the day rating, and the note, then show progress."""
    for goal in state.goals:
        if goal.name == task_name:
            goal.done = is_done
    state.day_rating = int(rating)
    state.daily_note = note
    return progress_page(state)


@route
def progress_page(state: State) -> Page:
    """Progress page: percent, day score, status, and the note."""
    content = ["Progress"]
    if len(state.goals) == 0:
        content.append("No tasks yet, so there is no progress to show.")
    else:
        percent = percent_done(state.goals)
        score = day_score(percent, state.day_rating)
        content.append(str(percent) + "% of tasks done")
        content.append(ProgressBar(percent / 100))
        content.append("Day score: " + str(score) + " / 100")
        content.append("Status: " + status_label(score))
        if state.daily_note != "":
            content.append("Note: " + state.daily_note)
    content.extend(nav_buttons())
    return Page(state, content)


# ------------------------------ unit tests ------------------------------
def make_state() -> State:
    """Build a fresh State with two goals for the tests."""
    return State([Goal("Read", True), Goal("Run", False)], "Tyler", 0, "", "")


def test_helpers() -> None:
    """Unit tests for the helper functions."""
    goals = make_state().goals
    assert_equal(count_done(goals), 1)
    assert_equal(count_done([]), 0)
    assert_equal(percent_done(goals), 50)
    assert_equal(percent_done([]), 0)
    assert_equal(day_score(50, 0), 50)
    assert_equal(day_score(50, 4), 65)
    assert_equal(status_label(80), "Locked in")
    assert_equal(status_label(50), "On track")
    assert_equal(status_label(49), "Need a push")
    assert_equal(goal_exists(goals, "read"), True)
    assert_equal(goal_exists(goals, "Swim"), False)
    assert_equal(goal_line(goals[0]), "[x] Read")
    assert_equal(goal_line(goals[1]), "[ ] Run")
    assert_equal(goal_names(goals), ["Read", "Run"])


def test_page_routes() -> None:
    """Unit tests for the routes that only show a page."""
    state = make_state()
    assert_equal(index(state).state, state)
    assert_equal(profile_page(state).state, state)
    assert_equal(tasks_page(state).state, state)
    assert_equal(checkin_page(state).state, state)
    assert_equal(progress_page(state).state, state)
    empty = State([], "", 0, "", "")
    assert_equal(len(checkin_page(empty).state.goals), 0)
    assert_equal(len(progress_page(empty).state.goals), 0)


def test_save_profile() -> None:
    """Unit test for save_profile."""
    state = make_state()
    save_profile(state, "  Sam ")
    assert_equal(state.user_name, "Sam")


def test_add_goal() -> None:
    """Unit tests for add_goal, including blank and repeated names."""
    state = make_state()
    add_goal(state, "Study")
    assert_equal(len(state.goals), 3)
    add_goal(state, "   ")
    assert_equal(len(state.goals), 3)
    add_goal(state, "study")
    assert_equal(len(state.goals), 3)


def test_save_checkin() -> None:
    """Unit test for save_checkin."""
    state = make_state()
    save_checkin(state, "Run", True, "4", "Good day")
    assert_equal(state.goals[1].done, True)
    assert_equal(state.day_rating, 4)
    assert_equal(state.daily_note, "Good day")


def run_tests() -> None:
    """Run every unit test."""
    test_helpers()
    test_page_routes()
    test_save_profile()
    test_add_goal()
    test_save_checkin()


run_tests()

start_server(State([], "", 0, "", ""))
