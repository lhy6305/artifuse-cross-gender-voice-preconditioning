from __future__ import annotations

import argparse
import csv
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

import librosa
import numpy as np
import sounddevice as sd
import soundfile as sf


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = ROOT / "artifacts" / "listening_review" / "stage0_rule_listening_pack" / "v1" / "listening_review_queue.csv"
REVIEW_OPTIONS = ["pending", "reviewed", "needs_check", "skipped"]
BOOL_OPTIONS = ["yes", "no", "maybe"]
ISSUE_OPTIONS = ["no", "slight", "yes"]
STRENGTH_OPTIONS = ["too_weak", "ok", "too_strong"]

REVIEW_STATUS_LABELS = {
    "pending": "待审",
    "reviewed": "已审",
    "needs_check": "待复核",
    "skipped": "跳过",
}
BOOL_LABELS = {
    "": "",
    "yes": "是",
    "no": "否",
    "maybe": "存疑",
}
ISSUE_LABELS = {
    "": "",
    "no": "无",
    "slight": "轻微",
    "yes": "明显",
}
STRENGTH_LABELS = {
    "": "",
    "too_weak": "太弱",
    "ok": "合适",
    "too_strong": "过强",
}
QUANT_GRADE_LABELS = {
    "strong_pass": "强通过",
    "pass": "通过",
    "borderline": "边界",
    "fail": "失败",
}
FLAG_LABELS = {
    "pass": "通过",
    "borderline": "边界",
    "fail": "失败",
    "safe": "安全",
    "risky": "风险",
    "likely": "明显",
    "weak": "偏弱",
}

