# -*- coding: utf-8 -*-
"""按 TexturePacker/Cocos plist 切帧，输出序列帧、GIF 和自包含预览页。"""
import base64
import io
import json
import os
import plistlib

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PLIST = os.path.join(HERE, "model10040118_2.plist")
PNG = os.path.join(HERE, "model10040118_2.png")
FRAME_DIR = os.path.join(HERE, "frames")


def parse_rect(text):
    nums = [int(n) for n in text.replace("{", " ").replace("}", " ").replace(",", " ").split()]
    return nums


def main():
    with open(PLIST, "rb") as f:
        data = plistlib.load(f)

    sheet = Image.open(PNG).convert("RGBA")
    frames = data["frames"]
    meta = data["metadata"]

    os.makedirs(FRAME_DIR, exist_ok=True)

    actions = {}
    for name, info in frames.items():
        action, index = name.replace(".png", "").rsplit("_", 1)
        actions.setdefault(action, []).append((int(index), name, info))

    manifest = {}
    for action, items in actions.items():
        items.sort()
        seq = []
        for index, name, info in items:
            x, y, w, h = parse_rect(info["frame"])
            rotated = info["rotated"]
            # 旋转帧在图集中占用 h x w，还原时反向旋转 90°
            crop_box = (x, y, x + (h if rotated else w), y + (w if rotated else h))
            sprite = sheet.crop(crop_box)
            if rotated:
                sprite = sprite.transpose(Image.Transpose.ROTATE_90)
            sw, sh = parse_rect(info["sourceSize"])
            sx, sy, _, _ = parse_rect(info["sourceColorRect"])
            canvas = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
            canvas.paste(sprite, (sx, sy))
            canvas.save(os.path.join(FRAME_DIR, name))
            seq.append({
                "index": index,
                "name": name,
                "file": "frames/" + name,
                "w": sw,
                "h": sh,
            })
        manifest[action] = seq

    with open(os.path.join(HERE, "frames.json"), "w", encoding="utf-8") as f:
        json.dump({"actions": manifest, "texture": "model10040118_2.png"}, f, ensure_ascii=False, indent=2)

    # GIF：攻击按原始帧号间隔(30fps)排时间，待机按 8fps 循环
    def make_gif(action, fps, scale, background, out_name):
        seq = manifest[action]
        durations = []
        if action.startswith("attack"):
            for i, fr in enumerate(seq):
                nxt = seq[i + 1]["index"] if i + 1 < len(seq) else fr["index"] + 4
                durations.append(max(1, round((nxt - fr["index"]) * 1000 / fps / 10) * 10))
        else:
            durations = [int(1000 / fps)] * len(seq)
        images = []
        for fr in seq:
            im = Image.open(os.path.join(HERE, fr["file"])).convert("RGBA")
            im = im.resize((int(fr["w"] * scale), int(fr["h"] * scale)), Image.LANCZOS)
            bg = Image.new("RGBA", im.size, background)
            bg.alpha_composite(im)
            images.append(bg.convert("RGB"))
        path = os.path.join(HERE, out_name)
        images[0].save(path, save_all=True, append_images=images[1:], duration=durations,
                       loop=0, disposal=2, optimize=False)
        print(f"{out_name}: {len(images)} 帧, {sum(durations)}ms/循环")

    make_gif("attack8", 30, 0.9, (255, 255, 255, 255), "attack8.gif")
    make_gif("idle8", 8, 0.9, (255, 255, 255, 255), "idle8.gif")

    # 拼一张预览图，方便核对切帧方向
    cols, cell = 4, 300
    rows = (len(frames) + cols - 1) // cols
    sheet_preview = Image.new("RGBA", (cols * cell, rows * cell), (246, 246, 248, 255))
    all_items = sorted(((n, i) for a in manifest for n, i in [(f["name"], f) for f in manifest[a]]))
    for k, (name, fr) in enumerate(all_items):
        im = Image.open(os.path.join(HERE, fr["file"])).convert("RGBA")
        im.thumbnail((cell - 20, cell - 20), Image.LANCZOS)
        cx, cy = (k % cols) * cell, (k // cols) * cell
        sheet_preview.alpha_composite(im, (cx + (cell - im.width) // 2, cy + (cell - im.height) // 2))
    sheet_preview.convert("RGB").save(os.path.join(HERE, "contact_sheet.png"))

    with open(os.path.join(HERE, "frames.json"), "w", encoding="utf-8") as f:
        json.dump({"actions": manifest, "texture": "model10040118_2.png", "size": list(sheet.size)},
                  f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
