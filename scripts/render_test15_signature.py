#!/usr/bin/env python3

import json
import random
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/Users/akg/EVADAVA/CanvasGlassNew")
OUTPUT_DIR = ROOT / "output" / "generated"
FILTER_PATH = OUTPUT_DIR / "test15_signature_filter.txt"
MANIFEST_PATH = OUTPUT_DIR / "test15_signature_manifest.json"
OUTPUT_PATH = ROOT / "output" / "video_render_test15_signature.mp4"
BADGE_DIR = OUTPUT_DIR / "qr_placeholders"

SEGMENT_DURATION = 300.0
TOTAL_DURATION = 900.0
SEED = 20260310
FRAME_RATE = 25

BACKGROUNDS = [
    ROOT / "output" / "bg_test1_1920.png",
    ROOT / "output" / "bg_test2_1920.png",
    ROOT / "output" / "bg_test3_1920.png",
]

MONOLOGUES = [
    ROOT / "output" / "renders" / "mon1_badged_tight.mov",
    ROOT / "output" / "renders" / "mon2_badged_tight.mov",
    ROOT / "output" / "renders" / "mon3_badged_tight.mov",
    ROOT / "output" / "renders" / "mon4_badged_tight.mov",
]

MONOLOGUE_TEXT = ROOT / "output" / "mon1_heygen.txt"

AMBIENCE_POOL = sorted((ROOT / "assets" / "audio" / "asmr_gallery" / "compiled_lossless").glob("*.flac"))


def run(cmd):
    subprocess.run(cmd, check=True)


def probe_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nk=1:nw=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


def estimate_qre_cue_seconds(monologue_duration: float) -> float:
    paragraphs = [p.strip() for p in MONOLOGUE_TEXT.read_text().strip().split("\n\n") if p.strip()]
    target_index = next(
        idx for idx, paragraph in enumerate(paragraphs) if "QR code" in paragraph or "playlist" in paragraph
    )
    word_counts = []
    for paragraph in paragraphs:
        clean = paragraph
        while "[pause" in clean:
            start = clean.index("[pause")
            end = clean.index("]", start)
            clean = clean[:start] + clean[end + 1 :]
        words = [word for word in clean.split() if word]
        word_counts.append(len(words))
    words_before = sum(word_counts[:target_index])
    total_words = sum(word_counts)
    return round(monologue_duration * (words_before / total_words), 3)


def choose_signature():
    rng = random.Random(SEED)
    ambience = rng.sample(AMBIENCE_POOL, 2)
    phase_offsets = [round(rng.uniform(0.0, 18.0), 3), round(rng.uniform(6.0, 24.0), 3)]

    video_segments = []
    for idx in range(3):
        zoom_amp = round(rng.uniform(0.0025, 0.0045), 4)
        base_scale = round(rng.uniform(1.004, 1.006), 4)
        if idx == 2:
            zoom_amp = round(rng.uniform(0.0018, 0.0030), 4)
            base_scale = round(rng.uniform(1.002, 1.004), 4)
        video_segments.append(
            {
                "segment": idx + 1,
                "zoom_base": base_scale,
                "zoom_amp": zoom_amp,
                "zoom_cycle_s": round(rng.uniform(118.0, 156.0), 1),
                "pan_x_px": round(rng.uniform(0.8, 1.6), 1),
                "pan_y_px": round(rng.uniform(0.5, 1.2), 1),
                "pan_x_cycle_s": round(rng.uniform(135.0, 175.0), 1),
                "pan_y_cycle_s": round(rng.uniform(145.0, 190.0), 1),
                "lens_t_s": round(rng.uniform(125.0, 170.0), 3),
                "lens_dur_s": round(rng.uniform(0.6, 0.9), 3),
                "lens_sigma": round(rng.uniform(0.14, 0.22), 3),
                "shadow_t_s": round(rng.uniform(245.0, 282.0), 3),
                "shadow_dur_s": round(rng.uniform(0.8, 1.2), 3),
                "shadow_alpha": round(rng.uniform(0.025, 0.045), 3),
                "shadow_w": int(rng.uniform(460, 620)),
                "shadow_h": int(rng.uniform(280, 420)),
                "shadow_y": int(rng.uniform(140, 240)),
            }
        )
    return ambience, phase_offsets, video_segments


