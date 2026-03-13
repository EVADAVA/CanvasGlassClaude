from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import streamlit as st


BASE_DIR = Path("/Users/akg/EVADAVA/CanvasGlassNew")
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
SCRIPTS_DIR = BASE_DIR / "scripts"
START_SCRIPT = SCRIPTS_DIR / "start_episode.py"

PIPELINE_STEPS = [
    "MS start/test",
    "ADNA",
    "NB",
    "Paintings",
    "PD",
    "Wine",
    "Spotify",
    "Avatar",
    "HeyGen prompts",
    "HeyGen generation",
    "QR",
    "Publisher",
    "Render",
    "Publish",
]

STATUS_TO_STEP = {
    "selected": 0,
    "adna_ready": 1,
    "nb_ready": 2,
    "awaiting_paintings": 3,
    "pd_ready": 4,
    "wine_ready": 5,
    "playlist_ready": 6,
    "awaiting_spotify_cover_selection": 6,
    "cover_selected": 6,
    "avatar_draft_ready": 7,
    "avatar_final_ready": 8,
    "heygen_prompt_ready_not_sent": 8,
    "heygen_generation_started": 9,
    "qr_ready": 10,
    "publisher_ready": 11,
    "render_ready": 12,
    "published": 13,
}


@dataclass
class RunState:
    manifest_path: Path
    data: dict[str, Any]

    @property
    def run_id(self) -> str:
        return self.data.get("episode_slug") or self.data.get("episode_id") or self.manifest_path.stem

    @property
    def status(self) -> str:
        return self.data.get("status", "unknown")

    @property
    def created_at(self) -> str:
        return self.data.get("created_at", "")

    @property
    def artist_name(self) -> str:
        return self.data.get("artist_name", "Unknown")


def list_manifests() -> list[RunState]:
    manifests: list[RunState] = []
    for manifest_path in sorted(OUTPUT_DIR.glob("*/publish/*_start-manifest.json")):
        try:
            data = json.loads(manifest_path.read_text())
        except json.JSONDecodeError:
            continue
        manifests.append(RunState(manifest_path=manifest_path, data=data))
    manifests.sort(key=lambda item: item.created_at or "", reverse=True)
    return manifests


def read_text_if_exists(path_str: str) -> str:
    path = Path(path_str)
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text()


def existing_input_files(run: RunState) -> list[Path]:
    run_input_dir = Path(run.data.get("input_dir", ""))
    if not run_input_dir.exists():
        return []
    return sorted(path for path in run_input_dir.iterdir() if path.is_file())


def expected_inputs(run: RunState) -> list[Path]:
    return [Path(item) for item in run.data.get("expected_inputs", [])]


def artifact_rows(run: RunState) -> list[tuple[str, str, bool]]:
    rows: list[tuple[str, str, bool]] = []
    for key, value in sorted(run.data.get("artifacts", {}).items()):
        path = Path(value)
        rows.append((key, value, path.exists()))
    return rows


def compute_step_states(status: str) -> list[str]:
    current_index = STATUS_TO_STEP.get(status, -1)
    states: list[str] = []
    for idx, _ in enumerate(PIPELINE_STEPS):
        if idx < current_index:
            states.append("done")
        elif idx == current_index:
            states.append("current")
        else:
            states.append("pending")
    return states


def run_start_command(mode: str, artist_name: str) -> tuple[bool, str]:
    cmd = [sys.executable, str(START_SCRIPT)]
    if mode == "test":
        cmd.append("--test")
    else:
        cmd.append("--release")
    cmd.append(artist_name)
    completed = subprocess.run(cmd, capture_output=True, text=True, cwd=str(BASE_DIR))
    output = completed.stdout.strip()
    error = completed.stderr.strip()
    if completed.returncode == 0:
        return True, output or "Run created."
    return False, error or output or "Unknown error"


def render_pipeline(run: RunState) -> None:
    st.subheader("Pipeline")
    states = compute_step_states(run.status)
    columns = st.columns(5)
    for idx, step in enumerate(PIPELINE_STEPS):
        with columns[idx % 5]:
            state = states[idx]
            if state == "done":
                st.success(f"{step} ✅")
            elif state == "current":
                st.warning(f"{step} ⏳")
            else:
                st.info(f"{step} ⚪")


