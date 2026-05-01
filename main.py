import pygame
import sys
import math
import random
import json
import os

# --- INICIALIZAÇÃO ---
pygame.init()
pygame.font.init()

# --- SISTEMA DE ASSETS (AUDIO, IMAGENS E FONTES) ---
AUDIO_ENABLED = False
try:
    pygame.mixer.init()
    AUDIO_ENABLED = True
except Exception as e:
    print("Aviso: Nao foi possivel inicializar o sistema de audio.", e)

CURRENT_MUSIC = None
SFX = {}
IMAGES = {}

def load_sfx():
    if not AUDIO_ENABLED: return
    sfx_files = {
        'attack': 'attack.wav', 
        'jump': 'jump.wav', 
        'hit': 'hit.wav', 
        'select': 'select.wav',
        'typing': 'typing.wav',    
        'delete': 'delete.wav',    
        'confirm': 'confirm.wav',  
        'death': 'death.wav'       
    }
    for key, filename in sfx_files.items():
        path_assets = os.path.join("assets", filename)
        if os.path.exists(path_assets):
            try: SFX[key] = pygame.mixer.Sound(path_assets)
            except: pass
        elif os.path.exists(filename):
            try: SFX[key] = pygame.mixer.Sound(filename)
            except: pass

def play_sfx(sound_name):
    if sound_name in SFX:
        try: SFX[sound_name].play()
        except: pass

def play_music(track_name):
    global CURRENT_MUSIC
    if not AUDIO_ENABLED or CURRENT_MUSIC == track_name: return
    
    for ext in ['.ogg', '.mp3', '.wav']:
        filename = f"{track_name}{ext}"
        path_assets = os.path.join("assets", filename)
        
        target_path = None
        if os.path.exists(path_assets):
            target_path = path_assets
        elif os.path.exists(filename):
            target_path = filename
            
        if target_path:
            try:
                pygame.mixer.music.load(target_path)
                pygame.mixer.music.play(-1)
                CURRENT_MUSIC = track_name
                return
            except Exception as e:
                print(f"Erro ao tocar {target_path}:", e)
    
    if track_name == 'gameover':
        play_music('menu')

def load_images():
    themes = ['forest', 'cave', 'volcano', 'electric']
    for theme in themes:
        for ext in ['.png', '.jpg', '.jpeg']:
            filename = f"bg_{theme}{ext}"
            path_assets = os.path.join("assets", filename)
            target_path = None
            if os.path.exists(path_assets): target_path = path_assets
            elif os.path.exists(filename): target_path = filename
                
            if target_path:
                try:
                    img = pygame.image.load(target_path).convert_alpha()
                    IMAGES[f'bg_{theme}'] = img
                    break
                except Exception as e:
                    print(f"Erro ao carregar imagem {target_path}:", e)

        for ext in ['.png', '.jpg', '.jpeg']:
            plat_name = f"plat_{theme}{ext}"
            plat_path = os.path.join("assets", plat_name)
            target_plat = None
            if os.path.exists(plat_path): target_plat = plat_path
            elif os.path.exists(plat_name): target_plat = plat_name
            if target_plat:
                try:
                    img = pygame.image.load(target_plat).convert_alpha()
                    IMAGES[f'plat_{theme}'] = img
                    break
                except Exception as e:
                    print(f"Erro ao carregar textura {target_plat}:", e)

# --- CONSTANTES BASE DA JANELA ---
WINDOW_W, WINDOW_H = 1280, 720
GAME_W, GAME_H = 800, 480
GAME_X, GAME_Y = 240, 120
ZOOM_OUT = 1.45
FLOOR_Y = 800

# FISICA
FPS = 60
GRAVITY = 1.6

