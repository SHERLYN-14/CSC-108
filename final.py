# IMPORT LIBRARIES
# pygame -- is for application 
# sys -- system functionality (exiting the game)
# time -- delay for the program
# heapq -- Priority queue for algorithm ( A* Algorithm)

import pygame, sys,  time, heapq

# __init__ method
class PuzzleState:
    def __init__(self, board, moves=0, prev=None):
        self.board = board                      # 2D list representing the puzzle state.
        self.moves = moves                      # Number of moves taken to reach this state.
        self.prev = prev                        # Previous state in the path.
        self.empty_pos = self.find_empty()      # Position of the empty tile (0).

# find_empty method
    def find_empty(self):                       
        for i in range(3):                      # Iterate through rows.   
            for j in range(3):                  # Iterate through columns.
                if self.board[i][j] == 0:       # If empty tile is found:
                    return (i, j)               # Return its position as (row, col).
        return None


    def is_goal(self):
        return self.board == [[0, 1, 2], [3, 4, 5], [6, 7, 8]]      # board matches the solved state

    def neighbors(self):
        x, y = self.empty_pos
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
        neighbors = []

        for dx, dy in directions:
            nx, ny = x + dx, y + dy                     # Calculate new positions.
            if 0 <= nx < 3 and 0 <= ny < 3:             # Ensure the new position is valid.
                new_board = [row[:] for row in self.board]      # Copy current board.
                # Swap empty tile with the target tile.
                new_board[x][y], new_board[nx][ny] = new_board[nx][ny], new_board[x][y]
                # Append the new state to neighbors.
                neighbors.append(PuzzleState(new_board, self.moves + 1, self))

        return neighbors

    # Used for comparison and hashing when storing states in data structures.
    def __eq__(self, other):
        return self.board == other.board        # Checks if two states are identical.

    def __lt__(self, other):
        return self.moves < other.moves         # Compares states based on moves (priority queue).

    def __hash__(self):
        return hash(str(self.board))            # Hashes the state for storing in sets.


# Heuristic Function
# Calculates the Manhattan distance heuristic, measuring how far each tile is from its target position.
def manhattan_distance(state):
    distance = 0
    for i in range(3):                      # Loop through rows.
        for j in range(3):                  # Loop through columns.
            value = state.board[i][j]
            if value != 0:
                target_x, target_y = value // 3, value % 3          # Compute target position.
                distance += abs(i - target_x) + abs(j - target_y)
    return distance

#A Algorithm*
def astar_solve(initial_state):
    priority_queue = []
    heapq.heappush(priority_queue, (0, initial_state))      # Push initial state with cost 0.
    visited = set()

    while priority_queue:
        _, current = heapq.heappop(priority_queue)          # Get state with lowest cost.

        if current.is_goal():                               # If it's the goal state, reconstruct path.
            return reconstruct_path(current)

        visited.add(hash(current))                           # Mark current state as visited.

        for neighbor in current.neighbors():                # Loop through neighbors.
            if hash(neighbor) not in visited:               # Process unvisited states.
                cost = neighbor.moves + manhattan_distance(neighbor)    # Total cost (g + h).
                heapq.heappush(priority_queue, (cost, neighbor))         # Add to priority queue.


    return None         # Return None if no solution exists.


def reconstruct_path(state):
    path = []
    while state:
        path.append(state.board)    # Append the current state's board.
        state = state.prev          # Move to the previous state.
    return path[::-1]               # Reverse the path to start with the initial state.


# Drawing the Board
# Pygame visualization
def draw_board(screen, board, font, move_count, show_solve_button=False):
    screen.fill((255, 255, 255))  # White background
    tile_size = 90
    gap = 10

    # Draw puzzle board
    for i in range(3):
        for j in range(3):
            value = board[i][j]
            x, y = j * (tile_size + gap), i * (tile_size + gap)
            if value != 0:      # Draw tiles with numbers (0 - 8)
                pygame.draw.rect(screen, (0, 150, 200), (x, y, tile_size, tile_size), border_radius=10)
                text_surface = font.render(str(value), True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(x + tile_size // 2, y + tile_size // 2))
                screen.blit(text_surface, text_rect)
            else:
                pygame.draw.rect(screen, (200, 200, 200), (x, y, tile_size, tile_size), border_radius=10)

    # Display move count
    move_text = font.render(f"Moves: {move_count}", True, (0, 0, 0))
    screen.blit(move_text, (10, 320))

    # Draw solve button if needed
    if show_solve_button:
        button_width, button_height = 150, 50
        # Draw a blue rectangle for the "SOLVE" button
        pygame.draw.rect(screen, (0, 0, 155), (230, 310, button_width, button_height))
        # Render the "SOLVE" text
        button_text = font.render("SOLVE(AI)", True, (255, 255, 255))
        #button_rect = button_text.get_rect(center=(280, 330))
        button_rect = button_text.get_rect(center=(230 + button_width // 2, 310 + button_height // 2))  # Centered in the 
        # Blit the text onto the button
        screen.blit(button_text, button_rect)


def get_tile_at_pos(pos):
    x, y = pos
    col = x // 100
    row = y // 100
    if 0 <= row < 3 and 0 <= col < 3:
        return row, col
    return None


def main():
    pygame.init()

    # Screen setup
    screen = pygame.display.set_mode((350, 350))
    pygame.display.set_caption("Eight Puzzle Game")
    font = pygame.font.Font(None, 48)

    # For puzzle setup 
    original_board = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8]
    ]
    puzzle_state = PuzzleState([row[:] for row in original_board])  # Copy of the original board
    arranging = True
    move_count = 0
    solution = []

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if arranging:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    tile = get_tile_at_pos(pos)
                    if tile:
                        empty_x, empty_y = puzzle_state.empty_pos
                        if abs(tile[0] - empty_x) + abs(tile[1] - empty_y) == 1:
                            # Swap clicked tile with the empty tile
                            puzzle_state.board[empty_x][empty_y], puzzle_state.board[tile[0]][tile[1]] = \
                                puzzle_state.board[tile[0]][tile[1]], puzzle_state.board[empty_x][empty_y]
                            puzzle_state.empty_pos = tile

                    # Check if "SOLVE" button is clicked
                    if 230 <= pos[0] <= 330 and 310 <= pos[1] <= 350:
                        arranging = False
                        solution = astar_solve(PuzzleState(puzzle_state.board))
                        if not solution:
                            print("No solution found!")
                            pygame.quit()
                            sys.exit()
                        move_count = 0

        if arranging:
            draw_board(screen, puzzle_state.board, font, move_count, show_solve_button=True)
        else:
            if move_count < len(solution):
                draw_board(screen, solution[move_count], font, move_count)
                pygame.display.flip()
                time.sleep(0.5)
                move_count += 1
            elif move_count == len(solution):  # After showing all solution steps
                draw_board(screen, original_board, font, move_count)  # Display the solved board
                pygame.display.flip()
                time.sleep(2)
                arranging = True  # Reset to arranging mode
                puzzle_state = PuzzleState([row[:] for row in original_board])  # Reset to original board

        pygame.display.flip()


if __name__ == "__main__":
    main()
