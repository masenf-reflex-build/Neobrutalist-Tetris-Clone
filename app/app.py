import reflex as rx
from app.states.tetris_state import TetrisState, GRID_WIDTH, GRID_HEIGHT, SHAPE_COLORS


def cell_component(value: int, row_idx: int, col_idx: int) -> rx.Component:
    color_class = rx.cond(
        value > 0,
        rx.Var.create(SHAPE_COLORS)[value - 1],
        rx.cond((row_idx + col_idx) % 2 == 0, "bg-gray-800", "bg-gray-900"),
    )
    return rx.el.div(
        class_name=rx.cond(
            value > 0,
            color_class + " border-t-2 border-l-2 border-r-2 border-b-4 border-black",
            color_class
            + " border-t-2 border-l-2 border-r-2 border-b-4 border-transparent",
        )
    )


def game_grid() -> rx.Component:
    return rx.el.div(
        rx.foreach(
            TetrisState.rendered_grid,
            lambda row, row_idx: rx.el.div(
                rx.foreach(
                    row, lambda value, col_idx: cell_component(value, row_idx, col_idx)
                ),
                class_name=f"grid grid-cols-{GRID_WIDTH}",
            ),
        ),
        class_name=f"grid grid-rows-{GRID_HEIGHT} w-[250px] h-[500px] border-4 border-black bg-gray-800 shadow-[8px_8px_0px_rgba(0,0,0,1)]",
    )


def game_info_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            info_card("Score", TetrisState.score.to_string()),
            info_card("Lines", TetrisState.lines_cleared.to_string()),
            info_card("Level", TetrisState.level.to_string()),
            next_piece_preview(),
            class_name="grid grid-cols-4 md:grid-cols-2 lg:flex lg:flex-col gap-2 md:gap-4",
        ),
        class_name="flex flex-col gap-4 w-full md:w-auto",
    )


def info_card(title: str, value: rx.Var[str]) -> rx.Component:
    return rx.el.div(
        rx.el.h3(title, class_name="text-[8px] md:text-lg font-bold text-black"),
        rx.el.p(value, class_name="text-[10px] md:text-3xl font-extrabold text-black"),
        class_name="p-1 md:p-4 bg-yellow-400 border-2 md:border-4 border-black shadow-[2px_2px_0px_rgba(0,0,0,1)] md:shadow-[4px_4px_0px_rgba(0,0,0,1)] w-full flex flex-col justify-center items-center",
    )


def next_piece_preview() -> rx.Component:
    return rx.el.div(
        rx.el.h3("Next", class_name="text-[8px] md:text-lg font-bold text-black"),
        rx.el.div(
            rx.foreach(
                TetrisState.next_piece_grid,
                lambda row, row_idx: rx.el.div(
                    rx.foreach(
                        row,
                        lambda value, col_idx: rx.el.div(
                            class_name=rx.cond(
                                value > 0,
                                rx.Var.create(SHAPE_COLORS)[value - 1],
                                "bg-transparent",
                            )
                            + " w-1 h-1 md:w-5 md:h-5"
                        ),
                    ),
                    class_name="grid grid-cols-4",
                ),
            ),
            class_name="grid grid-rows-4 w-4 h-4 md:w-20 md:h-20 bg-gray-800",
        ),
        class_name="p-1 md:p-4 bg-lime-400 border-2 md:border-4 border-black shadow-[2px_2px_0px_rgba(0,0,0,1)] md:shadow-[4px_4px_0px_rgba(0,0,0,1)] flex flex-col items-center justify-center gap-1 md:gap-2",
    )


def game_overlay(
    title: str, button_text: str, on_click: rx.event.EventHandler
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2(title, class_name="text-5xl font-extrabold text-black mb-8"),
            rx.el.button(
                button_text,
                on_click=on_click,
                class_name="px-8 py-4 bg-pink-500 text-white text-2xl font-bold border-4 border-black shadow-[8px_8px_0px_rgba(0,0,0,1)] hover:bg-pink-600 hover:shadow-[4px_4px_0px_rgba(0,0,0,1)] hover:translate-x-1 hover:translate-y-1 transition-all",
            ),
            class_name="flex flex-col items-center justify-center p-12 bg-yellow-400 border-4 border-black shadow-[8px_8px_0px_rgba(0,0,0,1)]",
        ),
        class_name="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-10",
    )


def mobile_controls() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.button(
                rx.icon(tag="arrow-left", class_name="w-8 h-8"),
                on_click=lambda: TetrisState.handle_key_down("ArrowLeft"),
                class_name="p-4 bg-black bg-opacity-30 rounded-full",
            ),
            rx.el.button(
                rx.icon(tag="arrow-right", class_name="w-8 h-8"),
                on_click=lambda: TetrisState.handle_key_down("ArrowRight"),
                class_name="p-4 bg-black bg-opacity-30 rounded-full",
            ),
            class_name="flex gap-16 text-white",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon(tag="arrow-down", class_name="w-8 h-8"),
                on_click=lambda: TetrisState.handle_key_down("ArrowDown"),
                class_name="p-4 bg-black bg-opacity-30 rounded-full",
            ),
            rx.el.button(
                rx.icon(tag="rotate-ccw", class_name="w-8 h-8"),
                on_click=lambda: TetrisState.handle_key_down("ArrowUp"),
                class_name="p-4 bg-black bg-opacity-30 rounded-full",
            ),
            class_name="flex gap-8 text-white",
        ),
        class_name="absolute bottom-8 flex flex-col items-center gap-4 md:hidden",
    )


def hard_drop_button() -> rx.Component:
    return rx.el.div(
        rx.el.button(
            rx.icon(tag="chevrons-down", class_name="w-6 h-6"),
            "Drop",
            on_click=TetrisState.hard_drop,
            class_name="p-2 bg-pink-500 text-white rounded-lg border-2 border-black shadow-[4px_4px_0px_rgba(0,0,0,1)] text-xs font-bold flex items-center gap-1",
        ),
        class_name="absolute -top-12 flex justify-center w-full md:hidden",
    )


def index() -> rx.Component:
    return rx.el.main(
        rx.window_event_listener(on_key_down=TetrisState.handle_key_down),
        rx.el.div(
            rx.el.div(
                game_info_panel(),
                rx.el.div(
                    game_grid(),
                    hard_drop_button(),
                    mobile_controls(),
                    rx.cond(
                        ~TetrisState.game_started & ~TetrisState.game_over,
                        game_overlay("NEOTRIS", "Start Game", TetrisState.start_game),
                        None,
                    ),
                    rx.cond(
                        TetrisState.game_over,
                        game_overlay("Game Over", "Play Again", TetrisState.start_game),
                        None,
                    ),
                    class_name="relative flex items-center justify-center",
                ),
                class_name="flex flex-col-reverse md:flex-row items-center justify-center gap-4 md:gap-16",
            ),
            class_name="flex flex-col items-center justify-center p-4 md:p-8",
        ),
        class_name="w-screen h-screen bg-blue-300 flex items-center justify-center font-['Press_Start_2P'] overflow-hidden",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index)