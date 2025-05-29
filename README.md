# FlappyCl - A Flappy Bird Clone in Python

A simple Flappy Bird clone created using Python and the Pygame library. Fly the bird through the pipes and try to get the highest score!

**GitHub Repository:** [azario0/flappycl](https://github.com/azario0/flappycl)

## Features

*   Classic Flappy Bird gameplay: tap to flap, avoid pipes.
*   Dynamic pipe generation with random gap heights.
*   Scrolling background and ground.
*   Score tracking.
*   High score display (session-based).
*   Basic bird rotation animation.
*   Asset loading with fallback to colored rectangles if images are missing.
*   Automatic resizing of provided image assets to fit game dimensions.
## Requirements

*   Python 3.x
*   Pygame library

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/azario0/flappycl.git
    cd flappycl
    ```

2.  **Install Pygame:**
    If you don't have Pygame installed, you can install it using pip:
    ```bash
    pip install pygame
    ```
    Or, if you use a virtual environment (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install pygame
    ```

## How to Play

1.  **Run the game:**
    Navigate to the directory where you cloned the repository and run:
    ```bash
    python flappy.py
    ```
    (Assuming your main Python file is named `flappy.py`. Adjust if necessary.)

2.  **Controls:**
    *   **Spacebar:** Press Spacebar to make the bird flap upwards.
    *   **Spacebar (on Start/Game Over screen):** Press Spacebar to start or restart the game.
    *   **Escape Key (ESC):** Press Escape to quit the game at any time.

3.  **Objective:**
    Guide the bird through the gaps in the pipes. Each successfully passed pipe pair scores one point. Avoid hitting the pipes or the ground.

## Assets

The game uses the following image assets. If these files are not present in the same directory as the script, the game will attempt to run using colored rectangles as fallbacks.

*   `bird.png`: The bird sprite.
*   `pipe.png`: A segment of the pipe.
*   `background.png`: The game's background image.
*   `ground.png`: The scrolling ground strip.

You can replace these with your own assets. The game will attempt to resize them to fit the required dimensions. Recommended base dimensions for assets before resizing are:
*   Bird: ~34x24 pixels
*   Pipe Segment: ~52x320 pixels
*   Background: ~288x512 pixels
*   Ground Strip: ~288x100 pixels

## Future Enhancements (Ideas)

*   Sound effects (flapping, scoring, collision).
*   Persistent high score saving (e.g., to a file).
*   Different bird skins or themes.
*   Difficulty levels.
*   Smoother animations or transitions.
*   Pause functionality.

## Contributing

Contributions are welcome! If you have suggestions for improvements or want to fix a bug, feel free to:
1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add some feature'`).
5.  Push to the branch (`git push origin feature/your-feature-name`).
6.  Open a Pull Request.

