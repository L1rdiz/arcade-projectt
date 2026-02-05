import arcade
import random
import math
import json
import os
from dataclasses import dataclass
from typing import List, Tuple, Optional


SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Pent: CyberArcade"

BACKGROUND_COLOR = (20, 20, 40)
PLATFORM_COLOR = (120, 120, 160)
COIN_COLOR = (255, 215, 0)
PLAYER_COLOR = (70, 130, 180)
ENEMY_COLOR = (220, 60, 60)
HAZARD_COLOR = (255, 140, 0)
GRAVITY = 0.8
PLAYER_JUMP_SPEED = 16
PLAYER_MOVE_SPEED = 6
PLAYER_SIZE = 45
COIN_SIZE = 22
ENEMY_SIZE = 45
HAZARD_WIDTH = 65
HAZARD_HEIGHT = 25
SAVE_FILE = "game_save.json"



@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    color: Tuple[int, int, int]
    size: float
    lifetime: float
    age: float = 0.0
    fade_out: bool = True
    gravity_effect: float = 1.0


class ParticleSystem:
    def __init__(self):
        self.particles: List[Particle] = []

    def add_particle(self, x: float, y: float,
                     color: Tuple[int, int, int] = (255, 255, 255),
                     count: int = 1,
                     speed: float = 2.0,
                     size: float = 3.0,
                     lifetime: float = 1.0,
                     fade_out: bool = True,
                     gravity_effect: float = 1.0):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            velocity = random.uniform(0.5, 1.5) * speed
            vx = math.cos(angle) * velocity
            vy = math.sin(angle) * velocity

            self.particles.append(
                Particle(
                    x=x, y=y,
                    vx=vx, vy=vy,
                    color=color,
                    size=random.uniform(size * 0.5, size * 1.5),
                    lifetime=lifetime * random.uniform(0.7, 1.3),
                    fade_out=fade_out,
                    gravity_effect=gravity_effect))

    def create_coin_effect(self, x: float, y: float):
        colors = [
            (255, 215, 0),
            (255, 255, 100),
            (255, 200, 50),]
        color = random.choice(colors)
        self.add_particle(
            x, y,
            color=color,
            count=12,
            speed=3.0,
            size=4.0,
            lifetime=0.8,
            gravity_effect=0.5)

    def create_jump_effect(self, x: float, y: float):
        colors = [
            (150, 150, 180),
            (120, 120, 150),
            (180, 180, 200),]
        for i in range(3):
            offset = random.uniform(-15, 15)
            color = colors[i % len(colors)]
            self.add_particle(
                x + offset, y - PLAYER_SIZE / 2,
                color=color,
                count=random.randint(2, 4),
                speed=random.uniform(1.0, 2.0),
                size=random.uniform(2.0, 4.0),
                lifetime=random.uniform(0.3, 0.6),
                gravity_effect=0.3)

    def create_landing_effect(self, x: float, y: float):
        colors = [
            (150, 150, 180),
            (120, 120, 150),
            (180, 180, 200),]
        for i in range(5):
            offset = random.uniform(-20, 20)
            color = colors[i % len(colors)]
            self.add_particle(
                x + offset, y - PLAYER_SIZE / 2,
                color=color,
                count=random.randint(3, 6),
                speed=random.uniform(1.5, 3.0),
                size=random.uniform(3.0, 6.0),
                lifetime=random.uniform(0.4, 0.8),
                gravity_effect=0.8)

    def create_enemy_hit_effect(self, x: float, y: float):
        colors = [
            (255, 100, 100),
            (255, 150, 100),
            (255, 100, 150),]
        color = random.choice(colors)
        self.add_particle(
            x, y,
            color=color,
            count=random.randint(8, 15),
            speed=random.uniform(2.0, 4.0),
            size=random.uniform(3.0, 5.0),
            lifetime=random.uniform(0.5, 0.9),
            fade_out=True,
            gravity_effect=0.7)

    def create_hazard_effect(self, x: float, y: float):
        colors = [
            (255, 140, 0),
            (255, 100, 50),
            (255, 180, 50),]
        color = random.choice(colors)
        self.add_particle(
            x, y,
            color=color,
            count=random.randint(10, 20),
            speed=random.uniform(3.0, 6.0),
            size=random.uniform(2.0, 4.0),
            lifetime=random.uniform(0.6, 1.0),
            fade_out=True,
            gravity_effect=0.6)

    def create_sparkle_effect(self, x: float, y: float):
        colors = [
            (255, 255, 255, 200),
            (200, 220, 255, 180),
            (255, 255, 200, 150),]
        if random.random() < 0.3:
            color = random.choice(colors)
            self.add_particle(
                x, y,
                color=color[:3],
                count=1,
                speed=random.uniform(0.1, 0.5),
                size=random.uniform(1.0, 2.0),
                lifetime=random.uniform(0.5, 1.5),
                fade_out=True,
                gravity_effect=0.1)

    def create_level_complete_effect(self, x: float, y: float):
        colors = [
            (100, 255, 100),
            (100, 255, 200),
            (200, 255, 100),
            (255, 255, 100)]
        for i in range(20):
            angle = (i / 20) * math.pi * 2
            color = colors[i % len(colors)]
            self.add_particle(
                x, y,
                color=color,
                count=1,
                speed=random.uniform(2.0, 5.0),
                size=random.uniform(4.0, 8.0),
                lifetime=random.uniform(1.0, 2.0),
                fade_out=True,
                gravity_effect=0.0)
            self.particles[-1].vx = math.cos(angle) * random.uniform(2.0, 5.0)
            self.particles[-1].vy = math.sin(angle) * random.uniform(2.0, 5.0)

    def update(self, delta_time: float):
        particles_to_remove = []
        for particle in self.particles:
            particle.age += delta_time
            if particle.age >= particle.lifetime:
                particles_to_remove.append(particle)
                continue

            particle.vy -= GRAVITY * particle.gravity_effect * delta_time * 60
            particle.x += particle.vx * delta_time * 60
            particle.y += particle.vy * delta_time * 60

        for particle in particles_to_remove:
            if particle in self.particles:
                self.particles.remove(particle)

    def draw(self):
        for particle in self.particles:
            alpha = 255
            if particle.fade_out:
                life_ratio = 1.0 - (particle.age / particle.lifetime)
                alpha = int(255 * life_ratio)

            color_with_alpha = (*particle.color, alpha)
            arcade.draw_circle_filled(
                particle.x, particle.y,
                particle.size,
                color_with_alpha)


