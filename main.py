import tkinter as tk
import math
import random
import pygame
def merge_vertical(data):
    # x と color ごとにまとめる
    grouped = {}
    for item in data:
        key = (item["x"], item["color"])
        grouped.setdefault(key, []).append(item)

    merged_result = []

    for (x, color), items in grouped.items():
        # y の昇順で並べる
        items.sort(key=lambda i: i["y"])

        merged = []
        for item in items:
            if not merged:
                merged.append(item.copy())
            else:
                last = merged[-1]
                last_end = last["y"] + last["height"]
                curr_start = item["y"]
                curr_end = item["y"] + item["height"]

                if curr_start <= last_end + 5:  # 縦に接している/重なっている
                    last["height"] = max(last_end, curr_end) - last["y"]
                else:
                    merged.append(item.copy())
        merged_result.extend(merged)

    return merged_result
def merge_intervals(data):
    merged = []
    for i in data:
        if len(merged) == 0:
            merged.append(i.copy())
            continue
        for j in merged:
            # jがiと重なっているかをチェック
            if (i["x"] < j["x"] + j["width"] and
                i["x"] + i["width"] > j["x"] and
                i["y"] == j["y"]):
                # 同色の場合マージ
                if i["color"] == j["color"]:
                    j["x"] = min(j["x"], i["x"])
                    j["width"] = max(j["x"] + j["width"], i["x"] + i["width"]) - j["x"]
                    break
                else:
                    # jがiより小さい場合jを削除
                    if j["width"] < i["width"]:
                        merged.remove(j)
                        merged.append(i.copy())
                        break
                    # jがiより大きい場合はjを二つに分割しiを追加
                    elif i["x"] < j["x"] and i["x"] + i["width"] > j["x"] + j["width"]:
                        new_rect1 = j.copy()
                        new_rect2 = i.copy()
                        new_rect1["width"] = i["x"] - j["x"]
                        new_rect2["x"] = i["x"] + i["width"]
                        new_rect2["y"] = j["y"]
                        new_rect2["width"] = j["x"] + j["width"] - new_rect2["x"]
                        new_rect2["color"] = j["color"]
                        merged.remove(j)
                        merged.append(new_rect1)
                        merged.append(new_rect2)
                        merged.append(i.copy())
                        break
                    elif i["x"] < j["x"]:
                        xw = j["x"] + j["width"]
                        j["x"] = i["x"] + i["width"]
                        j["width"] = xw - j["x"]
                        merged.append(i.copy())
                    elif i["x"] > j["x"]:
                        j["width"] = i["x"] - j["x"]
                        merged.append(i.copy())


            else:
                merged.append(i.copy())
                break
    return merged

def get_angle(x1, y1, x2, y2, degree=True):
    """
    2点 (x1, y1), (x2, y2) から角度を求める関数

    Parameters
    ----------
    x1, y1 : float
        始点の座標
    x2, y2 : float
        終点の座標
    degree : bool (default=True)
        True なら角度を度(°)で返す。False ならラジアン(rad)で返す。

    Returns
    -------
    float
        始点から終点への角度
    """
    dx = x2 - x1
    dy = y2 - y1
    theta = math.atan2(dy, dx)  # ラジアン

    return math.degrees(theta) if degree else theta
