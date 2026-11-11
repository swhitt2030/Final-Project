from dataclasses import dataclass, field
from math import sin, cos, radians, sqrt
from drafter import *
import matplotlib.pyplot as plt


# Gravity constant (meters per second squared)
GRAVITY = 9.81


@dataclass
class Trajectory:
    """Stores the results of one rocket calculation."""
    velocity: float
    starting_height: float
    launch_angle: float
    maximum_height: float
    flight_time: float
    horizontal_distance: float


@dataclass
class State:
    """Stores user inputs and previous rocket calculations."""
    velocity: str = ""
    starting_height: str = ""
    launch_angle: str = ""
    saved_trajectories: list[Trajectory] = field(default_factory=list)
    message: str = ""


def calculate_values(
    velocity: float,
    starting_height: float,
    launch_angle: float
) -> Trajectory:
    """Calculates the rocket's height, flight time, and distance."""

    angle = radians(launch_angle)

    vertical_velocity = velocity * sin(angle)
    horizontal_velocity = velocity * cos(angle)

    # Calculate the time until the rocket reaches the ground.
    flight_time = (
        vertical_velocity
        + sqrt(vertical_velocity ** 2
               + 2 * GRAVITY * starting_height)
    ) / GRAVITY

    # Calculate maximum height.
    maximum_height = (
        starting_height
        + vertical_velocity ** 2 / (2 * GRAVITY)
    )

    # Calculate horizontal distance.
    horizontal_distance = horizontal_velocity * flight_time

    return Trajectory(
        velocity,
        starting_height,
        launch_angle,
        maximum_height,
        flight_time,
        horizontal_distance
    )


def draw_graph(trajectory: Trajectory) -> None:
    """Creates a professional graph of the rocket's trajectory."""

    angle = radians(trajectory.launch_angle)

    horizontal_velocity = trajectory.velocity * cos(angle)
    vertical_velocity = trajectory.velocity * sin(angle)

    distances = []
    heights = []

    # Calculate 101 points along the rocket's path.
    for step in range(101):
        time = trajectory.flight_time * step / 100

        height = (
            trajectory.starting_height
            + vertical_velocity * time
            - 0.5 * GRAVITY * time ** 2
        )

        distance = horizontal_velocity * time

        distances.append(distance)
        heights.append(height)

    # Create the graph.
    plt.figure(figsize=(9, 5))

    plt.plot(
        distances,
        heights,
        linewidth=3,
        label="Rocket Trajectory"
    )

    # Mark the launch point.
    plt.scatter(
        [0],
        [trajectory.starting_height],
        color="green",
        s=80,
        label="Launch Point",
        zorder=3
    )

    # Mark the landing point.
    plt.scatter(
        [trajectory.horizontal_distance],
        [0],
        color="red",
        s=80,
        label="Landing Point",
        zorder=3
    )

    # Calculate the location of maximum height.
    highest_distance = (
        horizontal_velocity * vertical_velocity / GRAVITY
    )

    # Mark the maximum height.
    plt.scatter(
        [highest_distance],
        [trajectory.maximum_height],
        color="orange",
        s=100,
        label="Maximum Height",
        zorder=3
    )

    plt.annotate(
        "Maximum Height: "
        + str(round(trajectory.maximum_height, 2))
        + " m",
        (highest_distance, trajectory.maximum_height),
        xytext=(10, 15),
        textcoords="offset points"
    )

    # Add graph titles and labels.
    plt.title("Rocket Trajectory", fontsize=16)
    plt.xlabel("Horizontal Distance (meters)")
    plt.ylabel("Height (meters)")

    # Make the graph easier to read.
    plt.xlim(0, max(trajectory.horizontal_distance * 1.1, 1))
    plt.ylim(0, max(trajectory.maximum_height * 1.2, 1))

    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()


@route
def index(
    state: State,
    velocity: str = "",
    starting_height: str = "",
    launch_angle: str = ""
) -> Page:
    """Displays the home page."""

    return Page(state, [
        Text("ROCKET TRAJECTORY ESTIMATOR"),
        Text("Welcome! Explore the science of rocket motion."),
        Text("Enter your rocket's starting information to "
             "calculate its trajectory."),
        Button("Start Calculator", "input_page"),
        Button("View History", "history_page"),
        Button("About This Website", "about_page")
    ])


@route
def input_page(state: State) -> Page:
    """Allows the user to enter rocket measurements."""

    return Page(state, [
        Div(
            Header("ROCKET CALCULATOR"),
            Text("Enter your rocket information below.")
        ),

        Div(
            Text("Initial Velocity (meters per second):"),
            TextBox("velocity", state.velocity),
            style_margin="15px"
        ),

        Div(
            Text("Starting Height (meters):"),
            TextBox("starting_height", state.starting_height),
            style_margin="15px"
        ),

        Div(
            Text("Launch Angle (degrees):"),
            TextBox("launch_angle", state.launch_angle),
            style_margin="15px"
        ),

        Div(
            Button("Calculate Trajectory", "calculate_trajectory"),
            style_margin="15px"
        )
    ])



