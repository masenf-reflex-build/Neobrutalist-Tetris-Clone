import reflex as rx
import asyncio
import random

GRID_WIDTH = 10
GRID_HEIGHT = 20
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 0], [0, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
]
SHAPE_COLORS = [
    "bg-cyan-400",
    "bg-yellow-400",
    "bg-purple-500",
    "bg-green-500",
    "bg-red-500",
    "bg-blue-500",
    "bg-orange-500",
]


class TetrisState(rx.State):
    grid: list[list[int]] = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
    current_piece_shape: list[list[int]] = []
    current_piece_shape_index: int = 0
    current_piece_color_index: int = 0
    current_piece_pos: tuple[int, int] = (0, 0)
    score: int = 0
    lines_cleared: int = 0
    level: int = 1
    game_over: bool = False
    game_started: bool = False
    next_piece_shape: list[list[int]] = []
    next_piece_shape_index: int = 0
    shape_color_map: dict[int, int] = {}

    def _generate_shape_color_map(self):
        colors = list(range(len(SHAPE_COLORS)))
        random.shuffle(colors)
        self.shape_color_map = {i: colors[i] for i in range(len(SHAPES))}

    @rx.var
    def game_speed(self) -> float:
        return max(0.1, 0.8 - (self.level - 1) * 0.05)

    @rx.var
    def next_piece_grid(self) -> list[list[int]]:
        if not self.next_piece_shape:
            return [[0] * 4 for _ in range(4)]
        piece = self.next_piece_shape
        h, w = (len(piece), len(piece[0]))
        grid = [[0] * 4 for _ in range(4)]
        start_row = (4 - h) // 2
        start_col = (4 - w) // 2
        color_index = self.shape_color_map.get(self.next_piece_shape_index, 0)
        for r in range(h):
            for c in range(w):
                if piece[r][c]:
                    grid[start_row + r][start_col + c] = color_index + 1
        return grid

    @rx.var
    def rendered_grid(self) -> list[list[int]]:
        grid_copy = [row[:] for row in self.grid]
        if self.current_piece_shape:
            shape = self.current_piece_shape
            pos_r, pos_c = self.current_piece_pos
            for r in range(len(shape)):
                for c in range(len(shape[0])):
                    if shape[r][c] == 1:
                        if 0 <= pos_r + r < GRID_HEIGHT and 0 <= pos_c + c < GRID_WIDTH:
                            grid_copy[pos_r + r][pos_c + c] = (
                                self.current_piece_color_index + 1
                            )
        return grid_copy

    @rx.event
    def start_game(self):
        self.reset_game()
        self.game_started = True
        self.game_over = False
        self._new_piece()
        return TetrisState.game_loop

    @rx.event
    def reset_game(self):
        self.grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.game_over = False
        self._generate_shape_color_map()
        next_shape_index = random.randint(0, len(SHAPES) - 1)
        self.next_piece_shape = SHAPES[next_shape_index]
        self.next_piece_shape_index = next_shape_index
        self._new_piece()

    def _is_valid_position(self, shape: list[list[int]], pos: tuple[int, int]) -> bool:
        pos_r, pos_c = pos
        for r in range(len(shape)):
            for c in range(len(shape[0])):
                if shape[r][c] == 1:
                    board_r, board_c = (pos_r + r, pos_c + c)
                    if not (0 <= board_r < GRID_HEIGHT and 0 <= board_c < GRID_WIDTH):
                        return False
                    if self.grid[board_r][board_c] != 0:
                        return False
        return True

    def _new_piece(self):
        self.current_piece_shape = self.next_piece_shape
        self.current_piece_shape_index = self.next_piece_shape_index
        self.current_piece_color_index = self.shape_color_map.get(
            self.current_piece_shape_index, 0
        )
        next_shape_index = random.randint(0, len(SHAPES) - 1)
        self.next_piece_shape = SHAPES[next_shape_index]
        self.next_piece_shape_index = next_shape_index
        start_col = (GRID_WIDTH - len(self.current_piece_shape[0])) // 2
        self.current_piece_pos = (0, start_col)
        if not self._is_valid_position(
            self.current_piece_shape, self.current_piece_pos
        ):
            self.game_over = True
            self.game_started = False

    def _lock_piece(self):
        shape = self.current_piece_shape
        pos_r, pos_c = self.current_piece_pos
        for r in range(len(shape)):
            for c in range(len(shape[0])):
                if shape[r][c] == 1:
                    self.grid[pos_r + r][pos_c + c] = self.current_piece_color_index + 1
        self._clear_lines()
        self._new_piece()

    def _clear_lines(self):
        new_grid = [row for row in self.grid if any((cell == 0 for cell in row))]
        lines_cleared_count = GRID_HEIGHT - len(new_grid)
        if lines_cleared_count > 0:
            self.lines_cleared += lines_cleared_count
            self.score += [0, 100, 300, 500, 800][lines_cleared_count] * self.level
            for _ in range(lines_cleared_count):
                new_grid.insert(0, [0] * GRID_WIDTH)
            self.grid = new_grid
            new_level = 1 + self.lines_cleared // 10
            if new_level > self.level:
                self.level = new_level
                self._generate_shape_color_map()

    @rx.event
    def move(self, dr: int, dc: int):
        if self.game_over:
            return
        pos_r, pos_c = self.current_piece_pos
        new_pos = (pos_r + dr, pos_c + dc)
        if self._is_valid_position(self.current_piece_shape, new_pos):
            self.current_piece_pos = new_pos
        elif dr == 1 and dc == 0:
            self._lock_piece()

    @rx.event
    def rotate(self):
        if self.game_over:
            return
        rotated_shape = [list(row) for row in zip(*self.current_piece_shape[::-1])]
        if self._is_valid_position(rotated_shape, self.current_piece_pos):
            self.current_piece_shape = rotated_shape
        else:
            pos_r, pos_c = self.current_piece_pos
            for offset in [-1, 1, -2, 2]:
                if self._is_valid_position(rotated_shape, (pos_r, pos_c + offset)):
                    self.current_piece_pos = (pos_r, pos_c + offset)
                    self.current_piece_shape = rotated_shape
                    return

    @rx.event
    def handle_key_down(self, key: str):
        if not self.game_started or self.game_over:
            return
        if key == "ArrowLeft":
            self.move(0, -1)
        elif key == "ArrowRight":
            self.move(0, 1)
        elif key == "ArrowDown":
            self.move(1, 0)
            self.score += 1
        elif key == "ArrowUp" or key == "w":
            self.rotate()
        elif key == " ":
            self.hard_drop()

    @rx.event
    def hard_drop(self):
        if self.game_over:
            return
        landed = False
        while not landed:
            pos_r, pos_c = self.current_piece_pos
            new_pos = (pos_r + 1, pos_c)
            if self._is_valid_position(self.current_piece_shape, new_pos):
                self.current_piece_pos = new_pos
                self.score += 2
            else:
                landed = True
        self._lock_piece()

    @rx.event(background=True)
    async def game_loop(self):
        async with self:
            if not self.game_started or self.game_over:
                return
        while True:
            game_speed = self.game_speed
            await asyncio.sleep(game_speed)
            async with self:
                if not self.game_started or self.game_over:
                    break
                yield TetrisState.move(1, 0)