class Apprication:
    def __init__(self):
        pygame.mixer.init()
        self.root = tk.Tk()
        self.root.title("Splatoon")
        self.root.geometry("800x600")
        self.canvas = tk.Canvas(self.root, bg="lightgreen")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.keys = set()
        self.camera_x = 0
        self.camera_y = 0
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_pressed = False
        self.player_number = "player1"
        self.player_data = {
            "player1": {"x": -1000, "y": 0, "color": "yellow", "falling_speed": 0, "grounded": True, "bullet_frame": 0, "isSquid": False,"onInk": False, "isCPU": False, "yDir": 0},
            "player2": {"x": 1000, "y": 0, "color": "blue", "falling_speed": 0,"grounded": True, "bullet_frame": 0, "isSquid": False,"onInk": False, "isCPU": True, "yDir": 0},
        }
        self.ground_data = [
            {"position": [-1100,0,1100,-50], "color": "brown"},
            {"position": [-930,100,-700,0], "color": "gray"},
            {"position": [-650,180,-600,120], "color": "gray"},
            {"position": [-650,220,-300,180], "color": "gray"},
            {"position": [-450,700,-400,250], "color": "gray"},
            {"position": [-380,350,-100,300], "color": "gray"},
            {"position": [-200,50,200,0], "color": "gray"},
            {"position": [-50,300,50,100], "color": "gray"},
            {"position": [700,100,930,0], "color": "gray"},
            {"position": [600,180,650,120], "color": "gray"},
            {"position": [300,220,650,180], "color": "gray"},
            {"position": [400,700,450,250], "color": "gray"},
            {"position": [100,350,380,300], "color": "gray"},
        ]
        self.painted_data = []
        self.bullet_data = []
        self.canvas.bind("<KeyPress>", self.key_press)
        self.canvas.bind("<KeyRelease>", self.key_release)
        self.canvas.bind("<Motion>", self.mouse_move)
        self.canvas.bind("<ButtonPress-1>", self.mouse_press)
        self.canvas.bind("<ButtonRelease-1>", self.mouse_release)
        self.canvas.focus_set()
    def add_bullet_data(self, x, y, Direction, color, attack):
        if attack == 0:
            self.bullet_data.append({"x": x, "y": y,"Direction":Direction, "color": color, "falling_speed": 10,"frame": 20,"attack": attack})
        else:
            self.bullet_data.append({"x": x, "y": y,"Direction":Direction, "color": color, "falling_speed": 0,"frame": 0,"attack": attack})
    def mouse_move(self, event):
        self.mouse_x = event.x
        self.mouse_y = event.y
    def mouse_press(self, event):
        self.mouse_pressed = True
    def mouse_release(self, event):
        self.mouse_pressed = False
    def key_press(self, event):
        self.keys.add(event.keysym)
        if event.keysym == "Escape":
            self.root.quit()
        elif event.keysym == "e":
            self.player_data[self.player_number]["isSquid"] = not self.player_data[self.player_number]["isSquid"]
    def key_release(self, event):
        if event.keysym in self.keys:
            self.keys.remove(event.keysym)
    def draw_players(self):
        for i in self.player_data:
            player = self.player_data[i]
            if player["onInk"] and player["isSquid"]:
                if self.player_number == i:
                    self.canvas.create_oval(self.camera_x + player["x"] - 10, self.camera_y + 500 - player["y"] - 3, 
                                            self.camera_x + player["x"] + 10, self.camera_y + 500 - player["y"], 
                                            fill=player["color"], outline="black",tags=[i,"player"])
            if player["isSquid"]:
                self.canvas.create_oval(self.camera_x + player["x"] - 10, self.camera_y + 500 - player["y"] - 3, 
                                        self.camera_x + player["x"] + 10, self.camera_y + 500 - player["y"], 
                                        fill=player["color"], outline="black",tags=[i,"player"])
            else:
                self.canvas.create_oval(self.camera_x + player["x"] - 10, self.camera_y + 500 - player["y"] - 20, 
                                        self.camera_x + player["x"] + 10, self.camera_y + 500 - player["y"], 
                                        fill=player["color"], outline="black",tags=[i,"player"])
    def draw_ground(self):
        for i in self.ground_data:
            ground = i["position"]
            self.canvas.create_rectangle(self.camera_x + ground[0], self.camera_y + 500 - ground[1],
                                         self.camera_x + ground[2], self.camera_y + 500 - ground[3], 
                                         fill=i["color"], outline="black", tags="ground")
    def draw_bullets(self):
        for i in self.bullet_data:
            bullet = i
            if i["attack"] == 0:
                continue
            self.canvas.create_oval(self.camera_x + bullet["x"] - 2, self.camera_y + 500 - bullet["y"] - 2,
                                         self.camera_x + bullet["x"] + 2, self.camera_y + 500 - bullet["y"] + 2, 
                                         fill=bullet["color"], width=0, tags="bullet")
    def draw_painted(self):
        for i in self.painted_data:
            self.canvas.create_rectangle(self.camera_x + i["x"], self.camera_y + 500 - i["y"] - i["height"],
                                         self.camera_x + i["x"] + i["width"], self.camera_y + 500 - i["y"], 
                                         fill=i["color"], width=0, tags="painted")
    def first_draw(self):
        self.draw_players()
        self.draw_ground()
    def update(self):
        # プレイヤー制御
        count = 1
        for i in self.player_data:
            # 落下計算
            player = self.player_data[i]
            if not player["grounded"]:
                player["falling_speed"] += 0.25
                player["y"] -= player["falling_speed"]
            else:
                player["falling_speed"] = 0
        
            player["grounded"] = False
            for i in self.ground_data:
                ground = i["position"]
                if (player["x"] >= ground[0] and player["x"] <= ground[2] and 
                    player["y"] <= ground[1] and player["y"] >= ground[1] - player["falling_speed"]*2):
                    player["grounded"] = True
                    player["y"] = ground[1]
                    break
            # プレイヤー制御
            if True:
                if self.player_number == "player" + str(count):
                    # 左右移動
                    last_x = player["x"]
                    speed = 0.5 if self.mouse_pressed else 1.5
                    if player["isSquid"] and player["onInk"]:
                        speed = 4
                    if player["isSquid"] and player["falling_speed"] < 0:
                        speed = 3
                    if "a" in self.keys:
                        player["x"] -= speed
                    if "d" in self.keys:
                        player["x"] += speed
                    # 壁との衝突判定
                    for i in self.ground_data:
                        ground = i["position"]
                        if (player["x"] >= ground[0] and player["x"] <= ground[2] and 
                            player["y"] + 1 <= ground[1] and player["y"] + 1 >= ground[3]):
                            if abs(player["x"] - ground[0]) < abs(player["x"] - ground[2]):
                                player["x"] = ground[0] + 1
                            else:
                                player["x"] = ground[2] + 1
                            self.check_player_on_ink(player)
                            if player["isSquid"] and player["onInk"] and ("d" in self.keys or "a" in self.keys):
                                player["y"] += 7
                                player["grounded"] = False
                                player["falling_speed"] = 0
                    # ジャンプ
                    if ("w" in self.keys or "space" in self.keys) and player["grounded"]:
                        player["falling_speed"] = -6
                        player["grounded"] = False
                    # 弾を撃つ
                    if self.mouse_pressed and player["bullet_frame"] <= 0:
                        player["isSquid"] = False
                        pygame.mixer.Sound("shot.wav").play()
                        self.add_bullet_data(player["x"], player["y"] + 10, get_angle(player["x"],-(player["y"] + 10),self.mouse_x - self.camera_x,-(self.camera_y + 500 - self.mouse_y)) + random.randint(-2,2), player["color"], 28)
                        player["bullet_frame"] = 3
                    else:
                        player["bullet_frame"] -= 1
                    # イカ状態
                    self.check_player_on_ink(player)
            # CPU制御
            if player["isCPU"]:
                print("CPU Control")
                # 左右移動
                last_x = player["x"]
                speed = 0.5 if self.mouse_pressed else 1.5
                if player["isSquid"] and player["onInk"]:
                    speed = 4
                if player["isSquid"] and player["falling_speed"] < 0:
                    speed = 3
                moved = False
                if player["x"] > self.player_data["player1"]["x"]: # あとで必ず編集
                    player["x"] -= speed
                    moved = True
                if player["x"] < self.player_data["player1"]["x"]:
                    player["x"] += speed
                    moved = True
                touched = False
                # 壁との衝突判定
                for i in self.ground_data:
                    ground = i["position"]
                    if (player["x"] >= ground[0] and player["x"] <= ground[2] and 
                        player["y"] + 1 <= ground[1] and player["y"] + 1 >= ground[3]):
                        if abs(player["x"] - ground[0]) < abs(player["x"] - ground[2]):
                            player["x"] = ground[0] + 1
                        else:
                            player["x"] = ground[2] + 1
                        self.check_player_on_ink(player)
                        if player["isSquid"] and player["onInk"] and moved:
                            player["y"] += 7
                            player["grounded"] = False
                            player["falling_speed"] = 0
                        touched = True
                
                # 弾を撃つ
                if not player["onInk"] and player["isSquid"] and (player["grounded"] or touched):
                    player["yDir"] = 20
                    player["falling_speed"] = -6
                    player["grounded"] = False
                if player["yDir"] > -5:
                    if player["bullet_frame"] <= 0:
                        player["isSquid"] = False
                        pygame.mixer.Sound("shot.wav").play()
                        self.add_bullet_data(player["x"], player["y"] + 10, get_angle(player["x"],-(player["y"] + 10),player["x"] + (int(self.player_data["player1"]["x"] > player["x"]) - 0.5)*20,-(player["y"] + 10) - player["yDir"]), player["color"], 28)
                        player["bullet_frame"] = 3
                    else:
                        player["bullet_frame"] -= 1
                    player["yDir"] -= 1
                    print("yDir:", player["yDir"])
                else:
                    player["isSquid"] = True
                # イカ状態
                self.check_player_on_ink(player)

            count += 1
        # カメラ制御
        if abs(self.player_data["player1"]["x"] - self.player_data["player2"]["x"]) < 400:
            self.camera_x = ((-(self.player_data["player1"]["x"] + self.player_data["player2"]["x"])/2 + 400) + self.camera_x*4) / 5
        else:
            self.camera_x = ((-self.player_data[self.player_number]["x"] + 400) + self.camera_x*4) / 5

        # 弾の制御
        for i in self.bullet_data:
            bullet = i
            bullet["frame"] += 1
            if bullet["frame"] < 10:
                bullet["x"] += 10 * math.cos(math.radians(bullet["Direction"]))
            else:
                bullet["x"] += 5 * math.cos(math.radians(bullet["Direction"]))
            bullet["y"] -= 10 * math.sin(math.radians(bullet["Direction"]))
            if bullet["frame"] > 10:
                bullet["falling_speed"] += 1
            bullet["y"] -= bullet["falling_speed"]
            if(bullet["attack"] != 0 and random.randint(0, 100) < 70):
                self.add_bullet_data(bullet["x"], bullet["y"] + 10, 90, bullet["color"], 0)
            # 地面との衝突判定
            for j in self.ground_data:
                ground = j["position"]
                if (bullet["x"] >= ground[0] and bullet["x"] <= ground[2] and 
                    bullet["y"] <= ground[1] and bullet["y"] >= ground[3]):
                    if(abs(bullet["y"] - ground[1]) < 5):
                        self.painted_data.append({"x": bullet["x"], "y": ground[1],"width":5,"height":6, "color": bullet["color"]})
                    else:
                        if abs(bullet["x"] - ground[0]) < abs(bullet["x"] - ground[2]):
                            self.painted_data.append({"x": ground[0], "y": bullet["y"],"width":8, "height":6, "color": bullet["color"]})
                        else:
                            self.painted_data.append({"x": ground[2], "y": bullet["y"],"width":8, "height":6, "color": bullet["color"]})
                    self.bullet_data.remove(i)
                    break
            # 30フレームで削除
            try:
                if bullet["frame"] > 30:
                    self.bullet_data.remove(i)
                    continue
            except:pass


        # 塗りつぶしの統合
        self.painted_data = merge_intervals(self.painted_data)
        self.painted_data = merge_vertical(self.painted_data)      

        self.root.after(16,self.update)

    def check_player_on_ink(self, player):
        player["onInk"] = False
        for i in self.painted_data:
            if (player["x"] >= i["x"] and player["x"] <= i["x"] + i["width"] and 
                        player["y"] <= i["y"] + i["height"] and player["y"] >= i["y"] and player["color"] == i["color"]):
                player["onInk"] = True
                break

    def draw(self):
        self.canvas.delete("ground")
        self.draw_ground()
        self.canvas.delete("bullet")
        self.draw_bullets()
        self.canvas.delete("painted")
        self.draw_painted()
        self.canvas.delete("player")
        self.draw_players()
        self.root.after(40,self.draw)

    def run(self):
        self.first_draw()
        self.root.after(16,self.update)
        self.root.after(40,self.draw)
        self.root.mainloop()
if __name__ == "__main__":
    app = Apprication()
    app.run()