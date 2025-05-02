import curses
from enum import Enum
import json
import logging

from graphos.src.constants import LOG_OUTPUT, MOUSE_OUTPUT
from graphos.src.cursor import Cursor
from graphos.src.edge import Edge
from graphos.src.menu import Menu
from graphos.src.modal import Modal
from graphos.src.node import Node
from graphos.src.offset import Offset

logger = logging.getLogger(__name__)

logging.basicConfig(
    filename=LOG_OUTPUT,
    level=logging.DEBUG,
    format="%(levelname)s - %(message)s",
)


class View:
    def __init__(self, window: curses.window):
        self.window = window
        # Enable mouse events
        curses.mouseinterval(0)  # Set mouse interval to 0 for immediate response
        curses.mousemask(curses.REPORT_MOUSE_POSITION | curses.ALL_MOUSE_EVENTS)
        print("\033[?1003h")

        # Initialize curses color
        curses.start_color()
        curses.use_default_colors()
        for i in range(curses.COLORS - 1):
            curses.init_pair(i + 1, i, -1)

        # Hide the cursor
        curses.curs_set(0)

        window_height, window_width = self.window.getmaxyx()

        self.nodes: list[Node] = []
        self.edges: list[Edge] = []

        self.cursor = Cursor(window_width // 2, window_height // 2)
        self.menu = Menu(window_width, window_height, self.cursor.x, self.cursor.y)
        self.selected_nodes = []
        self.offset = Offset(0, 0)
        self.last_mouse_press = None

    def select_node(self, node: Node):
        if node in self.selected_nodes:
            node.selected = False
            self.selected_nodes.remove(node)
            return
        
        self.selected_nodes.append(node)
        node.selected = True

        while len(self.selected_nodes) > 2:
            popped_node = self.selected_nodes.pop(0)
            popped_node.selected = False

    def set_last_mouse_press(self, x, y):
        self.last_mouse_press = (x, y)

    def get_last_mouse_press(self):
        return self.last_mouse_press

    def setup_keybindings(self):
        self.keybindings = {}
        self.keybindings[curses.KEY_MOUSE] = self.handle_mouse_event
        self.keybindings[curses.KEY_UP] = self.move_cursor_up
        self.keybindings[curses.KEY_DOWN] = self.move_cursor_down
        self.keybindings[curses.KEY_LEFT] = self.move_cursor_left
        self.keybindings[curses.KEY_RIGHT] = self.move_cursor_right
        self.keybindings[ord("a")] = self.pan_left
        self.keybindings[ord("d")] = self.pan_right
        self.keybindings[ord("w")] = self.pan_up
        self.keybindings[ord("s")] = self.pan_down
        self.keybindings[ord("n")] = self.new_node
        self.keybindings[ord("e")] = self.new_edge
        self.keybindings[ord("c")] = self.reset
        self.keybindings[ord("z")] = self.save_state
        self.keybindings[ord("g")] = self.grab
        self.keybindings[ord("q")] = self.quit

    def loop(self):
        curses.beep()

        self.setup_keybindings()

        while True:
            self.render()
            self.handle_input()

    def render(self):

        # Clear the window
        self.window.clear()

        # Update nodes of cursor state
        for node in self.nodes:
            node.assess_position(self.cursor)

        for edge in self.edges:
            edge.render(self.window, self.offset)

        for node in self.nodes:
            if not node.focused:
                node.render(self.window, self.offset)

        for node in self.nodes:
            if node.focused:
                node.render(self.window, self.offset)

        # Draw border around the window
        self.window.border(0)

        # Draw border around the window
        self.menu.assess_window(self.window.getmaxyx()[1], self.window.getmaxyx()[0], self.cursor.x, self.cursor.y)
        self.menu.render(self.window)

        # Draw cursor
        self.cursor.assess_position(self.window, self.cursor, self.offset)
        self.cursor.render(self.window, self.offset)
        self.window.refresh()

    def move_cursor_up(self):
        if self.cursor.y > 1:
            if self.cursor.grab:
                for node in self.nodes:
                    if node.grabbed:
                        node.move_up()
            self.cursor.y -= 1
    
    def move_cursor_down(self):
        if self.cursor.y < self.window.getmaxyx[0] - 2:
            if self.cursor.grab:
                for node in self.nodes:
                    if node.grabbed:
                        node.move_down()
            self.cursor.y += 1

    def move_cursor_left(self):
        if self.cursor.x > 1:
            if self.cursor.grab:
                for node in self.nodes:
                    if node.grabbed:
                        node.move_left()
            self.cursor.x -= 1
    
    def move_cursor_right(self):
        if self.cursor.x < self.window.getmaxyx[1] - 3:
            if self.cursor.grab:
                for node in self.nodes:
                    if node.grabbed:
                        node.move_right()
            self.cursor.x += 1
    
    def save_state(self):
        # Save the current state
        state = {
            "nodes": self.nodes,
            "edges": self.edges,
        }
        with open("resources/save.json", "w") as f:
            f.write(json.dumps(state, indent=4))

    def pan_left(self):
        self.offset.x -= 1
        self.cursor.x += 1

    def pan_right(self):
        self.offset.x += 1
        self.cursor.x -= 1

    def pan_up(self):
        self.offset.y -= 1
        self.cursor.y += 1

    def pan_down(self):
        self.offset.y += 1
        self.cursor.y -= 1

    def grab(self):
        # Grab the rectangle
        self.cursor.toggle_grab()
        if self.cursor.grab:
            for node in self.nodes:
                if node.focused:
                    node.grabbed = True
        else:
            for node in self.nodes:
                node.grabbed = False

    def reset(self):
        self.nodes.clear()
        self.edges.clear()
        self.stdscr.clear()

    def new_edge(self):
        if len(self.selected_nodes) == 2:
            for node in self.selected_nodes:
                node.selected = False
            self.edges.append(Edge(self.selected_nodes[0], self.selected_nodes[1]))
            self.selected_nodes.clear()

    def is_node_at_cursor(self):
        for node in self.nodes:
            if node.y == self.cursor.y and node.x == self.cursor.x:
                return True
        return False

    def new_node(self):
        if self.is_node_at_cursor():
            curses.beep()
        else:
            modal = Modal(self.window, "Node name (press enter to create, ctrl+h to delete):")
            modal.render()

            new_node = Node(x=self.cursor.x, y=self.cursor.y, width=10, height=4, value=modal.title)
            self.nodes.append(new_node)

    def quit(self):
        exit(0)

    def handle_mouse_event(self):
        event = curses.getmouse()
        if event[4] != 134217728:
            logger.debug(f"Mouse event: {event}")
            with open(MOUSE_OUTPUT, "a") as f:
                f.write(f"{event}\n")
        y = event[2]
        x = event[1]
        event_type = event[4]
        if event_type == 2:  # Mouse button pressed
            self.set_last_mouse_press(x, y)
            self.cursor.grab = True
            for node in self.nodes:
                node.assess_position(self.cursor)
                if node.focused:
                    node.grabbed = True
        elif event_type == 1:  # Mouse button released
            last_mouse_press = self.get_last_mouse_press()
            self.cursor.grab = False
            for node in self.nodes:
                node.assess_position(self.cursor)
                if node.focused:
                    logger.debug(f"x: {x}, y: {y}")
                    logger.debug(f"cursor.x: {self.cursor.x}, cursor.y: {self.cursor.y}")
                    logger.debug(f"last_mouse_press: {last_mouse_press}")
                    if last_mouse_press is not None and last_mouse_press == (x, y):
                        logger.debug(f"Clicked on node: {node.value}")
                        self.select_node(node)
                    node.grabbed = False
        if self.cursor.grab:
            for node in self.nodes:
                if node.grabbed:
                    node.move(x - self.cursor.x, y - self.cursor.y)

        self.cursor.x = x
        self.cursor.y = y

    def handle_input(self) -> bool:
        self.keybindings.get(self.window.getch(), lambda: None)()