class SaveSystem:
    @staticmethod
    def load_game_data():
        default_data = {
            "max_level_reached": 1,
            "level_records": {
                1: 0,
                2: 0,
                3: 0,
                4: 0,
                5: 0},
            "total_score": 0,
            "total_coins": 0,
            "games_played": 0,
            "games_won": 0}

        try:
            if os.path.exists(SAVE_FILE):
                with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Объединяем с дефолтными значениями
                    for key, value in default_data.items():
                        if key not in data:
                            data[key] = value
                    return data
            else:
                return default_data
        except Exception as e:
            print(f"Ошибка загрузки сохранения: {e}")
            return default_data

    @staticmethod
    def save_game_data(data):
        try:
            with open(SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False

    @staticmethod
    def update_level_record(level, score, coins_collected):
        data = SaveSystem.load_game_data()
        if level > data["max_level_reached"]:
            data["max_level_reached"] = level
        if score > data["level_records"].get(str(level), 0):
            data["level_records"][str(level)] = score
        data["total_score"] += score
        data["total_coins"] += coins_collected
        data["games_played"] += 1
        if level == 5:
            data["games_won"] += 1
        SaveSystem.save_game_data(data)
        return data

    @staticmethod
    def reset_save_data():
        default_data = {
            "max_level_reached": 1,
            "level_records": {
                1: 0,
                2: 0,
                3: 0,
                4: 0,
                5: 0},
            "total_score": 0,
            "total_coins": 0,
            "games_played": 0,
            "games_won": 0}
        SaveSystem.save_game_data(default_data)
        return default_data


LEVELS = {
    1: {
        "name": "Начальный",
        "time": 90,
        "coins": 5,
        "enemies": 0,
        "hazards": 0,
        "background": (40, 60, 100),
        "platforms": [
            [0, 120, 1200, 40],
            [100, 220, 300, 25],
            [450, 320, 300, 25],
            [800, 240, 300, 25],
            [300, 420, 250, 25],
            [650, 400, 250, 25]]},
    2: {
        "name": "Городской парк",
        "time": 85,
        "coins": 8,
        "enemies": 2,
        "hazards": 2,
        "background": (60, 100, 80),
        "platforms": [
            [0, 120, 1200, 40],
            [150, 220, 250, 25],
            [450, 280, 250, 25],
            [750, 220, 250, 25],
            [200, 380, 200, 25],
            [500, 420, 200, 25],
            [800, 380, 200, 25]]},
    3: {
        "name": "Горный хребет",
        "time": 80,
        "coins": 10,
        "enemies": 3,
        "hazards": 4,
        "background": (30, 40, 70),
        "platforms": [
            [0, 120, 400, 40],
            [500, 120, 400, 40],
            [200, 240, 150, 25],
            [600, 240, 150, 25],
            [1000, 240, 150, 25],
            [350, 360, 120, 25],
            [750, 360, 120, 25],
            [150, 480, 100, 25],
            [450, 480, 100, 25],
            [800, 480, 100, 25]]},
    4: {
        "name": "Заброшенный завод",
        "time": 70,
        "coins": 12,
        "enemies": 4,
        "hazards": 6,
        "background": (50, 50, 60),
        "platforms": [
            [0, 120, 1200, 40],
            [50, 200, 150, 20],
            [300, 200, 150, 20],
            [550, 200, 150, 20],
            [800, 200, 150, 20],
            [250, 350, 200, 20],
            [500, 400, 200, 20],
            [750, 350, 200, 20],
            [150, 500, 80, 15],
            [450, 550, 80, 15],
            [750, 500, 80, 15]]},
    5: {
        "name": "Космическая станция",
        "time": 60,
        "coins": 15,
        "enemies": 5,
        "hazards": 8,
        "background": (10, 10, 40),
        "platforms": [
            [0, 120, 300, 30],
            [450, 120, 300, 30],
            [900, 120, 300, 30],
            [50, 250, 120, 20],
            [300, 350, 120, 20],
            [550, 280, 120, 20],
            [800, 400, 120, 20],
            [1050, 320, 120, 20],
            [200, 500, 200, 15],
            [650, 550, 200, 15],]}}


class StartView(arcade.View):
    def __init__(self):
        super().__init__()
        self.save_data = SaveSystem.load_game_data()
        self.show_stats = False
        self.particle_system = ParticleSystem()
        self.sparkle_timer = 0

    def on_show(self):
        arcade.set_background_color(BACKGROUND_COLOR)

    def on_draw(self):
        self.clear()
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, BACKGROUND_COLOR)
        for x in range(0, SCREEN_WIDTH, 60):
            arcade.draw_line(x, 0, x, SCREEN_HEIGHT, (35, 35, 65), 1)
            if random.random() < 0.01:
                y = random.randint(0, SCREEN_HEIGHT)
                self.particle_system.create_sparkle_effect(x, y)
        self.particle_system.draw()
        arcade.draw_text("ПЕНТ:КИБЕРПУТЬ",
                         SCREEN_WIDTH / 2, SCREEN_HEIGHT - 80,
                         (0, 200, 255), 64,
                         anchor_x="center",
                         bold=True)
        arcade.draw_text("Путешествие по 5 уникальным мирам",
                         SCREEN_WIDTH / 2, SCREEN_HEIGHT - 130,
                         (180, 220, 255), 24,
                         anchor_x="center")
        arcade.draw_lrbt_rectangle_filled(
            30, SCREEN_WIDTH - 30,
                SCREEN_HEIGHT - 230, SCREEN_HEIGHT - 170,
            (40, 50, 90, 200))
        arcade.draw_text("5 МИРОВ",
                         SCREEN_WIDTH / 2, SCREEN_HEIGHT - 185,
                         arcade.color.YELLOW, 28,
                         anchor_x="center", bold=True)
        level_colors = [
            (100, 220, 100),
            (100, 180, 255),
            (255, 180, 100),
            (180, 180, 180),
            (200, 150, 255)]

        level_width = 180
        level_height = 100
        level_spacing = 30
        total_width = 5 * level_width + 4 * level_spacing
        start_x = (SCREEN_WIDTH - total_width) // 2

        for i in range(1, 6):
            level = LEVELS[i]
            color = level_colors[i - 1]
            x = start_x + (i - 1) * (level_width + level_spacing)
            y = SCREEN_HEIGHT - 320
            is_locked = i > self.save_data["max_level_reached"]
            if is_locked:
                arcade.draw_lrbt_rectangle_filled(
                    x, x + level_width, y, y + level_height,
                    (20, 30, 50))
                arcade.draw_lrbt_rectangle_outline(
                    x, x + level_width, y, y + level_height,
                    (100, 100, 100), 3)
            else:
                arcade.draw_lrbt_rectangle_filled(
                    x, x + level_width, y, y + level_height,
                    (30, 40, 70))
                arcade.draw_lrbt_rectangle_outline(
                    x, x + level_width, y, y + level_height,
                    color, 3)
            arcade.draw_text(f"{i}",
                             x + level_width / 2, y + level_height - 20,
                             color if not is_locked else (100, 100, 100), 24,
                             anchor_x="center", bold=True)
            arcade.draw_text(f"{level['name']}",
                             x + level_width / 2, y + level_height / 2,
                             arcade.color.WHITE if not is_locked else (150, 150, 150), 16,
                             anchor_x="center", anchor_y="center")
            details = f"{level['coins']} монет, {level['time']} сек"
            arcade.draw_text(details,
                             x + level_width / 2, y + 20,
                             (200, 200, 200) if not is_locked else (100, 100, 100), 14,
                             anchor_x="center")
            record = self.save_data["level_records"].get(str(i), 0)
            if record > 0 and not is_locked:
                arcade.draw_text(f"Рекорд: {record}",
                                 x + level_width / 2, y - 20,
                                 arcade.color.GOLD, 12,
                                 anchor_x="center")

        arcade.draw_lrbt_rectangle_filled(
            30, SCREEN_WIDTH - 30,
                SCREEN_HEIGHT - 450, SCREEN_HEIGHT - 390,
            (40, 50, 90, 200))

        arcade.draw_text("УПРАВЛЕНИЕ",
                         SCREEN_WIDTH / 2, SCREEN_HEIGHT - 405,
                         arcade.color.YELLOW, 28,
                         anchor_x="center", bold=True)
        cube_size = 120
        cube_spacing = 40
        controls_data = [
            ("← →", "Движение"),
            ("ПРОБЕЛ", "Прыжок"),
            ("R", "Рестарт"),
            ("ESC", "Меню")]

        total_controls_width = 4 * cube_size + 3 * cube_spacing
        controls_start_x = (SCREEN_WIDTH - total_controls_width) // 2
        controls_y = SCREEN_HEIGHT - 540
        for i, (key, desc) in enumerate(controls_data):
            x = controls_start_x + i * (cube_size + cube_spacing)
            arcade.draw_lrbt_rectangle_filled(
                x, x + cube_size, controls_y, controls_y + cube_size,
                (40, 60, 110))
            arcade.draw_lrbt_rectangle_filled(
                x + cube_size - 10, x + cube_size,
                controls_y, controls_y + cube_size - 10,
                (20, 40, 90))
            arcade.draw_lrbt_rectangle_filled(
                x, x + cube_size - 10,
                controls_y, controls_y + 10,
                (20, 40, 90))
            arcade.draw_text(key,
                             x + cube_size / 2, controls_y + cube_size - 35,
                             (0, 200, 255), 28,
                             anchor_x="center", bold=True)
            arcade.draw_text(desc,
                             x + cube_size / 2, controls_y + 25,
                             arcade.color.WHITE, 18,
                             anchor_x="center")

        center_y = SCREEN_HEIGHT - 650
        button_width, button_height = 300, 70
        arcade.draw_lrbt_rectangle_filled(
            SCREEN_WIDTH / 2 - button_width / 2,
            SCREEN_WIDTH / 2 + button_width / 2,
            center_y - button_height / 2,
            center_y + button_height / 2,
            (0, 180, 100))
        arcade.draw_lrbt_rectangle_filled(
            SCREEN_WIDTH / 2 - button_width / 2 + 5,
            SCREEN_WIDTH / 2 + button_width / 2 - 5,
            center_y - button_height / 2 - 5,
            center_y + button_height / 2 - 5,
            (0, 150, 80))
        arcade.draw_text("СТАРТ",
                         SCREEN_WIDTH / 2, center_y,
                         arcade.color.WHITE, 40,
                         anchor_x="center", anchor_y="center",
                         bold=True)
        if self.show_stats:
            arcade.draw_lrbt_rectangle_filled(
                100, SCREEN_WIDTH - 100,
                100, 350,
                (20, 30, 50, 230))
            arcade.draw_text("СТАТИСТИКА",
                             SCREEN_WIDTH / 2, 320,
                             arcade.color.YELLOW, 32,
                             anchor_x="center", bold=True)

            stats = [
                f"Максимальный уровень: {self.save_data['max_level_reached']}/5",
                f"Общий счет: {self.save_data['total_score']}",
                f"Собрано монет: {self.save_data['total_coins']}",
                f"Сыграно игр: {self.save_data['games_played']}",
                f"Побед: {self.save_data['games_won']}"]

            for i, stat in enumerate(stats):
                y_pos = 270 - i * 40
                arcade.draw_text(stat,
                                 SCREEN_WIDTH / 2, y_pos,
                                 arcade.color.WHITE, 24,
                                 anchor_x="center")
            arcade.draw_text("Нажмите S для закрытия статистики",
                             SCREEN_WIDTH / 2, 110,
                             (200, 200, 200), 20,
                             anchor_x="center")
        else:
            arcade.draw_text("Нажмите ПРОБЕЛ или кликните СТАРТ",
                             SCREEN_WIDTH / 2, 80,
                             arcade.color.YELLOW, 24,
                             anchor_x="center")
            arcade.draw_text("Нажмите S для просмотра статистики",
                             SCREEN_WIDTH / 2, 40,
                             (180, 180, 180), 18,
                             anchor_x="center")
            progress = self.save_data["max_level_reached"]
            arcade.draw_text(f"Прогресс: {progress}/5",
                             SCREEN_WIDTH - 200, SCREEN_HEIGHT - 50,
                             (100, 200, 255), 20)

    def on_update(self, delta_time: float):
        self.particle_system.update(delta_time)
        self.sparkle_timer += delta_time
        if self.sparkle_timer > 0.5:
            self.sparkle_timer = 0
            if random.random() < 0.3:  # 30% шанс
                x = random.randint(50, SCREEN_WIDTH - 50)
                y = random.randint(50, SCREEN_HEIGHT - 50)
                self.particle_system.create_sparkle_effect(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.show_stats:
            return

        button_x = SCREEN_WIDTH / 2
        button_y = SCREEN_HEIGHT - 650
        button_width, button_height = 300, 70

        if (abs(x - button_x) < button_width / 2 and
                abs(y - button_y) < button_height / 2):
            self.start_game()
        level_width = 180
        level_height = 100
        level_spacing = 30
        total_width = 5 * level_width + 4 * level_spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        level_y = SCREEN_HEIGHT - 320

        for i in range(1, 6):
            level_x = start_x + (i - 1) * (level_width + level_spacing)
            if (level_x <= x <= level_x + level_width and
                    level_y <= y <= level_y + level_height):
                if i <= self.save_data["max_level_reached"]:
                    self.start_game(i)
                break

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE or key == arcade.key.ENTER:
            if not self.show_stats:
                self.start_game()
        elif key == arcade.key.ESCAPE:
            arcade.close_window()
        elif key == arcade.key.S:
            self.show_stats = not self.show_stats
        elif key == arcade.key.R and modifiers & arcade.key.MOD_CTRL:
            self.save_data = SaveSystem.reset_save_data()

    def start_game(self, level_num=1):
        game_view = GameView()
        game_view.level = level_num
        game_view.load_level(level_num)
        self.window.show_view(game_view)


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.player_x = SCREEN_WIDTH // 4
        self.player_y = SCREEN_HEIGHT // 2
        self.player_dx = 0
        self.player_dy = 0
        self.jumping = False
        self.was_jumping = False
        self.coins = []
        self.enemies = []
        self.hazards = []
        self.platforms = []
        self.score = 0
        self.coins_collected = 0
        self.total_coins = 0
        self.level = 1
        self.time_left = 0
        self.game_over = False
        self.level_complete = False
        self.lives = 3
        self.last_enemy_collision_time = 0
        self.collision_cooldown = 0.5
        self.life_restored_this_level = False
        self.particle_system = ParticleSystem()
        self.save_data = SaveSystem.load_game_data()
        self.background_effect_timer = 0
        self.load_level(self.level)

    def load_level(self, level_num):
        if level_num not in LEVELS:
            self.level_complete = True
            self.game_over = True
            return

        level_data = LEVELS[level_num]

        self.player_x = 200
        self.player_y = 300
        self.player_dx = 0
        self.player_dy = 0
        self.jumping = False
        self.was_jumping = False
        self.coins_collected = 0
        self.platforms = []
        for plat in level_data["platforms"]:
            self.platforms.append(plat)
        self.coins = []
        self.total_coins = level_data["coins"]

        for i in range(self.total_coins):
            if self.platforms:
                plat_index = i % len(self.platforms)
                plat = self.platforms[plat_index]
                segments = min(2, self.total_coins // len(self.platforms) + 1)
                segment = (i // len(self.platforms)) % segments
                x = plat[0] + plat[2] * (segment + 1) / (segments + 1)
                y = plat[1] + plat[3] + 35
            else:
                x = random.randint(100, SCREEN_WIDTH - 100)
                y = random.randint(200, SCREEN_HEIGHT - 100)

            self.coins.append({
                "x": x,
                "y": y,
                "collected": False,
                "rotation": random.random() * 6.28,
                "bounce": random.random() * 6.28})

        self.enemies = []
        for i in range(level_data["enemies"]):
            if self.platforms[1:]:
                plat = random.choice(self.platforms[1:])
                x = plat[0] + plat[2] * 0.5
                y = plat[1] + plat[3] + ENEMY_SIZE / 2 + 5
            else:
                x = random.randint(100, SCREEN_WIDTH - 100)
                y = 200

            self.enemies.append({
                "x": x,
                "y": y,
                "dx": random.choice([-1.5, 1.5])})
        self.hazards = []
        for i in range(level_data["hazards"]):
            if random.random() > 0.4:
                x = random.randint(100, SCREEN_WIDTH - 100)
                y = 140
            else:
                if len(self.platforms) > 2:
                    plat1, plat2 = random.sample(self.platforms[1:], 2)
                    x = (plat1[0] + plat2[0] + plat2[2] / 2) / 2
                    y = (plat1[1] + plat2[1]) / 2
                else:
                    x = random.randint(100, SCREEN_WIDTH - 100)
                    y = random.randint(200, 400)

            self.hazards.append({
                "x": x,
                "y": y,
                "rotation": 0,
                "pulse": random.random() * 6.28})
        self.time_left = level_data["time"]

        self.game_over = False
        self.level_complete = False
        self.last_enemy_collision_time = 0
        self.life_restored_this_level = False

        if level_num > 1 and self.lives < 3:
            if not self.life_restored_this_level:
                self.lives += 1
                self.life_restored_this_level = True
                self.score += 25

                self.particle_system.add_particle(
                    self.player_x, self.player_y,
                    color=(100, 255, 100),
                    count=15,
                    speed=2.0,
                    size=4.0,
                    lifetime=1.0,
                    fade_out=True,
                    gravity_effect=0.3)

    def on_draw(self):
        self.clear()
        level_color = LEVELS.get(self.level, {}).get("background", BACKGROUND_COLOR)
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, level_color)

        for x in range(0, SCREEN_WIDTH, 60):
            arcade.draw_line(x, 0, x, SCREEN_HEIGHT, (35, 35, 65), 1)
        for plat in self.platforms:
            x, y, width, height = plat
            arcade.draw_lrbt_rectangle_filled(x, x + width, y, y + height, PLATFORM_COLOR)
            arcade.draw_lrbt_rectangle_outline(x, x + width, y, y + height, arcade.color.BLACK, 2)

        for hazard in self.hazards:
            x, y = hazard["x"], hazard["y"]
            rotation = hazard["rotation"]
            pulse = math.sin(hazard["pulse"]) * 0.2 + 0.8

            points = []
            for i in range(6):
                angle = i * math.pi / 3 + rotation
                radius = HAZARD_HEIGHT * pulse if i % 2 == 0 else HAZARD_HEIGHT * 0.5 * pulse
                px = x + math.cos(angle) * radius
                py = y + math.sin(angle) * radius
                points.append((px, py))
            arcade.draw_polygon_filled(points, HAZARD_COLOR)
            arcade.draw_circle_filled(x, y, HAZARD_HEIGHT * 0.3, (200, 80, 0))

        for enemy in self.enemies:
            x, y = enemy["x"], enemy["y"]
            arcade.draw_circle_filled(x, y, ENEMY_SIZE / 2, ENEMY_COLOR)

            eye_direction = 1 if enemy["dx"] > 0 else -1
            arcade.draw_circle_filled(x + 10 * eye_direction, y + 8, 8, arcade.color.WHITE)
            arcade.draw_circle_filled(x - 10 * eye_direction, y + 8, 8, arcade.color.WHITE)
            arcade.draw_circle_filled(x + 10 * eye_direction, y + 8, 4, arcade.color.BLACK)
            arcade.draw_circle_filled(x - 10 * eye_direction, y + 8, 4, arcade.color.BLACK)

            arcade.draw_arc_outline(x, y - 5, 15, 10, arcade.color.BLACK, 0, 180, 3)

        for coin in self.coins:
            if not coin["collected"]:
                x, y = coin["x"], coin["y"]
                rotation = coin["rotation"]
                bounce = math.sin(coin["bounce"]) * 3
                arcade.draw_circle_filled(x, y + bounce, COIN_SIZE, COIN_COLOR)
                arcade.draw_circle_filled(x, y + bounce, COIN_SIZE * 0.7, (255, 235, 100))
                blink_x = x + math.cos(rotation) * COIN_SIZE * 0.4
                blink_y = y + bounce + math.sin(rotation) * COIN_SIZE * 0.4
                arcade.draw_circle_filled(blink_x, blink_y, COIN_SIZE * 0.3, (255, 255, 255, 200))
                arcade.draw_circle_outline(x, y + bounce, COIN_SIZE, (200, 170, 0), 2)

        arcade.draw_lrbt_rectangle_filled(
            self.player_x - PLAYER_SIZE / 2,
            self.player_x + PLAYER_SIZE / 2,
            self.player_y - PLAYER_SIZE / 2,
            self.player_y + PLAYER_SIZE / 2,
            PLAYER_COLOR)

        arcade.draw_circle_filled(self.player_x, self.player_y + PLAYER_SIZE * 0.3,
                                  PLAYER_SIZE * 0.4, (50, 100, 200))
        arcade.draw_circle_filled(self.player_x + 8, self.player_y + PLAYER_SIZE * 0.3 + 5,
                                  5, arcade.color.WHITE)
        arcade.draw_circle_filled(self.player_x - 8, self.player_y + PLAYER_SIZE * 0.3 + 5,
                                  5, arcade.color.WHITE)
        arcade.draw_circle_filled(self.player_x + 8, self.player_y + PLAYER_SIZE * 0.3 + 5,
                                  2, arcade.color.BLACK)
        arcade.draw_circle_filled(self.player_x - 8, self.player_y + PLAYER_SIZE * 0.3 + 5,
                                  2, arcade.color.BLACK)
        arcade.draw_arc_outline(
            self.player_x,
            self.player_y + PLAYER_SIZE * 0.3 - 8,
            10, 6,
            arcade.color.BLACK, 0, 180, 2)

        self.particle_system.draw()
        self.draw_ui()
        if self.game_over:
            self.draw_game_over_screen()

        if self.level_complete:
            self.draw_level_complete_screen()

    def draw_ui(self):
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, SCREEN_HEIGHT - 70, SCREEN_HEIGHT,
            (0, 0, 0, 180))

        level_name = LEVELS.get(self.level, {}).get("name", "Неизвестный уровень")
        arcade.draw_text(f"Уровень {self.level}: {level_name}",
                         20, SCREEN_HEIGHT - 40,
                         arcade.color.WHITE, 22)
        arcade.draw_text(f"Монеты: {self.coins_collected}/{self.total_coins}",
                         20, SCREEN_HEIGHT - 70,
                         arcade.color.GOLD, 20)
        arcade.draw_text(f"Очки: {self.score}",
                         SCREEN_WIDTH - 200, SCREEN_HEIGHT - 40,
                         arcade.color.WHITE, 22)
        record = self.save_data["level_records"].get(str(self.level), 0)
        if record > 0:
            arcade.draw_text(f"Рекорд: {record}",
                             SCREEN_WIDTH - 200, SCREEN_HEIGHT - 70,
                             arcade.color.GOLD, 18)

        minutes = int(self.time_left) // 60
        seconds = int(self.time_left) % 60
        time_color = arcade.color.WHITE
        if self.time_left < 30:
            time_color = arcade.color.RED
        arcade.draw_text(f"Время: {minutes:02d}:{seconds:02d}",
                         SCREEN_WIDTH / 2, SCREEN_HEIGHT - 55,
                         time_color, 20,
                         anchor_x="center")
        for i in range(3):
            heart_x = SCREEN_WIDTH - 350 - i * 35
            heart_y = SCREEN_HEIGHT - 50
            if i < self.lives:
                arcade.draw_text("♥", heart_x, heart_y, arcade.color.RED, 26)
            else:
                arcade.draw_text("♡", heart_x, heart_y, (100, 100, 100), 26)
        arcade.draw_text("ESC: Меню  R: Рестарт",
                         SCREEN_WIDTH / 2, 20,
                         (200, 200, 200), 18,
                         anchor_x="center")

    def draw_game_over_screen(self):
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
            (0, 0, 0, 180))
        arcade.draw_text("ИГРА ОКОНЧЕНА",
                         SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50,
                         arcade.color.RED, 60,
                         anchor_x="center", bold=True)
        arcade.draw_text(f"Счет: {self.score}",
                         SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                         arcade.color.WHITE, 40,
                         anchor_x="center")
        SaveSystem.update_level_record(self.level, self.score, self.coins_collected)
        arcade.draw_text("Нажмите ПРОБЕЛ для новой игры",
                         SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 60,
                         arcade.color.YELLOW, 26,
                         anchor_x="center")
        arcade.draw_text("Нажмите ESC для выхода в меню",
                         SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100,
                         arcade.color.WHITE, 22,
                         anchor_x="center")

    def draw_level_complete_screen(self):
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
            (0, 50, 0, 180))
        arcade.draw_text("УРОВЕНЬ ПРОЙДЕН!",
                         SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50,
                         arcade.color.GREEN, 60,
                         anchor_x="center", bold=True)
        arcade.draw_text(f"Собрано монет: {self.coins_collected}/{self.total_coins}",
                         SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                         arcade.color.GOLD, 40,
                         anchor_x="center")
        SaveSystem.update_level_record(self.level, self.score, self.coins_collected)

        if not hasattr(self, 'completion_effect_created'):
            self.particle_system.create_level_complete_effect(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            self.completion_effect_created = True
        if self.level < len(LEVELS) and self.life_restored_this_level and self.lives <= 3:
            arcade.draw_text(f"Жизнь восстановлена! (+1 ♥)",
                             SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 40,
                             (100, 255, 100), 28,
                             anchor_x="center")
            next_level = LEVELS.get(self.level + 1, {})
            arcade.draw_text(f"Следующий: {next_level.get('name', '')}",
                             SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 90,
                             arcade.color.CYAN, 30,
                             anchor_x="center")
            arcade.draw_text("Нажмите ПРОБЕЛ для продолжения",
                             SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 140,
                             arcade.color.YELLOW, 26,
                             anchor_x="center")
        elif self.level < len(LEVELS):
            next_level = LEVELS.get(self.level + 1, {})
            arcade.draw_text(f"Следующий: {next_level.get('name', '')}",
                             SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 60,
                             arcade.color.CYAN, 30,
                             anchor_x="center")
            arcade.draw_text("Нажмите ПРОБЕЛ для продолжения",
                             SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 120,
                             arcade.color.YELLOW, 26,
                             anchor_x="center")
        else:
            arcade.draw_text("ВЫ ПРОШЛИ ВСЕ УРОВНИ!",
                             SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 60,
                             arcade.color.GOLD, 40,
                             anchor_x="center", bold=True)
            arcade.draw_text("Нажмите ПРОБЕЛ для новой игры",
                             SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 120,
                             arcade.color.YELLOW, 26,
                             anchor_x="center")

    def on_update(self, delta_time):
        self.last_enemy_collision_time += delta_time
        self.particle_system.update(delta_time)
        self.background_effect_timer += delta_time
        if self.background_effect_timer > 0.2:
            self.background_effect_timer = 0
            if random.random() < 0.1:  # 10% шанс
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                self.particle_system.create_sparkle_effect(x, y)

        if self.game_over or self.level_complete:
            for coin in self.coins:
                coin["rotation"] += delta_time * 2
                coin["bounce"] += delta_time * 1.5
            for hazard in self.hazards:
                hazard["rotation"] += delta_time * 2
                hazard["pulse"] += delta_time * 3
            return

        self.time_left -= delta_time
        if self.time_left <= 0:
            self.game_over = True
            return

        self.player_dy -= GRAVITY
        old_player_y = self.player_y
        self.player_x += self.player_dx
        self.player_y += self.player_dy

        if old_player_y > self.player_y and not self.jumping:
            self.was_jumping = True

        if self.player_x < PLAYER_SIZE / 2:
            self.player_x = PLAYER_SIZE / 2
        if self.player_x > SCREEN_WIDTH - PLAYER_SIZE / 2:
            self.player_x = SCREEN_WIDTH - PLAYER_SIZE / 2
        if self.level >= 3:
            if self.player_y < -100:
                self.lives = 0
                self.game_over = True
                return
        else:
            if self.player_y < PLAYER_SIZE / 2:
                self.player_y = PLAYER_SIZE / 2
                self.player_dy = 0
                self.jumping = False

        if self.player_y > SCREEN_HEIGHT - PLAYER_SIZE / 2:
            self.player_y = SCREEN_HEIGHT - PLAYER_SIZE / 2
            self.player_dy = 0

        was_in_air = self.jumping
        self.jumping = True
        player_radius = PLAYER_SIZE / 2
        for plat in self.platforms:
            plat_x, plat_y, plat_w, plat_h = plat
            player_left = self.player_x - player_radius
            player_right = self.player_x + player_radius
            player_top = self.player_y + player_radius
            player_bottom = self.player_y - player_radius
            if (player_right > plat_x and
                    player_left < plat_x + plat_w and
                    player_bottom < plat_y + plat_h and
                    player_top > plat_y and
                    self.player_dy <= 0):

                self.player_y = plat_y + plat_h + player_radius
                self.player_dy = 0
                self.jumping = False
                if was_in_air and self.was_jumping:
                    self.particle_system.create_landing_effect(self.player_x, self.player_y)
                    self.was_jumping = False
                break

        for coin in self.coins:
            if not coin["collected"]:
                dx = coin["x"] - self.player_x
                dy = coin["y"] + math.sin(coin["bounce"]) * 3 - self.player_y
                distance = math.sqrt(dx * dx + dy * dy)
                if distance < (COIN_SIZE + player_radius):
                    coin["collected"] = True
                    self.coins_collected += 1
                    self.score += 100
                    # Эффект сбора монеты
                    self.particle_system.create_coin_effect(coin["x"], coin["y"])

        if all(coin["collected"] for coin in self.coins):
            self.level_complete = True
            bonus = int(self.time_left) * 10
            self.score += bonus
            return

        for enemy in self.enemies:
            enemy["x"] += enemy["dx"]

            if enemy["x"] < ENEMY_SIZE / 2 or enemy["x"] > SCREEN_WIDTH - ENEMY_SIZE / 2:
                enemy["dx"] *= -1

            dx = enemy["x"] - self.player_x
            dy = enemy["y"] - self.player_y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance < (ENEMY_SIZE / 2 + player_radius):
                if self.last_enemy_collision_time > self.collision_cooldown:
                    self.lives -= 1
                    self.last_enemy_collision_time = 0
                    self.particle_system.create_enemy_hit_effect(self.player_x, self.player_y)
                    knockback = 3
                    self.player_dx = -knockback if dx > 0 else knockback
                    self.player_dy = knockback * 0.3

                    if self.lives <= 0:
                        self.game_over = True

        for hazard in self.hazards:
            dx = hazard["x"] - self.player_x
            dy = hazard["y"] - self.player_y
            distance = math.sqrt(dx * dx + dy * dy)
            hazard_radius = HAZARD_HEIGHT
            if distance < (hazard_radius + player_radius):
                self.lives -= 1
                self.particle_system.create_hazard_effect(self.player_x, self.player_y)
                knockback = 8
                self.player_dx = -knockback if dx > 0 else knockback
                self.player_dy = knockback * 0.4
                if self.lives <= 0:
                    self.game_over = True

    def on_key_press(self, key, modifiers):
        if self.game_over:
            if key == arcade.key.SPACE:
                # Новая игра
                self.score = 0
                self.lives = 3
                self.level = 1
                self.load_level(self.level)
            elif key == arcade.key.ESCAPE:
                start_view = StartView()
                self.window.show_view(start_view)
            return

        if self.level_complete:
            if key == arcade.key.SPACE:
                if self.level < len(LEVELS):
                    self.level += 1
                    self.load_level(self.level)
                else:
                    self.score = 0
                    self.lives = 3
                    self.level = 1
                    self.load_level(self.level)
            elif key == arcade.key.ESCAPE:
                start_view = StartView()
                self.window.show_view(start_view)
            return

        if key == arcade.key.SPACE:
            if not self.jumping:
                self.player_dy = PLAYER_JUMP_SPEED
                self.jumping = True
                self.was_jumping = True
                self.particle_system.create_jump_effect(self.player_x, self.player_y)
        elif key == arcade.key.LEFT:
            self.player_dx = -PLAYER_MOVE_SPEED
        elif key == arcade.key.RIGHT:
            self.player_dx = PLAYER_MOVE_SPEED
        elif key == arcade.key.R:
            self.load_level(self.level)
        elif key == arcade.key.ESCAPE:
            start_view = StartView()
            self.window.show_view(start_view)

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.RIGHT):
            self.player_dx = 0


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
