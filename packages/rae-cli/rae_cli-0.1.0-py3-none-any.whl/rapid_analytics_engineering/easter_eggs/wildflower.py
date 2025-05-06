import random
import time

from asciimatics.screen import Screen


class WildFlower:
    """
    This is an Easter Egg built in to the application. It functions to draw a wildflower in the terminal.
    """

    def __init__(self):
        self.flower_icons = ["🌸", "🌻", "🌼", "🌺", "🌹", "🪻", "🌷", "🏵️", "🪷"]
        self.butterfly_icon = "🦋"
        self.bee_icon = "🐝"
        self.ladybug_icon = "🐞"
        self.static_grass = []

    def _draw_static_grass(self, screen, y_pos):
        """Draw a clean solid line of green double quotes as grass."""
        for x in range(screen.width):
            screen.print_at('"', x, y_pos, colour=2)

    def _draw_flower(self, screen, x, y, icon):
        """Draw a flower."""
        screen.print_at(icon, x, y)

    def _draw_insect(self, screen, insect):
        """Draw an insect (butterfly, bee, ladybug)."""
        if 0 <= insect["x"] < screen.width and 0 <= insect["y"] < screen.height:
            screen.print_at(insect["icon"], insect["x"], insect["y"])

    def _move_insect(self, insect, type_):
        """Move insects."""
        if type_ == "bee":
            # Bees move faster
            insect["x"] += random.choice([1, 2])
            insect["y"] += random.choice([-1, 0, 1])
        else:
            # Butterflies and ladybugs move gently
            insect["x"] += random.choice([0, 1])
            insect["y"] += random.choice([-1, 0, 1])
        return insect

    def _generate_insects(self, screen_width, screen_height):
        """Generate random counts of each insect type independently."""
        insects = []

        num_butterflies = random.randint(3, 7)
        num_bees = random.randint(2, 5)
        num_ladybugs = random.randint(1, 4)

        for _ in range(num_butterflies):
            insects.append(
                {
                    "icon": self.butterfly_icon,
                    "x": random.randint(0, screen_width // 2),
                    "y": random.randint(1, screen_height // 3),
                    "type": "butterfly",
                }
            )

        for _ in range(num_bees):
            insects.append(
                {"icon": self.bee_icon, "x": random.randint(0, screen_width // 2), "y": random.randint(1, screen_height // 3), "type": "bee"}
            )

        for _ in range(num_ladybugs):
            insects.append(
                {"icon": self.ladybug_icon, "x": random.randint(0, screen_width // 2), "y": random.randint(1, screen_height // 3), "type": "ladybug"}
            )

        return insects

    def _generate_flower_positions(self, screen_width, num_flowers, flower_spacing):
        """Ensure flowers are spaced apart nicely."""
        positions = []
        available_space = screen_width - (flower_spacing * (num_flowers + 1))
        flower_slots = [flower_spacing + i * (available_space // num_flowers + flower_spacing) for i in range(num_flowers)]

        for slot_x in flower_slots:
            shift = random.randint(-2, 2)
            positions.append(max(2, min(screen_width - 3, slot_x + shift)))

        return positions

    def _draw_field(self, screen):
        screen.clear()

        screen_width = screen.width
        screen_height = screen.height

        # 1. Generate static grass
        self._draw_static_grass(screen, screen_height - 2)

        # 2. Flowers
        num_flowers = random.randint(5, 8)
        flower_spacing = 6
        flower_positions = self._generate_flower_positions(screen_width, num_flowers, flower_spacing)
        flowers = []

        for x in flower_positions:
            y = random.randint(screen_height - 8, screen_height - 4)
            icon = random.choice(self.flower_icons)
            flowers.append((x, y, icon))
            self._draw_flower(screen, x, y, icon)

        screen.refresh()

        # 3. Insects
        insects = self._generate_insects(screen_width, screen_height)

        # 4. Animate insects moving
        for _ in range(70):
            screen.clear()

            # Redraw flowers
            for x, y, icon in flowers:
                self._draw_flower(screen, x, y, icon)

            # Redraw static grass
            self._draw_static_grass(screen, screen_height - 2)

            # Move and draw insects
            for insect in insects:
                self._move_insect(insect, insect["type"])
                self._draw_insect(screen, insect)

            screen.refresh()
            time.sleep(0.1)

        screen.wait_for_input(5)

    def draw_wildflower(self):
        Screen.wrapper(self._draw_field)
