from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
import os
from random import randint, choice

ORE_COLORS = {
    'red': ((1, 0, 0), 1),
    'green': ((0, 1, 0), 5),
    'purple': ((1, 0, 1), 10)
}

ORE_SIZE = 30
NUM_ORES = 50
MOVE_DIST = 10
BUILD_COST = 5
BUILD_COLOR = (0.5, 0.5, 0.5)
POINTS_FILE = os.path.join(os.getcwd(), "app1.txt")


class Ore:
    def __init__(self, x, y, color_name):
        self.x = x
        self.y = y
        self.color_name = color_name
        self.color, self.value = ORE_COLORS[color_name]


class MiningGame(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ores = []
        self.builds = []
        self.points = self.load_points()
        self.offset_x = 0
        self.offset_y = 0
        self.held_directions = set()

        self.center_square = Widget(size_hint=(None, None), size=(ORE_SIZE, ORE_SIZE))
        with self.center_square.canvas:
            Color(1, 1, 1)
            self.center_rect = Rectangle(size=self.center_square.size)
        self.add_widget(self.center_square)
        self.bind(size=self.update_center_square)

        self.points_label = Label(text=f"Points: {self.points}", size_hint=(0.3, 0.1), pos_hint={"right": 1.0, "top": 1.0}, font_size='20sp', color=(1, 1, 1, 1))
        self.add_widget(self.points_label)

        self.mine_button = Button(text="M", size_hint=(0.1, 0.1), pos_hint={"right": 0.98, "y": 0.15}, font_size='20sp')
        self.mine_button.bind(on_press=self.mine)
        self.add_widget(self.mine_button)

        self.build_button = Button(text="B", size_hint=(0.1, 0.1), pos_hint={"right": 0.98, "y": 0.28}, font_size='20sp')
        self.build_button.bind(on_press=self.build)
        self.add_widget(self.build_button)

        self.home_button = Button(text="Home", size_hint=(0.15, 0.1), pos_hint={"x": 0.02, "top": 0.98}, font_size='16sp')
        self.home_button.bind(on_press=self.go_home)
        self.add_widget(self.home_button)

        directions = {
            'up': {"center_x": 0.15, "center_y": 0.25},
            'down': {"center_x": 0.15, "center_y": 0.05},
            'left': {"center_x": 0.05, "center_y": 0.15},
            'right': {"center_x": 0.25, "center_y": 0.15}
        }

        self.dpad_buttons = {}
        for dir_name, hint in directions.items():
            btn = Button(size_hint=(0.1, 0.1), pos_hint=hint)
            btn.bind(on_press=self.on_dpad_press(dir_name))
            btn.bind(on_release=self.on_dpad_release(dir_name))
            self.add_widget(btn)
            self.dpad_buttons[dir_name] = btn

        self.spawn_ores()
        Clock.schedule_interval(self.update_graphics, 1 / 60)
        Clock.schedule_interval(self.update_movement, 1 / 20)

    def update_center_square(self, *args):
        self.center_square.pos = (self.width // 2 - ORE_SIZE // 2, self.height // 2 - ORE_SIZE // 2)
        self.center_rect.pos = self.center_square.pos

    def load_points(self):
        try:
            if os.path.exists(POINTS_FILE):
                with open(POINTS_FILE, "r") as f:
                    return int(f.read().strip())
        except:
            pass
        return 0

    def save_points(self):
        try:
            with open(POINTS_FILE, "w") as f:
                f.write(str(self.points))
        except Exception as e:
            print("Error saving points:", e)

    def spawn_ores(self):
        for _ in range(NUM_ORES):
            x = randint(-1000, 1000)
            y = randint(-1000, 1000)
            color_name = choice(list(ORE_COLORS.keys()))
            self.ores.append(Ore(x, y, color_name))

    def update_graphics(self, dt):
        self.canvas.after.clear()
        for ore in self.ores:
            screen_x = ore.x - self.offset_x + self.width // 2
            screen_y = ore.y - self.offset_y + self.height // 2
            with self.canvas.after:
                Color(*ore.color)
                Rectangle(pos=(screen_x, screen_y), size=(ORE_SIZE, ORE_SIZE))
        for build_x, build_y in self.builds:
            screen_x = build_x - self.offset_x + self.width // 2
            screen_y = build_y - self.offset_y + self.height // 2
            with self.canvas.after:
                Color(*BUILD_COLOR)
                Rectangle(pos=(screen_x, screen_y), size=(ORE_SIZE, ORE_SIZE))

    def update_movement(self, dt):
        for direction in self.held_directions:
            self.move(direction)

    def move(self, direction):
        if direction == 'up':
            self.offset_y += MOVE_DIST
        elif direction == 'down':
            self.offset_y -= MOVE_DIST
        elif direction == 'left':
            self.offset_x -= MOVE_DIST
        elif direction == 'right':
            self.offset_x += MOVE_DIST

    def on_dpad_press(self, direction):
        def inner(instance):
            self.held_directions.add(direction)
        return inner

    def on_dpad_release(self, direction):
        def inner(instance):
            self.held_directions.discard(direction)
        return inner

    def mine(self, instance):
        try:
            center_x = self.offset_x
            center_y = self.offset_y
            for ore in self.ores[:]:
                if abs(ore.x - center_x) < ORE_SIZE and abs(ore.y - center_y) < ORE_SIZE:
                    self.points += ore.value
                    self.ores.remove(ore)
                    self.points_label.text = f"Points: {self.points}"
                    self.save_points()
                    break
        except Exception as e:
            print(f"Mining error: {e}")

    def build(self, instance):
        if self.points >= BUILD_COST:
            self.points -= BUILD_COST
            self.builds.append((self.offset_x, self.offset_y))
            self.points_label.text = f"Points: {self.points}"
            self.save_points()

    def go_home(self, instance):
        from kivy.app import App
        App.get_running_app().root.clear_widgets()
        App.get_running_app().root.add_widget(App.get_running_app().home_screen)


def main():
    from kivy.app import App
    class TempWrapper(App):
        def build(self):
            return MiningGame()
    TempWrapper().run()


if __name__ == "__main__":
    main()        self.mine_button.bind(on_press=self.mine)
        self.add_widget(self.mine_button)

        Window.bind(on_key_down=self.on_key_down, on_key_up=self.on_key_up)
        Clock.schedule_interval(self.update, 1/60)

        self.center_square = Label(text="+", font_size='40sp', color=(1,1,1,1), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.add_widget(self.center_square)

        self.build_button = Button(text='B', size_hint=(0.1, 0.1), pos_hint={'x': 0.75, 'y': 0.05})
        self.build_button.bind(on_press=self.build)
        self.add_widget(self.build_button)

    def mine(self, *args):
        self.points += 1
        self.label.text = f"Points: {self.points}"
        self.save_points()

    def build(self, *args):
        if self.points >= 5:
            self.points -= 5
            self.label.text = f"Points: {self.points}"
            self.save_points()

    def update(self, dt):
        move_speed = 5
        if 'up' in self.held_directions:
            self.offset_y += move_speed
        if 'down' in self.held_directions:
            self.offset_y -= move_speed
        if 'left' in self.held_directions:
            self.offset_x += move_speed
        if 'right' in self.held_directions:
            self.offset_x -= move_speed

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        direction = {273: 'up', 274: 'down', 276: 'left', 275: 'right'}.get(key)
        if direction:
            self.held_directions.add(direction)

    def on_key_up(self, window, key, *args):
        direction = {273: 'up', 274: 'down', 276: 'left', 275: 'right'}.get(key)
        if direction and direction in self.held_directions:
            self.held_directions.remove(direction)

    def save_points(self):
        with open("/storage/emulated/0/app1.txt", "w") as f:
            f.write(str(self.points))

    def load_points(self):
        try:
            with open("/storage/emulated/0/app1.txt", "r") as f:
                return int(f.read())
        except:
            return 0
'''

# Save to display or give to user
app1_script_path = "/mnt/data/app1_script_output.py"
Path(app1_script_path).write_text(app1_script)
app1_script_path
self.center_square = Widget(size_hint=(None, None), size=(30, 30))
    with self.center_square.canvas:
        Color(1, 1, 1)
        self.center_rect = Rectangle(size=self.center_square.size)
    self.add_widget(self.center_square)
    self.bind(size=self.update_center_square)

    self.points_label = Label(text=f"Points: {self.points}", size_hint=(0.3, 0.1), pos_hint={"right": 1.0, "top": 1.0}, font_size='20sp', color=(1, 1, 1, 1))
    self.add_widget(self.points_label)

    self.mine_button = Button(text="M", size_hint=(0.1, 0.1), pos_hint={"right": 0.98, "y": 0.15}, font_size='20sp')
    self.mine_button.bind(on_press=self.mine)
    self.add_widget(self.mine_button)

    self.build_button = Button(text="B", size_hint=(0.1, 0.1), pos_hint={"right": 0.98, "y": 0.28}, font_size='20sp')
    self.build_button.bind(on_press=self.build)
    self.add_widget(self.build_button)

    directions = {
        'up': {"center_x": 0.15, "center_y": 0.25},
        'down': {"center_x": 0.15, "center_y": 0.05},
        'left': {"center_x": 0.05, "center_y": 0.15},
        'right': {"center_x": 0.25, "center_y": 0.15}
    }

    self.dpad_buttons = {}
    for dir_name, hint in directions.items():
        btn = Button(size_hint=(0.1, 0.1), pos_hint=hint)
        btn.bind(on_press=self.on_dpad_press(dir_name))
        btn.bind(on_release=self.on_dpad_release(dir_name))
        self.add_widget(btn)
        self.dpad_buttons[dir_name] = btn

    self.spawn_ores()
    Clock.schedule_interval(self.update_graphics, 1 / 60)
    Clock.schedule_interval(self.update_movement, 1 / 20)

def update_center_square(self, *args):
    self.center_square.pos = (self.width // 2 - 15, self.height // 2 - 15)
    self.center_rect.pos = self.center_square.pos

def load_points(self):
    if os.path.exists(POINTS_FILE):
        with open(POINTS_FILE, "r") as f:
            return int(f.read().strip())
    return 0

def save_points(self):
    with open(POINTS_FILE, "w") as f:
        f.write(str(self.points))

def spawn_ores(self):
    for _ in range(NUM_ORES):
        x = randint(-1000, 1000)
        y = randint(-1000, 1000)
        color_name = choice(list(ORE_COLORS.keys()))
        self.ores.append(Ore(x, y, color_name))

def update_graphics(self, dt):
    self.canvas.after.clear()
    for ore in self.ores:
        screen_x = ore.x - self.offset_x + self.width // 2
        screen_y = ore.y - self.offset_y + self.height // 2
        with self.canvas.after:
            Color(*ore.color)
            Rectangle(pos=(screen_x, screen_y), size=(30, 30))
    for build_x, build_y in self.builds:
        screen_x = build_x - self.offset_x + self.width // 2
        screen_y = build_y - self.offset_y + self.height // 2
        with self.canvas.after:
            Color(0.5, 0.5, 0.5)
            Rectangle(pos=(screen_x, screen_y), size=(30, 30))

def update_movement(self, dt):
    for direction in self.held_directions:
        self.move(direction)

def move(self, direction):
    if direction == 'up':
        self.offset_y += MOVE_DIST
    elif direction == 'down':
        self.offset_y -= MOVE_DIST
    elif direction == 'left':
        self.offset_x -= MOVE_DIST
    elif direction == 'right':
        self.offset_x += MOVE_DIST

def on_dpad_press(self, direction):
    def inner(instance):
        self.held_directions.add(direction)
    return inner

def on_dpad_release(self, direction):
    def inner(instance):
        self.held_directions.discard(direction)
    return inner

def mine(self, instance):
    center_x = self.offset_x
    center_y = self.offset_y
    for ore in self.ores[:]:
        if abs(ore.x - center_x) < 30 and abs(ore.y - center_y) < 30:
            self.points += ore.value
            self.ores.remove(ore)
            self.points_label.text = f"Points: {self.points}"
            self.save_points()
            break

def build(self, instance):
    if self.points >= 5:
        self.points -= 5
        self.builds.append((self.offset_x, self.offset_y))
        self.points_label.text = f"Points: {self.points}"
        self.save_points()