@route
def calculate_trajectory(
    state: State,
    velocity: str,
    starting_height: str,
    launch_angle: str
) -> Page:
    """Checks the inputs and calculates the rocket's trajectory."""

    # Convert the user's inputs into numbers.
    try:
        velocity_number = float(velocity)
        height_number = float(starting_height)
        angle_number = float(launch_angle)

    except ValueError:
        state.message = "Please fill in all three boxes with numbers."
        return Page(state, [
            Text(state.message),
            Button("Try Again", "input_page"),
            Button("Return Home", "index")
        ])

    # Save the user's inputs.
    state.velocity = velocity
    state.starting_height = starting_height
    state.launch_angle = launch_angle

    # Check that the inputs are valid.
    if velocity_number <= 0:
        state.message = "Velocity must be greater than zero."
        return Page(state, [
            Text(state.message),
            Button("Try Again", "input_page")
        ])

    if height_number < 0:
        state.message = "Starting height cannot be negative."
        return Page(state, [
            Text(state.message),
            Button("Try Again", "input_page")
        ])

    if angle_number < 0 or angle_number > 90:
        state.message = "Angle must be between 0 and 90 degrees."
        return Page(state, [
            Text(state.message),
            Button("Try Again", "input_page")
        ])

    if angle_number == 0 and height_number == 0:
        state.message = "Use a positive launch angle or starting height."
        return Page(state, [
            Text(state.message),
            Button("Try Again", "input_page")
        ])

    # Calculate the rocket's trajectory.
    result = calculate_values(
        velocity_number,
        height_number,
        angle_number
    )

    # Save the calculation in the history.
    state.saved_trajectories.append(result)

    state.message = "Your rocket calculation was successful!"

    return results_page(state)


@route
def results_page(state: State) -> Page:
    """Displays the rocket calculation and trajectory graph."""

    if len(state.saved_trajectories) == 0:
        return Page(state, [
            Text("No calculations have been completed."),
            Button("Start Calculator", "input_page"),
            Button("Return Home", "index")
        ])

    result = state.saved_trajectories[-1]

    # Draw the graph before displaying the page.
    draw_graph(result)

    return Page(state, [
        Text("ROCKET TRAJECTORY RESULTS"),
        Text(state.message),

        Text("Initial Velocity: "
             + str(result.velocity) + " m/s"),

        Text("Starting Height: "
             + str(result.starting_height) + " m"),

        Text("Launch Angle: "
             + str(result.launch_angle) + " degrees"),

        Text("Maximum Height: "
             + str(round(result.maximum_height, 2)) + " m"),

        Text("Flight Time: "
             + str(round(result.flight_time, 2)) + " seconds"),

        Text("Horizontal Distance: "
             + str(round(result.horizontal_distance, 2)) + " m"),

        Text("ROCKET TRAJECTORY GRAPH"),

        MatPlotLibPlot(),

        Button("Calculate Another Rocket", "input_page"),
        Button("View History", "history_page"),
        Button("Return Home", "index")
    ])


@route
def history_page(state: State) -> Page:
    """Displays the user's previous rocket calculations."""

    history = [
        Text("CALCULATION HISTORY"),
        Text("Here are your previously calculated trajectories.")
    ]

    # Check whether the user has saved calculations.
    if len(state.saved_trajectories) == 0:
        history.append(Text("No saved calculations yet."))

    else:
        # Display each saved rocket calculation.
        for number, trajectory in enumerate(
            state.saved_trajectories
        ):
            history.append(Text(
                "Calculation " + str(number + 1)
            ))

            history.append(Text(
                "Velocity: " + str(trajectory.velocity) + " m/s"
            ))

            history.append(Text(
                "Launch Angle: "
                + str(trajectory.launch_angle) + " degrees"
            ))

            history.append(Text(
                "Maximum Height: "
                + str(round(trajectory.maximum_height, 2)) + " m"
            ))

            history.append(Text(
                "Horizontal Distance: "
                + str(round(trajectory.horizontal_distance, 2))
                + " m"
            ))

    history.append(Button("Calculate Another Rocket", "input_page"))
    history.append(Button("Clear History", "clear_history"))
    history.append(Button("Return Home", "index"))

    return Page(state, history)


@route
def clear_history(state: State) -> Page:
    """Clears all saved rocket calculations."""

    state.saved_trajectories.clear()
    state.message = "Your calculation history has been cleared."

    return Page(state, [
        Text(state.message),
        Button("Calculate Again", "input_page"),
        Button("Return Home", "index")
    ])


@route
def about_page(state: State) -> Page:
    """Explains the purpose of the website."""

    return Page(state, [
        Text("ABOUT THE ROCKET TRAJECTORY ESTIMATOR"),

        Text("This website is an educational projectile motion "
             "calculator."),

        Text("Users enter an initial velocity, starting height, "
             "and launch angle."),

        Text("The program uses physics equations to calculate "
             "maximum height, flight time, and horizontal distance."),

        Text("It assumes constant gravity and no air resistance."),

        Text("This website is designed for educational and "
             "entertainment purposes, not real rocket launches."),

        Button("Start Calculator", "input_page"),
        Button("Return Home", "index")
    ])


# Test the calculation function.
def test_calculate_values():
    """Checks the accuracy of the projectile calculations."""

    result = calculate_values(30.0, 0.0, 45.0)

    assert abs(result.maximum_height - 22.94) < 0.05
    assert abs(result.flight_time - 4.32) < 0.05
    assert abs(result.horizontal_distance - 91.74) < 0.1


# Run the test.
test_calculate_values()


# Website information.
# Replace Your Name with your actual name.

set_site_information(
    "Sydney Whittaker",
    "An educational rocket trajectory calculator.",
    ["OpenStax College Physics 2e: Projectile Motion"],
    ["Rocket Trajectory Estimator: Enter velocity, starting "
     "height, and launch angle to calculate projectile motion."],
    []
)


# Start the website.

start_server(State())