def pick_font(size: int, mono: bool = False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Menlo.ttc" if mono else "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size=size)
            except OSError:
                pass
    return ImageFont.load_default()


def make_badge(path: Path, title: str, subtitle: str):
    image = Image.new("RGBA", (220, 220), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    gold = (200, 168, 75, 255)
    ivory = (231, 223, 208, 255)
    draw.rounded_rectangle((0, 0, 219, 219), radius=14, fill=(10, 8, 6, 133), outline=(184, 151, 42, 120), width=2)
    draw.rectangle((50, 22, 170, 142), fill=(247, 244, 236, 235))
    draw.rectangle((58, 30, 162, 134), fill=(10, 8, 6, 245))
    qr_blocks = [
        (66, 38, 18, 18),
        (90, 38, 14, 14),
        (112, 38, 22, 18),
        (66, 62, 16, 20),
        (96, 62, 28, 16),
        (130, 62, 16, 24),
        (66, 90, 22, 18),
        (94, 88, 16, 22),
        (118, 94, 28, 14),
        (72, 116, 14, 12),
        (94, 118, 24, 10),
        (126, 116, 12, 14),
    ]
    for x, y, w, h in qr_blocks:
        draw.rectangle((x, y, x + w, y + h), fill=(245, 238, 225, 255))

    title_font = pick_font(21, mono=False)
    subtitle_font = pick_font(16, mono=True)
    draw.text((18, 158), title, fill=gold, font=title_font)
    draw.text((18, 186), subtitle, fill=ivory, font=subtitle_font)
    image.save(path)


def build_segment_filter(input_index: int, seg: dict, label_in: str, label_out: str, shadow_label: str) -> list[str]:
    zoom_expr = f"{seg['zoom_base']}+{seg['zoom_amp']}*sin(2*PI*t/{seg['zoom_cycle_s']})"
    shadow_x_expr = (
        f"-{seg['shadow_w']}+((1920+{seg['shadow_w']}+240)*(t-{seg['shadow_t_s']})/{seg['shadow_dur_s']})"
    )

    return [
        (
            f"[{input_index}:v]format=rgba,fps={FRAME_RATE},scale='iw*({zoom_expr})':'ih*({zoom_expr})':eval=frame,"
            f"crop=1920:1080:'(in_w-1920)/2+{seg['pan_x_px']}*sin(2*PI*t/{seg['pan_x_cycle_s']})':"
            f"'(in_h-1080)/2+{seg['pan_y_px']}*sin(2*PI*t/{seg['pan_y_cycle_s']})',"
            f"boxblur=lr={seg['lens_sigma']}:lp=1:enable='between(t,{seg['lens_t_s']},{seg['lens_t_s'] + seg['lens_dur_s']})'"
            f"[{label_in}]"
        ),
        (
            f"color=c=black@0.0:s=1920x1080:d={SEGMENT_DURATION},format=rgba,"
            f"drawbox=x='{shadow_x_expr}':y={seg['shadow_y']}:w={seg['shadow_w']}:h={seg['shadow_h']}:"
            f"color=black@{seg['shadow_alpha']}:t=fill:enable='between(t,{seg['shadow_t_s']},{seg['shadow_t_s'] + seg['shadow_dur_s']})',"
            f"gblur=sigma=90[{shadow_label}]"
        ),
        f"[{label_in}][{shadow_label}]overlay=0:0[{label_out}]",
    ]


def main():
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise SystemExit("ffmpeg and ffprobe are required")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    BADGE_DIR.mkdir(parents=True, exist_ok=True)
    monologue_durations = [probe_duration(path) for path in MONOLOGUES]
    qre_trigger = estimate_qre_cue_seconds(monologue_durations[0])
    ambience_files, phase_offsets, video_segments = choose_signature()

    monologue_starts = [0.0, 300.0, 600.0, 780.0]
    qrp_triggers = [240.0, 540.0, 840.0]

    manifest = {
        "episode_id": "test15_signature",
        "episode_seed": SEED,
        "duration_s": TOTAL_DURATION,
        "segments": [
            {"painting": str(BACKGROUNDS[0]), "start_s": 0.0, "duration_s": SEGMENT_DURATION},
            {"painting": str(BACKGROUNDS[1]), "start_s": 300.0, "duration_s": SEGMENT_DURATION},
            {"painting": str(BACKGROUNDS[2]), "start_s": 600.0, "duration_s": SEGMENT_DURATION},
        ],
        "monologues": [
            {"path": str(path), "start_s": start, "duration_s": duration}
            for path, start, duration in zip(MONOLOGUES, monologue_starts, monologue_durations)
        ],
        "qr": {
            "qre_trigger_s": qre_trigger,
            "qre_label": "PLAYLIST",
            "qrp": [
                {"title": "PAINTING 1", "trigger_s": qrp_triggers[0]},
                {"title": "PAINTING 2", "trigger_s": qrp_triggers[1]},
                {"title": "PAINTING 3", "trigger_s": qrp_triggers[2]},
            ],
        },
        "audio_signature": {
            "ambience_tracks": [str(path) for path in ambience_files],
            "phase_offsets_s": phase_offsets,
            "voice_gain": [0.006, 0.003],
            "silence_gain": [0.010, 0.005],
        },
        "video_signature": {
            "modules": [
                "micro_zoom_drift",
                "subtle_pan_drift",
                "lens_breath",
                "passing_shadow",
            ],
            "segments": video_segments,
        },
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2))

    badge_specs = [
        ("qre_playlist.png", "QRE PLAYLIST", "placeholder"),
        ("qrp1.png", "QRP1", "painting 1"),
        ("qrp2.png", "QRP2", "painting 2"),
        ("qrp3.png", "QRP3", "painting 3"),
    ]
    badge_paths = []
    for filename, title, subtitle in badge_specs:
        badge_path = BADGE_DIR / filename
        make_badge(badge_path, title, subtitle)
        badge_paths.append(badge_path)

    voice_windows = "+".join(
        f"between(t,{start:.3f},{start + duration:.3f})" for start, duration in zip(monologue_starts, monologue_durations)
    )
    voice_volume_expr_a = f"if(gt({voice_windows},0),0.006,0.010)".replace(",", "\\,")
    voice_volume_expr_b = f"if(gt({voice_windows},0),0.003,0.005)".replace(",", "\\,")

    filter_lines = []
    filter_lines.extend(build_segment_filter(0, video_segments[0], "seg1base", "seg1", "seg1shadow"))
    filter_lines.extend(build_segment_filter(1, video_segments[1], "seg2base", "seg2", "seg2shadow"))
    filter_lines.extend(build_segment_filter(2, video_segments[2], "seg3base", "seg3", "seg3shadow"))
    filter_lines.append("[seg1][seg2][seg3]concat=n=3:v=1:a=0[base]")
    filter_lines.append(f"[base][3:v]overlay=x=48:y=680:enable='between(t,0.000,{monologue_durations[0]:.3f})'[v1]")
    filter_lines.append(
        f"[4:v]trim=duration=0.040,setpts=PTS-STARTPTS,loop=loop=-1:size=1:start=0,"
        f"trim=duration={monologue_durations[1]:.3f},setpts=PTS-STARTPTS[frozen2]"
    )
    filter_lines.append(
        f"[5:v]trim=duration=0.040,setpts=PTS-STARTPTS,loop=loop=-1:size=1:start=0,"
        f"trim=duration={monologue_durations[2]:.3f},setpts=PTS-STARTPTS[frozen3]"
    )
    filter_lines.append(
        f"[6:v]trim=duration=0.040,setpts=PTS-STARTPTS,loop=loop=-1:size=1:start=0,"
        f"trim=duration={monologue_durations[3]:.3f},setpts=PTS-STARTPTS[frozen4]"
    )
    filter_lines.append(
        f"[v1][frozen2]overlay=x=48:y=680:enable='between(t,300.000,{300.0 + monologue_durations[1]:.3f})'[v2]"
    )
    filter_lines.append(
        f"[v2][frozen3]overlay=x=48:y=680:enable='between(t,600.000,{600.0 + monologue_durations[2]:.3f})'[v3]"
    )
    filter_lines.append(
        f"[v3][frozen4]overlay=x=48:y=680:enable='between(t,780.000,{780.0 + monologue_durations[3]:.3f})'[v4]"
    )

    filter_lines.append(
        f"[v4][9:v]overlay=x=W-w-48:y=56:enable='between(t,{qre_trigger:.3f},{qre_trigger + 60.0:.3f})'[v5]"
    )
    filter_lines.append("[v5][10:v]overlay=x=W-w-48:y=56:enable='between(t,240.000,300.000)'[v6]")
    filter_lines.append("[v6][11:v]overlay=x=W-w-48:y=56:enable='between(t,540.000,600.000)'[v7]")
    filter_lines.append("[v7][12:v]overlay=x=W-w-48:y=56:enable='between(t,840.000,900.000)',format=yuv420p[vout]")

    filter_lines.append(
        f"[7:a]atrim=start={phase_offsets[0]:.3f}:duration={TOTAL_DURATION},asetpts=N/SR/TB,"
        f"volume='{voice_volume_expr_a}'[amb1]"
    )
    filter_lines.append(
        f"[8:a]atrim=start={phase_offsets[1]:.3f}:duration={TOTAL_DURATION},asetpts=N/SR/TB,"
        f"volume='{voice_volume_expr_b}'[amb2]"
    )
    filter_lines.append("[amb1][amb2]amix=inputs=2:normalize=0,alimiter=limit=0.30[bed]")
    for idx, (start, path) in enumerate(zip(monologue_starts, MONOLOGUES), start=1):
        delay_ms = int(round(start * 1000))
        filter_lines.append(
            f"[{idx + 2}:a]adelay={delay_ms}|{delay_ms},apad,atrim=0:{TOTAL_DURATION}[a{idx}]"
        )
    filter_lines.append("[bed][a1][a2][a3][a4]amix=inputs=5:normalize=0,alimiter=limit=0.96[aout]")

    FILTER_PATH.write_text(";\n".join(filter_lines) + "\n")

    cmd = [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-framerate",
        str(FRAME_RATE),
        "-t",
        str(int(SEGMENT_DURATION)),
        "-i",
        str(BACKGROUNDS[0]),
        "-loop",
        "1",
        "-framerate",
        str(FRAME_RATE),
        "-t",
        str(int(SEGMENT_DURATION)),
        "-i",
        str(BACKGROUNDS[1]),
        "-loop",
        "1",
        "-framerate",
        str(FRAME_RATE),
        "-t",
        str(int(SEGMENT_DURATION)),
        "-i",
        str(BACKGROUNDS[2]),
        "-i",
        str(MONOLOGUES[0]),
        "-i",
        str(MONOLOGUES[1]),
        "-i",
        str(MONOLOGUES[2]),
        "-i",
        str(MONOLOGUES[3]),
        "-stream_loop",
        "-1",
        "-i",
        str(ambience_files[0]),
        "-stream_loop",
        "-1",
        "-i",
        str(ambience_files[1]),
        "-i",
        str(badge_paths[0]),
        "-i",
        str(badge_paths[1]),
        "-i",
        str(badge_paths[2]),
        "-i",
        str(badge_paths[3]),
        "-filter_complex_script",
        str(FILTER_PATH),
        "-map",
        "[vout]",
        "-map",
        "[aout]",
        "-t",
        str(int(TOTAL_DURATION)),
        "-r",
        str(FRAME_RATE),
        "-c:v",
        "h264_videotoolbox",
        "-b:v",
        "12000k",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        str(OUTPUT_PATH),
    ]
    run(cmd)


if __name__ == "__main__":
    main()