RUBRIC_TEXT = """主观听审口径

当前默认目标：
- 只比较“修正前 / 修正后”的主观差异
- 若队列来自 stage1 cascade，也先忽略 RVC 输出

人工结论：
- direction_correct：变化方向是否符合预期
- effect_audible：是否听得出变化
- artifact_issue：是否引入失真、异响、削波、明显不自然
- strength_fit：变化太弱 / 合适 / 过强
- keep_recommendation：这条规则是否保留到下一轮

建议流程：
1. 先听源音频
2. 再听修正后音频
3. 若怀疑音调偏移影响判断，可试听“处理音(全局变速对齐F0)”
   这是对处理音再做一次全局变速/变调辅助试听，会改变时长，不代表原处理音本体
4. 必要时反复 A/B
5. 最后写主观判断
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default=str(DEFAULT_CSV), help="Review queue CSV path relative to repo root or absolute path.")
    parser.add_argument("--auto-close-ms", type=int, default=0, help="Auto close after N milliseconds for smoke tests.")
    return parser.parse_args()


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def invert_mapping(mapping: dict[str, str]) -> dict[str, str]:
    return {value: key for key, value in mapping.items()}


REVIEW_STATUS_VALUES = invert_mapping(REVIEW_STATUS_LABELS)
BOOL_VALUES = invert_mapping(BOOL_LABELS)
ISSUE_VALUES = invert_mapping(ISSUE_LABELS)
STRENGTH_VALUES = invert_mapping(STRENGTH_LABELS)


def parse_float(value: str | float | int | None) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


class ReviewApp:
    def __init__(self, root: tk.Tk, csv_path: Path) -> None:
        self.root = root
        self.csv_path = csv_path
        self.rows, self.fieldnames = self.load_rows()
        self.index = self.first_pending_index()
        self.selection_guard = False

        self.current_audio: np.ndarray | None = None
        self.current_sr: int | None = None
        self.aligned_audio_cache: dict[tuple[str, int], tuple[np.ndarray, int]] = {}

        self.status_text = tk.StringVar()
        self.identity_text = tk.StringVar()
        self.rule_text = tk.StringVar()
        self.auto_text = tk.StringVar()
        self.metric_text = tk.StringVar()
        self.path_text = tk.StringVar()
        self.playback_text = tk.StringVar()

        self.review_status_var = tk.StringVar()
        self.direction_correct_var = tk.StringVar()
        self.effect_audible_var = tk.StringVar()
        self.artifact_issue_var = tk.StringVar()
        self.strength_fit_var = tk.StringVar()
        self.keep_recommendation_var = tk.StringVar()
        self.normalize_peak_var = tk.BooleanVar(value=False)
        self.volume_scale_var = tk.DoubleVar(value=0.7)

        self.build_ui()
        self.refresh_row_list()
        self.select_index(self.index, force=True)

    def load_rows(self) -> tuple[list[dict[str, str]], list[str]]:
        with self.csv_path.open("r", encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
            return rows, list(rows[0].keys()) if rows else []

    def save_rows(self) -> None:
        with self.csv_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()
            writer.writerows(self.rows)

    def first_pending_index(self) -> int:
        for idx, row in enumerate(self.rows):
            if row.get("review_status", "pending") in {"pending", "待审"}:
                return idx
        return 0

    def build_ui(self) -> None:
        self.root.title("音频听审")
        self.root.geometry("1440x960")

        container = ttk.Frame(self.root, padding=10)
        container.pack(fill=tk.BOTH, expand=True)

        paned = ttk.Panedwindow(container, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(paned, padding=(0, 0, 8, 0))
        right_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=0)
        paned.add(right_frame, weight=1)

        ttk.Label(left_frame, text="文件列表").pack(anchor="w")
        self.listbox = tk.Listbox(left_frame, exportselection=False, width=42)
        list_scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=list_scrollbar.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.listbox.bind("<Button-1>", self.on_listbox_button_press)
        self.listbox.bind("<B1-Motion>", self.on_listbox_drag)
        self.listbox.bind("<ButtonRelease-1>", self.on_listbox_button_release)
        self.listbox.bind("<Double-Button-1>", self.on_listbox_double_click)

        canvas = tk.Canvas(right_frame, highlightthickness=0)
        detail_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=detail_scrollbar.set)
        detail_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.detail_frame = ttk.Frame(canvas, padding=(0, 0, 8, 0))
        self.detail_window = canvas.create_window((0, 0), window=self.detail_frame, anchor="nw")
        self.detail_canvas = canvas

        self.detail_frame.bind("<Configure>", self.on_detail_frame_configure)
        self.detail_canvas.bind("<Configure>", self.on_canvas_configure)
        self.detail_canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        ttk.Label(self.detail_frame, textvariable=self.status_text, font=("Segoe UI", 12, "bold")).pack(anchor="w")
        ttk.Label(self.detail_frame, textvariable=self.identity_text, wraplength=980, justify=tk.LEFT).pack(anchor="w", pady=(4, 0))
        ttk.Label(self.detail_frame, textvariable=self.rule_text, wraplength=980, justify=tk.LEFT).pack(anchor="w", pady=(4, 0))
        ttk.Label(self.detail_frame, textvariable=self.auto_text, wraplength=980, justify=tk.LEFT).pack(anchor="w", pady=(4, 0))
        ttk.Label(self.detail_frame, textvariable=self.metric_text, wraplength=980, justify=tk.LEFT).pack(anchor="w", pady=(4, 0))
        ttk.Label(self.detail_frame, textvariable=self.path_text, wraplength=980, justify=tk.LEFT).pack(anchor="w", pady=(4, 10))

        playback_button_row = ttk.Frame(self.detail_frame)
        playback_button_row.pack(fill=tk.X, pady=(0, 8))
        self.source_button = ttk.Button(playback_button_row, text="播放源音频", command=self.play_source)
        self.source_button.pack(side=tk.LEFT)
        self.original_button = ttk.Button(playback_button_row, text="播放修正后音频", command=self.play_original)
        self.original_button.pack(side=tk.LEFT, padx=(6, 0))
        self.processed_button = ttk.Button(playback_button_row, text="播放处理音", command=self.play_processed)
        self.processed_button.pack(side=tk.LEFT, padx=(6, 0))
        self.aligned_button = ttk.Button(playback_button_row, text="播放处理音(全局变速对齐F0)", command=self.play_processed_f0_aligned)
        self.aligned_button.pack(side=tk.LEFT, padx=(6, 0))
        self.baseline_button = ttk.Button(playback_button_row, text="播放raw->RVC", command=self.play_baseline)
        self.baseline_button.pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(playback_button_row, text="停止", command=self.stop_audio).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(playback_button_row, text="标记保留", command=self.mark_keep).pack(side=tk.LEFT, padx=(20, 0))
        ttk.Button(playback_button_row, text="标记待复核", command=self.mark_maybe).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(playback_button_row, text="标记淘汰", command=self.mark_reject).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(playback_button_row, text="保存", command=self.save_current_and_flush).pack(side=tk.RIGHT)

        playback_control_row = ttk.Frame(self.detail_frame)
        playback_control_row.pack(fill=tk.X, pady=(0, 10))
        ttk.Checkbutton(
            playback_control_row,
            text="播放时按最大峰值归一化",
            variable=self.normalize_peak_var,
            command=self.update_playback_text,
        ).pack(side=tk.LEFT)
        ttk.Label(playback_control_row, text="音量").pack(side=tk.LEFT, padx=(16, 6))
        ttk.Scale(
            playback_control_row,
            from_=0.25,
            to=8.0,
            variable=self.volume_scale_var,
            orient=tk.HORIZONTAL,
            length=320,
            command=lambda _value: self.update_playback_text(),
        ).pack(side=tk.LEFT)
        ttk.Label(playback_control_row, textvariable=self.playback_text).pack(side=tk.LEFT, padx=(10, 0))

        form = ttk.Frame(self.detail_frame)
        form.pack(fill=tk.X, pady=(0, 10))
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        self.make_radio_group(form, 0, 0, "审核状态", self.review_status_var, REVIEW_OPTIONS, REVIEW_STATUS_LABELS)
        self.make_radio_group(form, 0, 1, "方向正确", self.direction_correct_var, BOOL_OPTIONS, BOOL_LABELS)
        self.make_radio_group(form, 1, 0, "效果可辨", self.effect_audible_var, BOOL_OPTIONS, BOOL_LABELS)
        self.make_radio_group(form, 1, 1, "伪影 / 失真", self.artifact_issue_var, ISSUE_OPTIONS, ISSUE_LABELS)
        self.make_radio_group(form, 2, 0, "强度是否合适", self.strength_fit_var, STRENGTH_OPTIONS, STRENGTH_LABELS)
        self.make_radio_group(form, 2, 1, "是否保留规则", self.keep_recommendation_var, BOOL_OPTIONS, BOOL_LABELS)

        ttk.Label(self.detail_frame, text="审核备注").pack(anchor="w")
        self.notes_text = tk.Text(self.detail_frame, height=10, wrap=tk.WORD)
        self.notes_text.pack(fill=tk.BOTH, expand=True)

        rubric_frame = ttk.LabelFrame(self.detail_frame, text="听审口径", padding=8)
        rubric_frame.pack(fill=tk.BOTH, expand=False, pady=(10, 0))
        rubric_text = tk.Text(rubric_frame, height=10, wrap=tk.WORD)
        rubric_text.pack(fill=tk.BOTH, expand=True)
        rubric_text.insert("1.0", RUBRIC_TEXT)
        rubric_text.configure(state=tk.DISABLED)

    def on_detail_frame_configure(self, _event: tk.Event) -> None:
        self.detail_canvas.configure(scrollregion=self.detail_canvas.bbox("all"))

    def on_canvas_configure(self, event: tk.Event) -> None:
        self.detail_canvas.itemconfigure(self.detail_window, width=event.width)

    def on_mousewheel(self, event: tk.Event) -> None:
        if self.detail_canvas.winfo_exists():
            self.detail_canvas.yview_scroll(int(-event.delta / 120), "units")

    def make_radio_group(
        self,
        parent: ttk.Frame,
        row: int,
        col: int,
        label: str,
        variable: tk.StringVar,
        values: list[str],
        label_map: dict[str, str],
    ) -> None:
        frame = ttk.LabelFrame(parent, text=label, padding=8)
        frame.grid(row=row, column=col, sticky="nsew", pady=(4, 0), padx=(0 if col == 0 else 16, 0))
        for option in values:
            ttk.Radiobutton(frame, text=label_map[option], value=label_map[option], variable=variable).pack(anchor="w")

    def current_row(self) -> dict[str, str]:
        return self.rows[self.index]

    def update_playback_text(self) -> None:
        normalize_text = "on" if self.normalize_peak_var.get() else "off"
        volume_percent = int(round(self.volume_scale_var.get() * 100.0))
        self.playback_text.set(f"peak_norm={normalize_text} | volume={volume_percent}%")

    def format_row_label(self, row: dict[str, str]) -> str:
        status = REVIEW_STATUS_LABELS.get(row.get("review_status", "pending"), row.get("review_status", "pending"))
        utt_id = row.get("utt_id", "")
        group_value = row.get("group_value", "")
        direction = row.get("target_direction", "")
        return f"[{status}] {utt_id} | {group_value} | {direction}"

    def refresh_row_list(self) -> None:
        self.listbox.delete(0, tk.END)
        for row in self.rows:
            self.listbox.insert(tk.END, self.format_row_label(row))

    def listbox_hit_test(self, x: int, y: int) -> int | None:
        if not self.rows:
            return None
        index = self.listbox.nearest(y)
        bbox = self.listbox.bbox(index)
        if bbox is None:
            return None
        _x0, y0, _width, height = bbox
        inside_vertical = y0 <= y < (y0 + height)
        inside_horizontal = 0 <= x < self.listbox.winfo_width()
        if inside_vertical and inside_horizontal:
            return index
        return None

    def on_listbox_button_press(self, event: tk.Event) -> str:
        hit_index = self.listbox_hit_test(event.x, event.y)
        if hit_index is not None:
            self.select_index(hit_index)
            self.listbox.focus_set()
        return "break"

    def on_listbox_drag(self, event: tk.Event) -> str:
        return "break"

    def on_listbox_button_release(self, event: tk.Event) -> str:
        return "break"

    def on_listbox_double_click(self, _event: tk.Event) -> str:
        return "break"

    def select_index(self, new_index: int, *, force: bool = False) -> None:
        if not self.rows:
            return
        new_index = max(0, min(len(self.rows) - 1, new_index))
        if not force and new_index == self.index:
            return
        if not force:
            self.save_form_into_row()
            self.save_rows()
            self.refresh_row_list()
        self.index = new_index
        self.selection_guard = True
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(self.index)
        self.listbox.activate(self.index)
        self.listbox.see(self.index)
        self.selection_guard = False
        self.load_row_into_form()

    def load_row_into_form(self) -> None:
        if not self.rows:
            return
        row = self.current_row()
        cascade_mode = row.get("action_family") == "cascade_compare"
        pending_count = sum(1 for item in self.rows if item.get("review_status") in {"pending", "待审"})
        self.status_text.set(f"第 {self.index + 1} / {len(self.rows)} 条 | 待审={pending_count}")
        self.identity_text.set(
            f"{row.get('group_value', '')} | {row.get('source_gender', '')} -> {row.get('target_direction', '')} | "
            f"utt={row.get('utt_id', '')} | f0={row.get('f0_median_hz', '')} Hz | "
            f"confidence={row.get('confidence', '')} | strength={row.get('strength_label', '')}"
        )
        if cascade_mode:
            self.rule_text.set("模式=修正前后主观对照 | 当前先忽略 RVC 输出，只比较源音频与修正后音频。")
        else:
            self.rule_text.set(
                f"rule_id={row.get('rule_id', '')} | action={row.get('action_family', '')} | "
                f"alpha_default={row.get('alpha_default', '')} | alpha_max={row.get('alpha_max', '')} | "
                f"notes={row.get('rule_notes', '')}"
            )
        self.auto_text.set(
            f"自动量化：grade={QUANT_GRADE_LABELS.get(row.get('auto_quant_grade', ''), row.get('auto_quant_grade', ''))} | "
            f"score={row.get('auto_quant_score', '')} | direction={FLAG_LABELS.get(row.get('auto_direction_flag', ''), row.get('auto_direction_flag', ''))}"
            f"({row.get('auto_direction_score', '')}) | preserve={FLAG_LABELS.get(row.get('auto_preservation_flag', ''), row.get('auto_preservation_flag', ''))}"
            f"({row.get('auto_preservation_score', '')}) | audible={FLAG_LABELS.get(row.get('auto_audibility_flag', ''), row.get('auto_audibility_flag', ''))}"
            f"({row.get('auto_effect_score', '')}) | notes={row.get('auto_quant_notes', '') or 'ok'}"
        )
        self.metric_text.set(
            f"主差异：delta_log_centroid_minus_log_f0={row.get('delta_log_centroid_minus_log_f0', '')} | "
            f"delta_centroid={row.get('delta_spectral_centroid_hz_mean', '')} Hz | "
            f"delta_low_mid={row.get('delta_low_mid_0_1500_share_db', '')} dB | "
            f"delta_brilliance={row.get('delta_brilliance_3000_8000_share_db', '')} dB | "
            f"delta_f0={row.get('delta_f0_median_pct', '')}% | delta_rms={row.get('delta_rms_dbfs', '')} dB | "
            f"delta_voiced={row.get('delta_f0_voiced_ratio', '')} | delta_clip={row.get('delta_clipping_ratio', '')} | "
            f"stft_l1={row.get('stft_logmag_l1', '')}"
        )
        if cascade_mode:
            self.source_button.configure(text="播放源音频")
            if not self.original_button.winfo_manager():
                self.original_button.pack(side=tk.LEFT, padx=(6, 0), after=self.source_button)
            self.original_button.configure(text="播放修正后音频")
            self.processed_button.pack_forget()
            self.aligned_button.pack_forget()
            self.baseline_button.pack_forget()
            self.path_text.set(
                f"source={row.get('input_audio', '')}\n"
                f"preconditioned={row.get('original_copy', '')}"
            )
        else:
            self.source_button.configure(text="播放原音")
            if self.original_button.winfo_manager():
                self.original_button.pack_forget()
            if not self.processed_button.winfo_manager():
                self.processed_button.pack(side=tk.LEFT, padx=(6, 0), after=self.source_button)
            if not self.aligned_button.winfo_manager():
                self.aligned_button.pack(side=tk.LEFT, padx=(6, 0), after=self.processed_button)
            if self.baseline_button.winfo_manager():
                self.baseline_button.pack_forget()
            self.processed_button.configure(text="播放处理音")
            self.aligned_button.configure(text="播放处理音(全局变速对齐F0)")
            self.path_text.set(
                f"raw={row.get('input_audio', '')}\n"
                f"processed={row.get('processed_audio', '')}"
            )

        self.review_status_var.set(REVIEW_STATUS_LABELS.get(row.get("review_status", "pending"), "待审"))
        self.direction_correct_var.set(BOOL_LABELS.get(row.get("direction_correct", ""), row.get("direction_correct", "")))
        self.effect_audible_var.set(BOOL_LABELS.get(row.get("effect_audible", ""), row.get("effect_audible", "")))
        self.artifact_issue_var.set(ISSUE_LABELS.get(row.get("artifact_issue", ""), row.get("artifact_issue", "")))
        self.strength_fit_var.set(STRENGTH_LABELS.get(row.get("strength_fit", ""), row.get("strength_fit", "")))
        self.keep_recommendation_var.set(BOOL_LABELS.get(row.get("keep_recommendation", ""), row.get("keep_recommendation", "")))

        self.notes_text.delete("1.0", tk.END)
        self.notes_text.insert("1.0", row.get("review_notes", ""))
        self.update_playback_text()
        self.stop_audio()

    def save_form_into_row(self) -> None:
        row = self.current_row()
        row["review_status"] = REVIEW_STATUS_VALUES.get(self.review_status_var.get(), self.review_status_var.get())
        row["direction_correct"] = BOOL_VALUES.get(self.direction_correct_var.get(), self.direction_correct_var.get())
        row["effect_audible"] = BOOL_VALUES.get(self.effect_audible_var.get(), self.effect_audible_var.get())
        row["artifact_issue"] = ISSUE_VALUES.get(self.artifact_issue_var.get(), self.artifact_issue_var.get())
        row["strength_fit"] = STRENGTH_VALUES.get(self.strength_fit_var.get(), self.strength_fit_var.get())
        row["keep_recommendation"] = BOOL_VALUES.get(self.keep_recommendation_var.get(), self.keep_recommendation_var.get())
        row["review_notes"] = self.notes_text.get("1.0", tk.END).strip()

    def save_current_and_flush(self) -> None:
        self.save_form_into_row()
        self.save_rows()
        self.refresh_row_list()
        self.select_index(self.index, force=True)
        messagebox.showinfo("已保存", f"已保存到 {self.csv_path}")

    def next_pending_index(self) -> int | None:
        for idx in range(self.index + 1, len(self.rows)):
            if self.rows[idx].get("review_status") in {"pending", "待审"}:
                return idx
        return None

    def load_audio(self, path_value: str) -> tuple[np.ndarray, int]:
        audio, sr = sf.read(resolve_path(path_value), always_2d=False)
        audio = np.asarray(audio, dtype=np.float32)
        if audio.ndim == 2:
            audio = audio.mean(axis=1)
        return audio, sr

    def prepare_playback_audio(self, audio: np.ndarray) -> np.ndarray:
        output = np.array(audio, dtype=np.float32, copy=True)
        peak = float(np.max(np.abs(output))) if output.size else 0.0
        if self.normalize_peak_var.get() and peak > 1e-6:
            output = output * (0.9 / peak)
        elif peak > 1.0:
            output = output / peak
        output = output * float(self.volume_scale_var.get())
        final_peak = float(np.max(np.abs(output))) if output.size else 0.0
        if final_peak > 0.999:
            output = output * (0.999 / final_peak)
        return output

    def play_path(self, path_value: str) -> None:
        self.stop_audio()
        audio, sr = self.load_audio(path_value)
        playback_audio = self.prepare_playback_audio(audio)
        sd.play(playback_audio, sr)
        self.current_audio = playback_audio
        self.current_sr = sr

    def play_source(self) -> None:
        self.play_path(self.current_row()["input_audio"])

    def play_original(self) -> None:
        self.play_path(self.current_row()["original_copy"])

    def play_processed(self) -> None:
        path_value = self.current_row().get("processed_audio", "").strip()
        if not path_value:
            return
        self.play_path(path_value)

    def pitch_aligned_processed_audio(self) -> tuple[np.ndarray, int] | None:
        row = self.current_row()
        processed_path = row.get("processed_audio", "").strip()
        if not processed_path:
            return None
        source_f0 = parse_float(row.get("original_f0_median_hz")) or parse_float(row.get("f0_median_hz"))
        processed_f0 = parse_float(row.get("processed_f0_median_hz"))
        if source_f0 is None or processed_f0 is None or source_f0 <= 0.0 or processed_f0 <= 0.0:
            return None

        cache_key = (processed_path, int(round(source_f0 * 1000.0)) ^ int(round(processed_f0 * 1000.0)))
        cached = self.aligned_audio_cache.get(cache_key)
        if cached is not None:
            return cached

        audio, sr = self.load_audio(processed_path)
        pitch_factor = float(source_f0 / processed_f0)
        if abs(pitch_factor - 1.0) < 0.01:
            aligned = audio
        else:
            # This helper intentionally accepts that pitch change and speed
            # change are coupled: resample the processed waveform to a new
            # length, then play it back at the original sample rate.
            aligned_target_sr = max(float(sr) / max(pitch_factor, 1e-6), 1000.0)
            aligned = librosa.resample(
                audio.astype(np.float32),
                orig_sr=float(sr),
                target_sr=aligned_target_sr,
                res_type="kaiser_best",
            )
        result = (np.asarray(aligned, dtype=np.float32), sr)
        self.aligned_audio_cache[cache_key] = result
        return result

    def play_processed_f0_aligned(self) -> None:
        aligned = self.pitch_aligned_processed_audio()
        if aligned is None:
            messagebox.showwarning("无法对齐", "当前行缺少可用的原音/处理音 F0 中位数，无法做全局变速对齐试听。")
            return
        audio, sr = aligned
        self.stop_audio()
        playback_audio = self.prepare_playback_audio(audio)
        sd.play(playback_audio, sr)
        self.current_audio = playback_audio
        self.current_sr = sr

    def play_baseline(self) -> None:
        path_value = self.current_row().get("rvc_baseline_audio", "").strip()
        if not path_value:
            return
        self.play_path(path_value)

    def stop_audio(self) -> None:
        sd.stop()
        self.current_audio = None
        self.current_sr = None

    def quick_mark(self, keep_value: str, strength_value: str | None = None) -> None:
        self.review_status_var.set(REVIEW_STATUS_LABELS["reviewed"])
        self.keep_recommendation_var.set(BOOL_LABELS[keep_value])
        if strength_value is not None:
            self.strength_fit_var.set(STRENGTH_LABELS[strength_value])

    def mark_keep(self) -> None:
        self.quick_mark("yes", "ok")
        if not self.direction_correct_var.get():
            self.direction_correct_var.set(BOOL_LABELS["yes"])
        if not self.effect_audible_var.get():
            self.effect_audible_var.set(BOOL_LABELS["yes"])
        if not self.artifact_issue_var.get():
            self.artifact_issue_var.set(ISSUE_LABELS["no"])
        self.advance_after_quick_mark()

    def mark_maybe(self) -> None:
        self.review_status_var.set(REVIEW_STATUS_LABELS["needs_check"])
        self.keep_recommendation_var.set(BOOL_LABELS["maybe"])
        self.advance_after_quick_mark()

    def mark_reject(self) -> None:
        self.quick_mark("no")
        if not self.effect_audible_var.get():
            self.effect_audible_var.set(BOOL_LABELS["no"])
        self.advance_after_quick_mark()

    def advance_after_quick_mark(self) -> None:
        self.save_form_into_row()
        self.save_rows()
        self.refresh_row_list()
        next_index = self.next_pending_index()
        if next_index is None:
            self.select_index(self.index, force=True)
            return
        self.select_index(next_index, force=True)


def main() -> None:
    args = parse_args()
    csv_path = resolve_path(args.csv)
    root = tk.Tk()
    app = ReviewApp(root, csv_path)

    def close_app() -> None:
        if app.rows:
            app.save_form_into_row()
            app.save_rows()
        app.stop_audio()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close_app)
    if args.auto_close_ms > 0:
        root.after(args.auto_close_ms, close_app)
    root.mainloop()


if __name__ == "__main__":
    main()