def render_pause_box(run: RunState) -> None:
    status = run.status
    if status == "awaiting_paintings":
        st.error("Пауза: нужны 3 картины в input-папке этого run.")
        expected = expected_inputs(run)
        if expected:
            st.markdown("Ожидаемые файлы:")
            for path in expected:
                st.write(f"- `{path}`")
    elif status == "awaiting_spotify_cover_selection":
        st.warning("Пауза: нужен выбор финальной Spotify cover.")
    elif status == "heygen_prompt_ready_not_sent":
        st.warning("Пауза: HeyGen prompts готовы, генерация ещё не запущена.")
    else:
        next_step = run.data.get("next_step")
        if next_step:
            st.info(next_step)


def render_artifacts(run: RunState) -> None:
    st.subheader("Артефакты")
    rows = artifact_rows(run)
    if not rows:
        st.caption("Пока нет зарегистрированных артефактов.")
        return
    for key, value, exists in rows:
        marker = "✅" if exists else "⚪"
        st.write(f"{marker} `{key}`")
        st.code(value, language="text")
        if exists and value.endswith(".txt"):
            text = read_text_if_exists(value)
            if text:
                with st.expander(f"Показать {key}"):
                    st.text(text[:8000])


def render_input_status(run: RunState) -> None:
    st.subheader("Input")
    files = existing_input_files(run)
    if not files:
        st.caption("В input-папке пока нет файлов.")
        return
    for path in files:
        st.write(f"- `{path}`")


def render_redirects(run: RunState) -> None:
    redirects = run.data.get("redirects", {})
    if not redirects:
        return
    st.subheader("Redirects")
    for key, url in redirects.items():
        st.markdown(f"- `{key}`: [{url}]({url})")


st.set_page_config(page_title="Canvas & Glass Studio", page_icon="🎨", layout="wide")
st.title("Canvas & Glass Studio")
st.caption("Episode monitor for the current CanvasGlassNew pipeline.")

with st.sidebar:
    st.header("Новый run")
    mode = st.radio("Режим", ["test", "start"], horizontal=True)
    artist_name = st.text_input("Artist Name", value="")
    if st.button("Создать run", use_container_width=True):
        clean_name = artist_name.strip()
        if not clean_name:
            st.error("Нужно имя художника.")
        elif not START_SCRIPT.exists():
            st.error(f"Не найден script: {START_SCRIPT}")
        else:
            ok, message = run_start_command(mode, clean_name)
            if ok:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    st.divider()
    st.caption(f"BASE_DIR: {BASE_DIR}")


manifests = list_manifests()

if not manifests:
    st.warning("Пока нет ни одного run manifest. Создай новый `test` или `start` слева.")
    st.stop()

run_options = {f"{run.run_id} · {run.artist_name} · {run.status}": run for run in manifests}
selected_label = st.selectbox("Выбери run", list(run_options.keys()))
selected_run = run_options[selected_label]

status_col, meta_col = st.columns([1, 1])
with status_col:
    st.subheader("Статус")
    st.write(f"**Run:** `{selected_run.run_id}`")
    st.write(f"**Artist:** {selected_run.artist_name}")
    st.write(f"**Run type:** `{selected_run.data.get('run_type', 'unknown')}`")
    st.write(f"**Current status:** `{selected_run.status}`")

with meta_col:
    st.subheader("Метаданные")
    st.write(f"**Created:** {selected_run.created_at}")
    st.write(f"**Input dir:** `{selected_run.data.get('input_dir', '')}`")
    st.write(f"**Output dir:** `{selected_run.data.get('output_dir', '')}`")

render_pipeline(selected_run)
st.divider()

left, right = st.columns([2, 1])
with left:
    render_pause_box(selected_run)
    render_artifacts(selected_run)
with right:
    render_input_status(selected_run)
    render_redirects(selected_run)

st.divider()
with st.expander("Manifest JSON"):
    st.json(selected_run.data)
