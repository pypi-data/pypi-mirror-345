"""Example using GameSir T1d controller with pygame visualization."""

import pygame
import time
from gamesir_t1d import GameSirT1dPygame


def run(controller_name):
    """Initialize pygame and controller, then visualize controller input."""
    # Initialize pygame for window and graphics
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("GameSir T1d Test")
    clock = pygame.time.Clock()

    # Initialize our custom controller
    controller = GameSirT1dPygame(controller_name)
    print("Connecting to controller...")
    if not controller.init():
        print("Failed to connect to controller")
        # Clean up pygame on early exit
        pygame.quit()
        return

    running = True
    while running:
        # Process pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Read joystick values
        left_x = controller.get_axis(0)
        left_y = controller.get_axis(1)
        right_x = controller.get_axis(2)
        right_y = controller.get_axis(3)

        # Clear screen
        screen.fill((0, 0, 0))

        # Draw joystick positions
        pygame.draw.circle(
            screen, (50, 50, 50), (160, 240), 100
        )  # Left stick background
        pygame.draw.circle(
            screen, (0, 255, 0), (160 + int(left_x * 80), 240 + int(left_y * 80)), 20
        )  # Left stick position

        pygame.draw.circle(
            screen, (50, 50, 50), (480, 240), 100
        )  # Right stick background
        pygame.draw.circle(
            screen, (0, 255, 0), (480 + int(right_x * 80), 240 + int(right_y * 80)), 20
        )  # Right stick position

        # Update display
        pygame.display.flip()

        # Control frame rate
        clock.tick(60)

    # Clean up
    controller.quit()
    pygame.quit()


def test_without_pygame(controller_name):
    """Test the controller without pygame, printing state to console."""
    # GameSirT1dPygame already imported at the top
    
    # Create and initialize the controller
    controller = GameSirT1dPygame(controller_name)
    print("Initializing controller...")
    if not controller.init():
        print("Failed to initialize controller.")
        return

    print(f"Controller: {controller.get_name()}")
    print(f"Axes: {controller.get_numaxes()}")
    print(f"Buttons: {controller.get_numbuttons()}")
    print(f"Hats: {controller.get_numhats()}")

    try:
        while True:
            # Read axes
            axes = [controller.get_axis(i) for i in range(controller.get_numaxes())]

            # Read buttons
            buttons = [
                controller.get_button(i) for i in range(controller.get_numbuttons())
            ]

            # Read hat
            hat = controller.get_hat(0)

            # Print state
            print(f"\rAxes: {axes}, Buttons: {buttons}, Hat: {hat}", end="")

            # Wait a bit
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        controller.quit()


if __name__ == "__main__":
    controller_name = "Gamesir-T1d-XXXX"  # Change this to match your controller
    
    # Choose which test to run:
    # Uncomment the test you want to run:
    run(controller_name)        # Run the pygame visualization
    # test_without_pygame(controller_name)  # Run without pygame