# --- FUNCOES UTILITARIAS ---
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3: hex_color = ''.join([c*2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def get_font(size, is_bold=False):
    for f in ["font.ttf", "pixel.ttf", "retro.ttf"]:
        path_assets = os.path.join("assets", f)
        if os.path.exists(path_assets):
            try: return pygame.font.Font(path_assets, size)
            except: pass
        elif os.path.exists(f):
            try: return pygame.font.Font(f, size)
            except: pass
            
    for sys_font in ['georgia', 'palatino', 'bookantiqua', 'impact', 'arial']:
        try: return pygame.font.SysFont(sys_font, size, bold=is_bold)
        except: continue
    return pygame.font.SysFont(None, size, bold=is_bold)

FONTS = {
    'huge': get_font(64, True), 'large': get_font(48, True),
    'medium': get_font(24, True), 'small': get_font(16, True), 'tiny': get_font(13, True) 
}

# --- ALGORITMO DE RECORTE ---
def load_and_cut_overlay():
    global GAME_W, GAME_H, GAME_X, GAME_Y
    img_path = None
    possible_names = ["overlay.png", "Entre Mundos UI Overlay Bezel.jpg", "overlay.jpg", "image_bb8f3e.jpg"]
    
    for name in possible_names:
        path_assets = os.path.join("assets", name)
        if os.path.exists(path_assets):
            img_path = path_assets
            break
        elif os.path.exists(name):
            img_path = name
            break
            
    if img_path:
        try:
            img = pygame.image.load(img_path).convert_alpha()
            img = pygame.transform.scale(img, (WINDOW_W, WINDOW_H))
            cx, cy = WINDOW_W // 2, WINDOW_H // 2
            def is_empty(x, y):
                r, g, b, a = img.get_at((x, y))
                return a < 50 or (r > 200 and g > 200 and b > 200)
            if is_empty(cx, cy):
                left, right, top, bottom = cx, cx, cy, cy
                while left > 0 and is_empty(left, cy): left -= 1
                while right < WINDOW_W - 1 and is_empty(right, cy): right += 1
                while top > 0 and is_empty(cx, top): top -= 1
                while bottom < WINDOW_H - 1 and is_empty(cx, bottom): bottom += 1
                left, right, top, bottom = left+8, right-8, top+8, bottom-8
                if left < right and top < bottom:
                    GAME_X, GAME_Y = left, top
                    GAME_W, GAME_H = right - left, bottom - top
                    img.fill((0, 0, 0, 0), rect=(GAME_X, GAME_Y, GAME_W, GAME_H))
                return img
        except: pass
    border_img = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
    border_img.fill((26, 15, 10))
    return border_img

# --- CONFIGURACOES DE DADOS ---
THEMES = {
    'forest':   {'bg_top': '#0a1a2a', 'bg_bot': '#1c3b2b', 'plat_base': '#3e2723', 'plat_top': '#2d4c1e', 'hazard': '#5c8a58', 'name': 'FLORESTA', 'boss_name': 'ENT ANCIAO'},
    'cave':     {'bg_top': '#100a18', 'bg_bot': '#2a1a4a', 'plat_base': '#1a0f0a', 'plat_top': '#4a3a5e', 'hazard': '#9d50bb', 'name': 'MASMORRA', 'boss_name': 'GOLIAS DE CRISTAL'},
    'volcano':  {'bg_top': '#2a0a0a', 'bg_bot': '#3a0f0f', 'plat_base': '#1a0f0a', 'plat_top': '#8b2a2a', 'hazard': '#ff4b2b', 'name': 'VULCAO', 'boss_name': 'SENHOR DAS CINZAS'},
    'electric': {'bg_top': '#050a1a', 'bg_bot': '#0f2a4a', 'plat_base': '#050a1a', 'plat_top': '#2a4a6a', 'hazard': '#00d2ff', 'name': 'TEMPESTADE', 'boss_name': 'ARCANO SUPREMO'}
}

CLASSES = {
    'warrior': {'hp': 150, 'speed': 5.0, 'jump': -34, 'color': '#a82424', 'atkType': 'melee', 'cooldown': 400, 'dmg': 40, 'name': 'CAVALEIRO', 'icon': 'C', 'sp_name': 'IMPACTO METEORO', 'sp_color': '#ff4444'}, 
    'mage':    {'hp': 80,  'speed': 5.5, 'jump': -31, 'color': '#00d2ff', 'atkType': 'magic', 'cooldown': 250, 'dmg': 25, 'name': 'MAGO', 'icon': 'M', 'sp_name': 'SINGULARIDADE ARCANA', 'sp_color': '#00d2ff'},
    'rogue':   {'hp': 100, 'speed': 8.0, 'jump': -33, 'color': '#2a7e43', 'atkType': 'arrow', 'cooldown': 200, 'dmg': 15, 'name': 'ARQUEIRO', 'icon': 'R', 'sp_name': 'TEMPESTADE ESMERALDA', 'sp_color': '#00ff88'}
}

ITEM_DB = {
    'potion_min': {'id': 'potion_min', 'name': 'Pocao Menor', 'icon': '+HP', 'desc': 'Cura 50 HP.', 'type': 'consumable', 'val': 50, 'rarity': 'common', 'color': '#ffffff'},
    'potion_max': {'id': 'potion_max', 'name': 'Elixir Divino', 'icon': '++HP', 'desc': 'Cura 200 HP.', 'type': 'consumable', 'val': 200, 'rarity': 'rare', 'color': '#00d2ff'},
    'ring_str':   {'id': 'ring_str', 'name': 'Anel Tita', 'icon': 'ANL', 'desc': 'Dano Base +15.', 'type': 'equip_ring', 'val': 15, 'rarity': 'rare', 'color': '#00d2ff'},
    'ring_epic':  {'id': 'ring_epic', 'name': 'Selo do Abismo', 'icon': 'SEL', 'desc': 'Dano Base +35.', 'type': 'equip_ring', 'val': 35, 'rarity': 'epic', 'color': '#b57edc'},
    'crown_gods': {'id': 'crown_gods', 'name': 'Coroa dos Deuses', 'icon': 'COR', 'desc': 'Dano Base +80.', 'type': 'equip_ring', 'val': 80, 'rarity': 'legendary', 'color': '#ffcc00'},
    'book_exp':   {'id': 'book_exp', 'name': 'Tomo de Sabedoria', 'icon': 'LIV', 'desc': 'Concede 1500 XP.', 'type': 'consumable', 'val': 1500, 'rarity': 'epic', 'color': '#b57edc'}
}

DIFF_LEVELS = [
    {'name': 'FACIL', 'mult': 0.75, 'color': '#2ecc71'},
    {'name': 'NORMAL', 'mult': 1.0, 'color': '#f1c40f'},
    {'name': 'DIFICIL', 'mult': 1.35, 'color': '#e67e22'},
    {'name': 'PESADELO', 'mult': 2.0, 'color': '#e74c3c'}
]

# --- DESENHO DE MODELOS PROCEDURAIS ---
def draw_hero_model(surface, x, y, cid, direction, bob, swing, atk_timer, aim_angle, vy, scale=1.0, is_crouching=False):
    flip = (direction == -1)

    s = pygame.Surface((160, 160), pygame.SRCALPHA)
    cx, cy = 80, 130 
    
    if cid == 'warrior':
        armor_c = hex_to_rgb("#181820")
        armor_trim = hex_to_rgb("#3a3a4a")
        accent_c = hex_to_rgb("#a00000")
        
        if atk_timer <= 0:
            shield_s = pygame.Surface((60, 80), pygame.SRCALPHA)
            pygame.draw.polygon(shield_s, hex_to_rgb("#0a0a0f"), [(30,0), (10,20), (10,60), (30,80), (50,60), (50,20)])
            pygame.draw.polygon(shield_s, armor_trim, [(30,0), (10,20), (10,60), (30,80), (50,60), (50,20)], 4)
            pygame.draw.polygon(shield_s, accent_c, [(30,20), (20,40), (30,70), (40,40)])
            shield_rect = shield_s.get_rect(center=(cx - 15, cy - 35 + bob + (swing*0.2)))
            s.blit(shield_s, shield_rect)

        pygame.draw.polygon(s, hex_to_rgb("#111"), [(cx-10, cy-40+bob), (cx-35, cy-5), (cx-15, cy-15)])
        
        pygame.draw.rect(s, armor_c, (cx - 12 + swing, cy - 12, 10, 14), border_radius=2)
        pygame.draw.rect(s, armor_c, (cx - 16, cy - 50 + bob, 32, 40), border_radius=4)
        pygame.draw.rect(s, armor_trim, (cx - 16, cy - 50 + bob, 32, 40), 2, border_radius=4)
        pygame.draw.rect(s, accent_c, (cx - 4, cy - 40 + bob, 8, 20))
        pygame.draw.rect(s, armor_c, (cx + 4 - swing, cy - 12, 10, 14), border_radius=2)
        
        pygame.draw.rect(s, armor_c, (cx - 12, cy - 74 + bob, 24, 24), border_radius=3)
        pygame.draw.rect(s, armor_trim, (cx - 12, cy - 74 + bob, 24, 24), 2, border_radius=3)
        pygame.draw.rect(s, hex_to_rgb("#200000"), (cx + 4, cy - 64 + bob, 8, 4)) 
        pygame.draw.rect(s, hex_to_rgb("#ff2020"), (cx + 6, cy - 64 + bob, 4, 4)) 
        
        arm_s = pygame.Surface((120, 120), pygame.SRCALPHA)
        cx_arm, cy_arm = 40, 60
        final_angle = (1.0 - (atk_timer / 400.0)) * 1080 if atk_timer > 0 else 30 + math.sin(swing)*10
        
        pygame.draw.rect(arm_s, armor_c, (cx_arm, cy_arm-6, 25, 12), border_radius=3)
        pygame.draw.rect(arm_s, hex_to_rgb("#111"), (cx_arm+15, cy_arm-50, 6, 90))
        blade_c, edge_c = hex_to_rgb("#303030"), hex_to_rgb("#ff2020")
        pygame.draw.polygon(arm_s, blade_c, [(cx_arm+18, cy_arm-40), (cx_arm+45, cy_arm-60), (cx_arm+55, cy_arm-40), (cx_arm+45, cy_arm-20)])
        pygame.draw.polygon(arm_s, edge_c, [(cx_arm+18, cy_arm-40), (cx_arm+45, cy_arm-60), (cx_arm+55, cy_arm-40), (cx_arm+45, cy_arm-20)], 2)
        pygame.draw.polygon(arm_s, blade_c, [(cx_arm+18, cy_arm-40), (cx_arm-9, cy_arm-60), (cx_arm-19, cy_arm-40), (cx_arm-9, cy_arm-20)])
        pygame.draw.polygon(arm_s, edge_c, [(cx_arm+18, cy_arm-40), (cx_arm-9, cy_arm-60), (cx_arm-19, cy_arm-40), (cx_arm-9, cy_arm-20)], 2)
        
        arm_rot = pygame.transform.rotate(arm_s, final_angle)
        arm_rect = arm_rot.get_rect(center=(cx+5, int(cy - 40 + bob)))
        s.blit(arm_rot, arm_rect)

    elif cid == 'mage':
        cloak_c = hex_to_rgb("#301050")
        trim_c = hex_to_rgb("#5a1b8a")
        gold_c = hex_to_rgb("#d4a74c")
        skin_c = hex_to_rgb("#f4e4bc")

        pygame.draw.polygon(s, hex_to_rgb("#2e4a2e"), [(cx-10, cy-35), (cx-25, cy-10+bob), (cx, cy-10)])
        pygame.draw.rect(s, cloak_c, (cx-14, cy-15, 28, 15))
        
        body_rect = pygame.Rect(cx - 14, cy - 48 + bob, 28, 40)
        pygame.draw.rect(s, trim_c, body_rect, border_radius=4)
        pygame.draw.rect(s, gold_c, body_rect, 2, border_radius=4)
        
        pygame.draw.rect(s, skin_c, (cx - 10, cy - 65 + bob, 20, 20), border_radius=8)
        pygame.draw.rect(s, (0,0,0), (cx + 4, cy - 60 + bob, 4, 4))
        pygame.draw.polygon(s, cloak_c, [(cx-18, cy-55+bob), (cx+18, cy-55+bob), (cx, cy-95+bob)])

        arm_s = pygame.Surface((80, 80), pygame.SRCALPHA)
        cx_arm, cy_arm = 40, 40
        pygame.draw.rect(arm_s, hex_to_rgb("#4a2f1b"), (cx_arm-10, cy_arm-3, 35, 6))
        pygame.draw.circle(arm_s, hex_to_rgb("#00d2ff"), (cx_arm+25, cy_arm), 8)
        pygame.draw.circle(arm_s, (255,255,255), (cx_arm+25, cy_arm), 3)
        
        arm_rot = pygame.transform.rotate(arm_s, aim_angle)
        arm_rect = arm_rot.get_rect(center=(cx+5, int(cy - 35 + bob)))
        s.blit(arm_rot, arm_rect)

    elif cid == 'rogue':
        cloak_c = hex_to_rgb("#2e4a2e")
        tunic_c = hex_to_rgb("#2a7e43")
        belt_c = hex_to_rgb("#4a2f1b")
        skin_c = hex_to_rgb("#f1c27d")

        pygame.draw.polygon(s, cloak_c, [(cx-10, cy-35), (cx-25, cy-10+bob), (cx-5, cy-10)])
        pygame.draw.rect(s, (40,40,40), (cx - 12 + swing, cy - 12, 10, 12), border_radius=2)
        
        body_rect = pygame.Rect(cx - 14, cy - 45 + bob, 28, 35)
        pygame.draw.rect(s, tunic_c, body_rect, border_radius=4)
        pygame.draw.rect(s, belt_c, (cx-15, cy-25+bob, 30, 6))

        pygame.draw.rect(s, (40,40,40), (cx + 4 - swing, cy - 12, 10, 12), border_radius=2)
        
        pygame.draw.rect(s, skin_c, (cx - 10, cy - 65 + bob, 20, 20), border_radius=6)
        pygame.draw.polygon(s, hex_to_rgb("#1e3a1e"), [(cx-14, cy-55+bob), (cx, cy-75+bob), (cx+14, cy-55+bob)])
        pygame.draw.rect(s, (0,0,0), (cx + 4, cy - 60 + bob, 4, 4))

        arm_s = pygame.Surface((80, 80), pygame.SRCALPHA)
        cx_arm, cy_arm = 40, 40
        pygame.draw.line(arm_s, hex_to_rgb("#5c4033"), (cx_arm+5, cy_arm-18), (cx_arm+15, cy_arm), 3)
        pygame.draw.line(arm_s, hex_to_rgb("#5c4033"), (cx_arm+15, cy_arm), (cx_arm+5, cy_arm+18), 3)
        if atk_timer > 100:
            pygame.draw.line(arm_s, (150,150,150), (cx_arm+5, cy_arm-18), (cx_arm, cy_arm), 1)
            pygame.draw.line(arm_s, (150,150,150), (cx_arm+5, cy_arm+18), (cx_arm, cy_arm), 1)
            pygame.draw.line(arm_s, (200,200,200), (cx_arm, cy_arm), (cx_arm+25, cy_arm), 2)
        else:
            pygame.draw.line(arm_s, (150,150,150), (cx_arm+5, cy_arm-18), (cx_arm+5, cy_arm+18), 1)
            
        arm_rot = pygame.transform.rotate(arm_s, aim_angle)
        arm_rect = arm_rot.get_rect(center=(cx+5, int(cy - 35 + bob)))
        s.blit(arm_rot, arm_rect)

    if flip:
        s = pygame.transform.flip(s, True, False)

    # Logica Visual do Agachamento (Encolhe a imagem verticalmente)
    if scale != 1.0 or is_crouching:
        w = int(160 * scale)
        h = int(160 * scale * (0.6 if is_crouching else 1.0))
        s = pygame.transform.scale(s, (w, h))
    
    # Mantem os pes sempre cravados no chao, mesmo encolhido
    feet_y_in_surface = cy * scale * (0.6 if is_crouching else 1.0)
    dest_x = x - (80 * scale)
    dest_y = y - feet_y_in_surface
    surface.blit(s, (dest_x, dest_y))

def draw_boss_model(surface, bx, by, theme, anim_frame, flash_timer, enraged):
    color = hex_to_rgb("#ffffff") if flash_timer > 0 else hex_to_rgb(THEMES[theme]['hazard'])
    if enraged and flash_timer == 0: color = hex_to_rgb("#ff0000") 
    bob = math.sin(anim_frame) * 8

    if theme == 'forest':
        body_color = (35, 20, 10) if flash_timer == 0 else color
        leaf_color = (30, 80, 40) if flash_timer == 0 else color
        pygame.draw.rect(surface, body_color, (bx - 40, by - 120 + bob, 80, 120), border_radius=10)
        if flash_timer == 0:
            pygame.draw.line(surface, (20, 10, 5), (bx - 20, by - 120 + bob), (bx - 20, by + bob), 4)
            pygame.draw.line(surface, (20, 10, 5), (bx + 20, by - 120 + bob), (bx + 20, by + bob), 4)
        pygame.draw.circle(surface, leaf_color, (bx, int(by - 130 + bob)), 60)
        pygame.draw.circle(surface, leaf_color, (bx - 45, int(by - 110 + bob)), 45)
        pygame.draw.circle(surface, leaf_color, (bx + 45, int(by - 110 + bob)), 45)
        pygame.draw.circle(surface, color, (bx - 15, int(by - 60 + bob)), 8)
        pygame.draw.circle(surface, color, (bx + 15, int(by - 60 + bob)), 8)
        pygame.draw.circle(surface, (255, 255, 255), (bx - 15, int(by - 60 + bob)), 3)
        pygame.draw.circle(surface, (255, 255, 255), (bx + 15, int(by - 60 + bob)), 3)
        arm_sway = math.sin(anim_frame * 1.5) * 20
        pygame.draw.line(surface, body_color, (bx - 40, by - 70 + bob), (bx - 90, by - 30 + bob + arm_sway), 15)
        pygame.draw.line(surface, body_color, (bx + 40, by - 70 + bob), (bx + 90, by - 30 + bob - arm_sway), 15)

    elif theme == 'cave':
        body_color = (25, 15, 35) if flash_timer == 0 else color
        core_color = (150, 80, 200) if flash_timer == 0 else color
        pygame.draw.circle(surface, core_color, (bx, int(by - 70 + bob)), 30)
        poly_points = [(bx, by - 160 + bob), (bx - 80, by - 80 + bob), (bx, by + 20 + bob), (bx + 80, by - 80 + bob)]
        pygame.draw.polygon(surface, body_color, poly_points)
        pygame.draw.polygon(surface, color, poly_points, 6)
        c_bob = math.cos(anim_frame * 2) * 20
        pygame.draw.polygon(surface, color, [(bx - 100, by - 100 + c_bob), (bx - 130, by - 50 + c_bob), (bx - 70, by - 40 + c_bob)])
        pygame.draw.polygon(surface, color, [(bx + 100, by - 100 - c_bob), (bx + 130, by - 50 - c_bob), (bx + 70, by - 40 - c_bob)])

    elif theme == 'volcano':
        body_color = (20, 5, 5) if flash_timer == 0 else color
        pygame.draw.rect(surface, body_color, (bx - 65, by - 150 + bob, 130, 150), border_radius=20)
        pygame.draw.rect(surface, color, (bx - 65, by - 150 + bob, 130, 150), 5, border_radius=20)
        if flash_timer == 0:
            vein_y = by - 150 + bob + ((anim_frame * 30) % 150)
            if by - 150 + bob < vein_y < by + bob:
                pygame.draw.line(surface, color, (bx - 40, vein_y), (bx + 40, vein_y + 20), 4)
        pygame.draw.polygon(surface, color, [(bx - 40, by - 150 + bob), (bx - 90, by - 230 + bob), (bx - 10, by - 150 + bob)])
        pygame.draw.polygon(surface, color, [(bx + 40, by - 150 + bob), (bx + 90, by - 230 + bob), (bx + 10, by - 150 + bob)])
        pygame.draw.circle(surface, (255, 255, 255), (bx - 25, int(by - 100 + bob)), 10)
        pygame.draw.circle(surface, (255, 255, 255), (bx + 25, int(by - 100 + bob)), 10)
        pygame.draw.line(surface, color, (bx - 65, by - 80 + bob), (bx - 110, by - 30 + bob), 12)
        pygame.draw.line(surface, color, (bx + 65, by - 80 + bob), (bx + 110, by - 30 + bob), 12)

    elif theme == 'electric':
        body_color = (15, 20, 40) if flash_timer == 0 else color
        cloud_color = (25, 30, 50) if flash_timer == 0 else color
        pygame.draw.circle(surface, body_color, (bx, int(by - 80 + bob)), 70)
        pygame.draw.circle(surface, cloud_color, (bx - 40, int(by - 60 + bob)), 50)
        pygame.draw.circle(surface, cloud_color, (bx + 40, int(by - 60 + bob)), 50)
        pygame.draw.circle(surface, color, (bx, int(by - 80 + bob)), 25)
        pygame.draw.circle(surface, (255, 255, 255), (bx, int(by - 80 + bob)), 10)
        for i in range(5):
            ang = anim_frame * 2 + (i * math.pi * 2 / 5)
            nx = bx + math.cos(ang) * 110
            ny = by - 80 + bob + math.sin(ang) * 110
            mx = bx + math.cos(ang) * 55 + random.randint(-15, 15)
            my = by - 80 + bob + math.sin(ang) * 55 + random.randint(-15, 15)
            pygame.draw.line(surface, color, (bx, by - 80 + bob), (mx, my), 3)
            pygame.draw.line(surface, color, (mx, my), (nx, ny), 3)
            pygame.draw.circle(surface, color, (int(nx), int(ny)), 12)
            pygame.draw.circle(surface, (255, 255, 255), (int(nx), int(ny)), 5)

def draw_enemy_model(surface, bx, by, theme_idx, type, direction, anim_frame, flash_timer, atk_timer=120, state='normal'):
    color = hex_to_rgb("#ffffff") if flash_timer > 0 else hex_to_rgb(THEMES[theme_idx]['hazard'])
    bob = int(math.sin(anim_frame) * 5)
    flip = (direction == -1)

    s_w, s_h = 130, 130
    s = pygame.Surface((s_w, s_h), pygame.SRCALPHA)
    cx, cy = s_w // 2, s_h - 10 

    if type == 'bat':
        if theme_idx == 'forest':
            body_c = color if flash_timer > 0 else hex_to_rgb("#4a3b2c") 
            wing_c = color if flash_timer > 0 else hex_to_rgb("#2d5a27") 
            eye_c = (0, 255, 0)
        elif theme_idx == 'cave':
            body_c = color if flash_timer > 0 else hex_to_rgb("#2d2d34") 
            wing_c = color if flash_timer > 0 else hex_to_rgb("#1a1a1f")
            eye_c = (255, 0, 0)
        elif theme_idx == 'volcano':
            body_c = color if flash_timer > 0 else hex_to_rgb("#221111") 
            wing_c = color if flash_timer > 0 else hex_to_rgb("#8b2a2a") 
            eye_c = (255, 150, 0)
        else: 
            body_c = color if flash_timer > 0 else hex_to_rgb("#1a2a4a") 
            wing_c = color if flash_timer > 0 else hex_to_rgb("#00d2ff") 
            eye_c = (255, 255, 255)
            
        wing_y = math.sin(anim_frame * 3) * 20
        pygame.draw.polygon(s, wing_c, [(cx, cy-30), (cx-30, cy-40+wing_y), (cx-40, cy-20+wing_y), (cx-15, cy-20)]) 
        pygame.draw.polygon(s, wing_c, [(cx, cy-30), (cx+30, cy-40+wing_y), (cx+40, cy-20+wing_y), (cx+15, cy-20)]) 
        
        pygame.draw.ellipse(s, body_c, (cx-10, cy-40, 20, 24))
        pygame.draw.polygon(s, body_c, [(cx-6, cy-35), (cx-12, cy-48), (cx-2, cy-38)]) 
        pygame.draw.polygon(s, body_c, [(cx+6, cy-35), (cx+12, cy-48), (cx+2, cy-38)]) 
        
        pygame.draw.circle(s, eye_c, (cx+4, cy-32), 2.5) 
        pygame.draw.polygon(s, (255,255,255), [(cx+4, cy-28), (cx+6, cy-24), (cx+8, cy-28)]) 
        
    elif type == 'archer':
        if theme_idx == 'forest':
            skin_c = color if flash_timer > 0 else hex_to_rgb("#ffe0bd") 
            tunic_c = color if flash_timer > 0 else hex_to_rgb("#2d5a27") 
            trim_c = hex_to_rgb("#d4a74c") 
            bow_c = hex_to_rgb("#8b5a2b") 
        elif theme_idx == 'cave':
            skin_c = color if flash_timer > 0 else hex_to_rgb("#9999aa") 
            tunic_c = color if flash_timer > 0 else hex_to_rgb("#3a1a5a") 
            trim_c = hex_to_rgb("#a0a0a0") 
            bow_c = hex_to_rgb("#555566") 
        elif theme_idx == 'volcano':
            skin_c = color if flash_timer > 0 else hex_to_rgb("#3a1515") 
            tunic_c = color if flash_timer > 0 else hex_to_rgb("#111111") 
            trim_c = hex_to_rgb("#ff4b2b") 
            bow_c = hex_to_rgb("#220000") 
        else: 
            skin_c = color if flash_timer > 0 else hex_to_rgb("#e0ffff") 
            tunic_c = color if flash_timer > 0 else hex_to_rgb("#0a1a3a") 
            trim_c = hex_to_rgb("#00d2ff") 
            bow_c = hex_to_rgb("#ffffff") 
            
        pygame.draw.polygon(s, tunic_c, [(cx-5, cy-35), (cx-20, cy-5), (cx-5, cy-15)])
        pygame.draw.rect(s, hex_to_rgb("#3b2b1a"), (cx-6, cy-15, 6, 15), border_radius=2)
        pygame.draw.rect(s, hex_to_rgb("#3b2b1a"), (cx+4, cy-15, 6, 15), border_radius=2)
        
        pygame.draw.polygon(s, tunic_c, [(cx-10, cy-15), (cx-10, cy-38), (cx+8, cy-38), (cx+12, cy-15)])
        pygame.draw.polygon(s, trim_c, [(cx-10, cy-15), (cx-10, cy-38), (cx+8, cy-38), (cx+12, cy-15)], 2)
        
        pygame.draw.ellipse(s, skin_c, (cx-8, cy-52, 18, 20)) 
        pygame.draw.polygon(s, tunic_c, [(cx-10, cy-35), (cx-15, cy-55), (cx+10, cy-55)]) 
        pygame.draw.polygon(s, skin_c, [(cx-4, cy-46), (cx-18, cy-52), (cx-4, cy-42)]) 
        
        pygame.draw.rect(s, (0, 0, 0), (cx+4, cy-48, 4, 3))
        pygame.draw.rect(s, trim_c, (cx+5, cy-47, 2, 1)) 
        
        arm_y = cy-35
        bow_x = cx+15
        pygame.draw.arc(s, bow_c, (bow_x-10, arm_y-20, 20, 40), -math.pi/2, math.pi/2, 3) 
        if atk_timer > 60:
            pygame.draw.line(s, (200,200,200), (bow_x, arm_y-20), (cx, arm_y), 1)
            pygame.draw.line(s, (200,200,200), (bow_x, arm_y+20), (cx, arm_y), 1)
            pygame.draw.line(s, trim_c, (cx-5, arm_y), (bow_x+15, arm_y), 2) 
            pygame.draw.polygon(s, (150,150,150), [(bow_x+15, arm_y), (bow_x+10, arm_y-3), (bow_x+10, arm_y+3)]) 
        else:
            pygame.draw.line(s, (200,200,200), (bow_x, arm_y-20), (bow_x, arm_y+20), 1)

    elif type == 'wizard':
        if theme_idx == 'forest':
            skin_c = color if flash_timer > 0 else hex_to_rgb("#4a3a2a") 
            cloak_c = hex_to_rgb("#2d5a27")
            trim_c = hex_to_rgb("#d4a74c")
        elif theme_idx == 'cave':
            skin_c = color if flash_timer > 0 else hex_to_rgb("#3a1a5a") 
            cloak_c = hex_to_rgb("#222222")
            trim_c = hex_to_rgb("#9d50bb")
        elif theme_idx == 'volcano':
            skin_c = color if flash_timer > 0 else hex_to_rgb("#ff4b2b") 
            cloak_c = hex_to_rgb("#111111")
            trim_c = hex_to_rgb("#ffaa00")
        else: 
            skin_c = color if flash_timer > 0 else hex_to_rgb("#00d2ff") 
            cloak_c = hex_to_rgb("#050a1a")
            trim_c = hex_to_rgb("#ffffff")
            
        float_bob = math.sin(anim_frame * 2) * 10
        
        if state == 'telegraph':
            pulse = math.sin(anim_frame * 15) * 8
            pygame.draw.circle(s, trim_c, (cx+25, cy-40+float_bob), 15 + pulse, 2)
            pygame.draw.circle(s, (255,255,255), (cx+25, cy-40+float_bob), 5 + pulse/2)

        pygame.draw.polygon(s, cloak_c, [(cx-15, cy-10+float_bob), (cx-5, cy-50+float_bob), (cx+5, cy-50+float_bob), (cx+15, cy-10+float_bob)])
        pygame.draw.polygon(s, trim_c, [(cx-15, cy-10+float_bob), (cx-5, cy-50+float_bob), (cx+5, cy-50+float_bob), (cx+15, cy-10+float_bob)], 2)
        
        pygame.draw.circle(s, skin_c, (cx, cy-60+float_bob), 12)
        pygame.draw.rect(s, (0,0,0), (cx+4, cy-64+float_bob, 4, 4))
        pygame.draw.rect(s, trim_c, (cx+5, cy-63+float_bob, 2, 2))
        
        pygame.draw.polygon(s, cloak_c, [(cx-12, cy-55+float_bob), (cx, cy-80+float_bob), (cx+12, cy-55+float_bob)])
        
        pygame.draw.circle(s, skin_c, (cx+25, cy-40+float_bob), 6)
        if atk_timer > 30 and state != 'telegraph':
            pygame.draw.circle(s, trim_c, (cx+30, cy-40+float_bob), 4)
            pygame.draw.line(s, trim_c, (cx+30, cy-40+float_bob), (cx+45, cy-40+float_bob), 2)

    elif type == 'charger':
        if theme_idx == 'forest':
            skin_c = color if flash_timer > 0 else hex_to_rgb("#4a3a2a")
            eye_c = (255, 0, 0)
        elif theme_idx == 'cave':
            skin_c = color if flash_timer > 0 else hex_to_rgb("#3a5a3a")
            eye_c = (255, 255, 0)
        elif theme_idx == 'volcano':
            skin_c = color if flash_timer > 0 else hex_to_rgb("#221111")
            eye_c = (255, 100, 0)
        else: 
            skin_c = color if flash_timer > 0 else hex_to_rgb("#102040")
            eye_c = (0, 255, 255)
            
        run_bob = abs(math.cos(anim_frame*3))*5 if state == 'charging' else 0
        
        if state == 'telegraph':
            pygame.draw.ellipse(s, (255,0,0), (cx-40, cy-60, 80, 50), 4)
            run_bob = math.sin(anim_frame * 30) * 3 
        
        pygame.draw.rect(s, hex_to_rgb("#111"), (cx-20, cy-15-run_bob, 8, 15), border_radius=2)
        pygame.draw.rect(s, hex_to_rgb("#111"), (cx+10, cy-15-run_bob, 8, 15), border_radius=2)
        
        pygame.draw.rect(s, skin_c, (cx-30, cy-40-run_bob, 50, 30), border_radius=8)
        
        pygame.draw.ellipse(s, skin_c, (cx+10, cy-45-run_bob, 25, 25))
        pygame.draw.circle(s, eye_c, (cx+22, cy-38-run_bob), 4 if state in ['telegraph', 'charging'] else 3)
        
        pygame.draw.polygon(s, (200,200,200), [(cx+28, cy-30-run_bob), (cx+45, cy-40-run_bob), (cx+32, cy-25-run_bob)]) 
        pygame.draw.polygon(s, (200,200,200), [(cx+20, cy-42-run_bob), (cx+25, cy-55-run_bob), (cx+15, cy-45-run_bob)]) 

    elif type == 'tank':
        if theme_idx == 'forest':
            skin_c = color if flash_timer > 0 else hex_to_rgb("#4a3a2a") 
            armor_c = hex_to_rgb("#2d5a27") 
            wpn_c1, wpn_c2 = hex_to_rgb("#3a2a1a"), hex_to_rgb("#5c4033") 
            eye_c = (0, 255, 0)
        elif theme_idx == 'cave':
            skin_c = color if flash_timer > 0 else hex_to_rgb("#3a5a3a") 
            armor_c = hex_to_rgb("#222222") 
            wpn_c1, wpn_c2 = hex_to_rgb("#4a3018"), hex_to_rgb("#555") 
            eye_c = (255, 0, 0)
        elif theme_idx == 'volcano':
            skin_c = color if flash_timer > 0 else hex_to_rgb("#111111") 
            armor_c = hex_to_rgb("#8b2a2a") 
            wpn_c1, wpn_c2 = hex_to_rgb("#221111"), hex_to_rgb("#ff4b2b") 
            eye_c = (255, 200, 0)
        else: 
            skin_c = color if flash_timer > 0 else hex_to_rgb("#102040") 
            armor_c = hex_to_rgb("#a0b0c0") 
            wpn_c1, wpn_c2 = hex_to_rgb("#333344"), hex_to_rgb("#00d2ff") 
            eye_c = (0, 255, 255)
            
        pygame.draw.rect(s, hex_to_rgb("#111"), (cx-15, cy-15, 12, 15), border_radius=3)
        pygame.draw.rect(s, hex_to_rgb("#111"), (cx+5, cy-15, 12, 15), border_radius=3)
        
        pygame.draw.rect(s, skin_c, (cx-20, cy-55, 45, 45), border_radius=10)
        pygame.draw.rect(s, armor_c, (cx-22, cy-55, 50, 15), border_radius=5) 
        
        pygame.draw.rect(s, skin_c, (cx+15, cy-65, 20, 22), border_radius=4)
        pygame.draw.rect(s, (255,255,255), (cx+25, cy-48, 4, -8)) 
        pygame.draw.circle(s, eye_c, (cx+28, cy-58), 2) 
        pygame.draw.line(s, (0,0,0), (cx+22, cy-62), (cx+32, cy-58), 2) 
        
        wpn_y = cy-30 if atk_timer < 20 else cy-50
        pygame.draw.rect(s, wpn_c1, (cx+5, wpn_y-10, 45, 8)) 
        pygame.draw.rect(s, wpn_c2, (cx+35, wpn_y-20, 25, 28), border_radius=4) 
        pygame.draw.polygon(s, (200,200,200), [(cx+60, wpn_y-15), (cx+70, wpn_y-6), (cx+60, wpn_y+5)]) 

    elif type == 'jumper':
        if theme_idx == 'forest':
            skin_c = color if flash_timer > 0 else hex_to_rgb("#6b8c42") 
            rag_c = hex_to_rgb("#4a2f1b") 
            eye_c = (255, 255, 0)
        elif theme_idx == 'cave':
            skin_c = color if flash_timer > 0 else hex_to_rgb("#887799") 
            rag_c = hex_to_rgb("#222222")
            eye_c = (255, 50, 255) 
        elif theme_idx == 'volcano':
            skin_c = color if flash_timer > 0 else hex_to_rgb("#cc4422") 
            rag_c = hex_to_rgb("#1a0505")
            eye_c = (255, 255, 255)
        else: 
            skin_c = color if flash_timer > 0 else hex_to_rgb("#44ccff") 
            rag_c = hex_to_rgb("#112244")
            eye_c = (255, 255, 255)
            
        leg_bend = cy if bob < 2 else cy - 10
        pygame.draw.line(s, skin_c, (cx-10, cy-15-bob), (cx-20, cy-5-bob), 4)
        pygame.draw.line(s, skin_c, (cx-20, cy-5-bob), (cx-10, leg_bend), 4)
        pygame.draw.line(s, skin_c, (cx+10, cy-15-bob), (cx+20, cy-5-bob), 4)
        pygame.draw.line(s, skin_c, (cx+20, cy-5-bob), (cx+15, leg_bend), 4)
        
        pygame.draw.ellipse(s, skin_c, (cx-18, cy-35-bob, 36, 25))
        pygame.draw.ellipse(s, rag_c, (cx-12, cy-35-bob, 24, 25)) 
        
        pygame.draw.ellipse(s, skin_c, (cx-5, cy-45-bob, 25, 20))
        pygame.draw.polygon(s, skin_c, [(cx+15, cy-38-bob), (cx+30, cy-35-bob), (cx+15, cy-32-bob)]) 
        
        pygame.draw.polygon(s, skin_c, [(cx, cy-40-bob), (cx-15, cy-45-bob), (cx-5, cy-35-bob)])
        
        pygame.draw.circle(s, eye_c, (cx+12, cy-38-bob), 5)
        pygame.draw.circle(s, (0, 0, 0), (cx+14, cy-38-bob), 2)

    else:
        if theme_idx == 'forest':
            squish = int(math.sin(anim_frame) * 4)
            pygame.draw.rect(s, hex_to_rgb("#e8d5c4"), (cx-10, cy-20+squish, 20, 20-squish), border_radius=4) 
            pygame.draw.ellipse(s, color, (cx-25-squish, cy-35+squish, 50+squish*2, 25-squish)) 
            pygame.draw.circle(s, (255,255,255), (cx-10-squish, cy-28+squish), 5) 
            pygame.draw.circle(s, (255,255,255), (cx+12+squish, cy-25+squish), 4) 
            pygame.draw.circle(s, (0,0,0), (cx+2, cy-10+squish), 2.5) 
            pygame.draw.circle(s, (0,0,0), (cx+12, cy-10+squish), 2.5) 
            
        elif theme_idx == 'cave':
            wave = math.sin(anim_frame * 3) * 5
            pygame.draw.line(s, color, (cx-15, cy-10), (cx-25, cy+wave), 3) 
            pygame.draw.line(s, color, (cx, cy-10), (cx, cy-wave), 3) 
            pygame.draw.line(s, color, (cx+15, cy-10), (cx+25, cy+wave), 3) 
            pygame.draw.circle(s, hex_to_rgb("#2a2a35"), (cx, cy-20), 18) 
            crystal_col = (min(255, color[0]+50), min(255, color[1]+50), min(255, color[2]+50))
            pygame.draw.polygon(s, crystal_col, [(cx-15, cy-20), (cx-5, cy-45), (cx, cy-25)]) 
            pygame.draw.polygon(s, crystal_col, [(cx, cy-25), (cx+15, cy-40), (cx+12, cy-15)]) 
            pygame.draw.circle(s, color, (cx+8, cy-20), 4) 

        elif theme_idx == 'volcano':
            fire_y = cy - 10 + math.sin(anim_frame*5)*5
            pygame.draw.polygon(s, hex_to_rgb("#ff4b2b"), [(cx-15, cy-20), (cx, fire_y), (cx+15, cy-20)]) 
            pygame.draw.polygon(s, hex_to_rgb("#ffcc00"), [(cx-8, cy-20), (cx, fire_y-5), (cx+8, cy-20)]) 
            pygame.draw.rect(s, hex_to_rgb("#3a1f1f"), (cx-18, cy-45, 36, 30), border_radius=6) 
            pygame.draw.rect(s, hex_to_rgb("#221111"), (cx-10, cy-20, 20, 10), border_radius=2) 
            pygame.draw.circle(s, hex_to_rgb("#ffaa00"), (cx+8, cy-35), 6) 
            pygame.draw.circle(s, hex_to_rgb("#ffffff"), (cx+9, cy-35), 2) 

        elif theme_idx == 'electric':
            pygame.draw.circle(s, hex_to_rgb("#112233"), (cx, cy-25+bob), 18) 
            pygame.draw.circle(s, color, (cx, cy-25+bob), 12)
            pygame.draw.circle(s, (255,255,255), (cx, cy-25+bob), 6)
            for i in range(3): 
                ang = anim_frame * 5 + i * (math.pi * 2 / 3)
                sx = cx + math.cos(ang) * 25
                sy = cy - 25 + bob + math.sin(ang) * 25
                pygame.draw.circle(s, (255,255,255), (int(sx), int(sy)), 3)
                pygame.draw.line(s, color, (cx, cy-25+bob), (sx, sy), 2)

    if flip:
        s = pygame.transform.flip(s, True, False)
        
    surface.blit(s, (bx - cx, by - cy))

# --- DECORACOES (Arvores, Pedras, Arbustos) ---
class Decoration:
    def __init__(self, x, y, theme, dec_type):
        self.x = x
        self.y = y
        self.theme = theme
        self.type = dec_type
        self.scale = random.uniform(0.6, 1.2)
        self.flip = random.choice([True, False])
        
    def draw(self, surface, cam_x, cam_y):
        bx = int(self.x - cam_x)
        by = int(self.y - cam_y)
        
        # Otimizacao: Nao desenha se nao estiver na tela
        if bx < -200 or bx > surface.get_width() + 200: return
        
        s_w, s_h = int(140 * self.scale), int(180 * self.scale)
        s = pygame.Surface((s_w, s_h), pygame.SRCALPHA)
        cx, cy = s_w // 2, s_h
        
        if self.theme == 'forest':
            if self.type == 'tree':
                pygame.draw.rect(s, hex_to_rgb("#3e2723"), (cx-10, cy-80, 20, 80))
                pygame.draw.circle(s, hex_to_rgb("#1b5e20"), (cx, cy-90), 35)
                pygame.draw.circle(s, hex_to_rgb("#2e7d32"), (cx-20, cy-65), 30)
                pygame.draw.circle(s, hex_to_rgb("#2e7d32"), (cx+20, cy-65), 30)
                pygame.draw.circle(s, hex_to_rgb("#388e3c"), (cx, cy-75), 25)
            elif self.type == 'bush':
                pygame.draw.circle(s, hex_to_rgb("#1b5e20"), (cx-15, cy-15), 15)
                pygame.draw.circle(s, hex_to_rgb("#2e7d32"), (cx+15, cy-15), 15)
                pygame.draw.circle(s, hex_to_rgb("#388e3c"), (cx, cy-25), 20)
            elif self.type == 'flower':
                pygame.draw.line(s, hex_to_rgb("#4caf50"), (cx, cy), (cx, cy-20), 3)
                pygame.draw.circle(s, hex_to_rgb("#ffeb3b"), (cx, cy-20), 5)
                pygame.draw.circle(s, hex_to_rgb("#e91e63"), (cx-5, cy-25), 4)
                pygame.draw.circle(s, hex_to_rgb("#e91e63"), (cx+5, cy-25), 4)
                pygame.draw.circle(s, hex_to_rgb("#e91e63"), (cx, cy-30), 4)
                
        elif self.theme == 'cave':
            if self.type == 'crystal':
                c1 = hex_to_rgb("#9d50bb")
                c2 = hex_to_rgb("#6e3a8c")
                pygame.draw.polygon(s, c1, [(cx-10, cy), (cx, cy-50), (cx+10, cy)])
                pygame.draw.polygon(s, c2, [(cx, cy), (cx+10, cy-40), (cx+20, cy)])
                pygame.draw.polygon(s, c2, [(cx-20, cy), (cx-10, cy-30), (cx, cy)])
            elif self.type == 'mushroom':
                pygame.draw.rect(s, hex_to_rgb("#d7ccc8"), (cx-4, cy-20, 8, 20))
                pygame.draw.ellipse(s, hex_to_rgb("#7e57c2"), (cx-20, cy-30, 40, 15))
                pygame.draw.circle(s, hex_to_rgb("#b39ddb"), (cx-10, cy-25), 3)
                pygame.draw.circle(s, hex_to_rgb("#b39ddb"), (cx+10, cy-25), 2)
            elif self.type == 'rock':
                pygame.draw.polygon(s, hex_to_rgb("#424242"), [(cx-20, cy), (cx-10, cy-15), (cx+10, cy-20), (cx+25, cy-5), (cx+15, cy)])
                
        elif self.theme == 'volcano':
            if self.type == 'dead_tree':
                pygame.draw.rect(s, hex_to_rgb("#212121"), (cx-6, cy-70, 12, 70))
                pygame.draw.line(s, hex_to_rgb("#212121"), (cx, cy-40), (cx-20, cy-60), 4)
                pygame.draw.line(s, hex_to_rgb("#212121"), (cx, cy-50), (cx+25, cy-75), 4)
                pygame.draw.line(s, hex_to_rgb("#212121"), (cx-20, cy-60), (cx-30, cy-70), 2)
            elif self.type == 'rock':
                pygame.draw.polygon(s, hex_to_rgb("#1a1a1a"), [(cx-30, cy), (cx-15, cy-30), (cx+10, cy-25), (cx+30, cy)])
                pygame.draw.polygon(s, hex_to_rgb("#331a1a"), [(cx-15, cy), (cx-5, cy-20), (cx+15, cy)])
            elif self.type == 'ash':
                pygame.draw.ellipse(s, hex_to_rgb("#3e2723"), (cx-25, cy-10, 50, 10))
                
        elif self.theme == 'electric':
            if self.type == 'spire':
                pygame.draw.polygon(s, hex_to_rgb("#006080"), [(cx-15, cy), (cx, cy-80), (cx+15, cy)])
                pygame.draw.polygon(s, hex_to_rgb("#00d2ff"), [(cx-5, cy), (cx, cy-70), (cx+5, cy)])
            elif self.type == 'plant':
                pygame.draw.line(s, hex_to_rgb("#00acc1"), (cx, cy), (cx-10, cy-30), 2)
                pygame.draw.line(s, hex_to_rgb("#00acc1"), (cx, cy), (cx+10, cy-25), 2)
                pygame.draw.circle(s, hex_to_rgb("#e0f7fa"), (cx-10, cy-30), 4)
                pygame.draw.circle(s, hex_to_rgb("#e0f7fa"), (cx+10, cy-25), 4)

        if self.flip:
            s = pygame.transform.flip(s, True, False)
            
        surface.blit(s, (bx - cx, by - cy))

# --- EFEITOS E OBJETOS ---
class Particle:
    def __init__(self, x, y, color_hex, size=4, speed=1.0):
        self.x, self.y = x, y
        self.vx = (random.random() - 0.5) * 8 * speed
        self.vy = (random.random() - 0.5) * 8 * speed
        self.color = hex_to_rgb(color_hex)
        self.size = size
        self.life = 1.0
        self.decay = 0.03 + random.random() * 0.03

    def update(self):
        self.x += self.vx; self.y += self.vy; self.life -= self.decay

    def draw(self, surface, cam_x, cam_y):
        if self.life > 0:
            current_size = max(1, int(self.size * self.life))
            rect = (int(self.x - cam_x), int(self.y - cam_y), current_size, current_size)
            pygame.draw.rect(surface, self.color, rect)

class Platform:
    def __init__(self, x, y, w, h, is_trap=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.is_trap = is_trap
        self.trap_state = 'idle'
        self.trap_timer = 0
        self.vy = 0
        self.orig_x = x
        self.orig_y = y

    @property
    def x(self): return self.rect.x
    @property
    def y(self): return self.rect.y
    @property
    def w(self): return self.rect.w
    @property
    def h(self): return self.rect.h
    @property
    def left(self): return self.rect.left
    @property
    def right(self): return self.rect.right
    @property
    def top(self): return self.rect.top
    @property
    def bottom(self): return self.rect.bottom

    def trigger(self):
        if self.is_trap and self.trap_state == 'idle':
            self.trap_state = 'shaking'
            self.trap_timer = 30 # Meio segundo de aviso (treme antes de cair)

    def update(self):
        if self.is_trap:
            if self.trap_state == 'shaking':
                self.trap_timer -= 1
                self.rect.x = self.orig_x + random.randint(-4, 4)
                self.rect.y = self.orig_y + random.randint(-2, 2)
                if self.trap_timer <= 0:
                    self.trap_state = 'falling'
                    play_sfx('attack') # Som de queda
            elif self.trap_state == 'falling':
                self.vy += GRAVITY * 0.8
                self.rect.y += self.vy

class BiomeTrap:
    def __init__(self, game, x, y, theme, w=40, h=40):
        self.game = game; self.x = x; self.y = y; self.w = w; self.h = h
        self.theme = theme
        self.type = 'none'
        self.state = 'idle'
        self.timer = random.randint(0, 60)
        self.vy = 0
        self.dead = False
        self.damage = int((15 + game.level * 2) * game.get_difficulty_mult())
        
        if theme == 'forest': self.type = 'spikes'
        elif theme == 'cave': self.type = 'stalactite'
        elif theme == 'volcano': self.type = 'geyser'
        elif theme == 'electric': self.type = 'zap'
        
    def update(self, player):
        if self.type == 'spikes':
            if self.state == 'idle':
                # Distância de ativação
                if abs((self.x + self.w/2) - player.x) < 80 and abs(self.y - player.y) < 100:
                    self.state = 'warning'
                    self.timer = 30
                    play_sfx('select')
            elif self.state == 'warning':
                self.timer -= 1
                if self.timer <= 0:
                    self.state = 'active'
                    self.timer = 60
                    play_sfx('attack')
            elif self.state == 'active':
                self.timer -= 1
                hitbox = pygame.Rect(self.x, self.y - 30, self.w, 30)
                if player.get_rect().colliderect(hitbox):
                    player.take_damage(self.damage)
                if self.timer <= 0:
                    self.state = 'cooldown'
                    self.timer = 120
            elif self.state == 'cooldown':
                self.timer -= 1
                if self.timer <= 0: self.state = 'idle'
                
        elif self.type == 'stalactite':
            if self.state == 'idle':
                if abs((self.x + self.w/2) - player.x) < 100 and player.y > self.y:
                    self.state = 'warning'
                    self.timer = 20
                    self.game.spawn_particle(self.x + self.w/2, self.y, "#888888", 5)
            elif self.state == 'warning':
                self.timer -= 1
                self.x += random.randint(-2, 2)
                if self.timer <= 0:
                    self.state = 'falling'
            elif self.state == 'falling':
                self.vy += GRAVITY
                self.y += self.vy
                hitbox = pygame.Rect(self.x, self.y, self.w, self.h)
                if player.get_rect().colliderect(hitbox):
                    player.take_damage(self.damage)
                    self.dead = True
                    self.game.spawn_particle(self.x + self.w/2, self.y + self.h, "#888888", 15)
                for p in self.game.platforms:
                    if hitbox.colliderect(p.rect):
                        self.dead = True
                        self.game.spawn_particle(self.x + self.w/2, self.y + self.h, "#888888", 15)
                        break
                if self.y > FLOOR_Y + 500: self.dead = True
                        
        elif self.type == 'geyser':
            self.timer -= 1
            if self.state == 'idle' and self.timer <= 0:
                self.state = 'warning'
                self.timer = 60
            elif self.state == 'warning':
                if self.timer % 5 == 0:
                    self.game.spawn_particle(self.x + self.w/2, self.y, "#ff4b2b", 2)
                if self.timer <= 0:
                    self.state = 'active'
                    self.timer = 60
                    play_sfx('attack')
            elif self.state == 'active':
                self.game.spawn_particle(self.x + self.w/2, self.y - random.randint(0, self.h), "#ff4b2b", 1)
                hitbox = pygame.Rect(self.x, self.y - self.h, self.w, self.h)
                if player.get_rect().colliderect(hitbox):
                    player.take_damage(self.damage)
                if self.timer <= 0:
                    self.state = 'idle'
                    self.timer = random.randint(120, 240)
                    
        elif self.type == 'zap':
            self.timer -= 1
            if self.state == 'idle' and self.timer <= 0:
                self.state = 'warning'
                self.timer = 40
            elif self.state == 'warning':
                if self.timer % 10 == 0:
                    self.game.spawn_particle(self.x + random.randint(0, self.w), self.y, "#00d2ff", 1)
                if self.timer <= 0:
                    self.state = 'active'
                    self.timer = 45
                    play_sfx('attack')
            elif self.state == 'active':
                hitbox = pygame.Rect(self.x, self.y - 20, self.w, 40)
                if player.get_rect().colliderect(hitbox):
                    player.take_damage(self.damage, is_electric=True)
                if self.timer <= 0:
                    self.state = 'idle'
                    self.timer = random.randint(100, 200)

    def draw(self, surface, cam_x, cam_y):
        bx, by = int(self.x - cam_x), int(self.y - cam_y)
        
        if self.type == 'spikes':
            color = hex_to_rgb("#a0a0a0")
            if self.state == 'warning':
                pygame.draw.polygon(surface, color, [(bx, by), (bx+self.w/2, by-10), (bx+self.w, by)])
            elif self.state == 'active':
                pygame.draw.polygon(surface, color, [(bx, by), (bx+10, by-30), (bx+20, by)])
                pygame.draw.polygon(surface, color, [(bx+20, by), (bx+30, by-40), (bx+40, by)])
                
        elif self.type == 'stalactite':
            color = hex_to_rgb("#555566")
            pygame.draw.polygon(surface, color, [(bx, by), (bx+self.w, by), (bx+self.w/2, by+self.h)])
            pygame.draw.polygon(surface, hex_to_rgb("#333344"), [(bx+self.w/2, by), (bx+self.w, by), (bx+self.w/2, by+self.h)])
            
        elif self.type == 'geyser':
            if self.state == 'warning':
                pygame.draw.ellipse(surface, hex_to_rgb("#ff4b2b"), (bx, by-10, self.w, 20))
            elif self.state == 'active':
                pygame.draw.rect(surface, hex_to_rgb("#ff4b2b"), (bx, by-self.h, self.w, self.h), border_radius=10)
                pygame.draw.rect(surface, hex_to_rgb("#ffcc00"), (bx+10, by-self.h+10, self.w-20, self.h-20), border_radius=10)
                
        elif self.type == 'zap':
            if self.state == 'warning':
                s = pygame.Surface((self.w, 20), pygame.SRCALPHA)
                s.fill((0, 210, 255, 50))
                surface.blit(s, (bx, by-10))
            elif self.state == 'active':
                s = pygame.Surface((self.w, 30), pygame.SRCALPHA)
                s.fill((0, 210, 255, 100))
                surface.blit(s, (bx, by-15))
                for _ in range(3):
                    pts = []
                    for px in range(0, int(self.w), 20):
                        pts.append((bx + px, by - 15 + random.randint(0, 30)))
                    if len(pts) > 1:
                        pygame.draw.lines(surface, (255, 255, 255), False, pts, 2)

class SlashEffect:
    def __init__(self, x, y, angle, size=100, color=(220, 20, 20)):
        self.x = x
        self.y = y
        self.angle = angle
        self.size = size
        self.color = color
        self.life = 15
        self.max_life = 15

    def update(self):
        self.life -= 1

    def draw(self, surface, cam_x, cam_y):
        if self.life <= 0: return
        
        prog = 1.0 - (self.life / self.max_life)
        cx = int(self.x - cam_x)
        cy = int(self.y - cam_y)
        
        length = int(self.size * (0.8 + prog * 0.4))
        thickness = max(1, int(6 * (1.0 - prog)))
        
        points = []
        for i in range(15):
            t = i / 14.0
            a = self.angle - 0.6 + 1.2 * t
            r = length - abs(t - 0.5) * 30 * (1.0 - prog)
            points.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
            
        points_inner = []
        for i in range(14, -1, -1):
            t = i / 14.0
            a = self.angle - 0.6 + 1.2 * t
            r = length - thickness - abs(t - 0.5) * 30 * (1.0 - prog)
            points_inner.append((cx + math.cos(a) * r, cy + math.sin(a) * r))

        if len(points) > 2:
            pygame.draw.polygon(surface, self.color, points + points_inner)
            pygame.draw.lines(surface, (255, 255, 255), False, points, 1)

class ExplosionSphere:
    def __init__(self, x, y, max_radius=100, color="#9d50bb", life=20):
        self.x = x
        self.y = y
        self.max_radius = max_radius
        self.color = color if isinstance(color, tuple) else hex_to_rgb(color)
        self.life = life
        self.max_life = life

    def update(self):
        self.life -= 1

    def draw(self, surface, cam_x, cam_y):
        if self.life <= 0: return
        
        prog = 1.0 - (self.life / self.max_life)
        current_radius = int(self.max_radius * (1.0 - math.pow(1.0 - prog, 3)))
        if current_radius <= 0: current_radius = 1
        
        alpha = int(255 * (self.life / self.max_life))
        
        s = pygame.Surface((current_radius*2, current_radius*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (current_radius, current_radius), current_radius)
        pygame.draw.circle(s, (255, 255, 255, int(alpha * 0.8)), (current_radius, current_radius), int(current_radius * 0.6))
        
        cx = int(self.x - cam_x - current_radius)
        cy = int(self.y - cam_y - current_radius)
        surface.blit(s, (cx, cy))

class FloatingText:
    def __init__(self, x, y, text, color_hex, is_crit=False, is_level_up=False):
        self.x, self.y = x, y
        self.text = text; self.color = hex_to_rgb(color_hex)
        self.life, self.is_crit, self.is_level_up = 1.0, is_crit, is_level_up
        self.vy, self.vx = random.uniform(-6, -9), random.uniform(-1.5, 1.5)
        if self.is_level_up: self.font = FONTS['huge']; self.vy = -2; self.vx = 0; self.life = 2.0
        elif self.is_crit: self.font = FONTS['large']; self.color = hex_to_rgb("#ffcc00")
        else: self.font = FONTS['medium']
    def update(self):
        self.x += self.vx; self.y += self.vy
        if not self.is_level_up: self.vy += 0.6
        self.life -= 0.02 if not self.is_level_up else 0.01
    def draw(self, surface, cam_x, cam_y):
        if self.life > 0:
            shake_x = random.randint(-2, 2) if self.is_crit else 0
            shake_y = random.randint(-2, 2) if self.is_crit else 0
            txt_surf = self.font.render(self.text, True, self.color)
            out_surf = self.font.render(self.text, True, (0,0,0))
            alpha = max(0, int(min(1.0, self.life) * 255))
            txt_surf.set_alpha(alpha); out_surf.set_alpha(alpha)
            bx, by = int(self.x - cam_x) + shake_x, int(self.y - cam_y) + shake_y
            surface.blit(out_surf, (bx+2, by+2)); surface.blit(txt_surf, (bx, by))

class Portal:
    def __init__(self, x, y, theme, is_boss=False):
        self.x, self.y = x, y
        self.angle, self.particles, self.is_boss = 0, [], is_boss
        if is_boss: self.color = hex_to_rgb("#ffcc00"); self.text = "NOVO REINO"
        else: self.color = hex_to_rgb(THEMES[theme]['hazard']); self.text = "SAIDA"
        
    def update(self):
        self.angle += 3 if self.is_boss else 2
        if random.random() < (0.5 if self.is_boss else 0.3):
            self.particles.append(Particle(self.x + (random.random()-0.5)*50, self.y - 60 + (random.random()-0.5)*80, "#ffffff", 3, 0.5))
        for p in self.particles: p.update()
        self.particles = [p for p in self.particles if p.life > 0]
        
    def draw(self, surface, cam_x, cam_y):
        bx, by = int(self.x - cam_x), int(self.y - cam_y)
        width, height = (120, 180) if self.is_boss else (90, 130)
        
        p_w = 15
        p_col = hex_to_rgb("#1a1a24")
        
        for dx in [-width//2, width//2 - p_w]:
            pygame.draw.rect(surface, p_col, (bx + dx, by - height, p_w, height))
            pygame.draw.polygon(surface, p_col, [(bx + dx, by - height), (bx + dx + p_w//2, by - height - 20), (bx + dx + p_w, by - height)])
            pygame.draw.line(surface, self.color, (bx + dx + p_w//2, by - 10), (bx + dx + p_w//2, by - height - 10), 2)
            
        core_y = by - height//2
        pulse = math.sin(pygame.time.get_ticks() * 0.005) * 15
        
        for i in range(3):
            ang = math.radians(self.angle + i*120)
            rx = int(bx + math.cos(ang) * (30 + pulse*0.5))
            ry = int(core_y + math.sin(ang) * 10)
            pygame.draw.circle(surface, self.color, (rx, ry), 4)
            
        swirl = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.ellipse(swirl, (*self.color, 80), (10, 20, width-20, height-40))
        pygame.draw.ellipse(swirl, (*self.color, 160), (20-pulse//3, 30-pulse//3, width-40+pulse//1.5, height-60+pulse//1.5), 6)
        pygame.draw.ellipse(swirl, (255,255,255, 255), (30+pulse//4, 40+pulse//4, width-60-pulse//2, height-80-pulse//2), 2)
        
        s_rot = pygame.transform.rotate(swirl, math.sin(math.radians(self.angle*0.5))*10)
        surface.blit(s_rot, s_rot.get_rect(center=(bx, core_y)))
        
        txt = FONTS['tiny'].render(self.text, True, (255,255,255))
        out_txt = FONTS['tiny'].render(self.text, True, (0,0,0))
        for dx, dy in [(-1,-1),(-1,1),(1,-1),(1,1)]:
            surface.blit(out_txt, out_txt.get_rect(center=(bx + dx, by - height - 35 + dy)))
        surface.blit(txt, txt.get_rect(center=(bx, by - height - 35)))
        for p in self.particles: p.draw(surface, cam_x, cam_y)

class LootDrop:
    def __init__(self, x, y, item_id):
        self.x, self.y = x, y
        self.vx = random.uniform(-3, 3); self.vy = random.uniform(-10, -14)
        self.item_id = item_id; self.life = 1200; self.item_data = ITEM_DB[item_id]
    def update(self, platforms):
        self.life -= 1
        if self.vy < 15: self.vy += GRAVITY
        self.x += self.vx; self.y += self.vy
        rect = pygame.Rect(self.x - 10, self.y - 20, 20, 20)
        for p in platforms:
            if rect.colliderect(p.rect):
                if self.vy > 0: self.y = p.top; self.vy *= -0.5; self.vx *= 0.5; break
    def draw(self, surface, cam_x, cam_y):
        bx, by = int(self.x - cam_x), int(self.y - cam_y)
        if self.item_data['rarity'] in ['rare', 'epic', 'legendary']:
            beam_color = hex_to_rgb(self.item_data['color'])
            beam_surf = pygame.Surface((30, 300), pygame.SRCALPHA)
            alpha_pulse = 80 + int(math.sin(self.life*0.1)*40)
            for y_grad in range(300):
                a = int(alpha_pulse * (1.0 - (y_grad / 300.0)))
                pygame.draw.line(beam_surf, (*beam_color, a), (5, y_grad), (25, y_grad), 10)
                pygame.draw.line(beam_surf, (255,255,255, min(255, a+50)), (13, y_grad), (17, y_grad), 4)
            surface.blit(beam_surf, (bx - 15, by - 290), special_flags=pygame.BLEND_RGBA_ADD)

        bob = math.sin(self.life * 0.1) * 3 if self.vy == 0 else 0
        rect = pygame.Rect(bx - 10, by - 20 + bob, 20, 20)
        pygame.draw.rect(surface, hex_to_rgb(self.item_data['color']), rect, border_radius=4)
        pygame.draw.rect(surface, (0,0,0), rect, 2, border_radius=4)

class Projectile:
    def __init__(self, x, y, tx, ty, p_type, dmg, scale=1.0, is_enemy=False, color_override=None, is_fire=False, is_electric=False, source_enemy_type=None, duration=None):
        self.x, self.y = x, y
        dx, dy = tx - x, ty - y
        dist = math.hypot(dx, dy)
        if dist == 0: dist = 1
        speed = 22 if p_type == 'arrow' else (12 if p_type == 'rock' else (14 if not is_enemy else 9))
        self.vx = (dx / dist) * speed; self.vy = (dy / dist) * speed
        self.type = p_type; self.damage = dmg; self.scale = scale; self.is_enemy = is_enemy
        self.color_override = color_override
        self.dead = False; self.particles = []
        self.stuck = False; self.stuck_to = None; self.stick_offset = (0,0)
        self.life = 300 
        self.angle = math.degrees(math.atan2(-self.vy, self.vx)) if self.type == 'arrow' else 0
        self.is_fire = is_fire
        self.is_electric = is_electric
        self.source_enemy_type = source_enemy_type
        self.burn_timer = 0
        self.piercing = False
        self.enemies_hit = {} 
        self.is_homing = False
        self.game_ref = None
        self.duration = duration 
        if self.is_fire and not self.color_override: self.color_override = "#ff4b2b"

    def update(self):
        if getattr(self, 'piercing', False):
            for e in list(self.enemies_hit.keys()):
                if self.enemies_hit[e] > 0:
                    self.enemies_hit[e] -= 1
                    
        if self.stuck_to:
            if getattr(self.stuck_to, 'dead', True): 
                self.dead = True; return
            self.x = self.stuck_to.x + self.stick_offset[0]
            self.y = self.stuck_to.y + self.stick_offset[1]
            if self.is_fire:
                self.burn_timer += 1
                if self.burn_timer % 20 == 0: self.stuck_to.take_damage(2, False, 'fire') 
                self.particles.append(Particle(self.x, self.y, "#ff4b2b", 3, 0.5))
            self.life -= 1
            if self.life <= 0: self.dead = True
            for p in self.particles: p.update()
            self.particles = [p for p in self.particles if p.life > 0]
            return

        if self.stuck:
            if self.is_fire:
                self.particles.append(Particle(self.x, self.y, "#ff4b2b", 3, 0.5))
            self.life -= 1
            if self.life <= 0: self.dead = True
            for p in self.particles: p.update()
            self.particles = [p for p in self.particles if p.life > 0]
            return
            
        self.x += self.vx; self.y += self.vy
        
        if getattr(self, 'is_homing', False) and getattr(self, 'game_ref', None):
            closest_enemy = None
            min_dist = 1200 
            for e in self.game_ref.enemies:
                if not e.dead:
                    dist = math.hypot(e.x - self.x, e.y - self.y)
                    if dist < min_dist:
                        min_dist = dist
                        closest_enemy = e
            
            if closest_enemy:
                dx = closest_enemy.x - self.x
                dy = (closest_enemy.y - closest_enemy.h/2) - self.y
                target_angle = math.atan2(dy, dx)
                current_angle = math.atan2(self.vy, self.vx)
                
                angle_diff = (target_angle - current_angle + math.pi) % (math.pi * 2) - math.pi
                steer_speed = 0.08
                new_angle = current_angle + max(-steer_speed, min(steer_speed, angle_diff))
                
                speed = math.hypot(self.vx, self.vy)
                self.vx = math.cos(new_angle) * speed
                self.vy = math.sin(new_angle) * speed

        if getattr(self, 'is_ult_sphere', False) and getattr(self, 'game_ref', None):
            for e in self.game_ref.enemies:
                if not e.dead:
                    dist = math.hypot(e.x - self.x, e.y - self.y)
                    if dist < 350: 
                        e.vx += (self.x - e.x) * 0.005
                        e.vy += (self.y - e.y) * 0.005

        if getattr(self, 'duration', None) is not None:
            self.duration -= 1
            if self.duration <= 0:
                self.dead = True
                if getattr(self, 'is_ult_sphere', False) and getattr(self, 'game_ref', None):
                    self.game_ref.create_magic_explosion(self.x, self.y, self.damage * 2)

        if self.y > FLOOR_Y + 1500 or self.y < FLOOR_Y - 1500 or self.x < -1000 or self.x > 30000: self.dead = True
        
        if self.is_electric and random.random() < 0.3:
            self.particles.append(Particle(self.x + random.uniform(-10,10), self.y + random.uniform(-10,10), "#00d2ff", 2, 0.5))
        elif random.random() < 0.5:
            color = self.color_override if self.color_override else ("#5c4033" if self.type == 'rock' else ("#ff4b2b" if self.is_enemy else ("#00d2ff" if self.type == 'magic' else "#cccccc")))
            self.particles.append(Particle(self.x, self.y, color, int(4 * self.scale), 0.2))
            
        for p in self.particles: p.update()
        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self, surface, cam_x, cam_y):
        for p in self.particles: p.draw(surface, cam_x, cam_y)
        base_hex = self.color_override if self.color_override else ("#ff4b2b" if self.is_enemy else ("#cccccc" if self.type == 'arrow' else "#00d2ff"))
        color = hex_to_rgb(base_hex) if isinstance(base_hex, str) and base_hex.startswith('#') else base_hex
        if isinstance(color, str): color = hex_to_rgb(color)
        
        if getattr(self, 'is_ult_sphere', False):
            pygame.draw.circle(surface, (0, 0, 0), (int(self.x - cam_x), int(self.y - cam_y)), int(8 * self.scale))
            pygame.draw.circle(surface, color, (int(self.x - cam_x), int(self.y - cam_y)), int(10 * self.scale), 3)
            t = pygame.time.get_ticks() * 0.005
            for i in range(4):
                ang = t + (i * math.pi / 2)
                ox = int(self.x - cam_x + math.cos(ang) * 20 * self.scale)
                oy = int(self.y - cam_y + math.sin(ang) * 20 * self.scale)
                pygame.draw.circle(surface, color, (ox, oy), int(3 * self.scale))
                pygame.draw.circle(surface, (255, 255, 255), (ox, oy), int(1.5 * self.scale))
            for _ in range(5):
                ang = random.uniform(0, math.pi*2)
                r = random.uniform(10, 25) * self.scale
                ex = int(self.x - cam_x + math.cos(ang) * r)
                ey = int(self.y - cam_y + math.sin(ang) * r)
                pygame.draw.line(surface, color, (int(self.x - cam_x), int(self.y - cam_y)), (ex, ey), int(2 * self.scale))
                
        elif getattr(self, 'is_electric', False):
            pygame.draw.circle(surface, color, (int(self.x - cam_x), int(self.y - cam_y)), int(8 * self.scale))
            for _ in range(3):
                ang = random.uniform(0, math.pi*2)
                r = random.uniform(8, 20) * self.scale
                ex = int(self.x - cam_x + math.cos(ang) * r)
                ey = int(self.y - cam_y + math.sin(ang) * r)
                pygame.draw.line(surface, (255, 255, 255), (int(self.x - cam_x), int(self.y - cam_y)), (ex, ey), int(2 * self.scale))
                pygame.draw.line(surface, color, (int(self.x - cam_x), int(self.y - cam_y)), (ex, ey), 1)
                
        elif self.type == 'wind_blade':
            if not self.stuck:
                self.angle = math.degrees(math.atan2(-self.vy, self.vx))
            s = pygame.Surface((int(35 * self.scale), int(12 * self.scale)), pygame.SRCALPHA)
            pygame.draw.ellipse(s, color, (0, 0, int(35 * self.scale), int(12 * self.scale)))
            pygame.draw.ellipse(s, (255, 255, 255), (int(8 * self.scale), int(3 * self.scale), int(20 * self.scale), int(6 * self.scale)))
            s_rot = pygame.transform.rotate(s, self.angle)
            surface.blit(s_rot, s_rot.get_rect(center=(int(self.x - cam_x), int(self.y - cam_y))))
        elif self.type == 'arrow':
            if not self.stuck:
                self.angle = math.degrees(math.atan2(-self.vy, self.vx))
            s = pygame.Surface((int(20 * self.scale), int(4 * self.scale)), pygame.SRCALPHA)
            s.fill(color)
            s_rot = pygame.transform.rotate(s, self.angle)
            surface.blit(s_rot, s_rot.get_rect(center=(int(self.x - cam_x), int(self.y - cam_y))))
        elif self.type == 'rock':
            rock_c = hex_to_rgb("#5c4033"); spike_c = hex_to_rgb("#a0a0a0")
            bx, by = int(self.x - cam_x), int(self.y - cam_y); s = int(10 * self.scale)
            pygame.draw.polygon(surface, rock_c, [(bx-s, by+s//2), (bx-s//2, by-s), (bx+s//2, by-s), (bx+s, by+s//2), (bx, by+s)])
            pygame.draw.polygon(surface, spike_c, [(bx-s//2, by-s), (bx, by-s*2), (bx+s//2, by-s)])
            pygame.draw.polygon(surface, spike_c, [(bx+s, by+s//2), (bx+s*2, by), (bx+s//2, by-s)])
            pygame.draw.polygon(surface, spike_c, [(bx-s, by+s//2), (bx-s*2, by), (bx-s//2, by-s)])
        else:
            pygame.draw.circle(surface, color, (int(self.x - cam_x), int(self.y - cam_y)), int(8 * self.scale))
            pygame.draw.circle(surface, (255,255,255), (int(self.x - cam_x), int(self.y - cam_y)), int(4 * self.scale))

# --- ENTIDADES PRINCIPAIS ---
class Player:
    def __init__(self, game, class_id):
        self.game = game; self.class_id = class_id; self.cdef = CLASSES[class_id]
        self.x, self.y = 200.0, FLOOR_Y - 100
        self.vx, self.vy = 0.0, 0.0
        self.w, self.h = 34, 60
        self.level = 1; self.xp = 0; self.xp_next = 1000
        self.max_hp = self.cdef['hp']; self.hp = self.max_hp
        self.score = 0; self.base_dmg = self.cdef['dmg']
        self.on_ground = False; self.dir = 1; self.walk_frame = 0.0
        self.invincible = 0; self.atk_timer = 0
        self.sp_timer = 0; self.sp_cooldown = 20000 
        self.jump_buffer_timer = 0 
        self.is_ground_pounding = False
        self.is_ult_smashing = False
        self.air_jumps_left = 1 
        self.is_crouching = False
        self.inventory = []; self.equipment = {'ring': None}; self.bonus_dmg = 0
        self.active_ultimate = None 

    def get_power_level(self):
        return self.level + (self.bonus_dmg / 10.0)

    def get_rect(self): return pygame.Rect(self.x - self.w/2, self.y - self.h, self.w, self.h)

    def gain_xp(self, amount):
        self.xp += amount
        if self.xp >= self.xp_next:
            self.xp -= self.xp_next; self.level += 1; self.xp_next = int(self.xp_next * 1.5)
            self.max_hp += int(self.cdef['hp'] * 0.15)
            self.hp = self.max_hp
            self.base_dmg += int(self.cdef['dmg'] * 0.15)
            self.game.floating_texts.append(FloatingText(self.x, self.y - 120, f"LEVEL UP! NV.{self.level}", "#ffcc00", False, True))
            self.game.spawn_particle(self.x, self.y, "#ffcc00", 50, 3.0)
            self.game.shake = 30; self.game.hitstop = 10 

    def update(self, keys, mouse_pos, mouse_pressed):
        dt = 1000 / FPS
        
        if self.invincible > 0: self.invincible -= dt
        if self.atk_timer > 0: self.atk_timer -= dt
        
        ult_active = False
        if getattr(self, 'active_ultimate', None):
            if not self.active_ultimate.dead:
                ult_active = True
            else:
                self.active_ultimate = None
                
        if self.sp_timer > 0 and not ult_active:
            self.sp_timer -= dt
            
        if self.jump_buffer_timer > 0: self.jump_buffer_timer -= 1
        
        if self.jump_buffer_timer > 0 and self.on_ground:
            self.jump_buffer_timer = 0
            self.jump()
            
        self.is_crouching = False
        if self.on_ground and (keys[pygame.K_DOWN] or keys[pygame.K_s]):
            self.is_crouching = True
            
        if self.is_ground_pounding:
            self.vy = 40; self.vx = 0 
            if self.is_ult_smashing:
                self.game.spawn_particle(self.x, self.y - 30, self.cdef['sp_color'], 5, 2.0)
                self.game.spawn_particle(self.x, self.y - 30, "#ffffff", 2, 1.0)
            else:
                self.game.spawn_particle(self.x, self.y, "#ffffff", 1)
        else:
            move = 0
            if not self.is_crouching:
                if keys[pygame.K_LEFT] or keys[pygame.K_a]: move = -1; self.dir = -1
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]: move = 1; self.dir = 1
            self.vx += move * (self.cdef['speed'] * 0.25)
            
            self.vx *= 0.80
            if abs(self.vx) < 0.2: 
                self.vx = 0.0 
                
            self.vy += GRAVITY
            
            current_limit = self.cdef['speed']
            if self.vx > current_limit: self.vx = current_limit
            if self.vx < -current_limit: self.vx = -current_limit

        self.x += self.vx
        self.resolve_collisions(True)
        self.y += self.vy
        self.resolve_collisions(False)

        if self.on_ground and abs(self.vx) > 0.5: self.walk_frame += 0.3
        
        if self.y > FLOOR_Y + 1500: self.game.end_game() 

        if mouse_pressed[0] and self.atk_timer <= 0:
            mx, my = mouse_pos
            self.attack(mx + self.game.cam_x, my + self.game.cam_y)
            self.atk_timer = self.cdef['cooldown']
            
        if mouse_pressed[2] and self.sp_timer <= 0: 
            mx, my = mouse_pos
            self.use_special(mx + self.game.cam_x, my + self.game.cam_y)

    def resolve_collisions(self, is_horizontal):
        if not is_horizontal: self.on_ground = False
        rect = self.get_rect()
        for p in self.game.platforms:
            if rect.colliderect(p.rect):
                if is_horizontal:
                    if self.vx > 0: self.x = p.left - self.w/2
                    elif self.vx < 0: self.x = p.right + self.w/2
                    self.vx = 0
                else:
                    if self.vy > 0:
                        self.y = p.top; self.vy = 0; self.on_ground = True
                        p.trigger() # Armadilha treme se for pisada!
                        self.air_jumps_left = 1 
                        if self.is_ground_pounding:
                            if getattr(self, 'is_ult_smashing', False):
                                self.game.shake = 50
                                dmg, _ = self.calculate_damage(mult=4.0)
                                self.game.create_shockwave(self.x, self.y, custom_dmg=dmg)
                                self.game.explosions.append(ExplosionSphere(self.x, self.y, max_radius=250, color=self.cdef['sp_color'], life=30))
                                for i in range(8):
                                    ang = i * (math.pi / 4)
                                    self.game.slashes.append(SlashEffect(self.x, self.y - 20, ang, size=250, color=hex_to_rgb(self.cdef['sp_color'])))
                                self.game.floating_texts.append(FloatingText(self.x, self.y - 80, self.cdef['sp_name'], self.cdef['sp_color'], True))
                                self.is_ult_smashing = False
                            else:
                                self.game.shake = 30
                                self.game.create_shockwave(self.x, self.y)
                        self.is_ground_pounding = False
                    elif self.vy < 0:
                        self.y = p.bottom + self.h; self.vy = 0
                rect = self.get_rect()

    def jump(self):
        self.jump_buffer_timer = 0
        if self.on_ground:
            self.vy = self.cdef['jump']; self.on_ground = False
            self.game.spawn_particle(self.x, self.y, "#ffffff", 8)
            play_sfx('jump')
        elif self.air_jumps_left > 0: 
            self.air_jumps_left -= 1
            self.is_ground_pounding = False
            self.is_ult_smashing = False
            
            if self.air_jumps_left == 0:
                self.vy = self.cdef['jump'] * 1.15
                play_sfx('attack')
                if self.class_id == 'warrior':
                    self.game.slashes.append(SlashEffect(self.x, self.y, -math.pi/2, size=150, color=(255, 100, 50)))
                    self.game.spawn_particle(self.x, self.y, "#ff4444", 25, 3.0)
                elif self.class_id == 'mage':
                    self.game.explosions.append(ExplosionSphere(self.x, self.y, max_radius=80, color="#00d2ff", life=15))
                    self.game.spawn_particle(self.x, self.y, "#ffffff", 20, 2.0)
                elif self.class_id == 'rogue':
                    self.game.slashes.append(SlashEffect(self.x - 20, self.y, -math.pi/3, size=120, color=(50, 255, 50)))
                    self.game.slashes.append(SlashEffect(self.x + 20, self.y, -2*math.pi/3, size=120, color=(50, 255, 50)))
                    self.game.spawn_particle(self.x, self.y, "#00ff00", 20, 3.0)
            else:
                self.vy = self.cdef['jump'] * 0.85
                self.game.spawn_particle(self.x, self.y, self.cdef['color'], 12)
                play_sfx('jump')
        else:
            self.jump_buffer_timer = 10

    def calculate_damage(self, mult=1.0):
        crit_chance = 0.30 if self.class_id == 'rogue' else 0.20
        is_crit = random.random() < crit_chance
        variance = random.uniform(0.9, 1.1)
        dmg = (self.base_dmg + self.bonus_dmg) * mult * variance
        if is_crit: dmg *= 2.0
        return int(dmg), is_crit

    def use_special(self, tx, ty):
        self.sp_timer = self.sp_cooldown; self.game.shake = 35; self.game.hitstop = 8 
        dmg, is_crit = self.calculate_damage(mult=2.0)
        play_sfx('attack')
        
        if self.class_id == 'warrior':
            self.is_ground_pounding = True
            self.is_ult_smashing = True
            self.vy = -12 
            self.atk_timer = 400 
        elif self.class_id == 'mage':
            self.game.floating_texts.append(FloatingText(self.x, self.y - 80, self.cdef['sp_name'], self.cdef['sp_color'], True))
            p = Projectile(self.x, self.y - 35, tx, ty, self.cdef['atkType'], int(dmg * 2.5), scale=5.0, is_electric=True, duration=210)
            p.vx *= 0.5 
            p.vy *= 0.5
            p.color_override = self.cdef['sp_color']
            p.is_homing = True
            p.is_ult_sphere = True
            p.game_ref = self.game
            p.piercing = True 
            p.enemies_hit = {} 
            self.game.projectiles.append(p)
            self.active_ultimate = p 
            play_sfx('jump')
        elif self.class_id == 'rogue':
            self.game.floating_texts.append(FloatingText(self.x, self.y - 80, self.cdef['sp_name'], self.cdef['sp_color'], True))
            dx, dy = tx - self.x, ty - (self.y - 35)
            base_angle = math.atan2(dy, dx)
            
            self.game.slashes.append(SlashEffect(self.x, self.y - 35, base_angle, size=250, color=hex_to_rgb(self.cdef['sp_color'])))
            
            for angle_offset in [-0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6]:
                angle = base_angle + angle_offset
                nx = self.x + math.cos(angle) * 100
                ny = (self.y - 35) + math.sin(angle) * 100
                p = Projectile(self.x, self.y - 35, nx, ny, 'wind_blade', int(dmg * 1.5), scale=1.2, is_electric=False, duration=210)
                p.color_override = self.cdef['sp_color']
                p.piercing = True
                p.is_homing = True
                p.game_ref = self.game
                p.enemies_hit = {}
                self.game.projectiles.append(p)
            play_sfx('jump')

    def attack(self, tx, ty):
        dmg, is_crit = self.calculate_damage()
        play_sfx('attack')
        y_off = 15 if self.is_crouching else 30
        
        if self.cdef['atkType'] == "melee":
            self.game.spawn_particle(self.x + (self.dir*40), self.y-y_off, "#ffffff", 12, 2.5)
            
            ang = 0 if self.dir == 1 else math.pi
            self.game.slashes.append(SlashEffect(self.x + self.dir*20, self.y - y_off, ang, size=100))
            
            self.vx = 12 * self.dir
            atk_rect = pygame.Rect(self.x if self.dir == 1 else self.x - 65, self.y - 60, 65, 60)
            
            for e in self.game.enemies:
                if not e.dead and atk_rect.colliderect(e.get_rect()): 
                    e.vx = self.dir * 30; e.vy = -12
                    e.take_damage(dmg, is_crit, 'melee')
        else:
            is_fire = getattr(self, 'fire_arrows_timer', 0) > 0
            is_electric = (self.class_id == 'mage')
            p = Projectile(self.x, self.y - y_off, tx, ty, self.cdef['atkType'], dmg, is_fire=is_fire, is_electric=is_electric)
            p.is_crit = is_crit 
            self.game.projectiles.append(p)

    def take_damage(self, amt):
        if self.invincible > 0 or self.hp <= 0: return
        self.hp -= amt
        play_sfx('hit')
        self.game.floating_texts.append(FloatingText(self.x, self.y - 50, f"-{amt}", "#ff0000"))
        self.game.shake = 20; self.game.hitstop = 4; self.invincible = 1200
        
        if self.hp <= 0: 
            self.game.trigger_player_death() 
        else: 
            self.vy = -14; self.vx = -10 * self.dir

    def heal(self, amt):
        self.hp = min(self.max_hp, self.hp + amt)
        self.game.floating_texts.append(FloatingText(self.x, self.y - 50, f"+{amt} HP", "#00ff00"))
        self.game.spawn_particle(self.x, self.y, "#00ff00", 15)

    def add_item(self, item_id):
        self.inventory.append(item_id)
        self.game.floating_texts.append(FloatingText(self.x, self.y - 70, f"+ {ITEM_DB[item_id]['name']}", ITEM_DB[item_id]['color']))

    def use_item(self, index):
        if index >= len(self.inventory): return
        item_id = self.inventory[index]; item = ITEM_DB[item_id]
        if item['type'] == 'consumable':
            if item_id.startswith('potion_'): self.heal(item['val'])
            if item_id == 'book_exp': self.gain_xp(item['val'])
            self.inventory.pop(index)
        elif item['type'].startswith('equip_'):
            if item['type'] == 'equip_ring':
                if self.equipment['ring']: self.inventory.append(self.equipment['ring'])
                self.equipment['ring'] = item_id; self.bonus_dmg = item['val']
                self.inventory.pop(index)

    def draw(self, surface, cam_x, cam_y, mouse_pos):
        if self.invincible > 0 and (pygame.time.get_ticks() // 80) % 2 == 0: return
        bx, by = int(self.x - cam_x), int(self.y - cam_y)
        
        is_moving = self.on_ground and abs(self.vx) > 0.5
        
        if is_moving:
            swing = math.sin(self.walk_frame) * 14
            bob = math.sin(self.walk_frame * 2) * 2.5  
        else:
            swing = 0
            bob = math.sin(pygame.time.get_ticks() * 0.004) * 3
        
        dx, dy = mouse_pos[0] - bx, mouse_pos[1] - int(by - 30 + bob)
        aim_angle = math.degrees(math.atan2(-dy, dx)) if self.dir == 1 else math.degrees(math.atan2(-dy, -dx))
        
        draw_hero_model(surface, bx, by, self.class_id, self.dir, bob, swing, self.atk_timer, aim_angle, self.vy, scale=1.0, is_crouching=self.is_crouching)


class Enemy:
    def __init__(self, game, x, y, theme, type='basic'):
        self.game = game; self.x, self.y = x, y; self.vx, self.vy = 0, 0
        
        if type == 'boss': self.w, self.h = 140, 160
        elif type == 'tank': self.w, self.h = 60, 60
        elif type == 'charger': self.w, self.h = 70, 50
        elif type == 'wizard': self.w, self.h = 40, 60
        elif type == 'jumper': self.w, self.h = 40, 30
        else: self.w, self.h = 45, 50
            
        self.type = type; self.theme = theme
        power = self.game.player.get_power_level()
        
        diff_mult = self.game.get_difficulty_mult()
        base_mult = 1.1 + (self.game.level * 0.15) + (power * 0.08)
        mult = base_mult * diff_mult
        
        if type == 'boss':
            self.max_hp = int(1200 * mult); self.speed = (1.8 + (self.game.level * 0.05)) * diff_mult; self.xp_value = 500 + (self.game.level * 100)
        elif type == 'tank':
            self.max_hp = int(450 * mult); self.speed = (2.5 + (self.game.level * 0.05)) * diff_mult; self.xp_value = 150 + (self.game.level * 20)
        elif type == 'charger':
            self.max_hp = int(200 * mult); self.speed = (4.5 + (self.game.level * 0.10)) * diff_mult; self.xp_value = 100 + (self.game.level * 15)
        elif type == 'wizard':
            self.max_hp = int(100 * mult); self.speed = (2.5 + (self.game.level * 0.05)) * diff_mult; self.xp_value = 120 + (self.game.level * 20)
        else:
            self.max_hp = int(100 * mult)
            base_s = 4.5 if type == 'bat' else (3.5 if type == 'jumper' else (4.0 if type == 'archer' else 3.0))
            self.speed = (base_s + (self.game.level * 0.10)) * diff_mult
            self.xp_value = 50 + (self.game.level * 15)
            
        self.hp = self.max_hp; self.dead = False
        self.dir = 1 if random.random() > 0.5 else -1
        self.on_ground = False; self.anim_frame = 0.0; self.flash_timer = 0
        self.attack_timer = 120; self.start_y = y 
        self.state = 'normal'
        self.prev_vy = 0.0
        self.slow_timer = 0 
        self.shock_timer = 0 

    def get_rect(self):
        if self.type == 'boss': return pygame.Rect(self.x - 70, self.y - 160, 140, 160)
        return pygame.Rect(self.x - self.w/2, self.y - self.h, self.w, self.h)

    def update(self, player):
        if self.y > FLOOR_Y + 800:
            self.dead = True
            self.game.player.score += 2000 if self.type == 'boss' else 150
            self.game.player.gain_xp(self.xp_value)
            self.game.floating_texts.append(FloatingText(self.x, FLOOR_Y + 200, "QUEDA FATAL!", "#ff4444"))
            if self.type == 'boss': self.game.boss_defeated(self.x, FLOOR_Y)
            return

        if abs(self.x - player.x) > 1200:
            return

        if self.flash_timer > 0: self.flash_timer -= 1
        if self.slow_timer > 0: self.slow_timer -= 1
        
        if getattr(self, 'shock_timer', 0) > 0:
            self.shock_timer -= 1
            if self.shock_timer % 20 == 0:
                self.hp -= 1
                self.game.spawn_particle(self.x + random.uniform(-15, 15), self.y - self.h/2 + random.uniform(-15, 15), "#00d2ff", 2, 0.5)
                self.game.floating_texts.append(FloatingText(self.x, self.y - 40, "1", "#00d2ff"))
                if self.hp <= 0: 
                    self.take_damage(0)
                    return
        
        enraged = (self.type == 'boss' and self.hp < self.max_hp / 2)
        power = self.game.player.get_power_level()
        diff_mult = self.game.get_difficulty_mult()
        
        self.x += self.vx; self.vx *= 0.85
        
        rect = self.get_rect()
        for p in self.game.platforms:
            if rect.colliderect(p.rect) and p.top < self.y - 20: 
                if self.vx > 0: self.x = p.left - self.w/2
                elif self.vx < 0: self.x = p.right + self.w/2
                self.vx = 0
                break

        if self.type == 'bat' or self.type == 'wizard':
            dist_x, dist_y = player.x - self.x, (player.y - 30) - self.y
            
            if self.type == 'bat':
                if self.state == 'prep_swoop':
                    self.attack_timer -= 1; self.flash_timer = 2
                    if self.attack_timer <= 0:
                        self.state = 'swooping'; self.attack_timer = 25
                        dist = math.hypot(dist_x, dist_y)
                        if dist == 0: dist = 1
                        self.vx, self.vy = (dist_x / dist) * 20, (dist_y / dist) * 20
                elif self.state == 'swooping':
                    self.attack_timer -= 1; self.x += self.vx; self.y += self.vy
                    self.game.spawn_particle(self.x, self.y, "#ff0000", 1)
                    if self.attack_timer <= 0 or self.y > FLOOR_Y - 50:
                        self.state = 'normal'; self.attack_timer = 150; self.start_y = self.y
                else:
                    self.attack_timer -= 1
                    if self.attack_timer <= 0 and math.hypot(dist_x, dist_y) < 350:
                        self.state = 'prep_swoop'; self.attack_timer = 30; self.vx = 0; self.vy = 0
                    else:
                        if abs(dist_x) < 500 and abs(dist_y) < 400:
                            angle = math.atan2(dist_y, dist_x)
                            self.x += math.cos(angle) * self.speed; self.y += math.sin(angle) * self.speed
                            self.dir = 1 if dist_x > 0 else -1
                        else:
                            self.x += self.dir * self.speed
                            self.y = self.start_y + math.sin(self.anim_frame) * 40 
                            if self.x < 0 or self.x > 30000: self.dir *= -1
                        self.anim_frame += 0.1
            
            elif self.type == 'wizard':
                if self.state == 'normal':
                    self.attack_timer -= 1
                    if self.attack_timer <= 0 and abs(dist_x) < 700 and abs(dist_y) < 300:
                        self.state = 'telegraph'
                        self.attack_timer = 30
                        self.dir = 1 if dist_x > 0 else -1
                elif self.state == 'telegraph':
                    self.attack_timer -= 1
                    if self.attack_timer <= 0:
                        self.attack_timer = max(60, int(120 - self.game.level * 3 - power * 2))
                        dmg = int((18 + (self.game.level * 3) + (power * 2)) * diff_mult)
                        for dy in [-40, 0, 40]:
                            self.game.projectiles.append(Projectile(self.x, self.y - 30, player.x, player.y - 30 + dy, 'magic', dmg, scale=1.2, is_enemy=True, source_enemy_type=self.type))
                        self.state = 'normal'
                
                if self.state == 'normal':
                    cur_speed = self.speed * 0.5
                    if self.slow_timer > 0 or getattr(self, 'shock_timer', 0) > 0: cur_speed *= 0.4 
                    if abs(dist_x) < 400 and abs(dist_y) < 300:
                        self.dir = 1 if dist_x > 0 else -1
                        self.x -= self.dir * cur_speed
                    else:
                        self.x += self.dir * cur_speed
                        if self.x < 0 or self.x > 30000: self.dir *= -1
                
                self.anim_frame += 0.05
                self.y = self.start_y + math.sin(self.anim_frame) * 20
                
            return 

        self.prev_vy = self.vy; self.vy += GRAVITY; self.y += self.vy; self.on_ground = False
        rect = self.get_rect()
        for p in self.game.platforms:
            if rect.colliderect(p.rect):
                if self.vy > 0: 
                    self.y = p.top
                    self.vy = 0
                    self.on_ground = True
                    if self.type == 'boss' and self.state == 'smashing':
                        self.state = 'normal'
                        self.vx = 0
                        self.game.shake = 35
                        dmg = int((45 + (self.game.level * 6) + (power * 3)) * diff_mult)
                        haz_col = THEMES[self.theme]['hazard']
                        self.game.projectiles.append(Projectile(self.x, self.y, self.x - 100, self.y, 'rock', dmg, scale=2.0, is_enemy=True, color_override=haz_col, source_enemy_type=self.type))
                        self.game.projectiles.append(Projectile(self.x, self.y, self.x + 100, self.y, 'rock', dmg, scale=2.0, is_enemy=True, color_override=haz_col, source_enemy_type=self.type))
                        play_sfx('hit')
                    break

        if self.type == 'jumper' and not self.on_ground:
            if self.prev_vy < 0 and self.vy >= 0:
                dmg = int((12 + self.game.level * 2 + power * 1.5) * diff_mult)
                hazard_color = THEMES[self.theme]['hazard']
                self.game.projectiles.append(Projectile(self.x, self.y, self.x - 100, self.y + 100, 'magic', dmg, scale=0.8, is_enemy=True, color_override=hazard_color, source_enemy_type=self.type))
                self.game.projectiles.append(Projectile(self.x, self.y, self.x + 100, self.y + 100, 'magic', dmg, scale=0.8, is_enemy=True, color_override=hazard_color, source_enemy_type=self.type))
                self.game.spawn_particle(self.x, self.y, hazard_color, 10)

        if self.type == 'boss':
            dist_x = player.x - self.x
            self.dir = 1 if dist_x > 0 else -1
            self.attack_timer -= 2 if enraged else 1
            
            if self.state == 'normal' and self.attack_timer <= 0:
                self.attack_timer = max(50, 140 - int(self.game.level * 4 + power * 3))
                attack_choice = random.randint(1, 2)
                
                if self.theme == 'forest':
                    if attack_choice == 1:
                        for i in range(4):
                            tx = player.x + random.randint(-150, 150)
                            ty = FLOOR_Y
                            dmg = int((35 + (self.game.level * 4) + (power * 4)) * diff_mult)
                            self.game.projectiles.append(Projectile(tx, ty + 100, tx, ty - 200, 'magic', dmg, scale=1.5, is_enemy=True, color_override="#5c8a58", source_enemy_type=self.type))
                        play_sfx('attack')
                    else:
                        self.game.enemies.append(Enemy(self.game, self.x + self.dir*100, self.y - 50, self.theme, 'jumper'))
                        self.game.spawn_particle(self.x + self.dir*100, self.y - 50, "#5c8a58", 30, 2.0)
                        play_sfx('select')
                        
                elif self.theme == 'cave':
                    if attack_choice == 1:
                        dmg = int((30 + (self.game.level * 4) + (power * 4)) * diff_mult)
                        for i in range(8):
                            ang = i * (math.pi / 4)
                            tx = self.x + math.cos(ang) * 100
                            ty = self.y - 80 + math.sin(ang) * 100
                            self.game.projectiles.append(Projectile(self.x, self.y - 80, tx, ty, 'magic', dmg, scale=1.2, is_enemy=True, color_override="#9d50bb", source_enemy_type=self.type))
                        play_sfx('attack')
                    else:
                        self.vy = -24
                        self.vx = self.dir * 18
                        self.state = 'smashing'
                        self.on_ground = False
                        play_sfx('jump')
                        
                elif self.theme == 'volcano':
                    if attack_choice == 1:
                        dmg = int((40 + (self.game.level * 5) + (power * 4)) * diff_mult)
                        for i in range(3):
                            px = player.x + random.randint(-200, 200)
                            py = player.y - 600 - random.randint(0, 200)
                            self.game.projectiles.append(Projectile(px, py, px, player.y, 'rock', dmg, scale=2.0, is_enemy=True, color_override="#ff4b2b", is_fire=True, source_enemy_type=self.type))
                        play_sfx('attack')
                    else:
                        dmg = int((30 + (self.game.level * 4) + (power * 4)) * diff_mult)
                        base_angle = math.atan2((player.y - 30) - (self.y - 80), player.x - self.x)
                        for offset in [-0.2, 0, 0.2]:
                            tx = self.x + math.cos(base_angle + offset) * 100
                            ty = (self.y - 80) + math.sin(base_angle + offset) * 100
                            self.game.projectiles.append(Projectile(self.x, self.y - 80, tx, ty, 'magic', dmg, scale=1.8, is_enemy=True, color_override="#ffcc00", source_enemy_type=self.type))
                        play_sfx('attack')
                        
                elif self.theme == 'electric':
                    if attack_choice == 1:
                        dmg = int((35 + (self.game.level * 4) + (power * 4)) * diff_mult)
                        for i in range(2):
                            px = player.x + random.randint(-100, 100)
                            self.game.projectiles.append(Projectile(px, player.y - 800, px, player.y, 'arrow', dmg, scale=3.0, is_enemy=True, color_override="#00d2ff", source_enemy_type=self.type))
                        play_sfx('attack')
                    else:
                        dmg = int((25 + (self.game.level * 3) + (power * 3)) * diff_mult)
                        self.game.projectiles.append(Projectile(self.x, self.y - 80, player.x, player.y, 'magic', dmg, scale=1.5, is_enemy=True, color_override="#ffffff", source_enemy_type=self.type))
                        play_sfx('select')

        elif self.type == 'archer':
            dist_x = player.x - self.x
            if abs(dist_x) < 600 and abs(player.y - self.y) < 300:
                self.attack_timer -= 1
                if self.attack_timer <= 0:
                    self.attack_timer = max(20, int(45 - self.game.level - power))
                    self.dir = 1 if dist_x > 0 else -1
                    dmg = int((12 + (self.game.level * 2) + (power * 1.5)) * diff_mult)
                    self.game.projectiles.append(Projectile(self.x, self.y - 30, player.x, player.y - 30, 'arrow', dmg, scale=1.2, is_enemy=True, source_enemy_type=self.type))

        elif self.type == 'tank':
            dist_x = player.x - self.x
            if abs(dist_x) < 500 and abs(player.y - self.y) < 150:
                self.attack_timer -= 1
                if self.attack_timer == 15: self.dir = 1 if dist_x > 0 else -1; self.vx = 0
                elif self.attack_timer <= 0:
                    self.attack_timer = 100 - min(50, int(self.game.level * 2 + power * 2))
                    self.game.shake = 15; self.game.spawn_particle(self.x + (self.dir*40), self.y + 10, "#8b5e34", 25, 3.0)
                    dmg = int((20 + (self.game.level * 2.5) + (power * 2)) * diff_mult)
                    self.game.projectiles.append(Projectile(self.x + (self.dir*30), self.y + 10, self.x + (self.dir*100), self.y + 10, 'rock', dmg, scale=1.5, is_enemy=True, source_enemy_type=self.type))
                    self.game.projectiles.append(Projectile(self.x + (self.dir*30), self.y + 10, self.x + (self.dir*100), self.y - 30, 'rock', dmg, scale=1.2, is_enemy=True, source_enemy_type=self.type))
                    self.game.projectiles.append(Projectile(self.x + (self.dir*30), self.y + 10, self.x + (self.dir*100), self.y - 60, 'rock', dmg, scale=1.0, is_enemy=True, source_enemy_type=self.type))

        elif self.type == 'basic':
            dist_x = player.x - self.x
            if abs(dist_x) < 350 and abs(player.y - self.y) < 100:
                self.attack_timer -= 1
                if self.attack_timer <= 0:
                    self.attack_timer = max(70, int(130 - self.game.level * 2 - power * 2))
                    self.dir = 1 if dist_x > 0 else -1
                    dmg = int((10 + self.game.level * 1.5 + power * 1.5) * diff_mult)
                    hazard_color = THEMES[self.theme]['hazard']
                    self.game.projectiles.append(Projectile(self.x, self.y - 15, player.x, player.y - 20, 'magic', dmg, scale=1.0, is_enemy=True, color_override=hazard_color, source_enemy_type=self.type))
                    
        elif self.type == 'charger':
            dist_x = player.x - self.x
            if self.state == 'normal':
                self.attack_timer -= 1
                if self.attack_timer <= 0 and abs(dist_x) < 400 and abs(player.y - self.y) < 100:
                    self.state = 'telegraph'
                    self.attack_timer = 30 
                    self.dir = 1 if dist_x > 0 else -1
            elif self.state == 'telegraph':
                self.attack_timer -= 1
                if self.attack_timer <= 0:
                    self.state = 'charging'
                    self.attack_timer = 60 
                    play_sfx('jump')
            elif self.state == 'charging':
                self.attack_timer -= 1
                self.vx = self.dir * (self.speed * 3.5)
                self.game.spawn_particle(self.x, self.y, THEMES[self.theme]['hazard'], 2)
                if self.attack_timer <= 0:
                    self.state = 'normal'
                    self.attack_timer = 150 

        if self.on_ground:
            if self.type == 'jumper' and random.random() < 0.03: self.vy = -22; self.on_ground = False
            if self.type == 'tank' and self.attack_timer < 20: pass 
            else:
                dist_x = player.x - self.x
                target_dir = self.dir
                if self.type == 'archer':
                    if abs(dist_x) < 250 and abs(player.y - self.y) < 150:
                        target_dir = -1 if dist_x > 0 else 1 
                        if random.random() < 0.04: self.vy = -16; self.on_ground = False
                    elif abs(dist_x) < 600 and abs(player.y - self.y) < 150: target_dir = 1 if dist_x > 0 else -1 
                elif self.type != 'charger' or self.state not in ['charging', 'telegraph']:
                    if abs(dist_x) < 400 and abs(player.y - self.y) < 150 and self.type != 'boss': target_dir = 1 if dist_x > 0 else -1
                    
                next_x = self.x + (target_dir * 30); has_ground = False
                for p in self.game.platforms:
                    if p.left < next_x < p.right and abs(self.y - p.top) < 20: has_ground = True; break
                        
                current_speed = self.speed * 1.5 if enraged else self.speed
                if self.slow_timer > 0 or getattr(self, 'shock_timer', 0) > 0: current_speed *= 0.4
                
                if has_ground or (self.type == 'charger' and self.state == 'charging') or self.type == 'boss':
                    if self.type != 'charger' or self.state not in ['charging', 'telegraph']:
                        if self.type != 'boss': self.dir = target_dir
                        
                    if self.type == 'archer' and self.attack_timer < 15 and abs(dist_x) < 600: self.dir = 1 if dist_x > 0 else -1
                    elif self.type == 'basic' and self.attack_timer < 15 and abs(dist_x) < 350: self.dir = 1 if dist_x > 0 else -1
                    else: 
                        step = self.dir * current_speed
                        if self.state not in ['charging', 'telegraph', 'smashing']: self.x += step
                        self.anim_frame += 0.15 * (1.5 if enraged else 1.0)
                else:
                    if abs(dist_x) < 400 and abs(player.y - self.y) < 150 and self.type not in ['archer', 'boss']: self.dir = target_dir 
                    else: 
                        if self.state not in ['charging', 'telegraph', 'smashing'] and self.type != 'boss':
                            self.dir *= -1
                            step = self.dir * current_speed
                            if not (self.type == 'archer' and self.attack_timer < 15) and not (self.type == 'basic' and self.attack_timer < 15):
                                self.x += step

                rect = self.get_rect()
                for p in self.game.platforms:
                    if rect.colliderect(p.rect) and p.top < self.y - 20:
                        if self.dir > 0: self.x = p.left - self.w/2
                        elif self.dir < 0: self.x = p.right + self.w/2
                        self.dir *= -1 
                        if self.state == 'charging': self.state = 'normal'; self.attack_timer = 150
                        break

    def take_damage(self, amt, is_crit=False, source_type='melee', is_electric=False):
        if not (self.game.cam_x - 50 <= self.x <= self.game.cam_x + self.game.virt_w + 50 and self.game.cam_y - 50 <= self.y <= self.game.cam_y + self.game.virt_h + 50): return
        
        self.hp -= amt; self.flash_timer = 6
        
        if source_type == 'magic':
            self.slow_timer = 120 
        if is_electric:
            self.shock_timer = 150 
            
        self.game.floating_texts.append(FloatingText(self.x, self.y - 60, str(amt), "#ffffff", is_crit))
        play_sfx('hit')
        if is_crit or self.type == 'boss': self.game.hitstop = 4; self.game.shake = 10 if is_crit else 5
        
        if self.hp <= 0:
            self.dead = True
            self.game.shake = max(self.game.shake, 15)
            self.game.explosions.append(ExplosionSphere(self.x, self.y, max_radius=90, color=THEMES[self.theme]['hazard'], life=20))
            self.game.spawn_particle(self.x, self.y, "#ffffff", 15, 3.0)
            self.game.spawn_particle(self.x, self.y, THEMES[self.theme]['hazard'], 25, 4.0)
            self.game.slashes.append(SlashEffect(self.x, self.y, random.uniform(0, math.pi*2), size=120, color=hex_to_rgb(THEMES[self.theme]['hazard'])))
            
            self.game.player.score += 2000 if self.type == 'boss' else 150
            self.game.player.gain_xp(self.xp_value)
            
            if self.type == 'boss' or random.random() < 0.12:
                loot_chances = [('potion_min', 0.70), ('potion_max', 0.10), ('ring_str', 0.12), ('book_exp', 0.06), ('ring_epic', 0.015), ('crown_gods', 0.005)]
                if self.type == 'boss': loot_chances = [('ring_epic', 0.4), ('crown_gods', 0.3), ('book_exp', 0.3)]
                rand_val = random.random(); cumulative = 0; chosen_item = 'potion_min'
                for item_id, prob in loot_chances:
                    cumulative += prob
                    if rand_val <= cumulative: chosen_item = item_id; break
                self.game.loot_drops.append(LootDrop(self.x, self.y - 30, chosen_item))
            if self.type == 'boss': self.game.boss_defeated(self.x, self.y)

    def draw(self, surface, cam_x, cam_y):
        bx, by = int(self.x - cam_x), int(self.y - cam_y)
        enraged = (self.type == 'boss' and self.hp < self.max_hp / 2)
        if self.type == 'boss': draw_boss_model(surface, bx, by, self.theme, self.anim_frame, self.flash_timer, enraged)
        else: draw_enemy_model(surface, bx, by, self.theme, self.type, self.dir, self.anim_frame, self.flash_timer, self.attack_timer, self.state)

        if getattr(self, 'shock_timer', 0) > 0:
            for _ in range(3):
                ang = random.uniform(0, math.pi*2)
                r = random.uniform(10, self.w + 10)
                sx = bx + math.cos(ang) * (r * 0.2)
                sy = by - self.h/2 + math.sin(ang) * (r * 0.2)
                ex = bx + math.cos(ang) * r
                ey = by - self.h/2 + math.sin(ang) * r
                pygame.draw.line(surface, (0, 210, 255), (int(sx), int(sy)), (int(ex), int(ey)), 2)
                pygame.draw.line(surface, (255, 255, 255), (int(sx), int(sy)), (int(ex), int(ey)), 1)


# --- MOTOR PRINCIPAL DO JOGO ---
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption("Entre Mundos - RPG Ultimate")
        self.clock = pygame.time.Clock()
        
        load_sfx()
        load_images()
        
        self.border_image = load_and_cut_overlay()
        self.game_surface = pygame.Surface((GAME_W, GAME_H))
        
        self.base_zoom = ZOOM_OUT
        self.zoom = self.base_zoom
        self.virt_w = int(GAME_W * self.zoom)
        self.virt_h = int(GAME_H * self.zoom)
        self.world_surface = pygame.Surface((self.virt_w, self.virt_h))
        
        self.state = 'menu'; self.previous_state = 'menu'; self.level = 1
        self.cam_x = 0.0; self.cam_y = FLOOR_Y - self.virt_h + 60
        self.max_cam_x = 0.0 
        self.shake = 0; self.hitstop = 0; self.trash_mode = False
        self.menu_modal_open = False; self.menu_particles = [] 
        
        self.map_scroll_y = 0
        self.target_map_scroll_y = 0
        self.how_to_play_scroll = 0
        self.target_how_to_play_scroll = 0
        self.death_timer = 0 
        
        self.platforms = []; self.enemies = []; self.projectiles = []
        self.particles = []; self.floating_texts = []; self.loot_drops = []
        self.slashes = []; self.explosions = []; self.biome_traps = []
        self.decorations = [] 
        self.portal = None; self.player = None; self.boss = None
        self.selected_class = 'warrior'; self.input_text = ""
        self.keys = {}; self.mouse_pos = (0,0); self.world_mouse_pos = (0,0)
        self.mouse_pressed = [False, False, False]; self.just_clicked = False 

        self.instructions = [
            ("MOVIMENTO", "Setas Direcionais ou A / D", "#3498db"),
            ("PULO", "Seta para Cima, W ou Espaco (Pulo Duplo)", "#2ecc71"),
            ("AGACHAR", "Seta para Baixo ou S", "#e67e22"),
            ("ATACAR", "Botao Esquerdo do Mouse", "#e74c3c"),
            ("ESPECIAL", "Botao Direito do Mouse (Custa tempo de recarga)", "#9b59b6"),
            ("INVENTARIO", "Tecla I ou E (Equipe aneis e use pocoes)", "#f1c40f"),
            ("PAUSA", "Tecla P ou Esc (Para pausar o jogo)", "#aaaaaa"),
            ("DICA DE COMBATE", "Use o pulo duplo para esquivar de projeteis", "#00d2ff"),
            ("DICA DE CHEFES", "Fique atento aos padroes de ataque vermelhos", "#ff4444"),
        ]

        self.map_nodes = [
            {'lvl': 1, 'pos': (200, 1400), 'theme': 'forest', 'name': 'BOSQUE INICIAL'},
            {'lvl': 2, 'pos': (400, 1300), 'theme': 'forest', 'name': 'TRILHA DE FOLHAS'},
            {'lvl': 3, 'pos': (600, 1200), 'theme': 'forest', 'name': 'RAIZES PROFUNDAS'},
            {'lvl': 4, 'pos': (400, 1100), 'theme': 'forest', 'is_boss': True, 'name': 'DOMINIO DO ANCIAO'},
            {'lvl': 5, 'pos': (200, 1000), 'theme': 'cave', 'name': 'ENTRADA ESCURA'},
            {'lvl': 6, 'pos': (400, 900), 'theme': 'cave', 'name': 'MINAS ABANDONADAS'},
            {'lvl': 7, 'pos': (600, 800), 'theme': 'cave', 'name': 'CAVERNA DE CRISTAIS'},
            {'lvl': 8, 'pos': (400, 700), 'theme': 'cave', 'is_boss': True, 'name': 'COVIL DO GOLIAS'},
            {'lvl': 9, 'pos': (200, 600), 'theme': 'volcano', 'name': 'FOSSO DE MAGMA'},
            {'lvl': 10, 'pos': (400, 500), 'theme': 'volcano', 'name': 'RIO DE LAVA'},
            {'lvl': 11, 'pos': (600, 400), 'theme': 'volcano', 'name': 'CRATERA ARDENTE'},
            {'lvl': 12, 'pos': (400, 300), 'theme': 'volcano', 'is_boss': True, 'name': 'TRONO DAS CINZAS'},
            {'lvl': 13, 'pos': (200, 200), 'theme': 'electric', 'name': 'NUVENS CARREGADAS'},
            {'lvl': 14, 'pos': (400, 100), 'theme': 'electric', 'name': 'PICO DOS RAIOS'},
            {'lvl': 15, 'pos': (600, 0), 'theme': 'electric', 'name': 'CEU DESPEDACADO'},
            {'lvl': 16, 'pos': (400, -100), 'theme': 'electric', 'is_boss': True, 'name': 'TEMPLO DO ARCANO'},
        ]
        
        self.global_save = {'max_level': 1, 'ranking': [], 'difficulty': 1}
        self.load_save()
        
        self.change_state('menu')

    def change_state(self, new_state):
        self.previous_state = self.state
        self.state = new_state
        if new_state in ['menu', 'ranking', 'level_select', 'how_to_play', 'victory']: play_music('menu')
        elif new_state == 'game_over': play_music('gameover')
        elif new_state == 'playing': play_music('adventure')

        if new_state == 'level_select':
            max_lvl = self.global_save.get('max_level', 1)
            node_y = 1400
            for n in self.map_nodes:
                if n['lvl'] == max_lvl:
                    node_y = n['pos'][1]
            self.target_map_scroll_y = node_y - GAME_H // 2
            self.target_map_scroll_y = max(-400, min(1200, self.target_map_scroll_y))
            self.map_scroll_y = self.target_map_scroll_y

    def get_difficulty_mult(self):
        return DIFF_LEVELS[self.global_save.get('difficulty', 1)]['mult']

    def load_save(self):
        if os.path.exists('save_data.json'):
            try:
                with open('save_data.json', 'r') as f:
                    data = json.load(f)
                    self.global_save.update(data)
            except: pass

    def save_data(self):
        try:
            with open('save_data.json', 'w') as f:
                json.dump(self.global_save, f)
        except IOError as e:
            print(f"Aviso: Permissao negada ao tentar guardar o progresso do jogo: {e}")

    def save_ranking(self, name):
        self.global_save['ranking'].append({'name': name.upper()[:10], 'score': self.player.score})
        self.global_save['ranking'].sort(key=lambda x: x['score'], reverse=True)
        self.global_save['ranking'] = self.global_save['ranking'][:5]
        self.save_data()

    def start_game(self, start_level=1):
        self.level = start_level
        self.player = Player(self, self.selected_class)
        self.setup_level()
        self.change_state('playing')
        self.menu_modal_open = False

    def setup_level(self):
        self.platforms = []; self.enemies = []; self.projectiles = []; self.loot_drops = []; self.particles = []; self.floating_texts = []; self.slashes = []; self.explosions = []; self.biome_traps = []; self.decorations = []; self.portal = None
        self.player.x, self.player.y = 200, FLOOR_Y - 100
        self.player.vx, self.player.vy = 0, 0
        self.player.air_jumps_left = 1 
        self.cam_x = 0; self.cam_y = FLOOR_Y - self.virt_h + 60
        self.max_cam_x = 0 
        
        theme_name = self.get_theme_name()
        
        self.platforms.append(Platform(-100, FLOOR_Y, 1500, 400)) 

        lx, ly = 1400, FLOOR_Y 
        
        if self.level % 4 == 0: 
            arena_w = 2000
            self.platforms.append(Platform(lx, FLOOR_Y, arena_w, 400))
            self.boss = Enemy(self, lx + 800, FLOOR_Y, theme_name, 'boss')
            self.enemies.append(self.boss)
            self.platforms.append(Platform(lx + arena_w, FLOOR_Y - 500, 500, 900)) 
        else: 
            for i in range(30): 
                
                if random.random() < 0.10:
                    gap = random.randint(100, 200)
                    w = 600
                    ly = FLOOR_Y
                    self.platforms.append(Platform(lx + gap, ly, w, 400))
                    self.loot_drops.append(LootDrop(lx + gap + w/2, ly - 30, random.choice(list(ITEM_DB.keys()))))
                    lx += gap + w
                    continue 
                
                is_gap = random.random() < 0.15 
                gap = random.randint(150, 250) if is_gap else 0
                w = random.randint(500, 1000)
                
                if is_gap:
                    ly = ly + random.choice([-50, 0, 50])
                else:
                    if random.random() < 0.4:
                        ly += random.choice([-60, -30, 30, 60])
                        
                ly = max(FLOOR_Y - 300, min(FLOOR_Y, ly))
                
                is_trap = (random.random() < 0.25 and i > 2 and w < 800)
                self.platforms.append(Platform(lx + gap, ly, w, 400, is_trap))
                
                p_x = lx + gap
                p_y = ly
                
                # ADICAO DE DECORACOES E NATUREZA
                if not is_trap and w > 100:
                    num_decorations = random.randint(0, int(w / 150) + 1)
                    for _ in range(num_decorations):
                        if theme_name == 'forest':
                            dec_type = random.choices(['tree', 'bush', 'flower'], weights=[40, 40, 20])[0]
                        elif theme_name == 'cave':
                            dec_type = random.choices(['crystal', 'mushroom', 'rock'], weights=[40, 30, 30])[0]
                        elif theme_name == 'volcano':
                            dec_type = random.choices(['dead_tree', 'rock', 'ash'], weights=[30, 50, 20])[0]
                        else:
                            dec_type = random.choices(['spire', 'plant'], weights=[60, 40])[0]
                            
                        dx = p_x + random.randint(20, int(w - 20))
                        self.decorations.append(Decoration(dx, p_y, theme_name, dec_type))

                # ADICAO DAS ARMADILHAS DE BIOMA 
                if theme_name == 'forest' and w > 100 and random.random() < 0.5:
                    self.biome_traps.append(BiomeTrap(self, p_x + random.randint(20, int(w - 60)), p_y, theme_name))
                if theme_name == 'cave' and random.random() < 0.6:
                    self.biome_traps.append(BiomeTrap(self, p_x + random.randint(20, int(w - 50)), p_y - random.randint(250, 400), theme_name, 30, 80))
                if theme_name == 'volcano' and is_gap and gap > 100:
                    self.biome_traps.append(BiomeTrap(self, lx + gap/2 - 30, FLOOR_Y + 100, theme_name, 60, 450))
                if theme_name == 'electric' and not is_trap and random.random() < 0.4:
                    self.biome_traps.append(BiomeTrap(self, p_x, p_y, theme_name, w, 20))
                
                has_hill = False
                hx, hy, hw = 0, 0, 0
                if not is_gap and w > 600 and random.random() < 0.4:
                    has_hill = True
                    hw = random.randint(200, 350)
                    hx = lx + gap + (w//2) - (hw//2)
                    hy = ly - random.choice([60, 90, 120])
                    self.platforms.append(Platform(hx, hy, hw, 400))
                
                num_enemies = 1 + int(self.level * 0.5)
                if num_enemies > 6: num_enemies = 6
                
                for j in range(num_enemies):
                    rand = random.random()
                    if rand < 0.15: e_type = 'bat'
                    elif rand < 0.30: e_type = 'archer'
                    elif rand < 0.45: e_type = 'tank'
                    elif rand < 0.60: e_type = 'jumper'
                    elif rand < 0.75: e_type = 'basic'
                    elif rand < 0.85: e_type = 'charger'
                    else: e_type = 'wizard'

                    if has_hill and random.random() < 0.5:
                        if e_type in ['archer', 'wizard']:
                            ex = random.randint(hx + 30, hx + hw - 30)
                            ey = hy - 60
                        else:
                            ex = random.randint(lx + gap + 30, lx + gap + w - 30)
                            ey = ly - 60
                    else:
                        ex = random.randint(lx + gap + 30, lx + gap + w - 30)
                        ey = ly - 60
                    
                    self.enemies.append(Enemy(self, ex, ey, theme_name, e_type))
                
                lx += gap + w
                
            self.boss = None
            self.portal = Portal(lx + 300, FLOOR_Y, theme_name)
            self.platforms.append(Platform(lx, FLOOR_Y, 600, 400))

    def get_theme_name(self):
        if self.level >= 13: return 'electric'
        if self.level >= 9: return 'volcano'
        if self.level >= 5: return 'cave'
        return 'forest'

    def spawn_particle(self, x, y, color, count, speed=1.0):
        for _ in range(count): self.particles.append(Particle(x, y, color, random.randint(3,6), speed))

    def create_shockwave(self, x, y, custom_dmg=None):
        self.spawn_particle(x, y, "#ffffff", 50, 4.0)
        self.spawn_particle(x, y, "#8e0000", 30, 2.0)
        dmg = custom_dmg if custom_dmg else int((100 + self.player.bonus_dmg)*1.5)
        for e in self.enemies:
            if not e.dead and e.get_rect().colliderect(pygame.Rect(x-250, y-200, 500, 400)):
                e.vy = -12 
                e.take_damage(dmg, True, 'melee') 

    def create_magic_explosion(self, x, y, damage):
        self.explosions.append(ExplosionSphere(x, y, max_radius=120, color="#9d50bb", life=25))
        
        self.spawn_particle(x, y, "#ff00ff", 40, 5.0)
        self.spawn_particle(x, y, "#00d2ff", 40, 5.0)
        self.spawn_particle(x, y, "#ffffff", 20, 8.0)
        self.shake = 25
        play_sfx('attack')
        
        for e in self.enemies:
            if not e.dead and math.hypot(e.x - x, e.y - y) < 180:
                e.take_damage(damage, True, 'magic')
                
        p_center_y = self.player.y - (15 if getattr(self.player, 'is_crouching', False) else 30)
        if math.hypot(self.player.x - x, p_center_y - y) < 80:
            self.player.take_damage(damage)

    def trigger_player_death(self):
        play_sfx('death')
        self.state = 'player_dying'
        self.death_timer = 150 
        self.shake = 40
        self.hitstop = 0
        
        self.explosions.append(ExplosionSphere(self.player.x, self.player.y, max_radius=250, color="#ff0000", life=40))
        self.spawn_particle(self.player.x, self.player.y, "#ff0000", 60, 6.0)
        self.spawn_particle(self.player.x, self.player.y, "#000000", 40, 5.0)
        self.slashes.append(SlashEffect(self.player.x, self.player.y, 0, size=250, color=(255, 0, 0)))
        self.slashes.append(SlashEffect(self.player.x, self.player.y, math.pi/2, size=250, color=(255, 0, 0)))
        self.slashes.append(SlashEffect(self.player.x, self.player.y, math.pi/4, size=200, color=(200, 0, 0)))
        self.slashes.append(SlashEffect(self.player.x, self.player.y, -math.pi/4, size=200, color=(200, 0, 0)))

    def boss_defeated(self, bx, by):
        self.boss = None; self.shake = 60; self.hitstop = 15 
        self.portal = Portal(bx, FLOOR_Y, self.get_theme_name(), is_boss=True)

    def end_game(self):
        self.change_state('game_over')
        self.input_text = ""

    def update(self):
        if self.state == 'player_dying':
            self.death_timer -= 1
            
            for p in self.particles: p.update()
            for e in self.explosions: e.update()
            for s in self.slashes: s.update()
            for t in self.floating_texts: t.update()
            for bt in self.biome_traps: bt.update(self.player)
            
            if self.shake > 0: self.shake -= 1
            
            target_cam_x = self.player.x - self.virt_w * 0.5 
            self.cam_x += (target_cam_x - self.cam_x) * 0.02
            
            if self.death_timer <= 0:
                self.end_game()
            return

        if self.state != 'playing': return
        
        if self.hitstop > 0:
            self.hitstop -= 1
            for p in self.particles: p.update()
            for t in self.floating_texts: t.update()
            for e in self.explosions: e.update()
            return

        current_keys = pygame.key.get_pressed()
        
        self.player.update(current_keys, self.world_mouse_pos, self.mouse_pressed)
        
        # CAMERA LIVRE (Sem bloqueio para tras)
        target_cam_x = self.player.x - self.virt_w * 0.5 
        diff_x = target_cam_x - self.cam_x
        if abs(diff_x) > 10: self.cam_x += diff_x * 0.08
        
        # Mantem apenas a barreira do absoluto inicio do nivel
        if self.cam_x < -450: self.cam_x = -450

        dist_up = FLOOR_Y - self.player.y
        target_virt_h = max(GAME_H * self.base_zoom, dist_up + 350)
        target_zoom = target_virt_h / GAME_H
        
        self.zoom += (target_zoom - self.zoom) * 0.08
        self.virt_w = int(GAME_W * self.zoom)
        self.virt_h = int(GAME_H * self.zoom)
        
        self.cam_y = FLOOR_Y - self.virt_h + 60

        if self.portal:
            self.portal.update()
            if math.hypot(self.player.x - self.portal.x, self.player.y - (self.portal.y - 50)) < 50:
                self.level += 1
                if self.level > self.global_save.get('max_level', 1):
                    self.global_save['max_level'] = min(16, self.level)
                    self.save_data()
                    
                if self.level > 16:
                    self.change_state('victory')
                else:
                    self.setup_level()
        
        power = self.player.get_power_level()

        # ATUALIZACAO DAS PLATAFORMAS (Armadilhas que caem)
        for p in self.platforms:
            p.update()
        self.platforms = [p for p in self.platforms if p.y < FLOOR_Y + 1500]
        
        # ATUALIZACAO DAS ARMADILHAS DE BIOMA
        for bt in self.biome_traps[:]:
            bt.update(self.player)
        self.biome_traps = [bt for bt in self.biome_traps if not getattr(bt, 'dead', False)]

        for e in self.enemies[:]:
            e.update(self.player)
            
            p_h = 25 if getattr(self.player, 'is_crouching', False) else 45
            player_hitbox = pygame.Rect(self.player.x - 10, self.player.y - p_h, 20, p_h)
            enemy_hitbox = e.get_rect().inflate(-24, -24) 
            
            if not e.dead and player_hitbox.colliderect(enemy_hitbox): 
                if self.player.class_id == 'warrior' and self.player.atk_timer > 50:
                    e.vx = self.player.dir * 25
                    e.vy = -14
                    e.take_damage(int((self.player.base_dmg + self.player.bonus_dmg) * 1.2), False, 'melee')
                    self.spawn_particle(self.player.x, self.player.y - 30, "#ffaa00", 10)
                    self.shake = 5
                else:
                    collision_dmg = int((12 + (self.level * 2) + (power * 1)) * self.get_difficulty_mult())
                    self.player.take_damage(collision_dmg)
                    
        self.enemies = [e for e in self.enemies if not e.dead]
        
        for p1 in self.projectiles:
            if p1.dead or p1.type != 'magic' or p1.is_enemy: continue
            for p2 in self.projectiles:
                if p2.dead or p2.type != 'magic' or not p2.is_enemy: continue
                
                if getattr(p2, 'source_enemy_type', None) in ['basic', 'jumper']: continue
                
                dist = math.hypot(p1.x - p2.x, p1.y - p2.y)
                hit_radius = (10 * p1.scale) + (10 * p2.scale)
                
                if dist < hit_radius:
                    p2.dead = True
                    if getattr(p1, 'piercing', False):
                        self.spawn_particle(p2.x, p2.y, p2.color_override or "#ff4b2b", 10, 2.0)
                        play_sfx('hit')
                    else:
                        p1.dead = True
                        exp_x = (p1.x + p2.x) / 2
                        exp_y = (p1.y + p2.y) / 2
                        exp_dmg = int(max(p1.damage, p2.damage) * 1.5)
                        self.create_magic_explosion(exp_x, exp_y, exp_dmg)
                    break
        
        for i in range(len(self.projectiles)):
            p1 = self.projectiles[i]
            if p1.dead or p1.type != 'magic' or p1.is_enemy: continue
            for j in range(i + 1, len(self.projectiles)):
                p2 = self.projectiles[j]
                if p2.dead or p2.type != 'magic' or p2.is_enemy: continue
                
                dist = math.hypot(p1.x - p2.x, p1.y - p2.y)
                hit_radius = (10 * p1.scale) + (10 * p2.scale)
                
                if dist < hit_radius:
                    p2.dead = True
                    p1.scale = min(4.5, p1.scale + p2.scale) 
                    p1.damage = int((p1.damage + p2.damage) * 1.5)
                    p1.piercing = True 
                    p1.color_override = "#ff00ff" 
                    p1.is_electric = True
                    p1.enemies_hit = {} 
                    
                    nx, ny = p1.vx + p2.vx, p1.vy + p2.vy
                    m = math.hypot(nx, ny)
                    if m > 0.1:
                        p1.vx = (nx / m) * 14
                        p1.vy = (ny / m) * 14
                    
                    self.spawn_particle(p1.x, p1.y, "#ffffff", 20, 4.0)
                    play_sfx('jump')
                    break

        for p in self.projectiles[:]:
            p.update()
            
            if not p.stuck and not p.stuck_to and p.type == 'arrow':
                for plat in self.platforms:
                    if plat.rect.collidepoint(p.x, p.y):
                        p.stuck = True
                        p.vx = 0; p.vy = 0
                        p.life = 150
                        play_sfx('hit')
                        break
                        
            if p.stuck or p.stuck_to: continue 
            
            p_rect = pygame.Rect(p.x - 8*p.scale, p.y - 8*p.scale, 16*p.scale, 16*p.scale)
            
            if p.is_enemy:
                p_h = 25 if getattr(self.player, 'is_crouching', False) else 45
                player_hitbox = pygame.Rect(self.player.x - 10, self.player.y - p_h, 20, p_h)
                if player_hitbox.colliderect(p_rect):
                    self.player.take_damage(p.damage)
                    p.dead = True
            else:
                for e in self.enemies:
                    if not e.dead and p_rect.colliderect(e.get_rect()):
                        if getattr(p, 'piercing', False):
                            if e in p.enemies_hit and p.enemies_hit[e] > 0:
                                continue 
                            
                        is_crit = getattr(p, 'is_crit', False)
                        is_electric = getattr(p, 'is_electric', False)
                        
                        e.take_damage(p.damage, is_crit, p.type, is_electric)
                        
                        if getattr(p, 'piercing', False):
                            p.enemies_hit[e] = 12 
                            self.shake = max(self.shake, 6) 
                        else:
                            if p.type == 'arrow':
                                p.stuck_to = e
                                p.stick_offset = (p.x - e.x, p.y - e.y)
                            else:
                                p.dead = True
                            break
                        
        self.projectiles = [p for p in self.projectiles if not p.dead]
        
        for l in self.loot_drops[:]:
            l.update(self.platforms)
            if self.player.get_rect().colliderect(pygame.Rect(l.x - 10, l.y - 20, 20, 20)):
                self.player.add_item(l.item_id); l.life = 0
        self.loot_drops = [l for l in self.loot_drops if l.life > 0]
        
        for p in self.particles: p.update()
        self.particles = [p for p in self.particles if p.life > 0]
        for t in self.floating_texts: t.update()
        self.floating_texts = [t for t in self.floating_texts if t.life > 0]
        for s in self.slashes: s.update()
        self.slashes = [s for s in self.slashes if s.life > 0]
        for e in self.explosions: e.update()
        self.explosions = [e for e in self.explosions if e.life > 0]
            
        if self.shake > 0: self.shake -= 1

    def draw_text_center(self, text, font, color, y, outline=True, glow=False):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(GAME_W//2, y))
        if glow:
            glow_surf = font.render(text, True, hex_to_rgb("#d4a74c"))
            glow_surf.set_alpha(80)
            for dx, dy in [(-2,-2),(2,2),(-2,2),(2,-2),(-4,0),(4,0),(0,-4),(0,4)]:
                self.game_surface.blit(glow_surf, (rect.x + dx, rect.y + dy))
        if outline:
            out_surf = font.render(text, True, (0,0,0))
            for dx, dy in [(-2,0), (2,0), (0,-2), (0,2)]: self.game_surface.blit(out_surf, (rect.x + dx, rect.y + dy))
        self.game_surface.blit(surf, rect)
        
    def draw_hud_text(self, text, font, color, x, y):
        surf = font.render(text, True, color)
        out_surf = font.render(text, True, (0,0,0))
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1), (1,1)]: self.game_surface.blit(out_surf, (x + dx, y + dy))
        self.game_surface.blit(surf, (x, y))

    def draw_premium_button(self, text, x, y, w, h, is_hover, text_color=None):
        rect = pygame.Rect(x, y, w, h)
        bg_color = hex_to_rgb("#6b4423") if is_hover else hex_to_rgb("#2a1b10")
        pygame.draw.rect(self.game_surface, bg_color, rect, border_radius=8)
        pygame.draw.rect(self.game_surface, (40, 20, 10), rect.inflate(-6, -6), border_radius=6)
        border_color = hex_to_rgb("#ffcc00") if is_hover else hex_to_rgb("#d4a74c")
        pygame.draw.rect(self.game_surface, border_color, rect, 2, border_radius=8)
        txt_color = text_color if text_color else ((255,255,255) if is_hover else hex_to_rgb("#f4e4bc"))
        surf = FONTS['small'].render(text, True, txt_color)
        if is_hover or text_color: 
            out = FONTS['small'].render(text, True, (0,0,0))
            self.game_surface.blit(out, out.get_rect(center=(rect.centerx+1, rect.centery+1)))
        self.game_surface.blit(surf, surf.get_rect(center=rect.center))
        return rect

    def draw_shadow(self, surface, obj_x, obj_y, width):
        sx, sy = int(obj_x - self.cam_x), int(obj_y - self.cam_y)
        sh_surf = pygame.Surface((width, 14), pygame.SRCALPHA)
        pygame.draw.ellipse(sh_surf, (0, 0, 0, 120), (0, 0, width, 14))
        surface.blit(sh_surf, (sx - width//2, sy - 7))

    def draw_menu(self):
        self.game_surface.fill((10, 5, 15)) 
        for i in range(12):
            mx = (i * 100) % (GAME_W + 100) - 50
            my = GAME_H - 80 + math.sin(i) * 30
            pygame.draw.ellipse(self.game_surface, (5, 2, 8), (mx, my, 150, 150))
            pygame.draw.ellipse(self.game_surface, (0, 0, 0), (mx+20, my+20, 120, 150))
        if random.random() < 0.3:
            self.menu_particles.append([random.randint(0, GAME_W), GAME_H, random.uniform(-1, 1), random.uniform(-1, -3), random.randint(2, 5)])
        for p in self.menu_particles:
            p[0] += p[2]; p[1] += p[3]
            alpha = max(0, min(255, int(p[1] / GAME_H * 255)))
            s = pygame.Surface((p[4], p[4]), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 200, 50, alpha), (p[4]//2, p[4]//2), p[4]//2)
            self.game_surface.blit(s, (int(p[0]), int(p[1])))
        self.menu_particles = [p for p in self.menu_particles if p[1] > 0]

        self.draw_text_center("A LIGA DOS HEROIS", FONTS['large'], (255, 255, 255), int(GAME_H * 0.15), glow=True)
        
        mx, my = self.mouse_pos
        c_w = 190; c_h = 70; spacing = 15
        start_x = (GAME_W - (3 * c_w + 2 * spacing)) // 2; c_y = int(GAME_H * 0.32)
        
        for i, (cid, cdef) in enumerate(CLASSES.items()):
            cx = start_x + i * (c_w + spacing)
            rect = pygame.Rect(cx, c_y, c_w, c_h)
            
            is_hover = rect.collidepoint(mx, my) and not self.menu_modal_open
            if is_hover and self.just_clicked:
                play_sfx('select'); self.selected_class = cid; self.menu_modal_open = True; self.just_clicked = False
                
            is_sel = (self.selected_class == cid)
            bg = hex_to_rgb("#2a1b10") if is_sel else (hex_to_rgb("#3a2b20") if is_hover else hex_to_rgb("#1a0f0a"))
            border = hex_to_rgb("#00d2ff") if is_sel else hex_to_rgb("#4a2f1b")
            if is_hover and not is_sel: border = hex_to_rgb("#d4a74c")
            
            pygame.draw.rect(self.game_surface, bg, rect, border_radius=10)
            pygame.draw.rect(self.game_surface, border, rect, 3, border_radius=10)
            
            if is_sel: pygame.draw.circle(self.game_surface, (200, 150, 0, 100), (cx + 35, c_y + c_h//2), 26)

            bob = math.sin(pygame.time.get_ticks() * 0.005) * 4
            draw_hero_model(self.game_surface, cx + 35, c_y + c_h//2 + 20, cid, 1, bob, 0, 0, 0, 0, scale=0.40)
            
            t_name = FONTS['small'].render(cdef['name'], True, hex_to_rgb("#d4a74c") if is_sel else (255,255,255))
            out_name = FONTS['small'].render(cdef['name'], True, (0,0,0))
            
            t_rect = t_name.get_rect(midleft=(cx + 75, c_y + c_h//2))
            o_rect = out_name.get_rect(midleft=(cx + 76, c_y + c_h//2 + 1))
            
            self.game_surface.blit(out_name, o_rect)
            self.game_surface.blit(t_name, t_rect)

        curr_diff = self.global_save.get('difficulty', 1)
        diff_info = DIFF_LEVELS[curr_diff]
        b_diff_rect = pygame.Rect(GAME_W//2 - 150, int(GAME_H * 0.50), 300, 40)
        b_start_rect = pygame.Rect(GAME_W//2 - 150, int(GAME_H * 0.60), 300, 40)
        b_help_rect = pygame.Rect(GAME_W//2 - 150, int(GAME_H * 0.70), 300, 40)
        b_rank_rect = pygame.Rect(GAME_W//2 - 150, int(GAME_H * 0.80), 300, 40)
        
        b_diff = self.draw_premium_button(f"DIFICULDADE: {diff_info['name']}", b_diff_rect.x, b_diff_rect.y, b_diff_rect.w, b_diff_rect.h, b_diff_rect.collidepoint(mx, my) and not self.menu_modal_open, hex_to_rgb(diff_info['color']))
        b_start = self.draw_premium_button("INICIAR JORNADA", b_start_rect.x, b_start_rect.y, b_start_rect.w, b_start_rect.h, b_start_rect.collidepoint(mx, my) and not self.menu_modal_open)
        b_help = self.draw_premium_button("COMO JOGAR", b_help_rect.x, b_help_rect.y, b_help_rect.w, b_help_rect.h, b_help_rect.collidepoint(mx, my) and not self.menu_modal_open)
        b_rank = self.draw_premium_button("TABUA DE GLORIA", b_rank_rect.x, b_rank_rect.y, b_rank_rect.w, b_rank_rect.h, b_rank_rect.collidepoint(mx, my) and not self.menu_modal_open)
        
        if self.just_clicked and not self.menu_modal_open:
            if b_diff.collidepoint(mx, my):
                play_sfx('select')
                self.global_save['difficulty'] = (curr_diff + 1) % len(DIFF_LEVELS)
                self.save_data()
                self.just_clicked = False
            elif b_start.collidepoint(mx, my): play_sfx('select'); self.change_state('level_select'); self.just_clicked = False
            elif b_help.collidepoint(mx, my): play_sfx('select'); self.change_state('how_to_play'); self.just_clicked = False
            elif b_rank.collidepoint(mx, my): play_sfx('select'); self.change_state('ranking'); self.just_clicked = False

        if self.menu_modal_open:
            small_surf = pygame.transform.smoothscale(self.game_surface, (GAME_W//8, GAME_H//8))
            blur_surf = pygame.transform.smoothscale(small_surf, (GAME_W, GAME_H))
            self.game_surface.blit(blur_surf, (0, 0))
            
            dark = pygame.Surface((GAME_W, GAME_H), pygame.SRCALPHA)
            dark.fill((0, 0, 0, 180))
            self.game_surface.blit(dark, (0, 0))
            
            card_w, card_h = 440, 280
            card_x, card_y = (GAME_W - card_w)//2, (GAME_H - card_h)//2
            card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
            
            pygame.draw.rect(self.game_surface, hex_to_rgb("#111111"), card_rect, border_radius=15)
            pygame.draw.rect(self.game_surface, hex_to_rgb("#00d2ff"), card_rect.inflate(4, 4), 2, border_radius=16)
            pygame.draw.rect(self.game_surface, hex_to_rgb("#d4a74c"), card_rect, 4, border_radius=15)
            
            cdef = CLASSES[self.selected_class]
            
            t_title = FONTS['medium'].render(f"~ {cdef['name']} ~", True, hex_to_rgb("#d4a74c"))
            self.game_surface.blit(t_title, t_title.get_rect(center=(GAME_W//2, card_y + 30)))
            pygame.draw.line(self.game_surface, hex_to_rgb("#4a2f1b"), (card_x + 50, card_y + 50), (card_x + card_w - 50, card_y + 50), 2)
            
            pygame.draw.circle(self.game_surface, (40, 40, 40), (card_x + 100, card_y + 140), 60)
            bob = math.sin(pygame.time.get_ticks() * 0.005) * 5
            
            draw_hero_model(self.game_surface, card_x + 100, card_y + 180, self.selected_class, 1, bob, 0, 0, 0, 0, scale=0.8)
            
            stat_y = card_y + 70; line_h = 28
            stats = [(f"VIDA : {cdef['hp']}", "#2ecc71"), (f"FORCA: {cdef['dmg']}", "#e74c3c"), (f"AGIL.: {cdef['speed']}", "#3498db"), (f"PULO : {abs(cdef['jump'])}", "#f1c40f")]
            for j, (text, color) in enumerate(stats):
                pygame.draw.rect(self.game_surface, (25, 25, 25) if j%2==0 else (20, 20, 20), (card_x + 190, stat_y + (j * line_h) - 4, 220, line_h))
                lbl_surf = FONTS['small'].render(text, True, hex_to_rgb(color))
                self.game_surface.blit(lbl_surf, (card_x + 200, stat_y + (j * line_h)))
                
            ult_rect = pygame.Rect(card_x + 185, stat_y + (4 * line_h) + 6, 230, 30)
            pygame.draw.rect(self.game_surface, (30, 20, 40), ult_rect, border_radius=4)
            sp_txt = FONTS['tiny'].render(f"ULT: {cdef['sp_name']}", True, hex_to_rgb(cdef['sp_color']))
            self.game_surface.blit(sp_txt, sp_txt.get_rect(center=ult_rect.center))

            b_close = self.draw_premium_button("CONFIRMAR", GAME_W//2 - 100, card_y + card_h - 20, 200, 40, pygame.Rect(GAME_W//2 - 100, card_y + card_h - 20, 200, 40).collidepoint(mx, my))
            if self.just_clicked and (b_close.collidepoint(mx, my) or not card_rect.collidepoint(mx, my)):
                play_sfx('select'); self.menu_modal_open = False; self.just_clicked = False

    def draw_how_to_play(self):
        s = pygame.Surface((GAME_W, GAME_H), pygame.SRCALPHA)
        s.fill((20, 10, 15, 240))
        self.game_surface.blit(s, (0,0))
        
        self.draw_text_center("COMO JOGAR", FONTS['large'], hex_to_rgb("#d4a74c"), int(GAME_H * 0.15), glow=True)
        
        self.how_to_play_scroll += (self.target_how_to_play_scroll - self.how_to_play_scroll) * 0.15
        scroll = int(self.how_to_play_scroll)
        
        clip_rect = pygame.Rect(0, int(GAME_H * 0.25), GAME_W, int(GAME_H * 0.55))
        self.game_surface.set_clip(clip_rect)
        
        start_y = int(GAME_H * 0.28) - scroll
        for i, (title, desc, color) in enumerate(self.instructions):
            y = start_y + i * 45
            self.draw_hud_text(title + ":", FONTS['small'], hex_to_rgb(color), GAME_W//2 - 350, y)
            self.draw_hud_text(desc, FONTS['small'], (220, 220, 220), GAME_W//2 - 100, y)
            
        self.game_surface.set_clip(None)
        
        max_scroll = max(1, len(self.instructions) * 45 - int(GAME_H * 0.5))
        scroll_pct = min(1.0, max(0.0, scroll / max_scroll))
        bar_y = int(GAME_H * 0.25) + int(scroll_pct * (int(GAME_H * 0.55) - 40))
        pygame.draw.rect(self.game_surface, (50, 50, 50), (GAME_W - 30, int(GAME_H * 0.25), 10, int(GAME_H * 0.55)), border_radius=5)
        pygame.draw.rect(self.game_surface, hex_to_rgb("#d4a74c"), (GAME_W - 30, bar_y, 10, 40), border_radius=5)
        
        mx, my = self.mouse_pos
        b_back = self.draw_premium_button("VOLTAR AO MENU", GAME_W//2 - 150, int(GAME_H * 0.85), 300, 45, pygame.Rect(GAME_W//2 - 150, int(GAME_H * 0.85), 300, 45).collidepoint(mx, my))
        if self.just_clicked and b_back.collidepoint(mx, my):
            play_sfx('select')
            self.change_state('menu')
            self.just_clicked = False

    def draw_level_select(self):
        self.game_surface.fill((15, 15, 18)) 
        
        self.map_scroll_y += (self.target_map_scroll_y - self.map_scroll_y) * 0.15
        scroll = int(self.map_scroll_y)
        
        def draw_bg_layer(color, top_y, bottom_y):
            sy1 = top_y - scroll
            sy2 = bottom_y - scroll
            if sy2 > 0 and sy1 < GAME_H:
                pygame.draw.rect(self.game_surface, hex_to_rgb(color), (0, sy1, GAME_W, sy2 - sy1))

        draw_bg_layer('#0a1a12', 1050, 1600) 
        draw_bg_layer('#150a1f', 650, 1050) 
        draw_bg_layer('#2a0a0a', 250, 650) 
        draw_bg_layer('#050a1a', -400, 250) 

        t = pygame.time.get_ticks() * 0.001
        
        for i in range(20):
            fx = (math.sin(i * 12.3) * 350 + 400)
            fy = (1050 + (i * 25)) - scroll + math.sin(t+i)*10
            if 0 < fy < GAME_H:
                pygame.draw.circle(self.game_surface, hex_to_rgb('#1c3b2b'), (int(fx), int(fy)), 12)
                pygame.draw.circle(self.game_surface, hex_to_rgb('#2d4c1e'), (int(fx+5), int(fy)), 8)

            cx = (math.sin(i * 7.7) * 350 + 400)
            cy = (650 + (i * 20)) - scroll
            if 0 < cy < GAME_H:
                pygame.draw.polygon(self.game_surface, hex_to_rgb('#4a3a5e'), [(cx, cy-20), (cx-15, cy+10), (cx+15, cy+10)])
                pygame.draw.polygon(self.game_surface, hex_to_rgb('#9d50bb'), [(cx, cy-15), (cx-8, cy+10), (cx+8, cy+10)])

            vx = (math.sin(i * 3.1) * 350 + 400)
            vy = (250 + (i * 20)) - scroll
            if 0 < vy < GAME_H:
                pygame.draw.ellipse(self.game_surface, hex_to_rgb('#3a0f0f'), (vx-30, vy-15, 60, 30))
                pygame.draw.ellipse(self.game_surface, hex_to_rgb('#8b2a2a'), (vx-20, vy-10, 40, 20))

            ex = (math.sin(i * 9.9) * 350 + 400)
            ey = (-300 + (i * 25)) - scroll
            if 0 < ey < GAME_H:
                lx = ex + math.sin(t*10+i)*10
                pygame.draw.line(self.game_surface, hex_to_rgb('#00d2ff'), (ex, ey-15), (lx, ey), 3)
                pygame.draw.line(self.game_surface, hex_to_rgb('#ffffff'), (lx, ey), (ex-5, ey+15), 3)
        
        mx, my = self.mouse_pos
        max_lvl = self.global_save.get('max_level', 1)
        
        for i in range(len(self.map_nodes) - 1):
            n1, n2 = self.map_nodes[i], self.map_nodes[i+1]
            color = (80, 80, 80)
            if n1['lvl'] < max_lvl:
                color = hex_to_rgb(THEMES[n1['theme']]['border'] if 'border' in THEMES[n1['theme']] else THEMES[n1['theme']]['hazard'])
            p1 = (n1['pos'][0], n1['pos'][1] - scroll)
            p2 = (n2['pos'][0], n2['pos'][1] - scroll)
            pygame.draw.line(self.game_surface, color, p1, p2, 4)

        hovered_node = None

        for node in self.map_nodes:
            cx = node['pos'][0]
            cy = node['pos'][1] - scroll
            is_unlocked = node['lvl'] <= max_lvl
            is_hover = is_unlocked and math.hypot(mx - cx, my - cy) < 25
            
            if is_hover: 
                hovered_node = node
                if self.just_clicked:
                    play_sfx('select')
                    self.start_game(node['lvl'])
                    self.just_clicked = False

            node_color = hex_to_rgb(THEMES[node['theme']]['hazard']) if is_unlocked else (50, 50, 50)
            border_color = (255, 255, 255) if is_hover else ((100, 100, 100) if not is_unlocked else hex_to_rgb(THEMES[node['theme']]['plat_top']))
            
            radius = 20 if not node.get('is_boss') else 32
            if is_hover: radius += 5
            
            if node.get('is_boss'):
                for ang_i in range(8):
                    a = math.radians(ang_i * 45 + pygame.time.get_ticks() * 0.05)
                    sx = cx + math.cos(a) * (radius + 6)
                    sy = cy + math.sin(a) * (radius + 6)
                    pygame.draw.circle(self.game_surface, hex_to_rgb("#ff2222") if is_unlocked else (80,80,80), (int(sx), int(sy)), 6)
            
            pygame.draw.circle(self.game_surface, (0,0,0,120), (cx+3, cy+3), radius) 
            pygame.draw.circle(self.game_surface, node_color, (cx, cy), radius)
            pygame.draw.circle(self.game_surface, border_color, (cx, cy), radius, 3)
            
            lbl = FONTS['small'].render(str(node['lvl']), True, (255,255,255) if is_unlocked else (100,100,100))
            self.game_surface.blit(lbl, lbl.get_rect(center=(cx, cy)))

        self.draw_text_center("MAPA DOS REINOS", FONTS['large'], hex_to_rgb("#d4a74c"), int(GAME_H * 0.08), glow=True)
        self.draw_text_center("ESCOLHA O SEU DESTINO", FONTS['small'], (200,200,200), int(GAME_H * 0.15))

        if hovered_node:
            rx, ry = hovered_node['pos'][0], hovered_node['pos'][1] - scroll
            panel_w, panel_h = 260, 90
            
            px, py = mx + 20, my + 20
            if px + panel_w > GAME_W: px = mx - panel_w - 20
            if py + panel_h > GAME_H: py = my - panel_h - 20
            if px < 0: px = 10
            if py < 0: py = 10

            p_rect = pygame.Rect(px, py, panel_w, panel_h)
            pygame.draw.rect(self.game_surface, (15, 10, 15), p_rect, border_radius=8)
            pygame.draw.rect(self.game_surface, hex_to_rgb(THEMES[hovered_node['theme']]['hazard']), p_rect, 2, border_radius=8)

            t_name = FONTS['small'].render(hovered_node['name'], True, hex_to_rgb("#d4a74c"))
            t_desc = FONTS['tiny'].render(f"Nivel {hovered_node['lvl']} ({THEMES[hovered_node['theme']]['name']})", True, (200, 200, 200))
            
            self.game_surface.blit(t_name, (px + 15, py + 20))
            self.game_surface.blit(t_desc, (px + 15, py + 50))
            
            if hovered_node.get('is_boss'):
                t_boss = FONTS['tiny'].render(f"Chefe: {THEMES[hovered_node['theme']]['boss_name']}", True, hex_to_rgb("#ff7777"))
                self.game_surface.blit(t_boss, (px + 15, py + 70))

        b_back_y = int(GAME_H * 0.85)
        if b_back_y + 45 > GAME_H: b_back_y = GAME_H - 55

        b_back = self.draw_premium_button("VOLTAR AO MENU", GAME_W//2 - 150, b_back_y, 300, 45, pygame.Rect(GAME_W//2 - 150, b_back_y, 300, 45).collidepoint(mx, my))
        if self.just_clicked and b_back.collidepoint(mx, my):
            play_sfx('select')
            self.change_state('menu')
            self.just_clicked = False

    def draw_pause(self):
        self.draw_playing() 
        s = pygame.Surface((GAME_W, GAME_H), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        self.game_surface.blit(s, (0, 0))
        self.draw_text_center("PAUSA", FONTS['large'], hex_to_rgb("#d4a74c"), int(GAME_H * 0.25))

        mx, my = self.mouse_pos
        b_res = self.draw_premium_button("CONTINUAR", GAME_W//2 - 175, int(GAME_H * 0.4), 350, 45, pygame.Rect(GAME_W//2 - 175, int(GAME_H * 0.4), 350, 45).collidepoint(mx, my))
        b_rst = self.draw_premium_button("REINICIAR JOGO", GAME_W//2 - 175, int(GAME_H * 0.55), 350, 45, pygame.Rect(GAME_W//2 - 175, int(GAME_H * 0.55), 350, 45).collidepoint(mx, my))
        b_rnk = self.draw_premium_button("TABUA DE GLORIA", GAME_W//2 - 175, int(GAME_H * 0.7), 350, 45, pygame.Rect(GAME_W//2 - 175, int(GAME_H * 0.7), 350, 45).collidepoint(mx, my))
        b_mnu = self.draw_premium_button("MENU PRINCIPAL", GAME_W//2 - 175, int(GAME_H * 0.85), 350, 45, pygame.Rect(GAME_W//2 - 175, int(GAME_H * 0.85), 350, 45).collidepoint(mx, my))

        if self.just_clicked:
            if b_res.collidepoint(mx, my): play_sfx('select'); self.state = 'playing'; self.just_clicked = False
            elif b_rst.collidepoint(mx, my): play_sfx('select'); self.start_game(); self.just_clicked = False
            elif b_rnk.collidepoint(mx, my): play_sfx('select'); self.change_state('ranking'); self.just_clicked = False
            elif b_mnu.collidepoint(mx, my): play_sfx('select'); self.change_state('menu'); self.just_clicked = False

    def draw_inventory(self):
        s = pygame.Surface((GAME_W, GAME_H), pygame.SRCALPHA)
        s.fill((26, 15, 10, 240))
        self.game_surface.blit(s, (0,0))
        
        self.draw_text_center("MOCHILA DO HEROI", FONTS['large'], hex_to_rgb("#d4a74c"), int(GAME_H * 0.15))
        pygame.draw.rect(self.game_surface, (17,17,17), (GAME_W//2 - 200, int(GAME_H * 0.25), 400, 90), border_radius=10)
        pygame.draw.rect(self.game_surface, hex_to_rgb("#4a2f1b"), (GAME_W//2 - 200, int(GAME_H * 0.25), 400, 90), 4, border_radius=10)
        
        self.draw_text_center("ARMA", FONTS['tiny'], hex_to_rgb("#00d2ff"), int(GAME_H * 0.25) + 20)
        icon_w = CLASSES[self.player.class_id]['icon']
        t_w = FONTS['medium'].render(icon_w, True, (255,255,255))
        self.game_surface.blit(t_w, t_w.get_rect(center=(GAME_W//2 - 100, int(GAME_H * 0.25) + 50)))
        
        self.draw_text_center("ANEL EQUIPADO", FONTS['tiny'], hex_to_rgb("#00d2ff"), int(GAME_H * 0.25) + 20)
        r_txt = "VAZIO"; r_color = (255,255,255)
        if self.player.equipment['ring']:
            r_txt = ITEM_DB[self.player.equipment['ring']]['icon']
            r_color = hex_to_rgb(ITEM_DB[self.player.equipment['ring']]['color'])
        t_r = FONTS['medium'].render(r_txt, True, r_color)
        self.game_surface.blit(t_r, t_r.get_rect(center=(GAME_W//2 + 100, int(GAME_H * 0.25) + 50)))

        slot_s, gap = 50, 10
        start_x = GAME_W//2 - (5 * slot_s + 4 * gap) // 2
        start_y = int(GAME_H * 0.5)
        mx, my = self.mouse_pos
        tooltip = "MODO LIXEIRA: Selecione um item para o destruir!" if self.trash_mode else "Selecione um item magico..."
        
        for i in range(10):
            row = i // 5; col = i % 5
            x = start_x + col * (slot_s + gap); y = start_y + row * (slot_s + gap)
            rect = pygame.Rect(x, y, slot_s, slot_s)
            
            is_hover = rect.collidepoint(mx, my)
            if self.trash_mode:
                color = hex_to_rgb("#551111") if is_hover else hex_to_rgb("#222222")
                border = hex_to_rgb("#ff0000") if is_hover else hex_to_rgb("#555555")
            else:
                color = hex_to_rgb("#333333") if is_hover else hex_to_rgb("#222222")
                border = hex_to_rgb("#d4a74c") if is_hover else hex_to_rgb("#555555")
            
            pygame.draw.rect(self.game_surface, color, rect, border_radius=8)
            pygame.draw.rect(self.game_surface, border, rect, 3, border_radius=8)
            
            if i < len(self.player.inventory):
                item = ITEM_DB[self.player.inventory[i]]
                if is_hover:
                    tooltip = f"DESCARTAR: {item['name']} (Ira perder o item)" if self.trash_mode else f"{item['name']} - {item['desc']}"
                    if self.just_clicked:
                        if self.trash_mode:
                            play_sfx('delete'); self.player.inventory.pop(i)
                            self.floating_texts.append(FloatingText(self.player.x, self.player.y - 70, "- Item Destruido", "#ff0000"))
                        else:
                            play_sfx('select'); self.player.use_item(i)
                        self.just_clicked = False
                
                t_i = FONTS['small'].render(item['icon'], True, hex_to_rgb(item['color']))
                self.game_surface.blit(t_i, t_i.get_rect(center=rect.center))
                
        if self.trash_mode: self.draw_text_center(tooltip, FONTS['small'], hex_to_rgb("#ff4444"), int(GAME_H * 0.78), False)
        else: self.draw_text_center(tooltip, FONTS['small'], (170,170,170), int(GAME_H * 0.78), False)
        
        b_back = self.draw_premium_button("FECHAR [I]", GAME_W//2 - 200, int(GAME_H * 0.88), 240, 40, pygame.Rect(GAME_W//2 - 200, int(GAME_H * 0.88), 240, 40).collidepoint(mx, my))
        if self.just_clicked and b_back.collidepoint(mx, my):
            play_sfx('select'); self.state = 'playing'; self.trash_mode = False; self.just_clicked = False
            
        b_trash_rect = pygame.Rect(GAME_W//2 + 60, int(GAME_H * 0.88), 140, 40)
        is_trash_hover = b_trash_rect.collidepoint(mx, my)
        if is_trash_hover and self.just_clicked:
            play_sfx('select'); self.trash_mode = not self.trash_mode; self.just_clicked = False
            
        bg_trash = hex_to_rgb("#8b0000") if self.trash_mode else (hex_to_rgb("#5c2a2a") if is_trash_hover else hex_to_rgb("#2a1b10"))
        pygame.draw.rect(self.game_surface, bg_trash, b_trash_rect, border_radius=8)
        pygame.draw.rect(self.game_surface, hex_to_rgb("#ff0000") if self.trash_mode else hex_to_rgb("#4a2f1b"), b_trash_rect, 4, border_radius=8)
        surf_trash = FONTS['small'].render("LIXEIRA", True, (255,255,255))
        self.game_surface.blit(surf_trash, surf_trash.get_rect(center=b_trash_rect.center))

    def draw_game_over(self):
        s = pygame.Surface((GAME_W, GAME_H), pygame.SRCALPHA)
        s.fill((30, 5, 5, 220))
        self.game_surface.blit(s, (0,0))
        
        self.draw_text_center("VOCÊ MORREU", FONTS['large'], hex_to_rgb("#ff2222"), int(GAME_H * 0.20), glow=True)
        self.draw_text_center("A SUA JORNADA TERMINA AQUI...", FONTS['small'], hex_to_rgb("#888888"), int(GAME_H * 0.28))
        
        box_rect = pygame.Rect(GAME_W//2 - 200, int(GAME_H * 0.38), 400, 50)
        pygame.draw.rect(self.game_surface, hex_to_rgb("#1a0f0a"), box_rect, border_radius=8)
        pygame.draw.rect(self.game_surface, hex_to_rgb("#d4a74c"), box_rect, 2, border_radius=8)
        
        stats_txt = f"OURO: {self.player.score}  |  NIVEL: {self.player.level}"
        self.draw_text_center(stats_txt, FONTS['small'], hex_to_rgb("#f4e4bc"), int(GAME_H * 0.38) + 25, outline=False)
        
        self.draw_text_center("GRAVE O SEU NOME NAS LENDAS:", FONTS['tiny'], hex_to_rgb("#aaaaaa"), int(GAME_H * 0.55))
        
        rect = pygame.Rect(GAME_W//2 - 120, int(GAME_H * 0.60), 240, 40)
        pygame.draw.rect(self.game_surface, hex_to_rgb("#000000"), rect, border_radius=5)
        pygame.draw.rect(self.game_surface, hex_to_rgb("#ff0000"), rect, 2, border_radius=5)
        
        cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 else " "
        t = FONTS['small'].render(self.input_text + cursor, True, hex_to_rgb("#ffffff"))
        self.game_surface.blit(t, t.get_rect(center=rect.center))
        
        mx, my = self.mouse_pos
        btn_y = int(GAME_H * 0.75)
        btn_rect = pygame.Rect(GAME_W//2 - 140, btn_y, 280, 40)
        b_save = self.draw_premium_button("ACEITAR DESTINO", btn_rect.x, btn_rect.y, btn_rect.w, btn_rect.h, btn_rect.collidepoint(mx, my))
        
        if self.just_clicked and b_save.collidepoint(mx, my):
            play_sfx('confirm')
            name = self.input_text if self.input_text else "HERÓI"
            self.save_ranking(name); self.change_state('menu'); self.just_clicked = False

    def draw_victory(self):
        s = pygame.Surface((GAME_W, GAME_H), pygame.SRCALPHA)
        s.fill((15, 30, 15, 240))
        self.game_surface.blit(s, (0,0))
        
        self.draw_text_center("VITÓRIA GLORIOSA!", FONTS['large'], hex_to_rgb("#ffcc00"), int(GAME_H * 0.20), glow=True)
        self.draw_text_center("O MAL FOI DESTRUÍDO E OS REINOS ESTÃO SALVOS.", FONTS['small'], (220, 220, 220), int(GAME_H * 0.28))
        
        box_rect = pygame.Rect(GAME_W//2 - 200, int(GAME_H * 0.38), 400, 50)
        pygame.draw.rect(self.game_surface, hex_to_rgb("#0a1a0f"), box_rect, border_radius=8)
        pygame.draw.rect(self.game_surface, hex_to_rgb("#2ecc71"), box_rect, 2, border_radius=8)
        
        stats_txt = f"OURO ACUMULADO: {self.player.score}  |  NIVEL FINAL: {self.player.level}"
        self.draw_text_center(stats_txt, FONTS['small'], hex_to_rgb("#f4e4bc"), int(GAME_H * 0.38) + 25, outline=False)
        
        self.draw_text_center("GRAVE O SEU NOME COMO O GRANDE CAMPEAO:", FONTS['tiny'], hex_to_rgb("#aaaaaa"), int(GAME_H * 0.55))
        
        rect = pygame.Rect(GAME_W//2 - 120, int(GAME_H * 0.60), 240, 40)
        pygame.draw.rect(self.game_surface, hex_to_rgb("#000000"), rect, border_radius=5)
        pygame.draw.rect(self.game_surface, hex_to_rgb("#ffcc00"), rect, 2, border_radius=5)
        
        cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 else " "
        t = FONTS['small'].render(self.input_text + cursor, True, hex_to_rgb("#ffffff"))
        self.game_surface.blit(t, t.get_rect(center=rect.center))
        
        mx, my = self.mouse_pos
        btn_y = int(GAME_H * 0.75)
        btn_rect = pygame.Rect(GAME_W//2 - 140, btn_y, 280, 40)
        b_save = self.draw_premium_button("REGISTRAR LENDA", btn_rect.x, btn_rect.y, btn_rect.w, btn_rect.h, btn_rect.collidepoint(mx, my))
        
        if self.just_clicked and b_save.collidepoint(mx, my):
            play_sfx('confirm')
            name = self.input_text if self.input_text else "HERÓI"
            self.save_ranking(name); self.change_state('menu'); self.just_clicked = False

    def draw_ranking(self):
        s = pygame.Surface((GAME_W, GAME_H), pygame.SRCALPHA)
        s.fill((26, 15, 10, 255))
        self.game_surface.blit(s, (0,0))
        
        self.draw_text_center("TÁBUA DE GLÓRIA", FONTS['large'], hex_to_rgb("#d4a74c"), int(GAME_H * 0.15))
        
        y = int(GAME_H * 0.3)
        if not self.global_save['ranking']: self.draw_text_center("NENHUMA LENDA REGISTRADA.", FONTS['small'], (255,255,255), y)
        else:
            for i, r in enumerate(self.global_save['ranking']):
                txt = f"{i+1}. {r['name']} - {r['score']} pts"
                self.draw_text_center(txt, FONTS['medium'], (255,255,255), y)
                y += 40
                
        mx, my = self.mouse_pos
        b_back = self.draw_premium_button("VOLTAR", GAME_W//2 - 175, int(GAME_H * 0.8), 350, 45, pygame.Rect(GAME_W//2 - 175, int(GAME_H * 0.8), 350, 45).collidepoint(mx, my))
        if self.just_clicked and b_back.collidepoint(mx, my):
            play_sfx('select')
            self.change_state(getattr(self, 'previous_state', 'menu'))
            self.just_clicked = False

    def draw_playing(self):
        theme = THEMES[self.get_theme_name()]
        theme_idx = self.get_theme_name()
        
        if self.world_surface.get_width() != self.virt_w or self.world_surface.get_height() != self.virt_h:
            self.world_surface = pygame.Surface((self.virt_w, self.virt_h))

        bg_img = IMAGES.get(f'bg_{theme_idx}')
        if bg_img:
            ratio = self.virt_h / bg_img.get_height()
            bg_w = int(bg_img.get_width() * ratio)
            scaled_bg = pygame.transform.smoothscale(bg_img, (bg_w, self.virt_h))
            parallax_x = (self.cam_x * 0.2) % bg_w
            self.world_surface.blit(scaled_bg, (-parallax_x, 0))
            if parallax_x > 0:
                self.world_surface.blit(scaled_bg, (-parallax_x + bg_w, 0))
        else:
            c1 = hex_to_rgb(theme['bg_top'])
            c2 = hex_to_rgb(theme['bg_bot'])
            grad_steps = 20
            h_step = self.virt_h / grad_steps
            for i in range(grad_steps):
                r = c1[0] + (c2[0] - c1[0]) * i // grad_steps
                g = c1[1] + (c2[1] - c1[1]) * i // grad_steps
                b = c1[2] + (c2[2] - c1[2]) * i // grad_steps
                pygame.draw.rect(self.world_surface, (r,g,b), (0, int(i*h_step), self.virt_w, math.ceil(h_step)))

            if theme_idx in ['forest', 'cave']: pygame.draw.circle(self.world_surface, (255, 255, 240, 150), (int(self.virt_w*0.8), int(self.virt_h*0.2)), 40)
            else: pygame.draw.circle(self.world_surface, (255, 100, 50, 150), (int(self.virt_w*0.8), int(self.virt_h*0.2)), 60)

            bg_bot = hex_to_rgb(theme['bg_bot'])
            l1_col = (max(0, bg_bot[0]-10), max(0, bg_bot[1]-10), max(0, bg_bot[2]-10))
            for i in range(-2, int(self.virt_w/300) + 3):
                bx = (i * 300) - (self.cam_x * 0.1) % 300
                pygame.draw.polygon(self.world_surface, l1_col, [(bx, self.virt_h), (bx+150, self.virt_h-250), (bx+300, self.virt_h)])
                
            l2_col = (max(0, bg_bot[0]-25), max(0, bg_bot[1]-25), max(0, bg_bot[2]-25))
            for i in range(-2, int(self.virt_w/200) + 3):
                bx = (i * 200) - (self.cam_x * 0.25) % 200
                if theme_idx in ['forest', 'electric']: pygame.draw.polygon(self.world_surface, l2_col, [(bx+80, self.virt_h), (bx+100, self.virt_h-180), (bx+120, self.virt_h)])
                else: pygame.draw.ellipse(self.world_surface, l2_col, (bx, self.virt_h-120, 200, 240))
        
        t = pygame.time.get_ticks() / 1000.0
        haz_col = hex_to_rgb(theme['hazard'])
        for i in range(35):
            px = (math.sin(t + i) * 50 + i * (self.virt_w / 35) - self.cam_x * 0.5) % self.virt_w
            py = (math.cos(t * 0.8 + i*2) * 50 + i * (self.virt_h / 35) + (t * 15 * (1 if i%2==0 else -1))) % self.virt_h
            size = 2 if i%3 == 0 else 4
            s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            alpha = int(100 + math.sin(t*3 + i)*50)
            pygame.draw.circle(s, (*haz_col, alpha), (size, size), size)
            self.world_surface.blit(s, (px, py))

        surf = pygame.Surface((self.virt_w, self.virt_h), pygame.SRCALPHA)
        
        if self.portal: self.portal.draw(surf, self.cam_x, self.cam_y)

        # DESENHA DECORACOES (Atras das plataformas e jogadores)
        for dec in getattr(self, 'decorations', []):
            dec.draw(surf, self.cam_x, self.cam_y)

        plat_img = IMAGES.get(f'plat_{theme_idx}')
        
        for p in self.platforms:
            r = pygame.Rect(int(p.x - self.cam_x), int(p.y - self.cam_y), p.w, p.h)
            
            if plat_img:
                surf.set_clip(r)
                img_w = plat_img.get_width()
                img_h = plat_img.get_height()
                for tile_x in range(r.x, r.x + r.w, img_w):
                    for tile_y in range(r.y, r.y + r.h, img_h):
                        surf.blit(plat_img, (tile_x, tile_y))
                surf.set_clip(None)
                pygame.draw.rect(surf, (0,0,0), r, 2, border_radius=6)
            else:
                base_col = hex_to_rgb(theme['plat_base'])
                top_col = hex_to_rgb(theme['plat_top'])
                pygame.draw.rect(surf, base_col, r, border_radius=8)
                dark_col = (max(0, base_col[0]-15), max(0, base_col[1]-15), max(0, base_col[2]-15))
                pygame.draw.rect(surf, dark_col, (r.x, r.y + 35, r.w, r.h - 35), border_radius=8)
                pygame.draw.line(surf, (0,0,0), (r.x, r.y + 35), (r.x + r.w, r.y + 35), 2)
                pygame.draw.rect(surf, top_col, (r.x, r.y, r.w, 20), border_radius=8)
                hi_col = (min(255, top_col[0]+40), min(255, top_col[1]+40), min(255, top_col[2]+40))
                pygame.draw.rect(surf, hi_col, (r.x+2, r.y+2, r.w-4, 4), border_radius=4)
                sh_col = (max(0, dark_col[0]-25), max(0, dark_col[1]-25), max(0, dark_col[2]-25))
                pygame.draw.rect(surf, sh_col, (r.x+2, r.y+r.h-10, r.w-4, 8), border_radius=4)
                pygame.draw.rect(surf, (0,0,0), r, 3, border_radius=8)

        # DESENHA ARMADILHAS DE BIOMA
        for bt in self.biome_traps:
            bt.draw(surf, self.cam_x, self.cam_y)

        for l in self.loot_drops: 
            if l.vy == 0: self.draw_shadow(surf, l.x, l.y, 25)
            l.draw(surf, self.cam_x, self.cam_y)
            
        for e in self.enemies: 
            if e.on_ground: self.draw_shadow(surf, e.x, e.y, e.w + 10)
            e.draw(surf, self.cam_x, self.cam_y)
            
        for p in self.projectiles:
            if p.is_enemy: p.draw(surf, self.cam_x, self.cam_y)
            
        if self.player: 
            if self.player.on_ground: self.draw_shadow(surf, self.player.x, self.player.y, 45)
            self.player.draw(surf, self.cam_x, self.cam_y, self.world_mouse_pos)

        for p in self.projectiles:
            if not p.is_enemy: p.draw(surf, self.cam_x, self.cam_y)
            
        for s in self.slashes: s.draw(surf, self.cam_x, self.cam_y)
        for p in self.particles: p.draw(surf, self.cam_x, self.cam_y)
        for e in self.explosions: e.draw(surf, self.cam_x, self.cam_y)
            
        for t in self.floating_texts: t.draw(surf, self.cam_x, self.cam_y)

        sx, sy = 0, 0
        if self.shake > 0: sx = (random.random() - 0.5) * self.shake; sy = (random.random() - 0.5) * self.shake

        self.world_surface.blit(surf, (0, 0))
        
        if self.state == 'player_dying':
            darkness = pygame.Surface((self.virt_w, self.virt_h), pygame.SRCALPHA)
            alpha = min(220, 255 - int((self.death_timer / 150) * 255))
            darkness.fill((80, 0, 0, alpha)) 
            self.world_surface.blit(darkness, (0, 0))
            
        scaled_world = pygame.transform.smoothscale(self.world_surface, (GAME_W, GAME_H))
        self.game_surface.blit(scaled_world, (sx, sy))

        if self.boss and not self.boss.dead:
            self.draw_hud_text(f"{theme['boss_name']} (HP: {self.boss.hp}/{self.boss.max_hp})", FONTS['medium'], hex_to_rgb(theme['hazard']), 15, 15)

        self.draw_hud_text(f"HP: {self.player.hp}/{self.player.max_hp}", FONTS['medium'], hex_to_rgb("#e74c3c"), 15, 45 if self.boss and not self.boss.dead else 15)
        xp_pct = int((self.player.xp / self.player.xp_next) * 100)
        self.draw_hud_text(f"XP: {xp_pct}%", FONTS['small'], hex_to_rgb("#3498db"), 15, 75 if self.boss and not self.boss.dead else 45)
        stat_txt = f"OURO: {self.player.score:05d} | NIVEL: {self.player.level:02d} | DANO: {self.player.base_dmg + self.player.bonus_dmg}"
        self.draw_hud_text(stat_txt, FONTS['small'], hex_to_rgb("#f1c40f"), 15, 95 if self.boss and not self.boss.dead else 65)
        
        sp_pct = 1.0 - (self.player.sp_timer / self.player.sp_cooldown)
        
        if getattr(self.player, 'active_ultimate', None) and not self.player.active_ultimate.dead:
            sp_status = "EM USO..."
            sp_color = "#00d2ff"
        else:
            sp_status = "PRONTO! (Botao Dir)" if sp_pct >= 1.0 else f"RECARREGANDO... {int(sp_pct*100)}%"
            sp_color = self.player.cdef['sp_color'] if sp_pct >= 1.0 else "#888888"
            
        self.draw_hud_text(f"ULTIMATE: {sp_status}", FONTS['small'], hex_to_rgb(sp_color), 15, 115 if self.boss and not self.boss.dead else 85)
        
        inv_rect = pygame.Rect(GAME_W - 120, 15, 100, 30)
        is_hover = inv_rect.collidepoint(self.mouse_pos[0], self.mouse_pos[1])
        s_btn = pygame.Surface((100, 30), pygame.SRCALPHA)
        s_btn.fill((0,0,0, 200 if is_hover else 100))
        self.game_surface.blit(s_btn, (GAME_W - 120, 15))
        pygame.draw.rect(self.game_surface, hex_to_rgb("#d4a74c") if is_hover else (150,150,150), inv_rect, 1, border_radius=4)
        t3 = FONTS['tiny'].render("MOCHILA [I]", True, hex_to_rgb("#d4a74c") if is_hover else (255,255,255))
        self.game_surface.blit(t3, t3.get_rect(center=inv_rect.center))
        
        if self.just_clicked and is_hover:
            play_sfx('select'); self.state = 'inventory'; self.just_clicked = False

        pause_rect = pygame.Rect(GAME_W - 160, 15, 30, 30)
        is_hover_pause = pause_rect.collidepoint(self.mouse_pos[0], self.mouse_pos[1])
        s_btn_p = pygame.Surface((30, 30), pygame.SRCALPHA)
        s_btn_p.fill((0,0,0, 200 if is_hover_pause else 100))
        self.game_surface.blit(s_btn_p, (GAME_W - 160, 15))
        pygame.draw.rect(self.game_surface, hex_to_rgb("#d4a74c") if is_hover_pause else (150,150,150), pause_rect, 1, border_radius=4)
        t_p = FONTS['small'].render("II", True, hex_to_rgb("#d4a74c") if is_hover_pause else (255,255,255))
        self.game_surface.blit(t_p, t_p.get_rect(center=pause_rect.center))

        if self.just_clicked and is_hover_pause:
            play_sfx('select'); self.state = 'paused'; self.just_clicked = False

    def run(self):
        while True:
            self.just_clicked = False
            now = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: 
                        self.just_clicked = True
                elif event.type == pygame.MOUSEWHEEL:
                    if self.state == 'playing':
                        self.base_zoom = max(0.65, min(1.5, self.base_zoom - event.y * 0.1))
                    elif self.state == 'level_select':
                        self.target_map_scroll_y -= event.y * 60
                        self.target_map_scroll_y = max(-400, min(1200, self.target_map_scroll_y))
                    elif self.state == 'how_to_play':
                        self.target_how_to_play_scroll -= event.y * 45
                        max_scroll = max(0, len(self.instructions) * 45 - int(GAME_H * 0.5))
                        self.target_how_to_play_scroll = max(0, min(max_scroll, self.target_how_to_play_scroll))
                elif event.type == pygame.KEYDOWN:
                    self.keys[event.key] = True
                    if self.state == 'playing':
                        if event.key in [pygame.K_UP, pygame.K_w, pygame.K_SPACE]: 
                            self.player.jump() 
                        elif event.key in [pygame.K_DOWN, pygame.K_s] and not self.player.on_ground:
                            if self.player.class_id == 'warrior': self.player.is_ground_pounding = True
                        elif event.key in [pygame.K_i, pygame.K_e]: play_sfx('select'); self.state = 'inventory'
                        elif event.key in [pygame.K_ESCAPE, pygame.K_p]: play_sfx('select'); self.state = 'paused'
                    elif self.state == 'inventory':
                        if event.key in [pygame.K_i, pygame.K_e, pygame.K_ESCAPE]: play_sfx('select'); self.state = 'playing'
                    elif self.state == 'paused':
                        if event.key in [pygame.K_ESCAPE, pygame.K_p]: play_sfx('select'); self.state = 'playing'
                    elif self.state == 'how_to_play':
                        if event.key in [pygame.K_ESCAPE]: play_sfx('select'); self.change_state('menu')
                    elif self.state in ['game_over', 'victory']:
                        if event.key == pygame.K_BACKSPACE: 
                            self.input_text = self.input_text[:-1]
                            play_sfx('delete')
                        elif event.key == pygame.K_RETURN:
                            play_sfx('confirm')
                            name = self.input_text if self.input_text else "HERÓI"
                            self.save_ranking(name)
                            self.change_state('menu')
                        elif len(self.input_text) < 10 and event.unicode.isprintable():
                            self.input_text += event.unicode
                            play_sfx('typing')
                elif event.type == pygame.KEYUP:
                    if event.key in self.keys:
                        self.keys[event.key] = False

            self.mouse_pressed = pygame.mouse.get_pressed()
            mx, my = pygame.mouse.get_pos()
            self.mouse_pos = (mx - GAME_X, my - GAME_Y)
            
            world_mouse_x = (self.mouse_pos[0] * (self.virt_w / GAME_W))
            world_mouse_y = (self.mouse_pos[1] * (self.virt_h / GAME_H))
            self.world_mouse_pos = (world_mouse_x, world_mouse_y)

            self.update()
            
            if self.state == 'menu': self.draw_menu()
            elif self.state == 'level_select': self.draw_level_select()
            elif self.state in ['playing', 'player_dying']: self.draw_playing()
            elif self.state == 'paused': self.draw_pause()
            elif self.state == 'inventory': 
                self.draw_playing()
                self.draw_inventory()
            elif self.state == 'game_over': self.draw_game_over()
            elif self.state == 'victory': self.draw_victory()
            elif self.state == 'ranking': self.draw_ranking()
            elif self.state == 'how_to_play': self.draw_how_to_play()
            
            self.screen.fill((26, 15, 10)) 
            self.screen.blit(self.game_surface, (GAME_X, GAME_Y))
            if hasattr(self, 'border_image'):
                self.screen.blit(self.border_image, (0, 0))
            
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Game().run()