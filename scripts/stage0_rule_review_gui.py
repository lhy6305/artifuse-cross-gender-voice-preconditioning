from __future__ import annotations

import argparse
import csv
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

import numpy as np
import sounddevice as sd
import soundfile as sf


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = ROOT / "tmp" / "stage0_rule_listening_pack" / "v1" / "listening_review_queue.csv"
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

RUBRIC_TEXT = """规则试听量化口径

主方向
- 主指标：delta_log_centroid_minus_log_f0
- feminine / brightness_up：期望为正
- masculine / brightness_down：期望为负
- 主方向建议线：|主指标| >= 0.015 视为有方向，>= 0.030 视为更明显

改变量
- 同时看 spectral centroid 与频带占比变化
- high_band 规则优先看 brilliance share 是否上升
- low_band 规则优先看 low_mid share 是否下降

保真代价
- F0 漂移建议 <= 3%
- RMS 漂移建议 <= 1.5 dB
- voiced ratio 漂移建议 <= 0.08
- clipping increase 建议接近 0

人工结论
- direction_correct：方向对不对
- effect_audible：听感是否可辨
- artifact_issue：是否引入伪影/失真
- strength_fit：太弱 / 合适 / 过强
- keep_recommendation：是否保留到下一轮规则表"""


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


class ReviewApp:
    def __init__(self, root: tk.Tk, csv_path: Path) -> None:
        self.root = root
        self.csv_path = csv_path
        self.rows, self.fieldnames = self.load_rows()
        self.index = self.first_pending_index()
        self.current_audio: np.ndarray | None = None
        self.current_sr: int | None = None

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
        self.reviewer_var = tk.StringVar()
        self.normalize_peak_var = tk.BooleanVar(value=True)
        self.volume_scale_var = tk.DoubleVar(value=1.0)

        self.build_ui()
        self.bind_shortcuts()
        self.load_row_into_form()

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
        self.root.title("Stage0 规则试听审阅")
        self.root.geometry("1280x920")

        container = ttk.Frame(self.root, padding=10)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(container, textvariable=self.status_text, font=("Segoe UI", 12, "bold")).pack(anchor="w")
        ttk.Label(container, textvariable=self.identity_text, wraplength=1230, justify=tk.LEFT).pack(anchor="w", pady=(4, 0))
        ttk.Label(container, textvariable=self.rule_text, wraplength=1230, justify=tk.LEFT).pack(anchor="w", pady=(4, 0))
        ttk.Label(container, textvariable=self.auto_text, wraplength=1230, justify=tk.LEFT).pack(anchor="w", pady=(4, 0))
        ttk.Label(container, textvariable=self.metric_text, wraplength=1230, justify=tk.LEFT).pack(anchor="w", pady=(4, 0))
        ttk.Label(container, textvariable=self.path_text, wraplength=1230, justify=tk.LEFT).pack(anchor="w", pady=(4, 10))

        button_row = ttk.Frame(container)
        button_row.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(button_row, text="上一条", command=self.prev_row).pack(side=tk.LEFT)
        ttk.Button(button_row, text="下一条", command=self.next_row).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(button_row, text="下一条未审", command=self.next_pending_row).pack(side=tk.LEFT, padx=(6, 0))
        self.source_button = ttk.Button(button_row, text="播放源音频", command=self.play_source)
        self.source_button.pack(side=tk.LEFT, padx=(20, 0))
        self.original_button = ttk.Button(button_row, text="播放原音", command=self.play_original)
        self.original_button.pack(side=tk.LEFT, padx=(6, 0))
        self.processed_button = ttk.Button(button_row, text="播放处理音", command=self.play_processed)
        self.processed_button.pack(side=tk.LEFT, padx=(6, 0))
        self.baseline_button = ttk.Button(button_row, text="播放raw->RVC", command=self.play_baseline)
        self.baseline_button.pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(button_row, text="停止", command=self.stop_audio).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(button_row, text="标记保留", command=self.mark_keep).pack(side=tk.LEFT, padx=(20, 0))
        ttk.Button(button_row, text="标记待复核", command=self.mark_maybe).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(button_row, text="标记淘汰", command=self.mark_reject).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(button_row, text="保存", command=self.save_current_and_flush).pack(side=tk.RIGHT)

        playback_row = ttk.Frame(container)
        playback_row.pack(fill=tk.X, pady=(0, 10))
        ttk.Checkbutton(
            playback_row,
            text="播放时按片段峰值归一化",
            variable=self.normalize_peak_var,
            command=self.update_playback_text,
        ).pack(side=tk.LEFT)
        ttk.Label(playback_row, text="音量").pack(side=tk.LEFT, padx=(16, 6))
        volume_scale = ttk.Scale(
            playback_row,
            from_=0.25,
            to=2.0,
            variable=self.volume_scale_var,
            orient=tk.HORIZONTAL,
            command=lambda _value: self.update_playback_text(),
        )
        volume_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(playback_row, textvariable=self.playback_text, width=22).pack(side=tk.LEFT, padx=(10, 0))

        form = ttk.Frame(container)
        form.pack(fill=tk.X, pady=(0, 10))
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        self.make_radio_group(form, 0, 0, "巡检状态", self.review_status_var, REVIEW_OPTIONS, REVIEW_STATUS_LABELS)
        self.make_radio_group(form, 0, 1, "方向正确", self.direction_correct_var, BOOL_OPTIONS, BOOL_LABELS)
        self.make_radio_group(form, 1, 0, "效果可辨", self.effect_audible_var, BOOL_OPTIONS, BOOL_LABELS)
        self.make_radio_group(form, 1, 1, "伪影 / 失真", self.artifact_issue_var, ISSUE_OPTIONS, ISSUE_LABELS)
        self.make_radio_group(form, 2, 0, "强度是否合适", self.strength_fit_var, STRENGTH_OPTIONS, STRENGTH_LABELS)
        self.make_radio_group(form, 2, 1, "是否保留规则", self.keep_recommendation_var, BOOL_OPTIONS, BOOL_LABELS)

        reviewer_frame = ttk.Frame(form)
        reviewer_frame.grid(row=3, column=0, sticky="we", pady=(8, 0))
        ttk.Label(reviewer_frame, text="审核人").pack(anchor="w")
        ttk.Entry(reviewer_frame, textvariable=self.reviewer_var, width=24).pack(anchor="w", fill=tk.X, pady=(4, 0))

        ttk.Label(container, text="审核备注").pack(anchor="w")
        self.notes_text = tk.Text(container, height=10, wrap=tk.WORD)
        self.notes_text.pack(fill=tk.BOTH, expand=True)

        rubric_frame = ttk.LabelFrame(container, text="量化标准速查", padding=8)
        rubric_frame.pack(fill=tk.BOTH, expand=False, pady=(10, 0))
        rubric_text = tk.Text(rubric_frame, height=18, wrap=tk.WORD)
        rubric_text.pack(fill=tk.BOTH, expand=True)
        rubric_text.insert("1.0", RUBRIC_TEXT)
        rubric_text.configure(state=tk.DISABLED)

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

    def bind_shortcuts(self) -> None:
        self.root.bind("<Left>", lambda _: self.prev_row())
        self.root.bind("<Right>", lambda _: self.next_row())
        self.root.bind("n", lambda _: self.next_pending_row())
        self.root.bind("e", lambda _: self.play_source())
        self.root.bind("q", lambda _: self.play_original())
        self.root.bind("w", lambda _: self.play_processed())
        self.root.bind("r", lambda _: self.play_baseline())
        self.root.bind("<space>", lambda _: self.stop_audio())
        self.root.bind("1", lambda _: self.mark_keep())
        self.root.bind("2", lambda _: self.mark_maybe())
        self.root.bind("3", lambda _: self.mark_reject())
        self.root.bind("<Control-s>", lambda _: self.save_current_and_flush())

    def current_row(self) -> dict[str, str]:
        return self.rows[self.index]

    def update_playback_text(self) -> None:
        normalize_text = "on" if self.normalize_peak_var.get() else "off"
        volume_percent = int(round(self.volume_scale_var.get() * 100.0))
        self.playback_text.set(f"normalize={normalize_text} | volume={volume_percent}%")

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
            self.original_button.configure(text="播放修正后音频")
            self.processed_button.configure(text="播放RVC输出")
            self.baseline_button.configure(text="播放raw->RVC", state=tk.NORMAL)
            self.path_text.set(
                f"source={row.get('input_audio', '')}\n"
                f"preconditioned={row.get('original_copy', '')}\n"
                f"rvc_output={row.get('processed_audio', '')}\n"
                f"raw_rvc_baseline={row.get('rvc_baseline_audio', '')}"
            )
        else:
            self.original_button.configure(text="播放原音")
            self.processed_button.configure(text="播放处理音")
            self.baseline_button.configure(text="raw->RVC仅限stage1", state=tk.DISABLED)
            self.path_text.set(
                f"source={row.get('input_audio', '')}\n"
                f"original={row.get('original_copy', '')}\n"
                f"processed={row.get('processed_audio', '')}"
            )

        self.review_status_var.set(REVIEW_STATUS_LABELS.get(row.get("review_status", "pending"), "待审"))
        self.direction_correct_var.set(BOOL_LABELS.get(row.get("direction_correct", ""), row.get("direction_correct", "")))
        self.effect_audible_var.set(BOOL_LABELS.get(row.get("effect_audible", ""), row.get("effect_audible", "")))
        self.artifact_issue_var.set(ISSUE_LABELS.get(row.get("artifact_issue", ""), row.get("artifact_issue", "")))
        self.strength_fit_var.set(STRENGTH_LABELS.get(row.get("strength_fit", ""), row.get("strength_fit", "")))
        self.keep_recommendation_var.set(BOOL_LABELS.get(row.get("keep_recommendation", ""), row.get("keep_recommendation", "")))
        self.reviewer_var.set(row.get("reviewer", ""))

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
        row["reviewer"] = self.reviewer_var.get()
        row["review_notes"] = self.notes_text.get("1.0", tk.END).strip()

    def save_current_and_flush(self) -> None:
        self.save_form_into_row()
        self.save_rows()
        messagebox.showinfo("已保存", f"已保存到 {self.csv_path}")
        self.load_row_into_form()

    def move_to_index(self, new_index: int) -> None:
        if not self.rows:
            return
        self.save_form_into_row()
        self.index = max(0, min(len(self.rows) - 1, new_index))
        self.save_rows()
        self.load_row_into_form()

    def prev_row(self) -> None:
        self.move_to_index(self.index - 1)

    def next_row(self) -> None:
        self.move_to_index(self.index + 1)

    def next_pending_row(self) -> None:
        self.save_form_into_row()
        start = self.index + 1
        for idx in range(start, len(self.rows)):
            if self.rows[idx].get("review_status") in {"pending", "待审"}:
                self.index = idx
                self.save_rows()
                self.load_row_into_form()
                return
        messagebox.showinfo("下一条未审", "后面没有未审样本了。")

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
            peak = 0.9
        elif peak > 1.0:
            output = output / peak
            peak = 1.0

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
        self.play_path(self.current_row()["processed_audio"])

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
        self.next_row()

    def mark_maybe(self) -> None:
        self.review_status_var.set(REVIEW_STATUS_LABELS["needs_check"])
        self.keep_recommendation_var.set(BOOL_LABELS["maybe"])
        self.next_row()

    def mark_reject(self) -> None:
        self.quick_mark("no")
        if not self.effect_audible_var.get():
            self.effect_audible_var.set(BOOL_LABELS["no"])
        self.next_row()


def main() -> None:
    args = parse_args()
    csv_path = resolve_path(args.csv)
    root = tk.Tk()
    app = ReviewApp(root, csv_path)

    def close_app() -> None:
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
