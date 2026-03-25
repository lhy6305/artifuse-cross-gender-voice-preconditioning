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
DEFAULT_CSV = ROOT / "experiments" / "fixed_eval" / "v1" / "review_pack" / "review_queue_v1.csv"
REVIEW_OPTIONS = ["pending", "reviewed", "needs_check", "skipped"]
BOOL_OPTIONS = ["yes", "no", "maybe"]
ISSUE_OPTIONS = ["no", "slight", "yes"]

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
EVAL_BUCKET_LABELS = {
    "speech_female": "语音-女",
    "speech_male": "语音-男",
    "singing_female": "歌声-女",
    "singing_male": "歌声-男",
}
TRIAGE_LABELS = {
    "high": "高",
    "medium": "中",
    "low": "低",
}

RUBRIC_TEXT = """巡检判定速查

总原则
- 能用：干净、稳定、桶标签正确、可代表该类输入
- 不能用：明显异常、内容不对、桶标签不对、会误导后续评测

是否可用
- 能用：保留
- 不能用：淘汰

内容正常
- 能用：人声主体清楚、句子/发声完整
- 不能用：截断、空白、异常发声、主体不明

噪声问题
- 能用：无 / 轻微底噪
- 不能用：明显底噪、杂音、爆音、电流声

混响问题
- 能用：干声或轻微空间感
- 不能用：明显空洞、拖尾重、房间感强

削波可闻
- 能用：无明显爆裂感
- 不能用：刺耳、爆裂、峰值失真明显

伴奏问题
- 能用：纯人声，或背景几乎不可感知
- 不能用：伴奏、节拍、和声明显干扰

发音 / 歌词问题
- 能用：可辨、自然、无明显错乱
- 不能用：咬字怪、歌词乱、内容不可判

说话人 / 性别桶正确
- 能用：听感与数据桶一致
- 不能用：放错桶、性别感知明显不符、疑似串人

存疑时
- 标“存疑”并写一句原因
- 先别硬淘汰，留待复核"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default=str(DEFAULT_CSV), help="Queue CSV path relative to repo root or absolute path.")
    return parser.parse_args()


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def invert_mapping(mapping: dict[str, str]) -> dict[str, str]:
    return {v: k for k, v in mapping.items()}


REVIEW_STATUS_VALUES = invert_mapping(REVIEW_STATUS_LABELS)
BOOL_VALUES = invert_mapping(BOOL_LABELS)
ISSUE_VALUES = invert_mapping(ISSUE_LABELS)


class ReviewApp:
    def __init__(self, root: tk.Tk, csv_path: Path) -> None:
        self.root = root
        self.csv_path = csv_path
        self.rows, self.fieldnames = self.load_rows()
        self.index = self.first_pending_index()
        self.current_audio: np.ndarray | None = None
        self.current_sr: int | None = None
        self.is_playing = False

        self.status_text = tk.StringVar()
        self.priority_text = tk.StringVar()
        self.identity_text = tk.StringVar()
        self.feature_text = tk.StringVar()
        self.path_text = tk.StringVar()

        self.review_status_var = tk.StringVar()
        self.usable_var = tk.StringVar()
        self.content_ok_var = tk.StringVar()
        self.noise_issue_var = tk.StringVar()
        self.reverb_issue_var = tk.StringVar()
        self.clipping_audible_var = tk.StringVar()
        self.accompaniment_issue_var = tk.StringVar()
        self.pronunciation_issue_var = tk.StringVar()
        self.speaker_bucket_ok_var = tk.StringVar()
        self.reviewer_var = tk.StringVar()

        self.build_ui()
        self.bind_shortcuts()
        self.load_row_into_form()

    def load_rows(self) -> tuple[list[dict[str, str]], list[str]]:
        with self.csv_path.open("r", encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
            return rows, rows[0].keys() if rows else []

    def save_rows(self) -> None:
        with self.csv_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(self.fieldnames))
            writer.writeheader()
            writer.writerows(self.rows)

    def first_pending_index(self) -> int:
        for idx, row in enumerate(self.rows):
            if row.get("review_status", "pending") in {"pending", "待审"}:
                return idx
        return 0

    def build_ui(self) -> None:
        self.root.title("固定评测集巡检")
        self.root.geometry("1100x820")

        container = ttk.Frame(self.root, padding=10)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(container, textvariable=self.status_text, font=("Segoe UI", 12, "bold")).pack(anchor="w")
        ttk.Label(container, textvariable=self.priority_text).pack(anchor="w", pady=(4, 0))
        ttk.Label(container, textvariable=self.identity_text).pack(anchor="w", pady=(4, 0))
        ttk.Label(container, textvariable=self.feature_text, wraplength=1060, justify=tk.LEFT).pack(anchor="w", pady=(4, 0))
        ttk.Label(container, textvariable=self.path_text, wraplength=1060, justify=tk.LEFT).pack(anchor="w", pady=(4, 10))

        button_row = ttk.Frame(container)
        button_row.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(button_row, text="上一条", command=self.prev_row).pack(side=tk.LEFT)
        ttk.Button(button_row, text="下一条", command=self.next_row).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(button_row, text="下一条未审", command=self.next_pending_row).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(button_row, text="播放 / 停止", command=self.toggle_play).pack(side=tk.LEFT, padx=(20, 0))
        ttk.Button(button_row, text="标记保留", command=self.mark_keep).pack(side=tk.LEFT, padx=(20, 0))
        ttk.Button(button_row, text="标记存疑", command=self.mark_maybe).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(button_row, text="标记淘汰", command=self.mark_reject).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(button_row, text="保存", command=self.save_current_and_flush).pack(side=tk.RIGHT)

        form = ttk.Frame(container)
        form.pack(fill=tk.X, pady=(0, 10))

        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        self.make_radio_group(form, 0, 0, "巡检状态", self.review_status_var, REVIEW_OPTIONS, REVIEW_STATUS_LABELS)
        self.make_radio_group(form, 0, 1, "是否可用", self.usable_var, BOOL_OPTIONS, BOOL_LABELS)
        self.make_radio_group(form, 1, 0, "内容正常", self.content_ok_var, BOOL_OPTIONS, BOOL_LABELS)
        self.make_radio_group(form, 1, 1, "噪声问题", self.noise_issue_var, ISSUE_OPTIONS, ISSUE_LABELS)
        self.make_radio_group(form, 2, 0, "混响问题", self.reverb_issue_var, ISSUE_OPTIONS, ISSUE_LABELS)
        self.make_radio_group(form, 2, 1, "削波可闻", self.clipping_audible_var, ISSUE_OPTIONS, ISSUE_LABELS)
        self.make_radio_group(form, 3, 0, "伴奏问题", self.accompaniment_issue_var, ISSUE_OPTIONS, ISSUE_LABELS)
        self.make_radio_group(form, 3, 1, "发音 / 歌词问题", self.pronunciation_issue_var, ISSUE_OPTIONS, ISSUE_LABELS)
        self.make_radio_group(form, 4, 0, "说话人 / 性别桶正确", self.speaker_bucket_ok_var, BOOL_OPTIONS, BOOL_LABELS)

        reviewer_frame = ttk.Frame(form)
        reviewer_frame.grid(row=4, column=1, sticky="we", pady=(8, 0), padx=(16, 0))
        ttk.Label(reviewer_frame, text="审核人").pack(anchor="w")
        ttk.Entry(reviewer_frame, textvariable=self.reviewer_var, width=24).pack(anchor="w", fill=tk.X, pady=(4, 0))

        ttk.Label(container, text="审核备注").pack(anchor="w")
        self.notes_text = tk.Text(container, height=12, wrap=tk.WORD)
        self.notes_text.pack(fill=tk.BOTH, expand=True)

        rubric_frame = ttk.LabelFrame(container, text="判定标准速查", padding=8)
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
            text = label_map[option]
            ttk.Radiobutton(frame, text=text, value=text, variable=variable).pack(anchor="w")

    def bind_shortcuts(self) -> None:
        self.root.bind("<Left>", lambda _: self.prev_row())
        self.root.bind("<Right>", lambda _: self.next_row())
        self.root.bind("<space>", lambda _: self.toggle_play())
        self.root.bind("n", lambda _: self.next_pending_row())
        self.root.bind("1", lambda _: self.mark_keep())
        self.root.bind("2", lambda _: self.mark_maybe())
        self.root.bind("3", lambda _: self.mark_reject())
        self.root.bind("<Control-s>", lambda _: self.save_current_and_flush())

    def current_row(self) -> dict[str, str]:
        return self.rows[self.index]

    def load_row_into_form(self) -> None:
        if not self.rows:
            return
        row = self.current_row()
        self.status_text.set(
            f"第 {self.index + 1} / {len(self.rows)} 条 | 待审="
            f"{sum(1 for r in self.rows if r.get('review_status') in {'pending', '待审'})}"
        )
        self.priority_text.set(
            f"优先级：{TRIAGE_LABELS.get(row.get('triage_priority', ''), row.get('triage_priority', ''))} | "
            f"分数：{row.get('triage_score', '')} | 原因：{row.get('triage_reason', '')}"
        )
        self.identity_text.set(
            f"{EVAL_BUCKET_LABELS.get(row.get('eval_bucket', ''), row.get('eval_bucket', ''))} | "
            f"{row.get('dataset_name', '')} | {row.get('speaker_id', '')} | "
            f"{row.get('utt_id', '')} | {row.get('duration_sec', '')} 秒"
        )
        self.feature_text.set(
            f"均方根={row.get('rms_dbfs', '')} dBFS | 峰值={row.get('peak_dbfs', '')} dBFS | "
            f"静音比40dB={row.get('silence_ratio_40db', '')} | 有声比={row.get('f0_voiced_ratio', '')} | "
            f"F0中位数={row.get('f0_median_hz', '')} Hz | 特征状态={row.get('feature_status', '')}"
        )
        self.path_text.set(row.get("path_raw", ""))

        review_status = row.get("review_status") or "pending"
        usable_for_fixed_eval = row.get("usable_for_fixed_eval") or "yes"
        content_ok = row.get("content_ok") or "yes"
        noise_issue = row.get("noise_issue") or "no"
        reverb_issue = row.get("reverb_issue") or "no"
        clipping_audible = row.get("clipping_audible") or "no"
        accompaniment_issue = row.get("accompaniment_issue") or "no"
        pronunciation_issue = row.get("pronunciation_or_lyric_issue") or "no"
        speaker_bucket_ok = row.get("speaker_or_gender_bucket_ok") or "yes"

        self.review_status_var.set(REVIEW_STATUS_LABELS.get(review_status, review_status))
        self.usable_var.set(BOOL_LABELS.get(usable_for_fixed_eval, BOOL_LABELS["yes"]))
        self.content_ok_var.set(BOOL_LABELS.get(content_ok, BOOL_LABELS["yes"]))
        self.noise_issue_var.set(ISSUE_LABELS.get(noise_issue, ISSUE_LABELS["no"]))
        self.reverb_issue_var.set(ISSUE_LABELS.get(reverb_issue, ISSUE_LABELS["no"]))
        self.clipping_audible_var.set(ISSUE_LABELS.get(clipping_audible, ISSUE_LABELS["no"]))
        self.accompaniment_issue_var.set(ISSUE_LABELS.get(accompaniment_issue, ISSUE_LABELS["no"]))
        self.pronunciation_issue_var.set(ISSUE_LABELS.get(pronunciation_issue, ISSUE_LABELS["no"]))
        self.speaker_bucket_ok_var.set(BOOL_LABELS.get(speaker_bucket_ok, BOOL_LABELS["yes"]))
        self.reviewer_var.set(row.get("reviewer", ""))

        self.notes_text.delete("1.0", tk.END)
        self.notes_text.insert("1.0", row.get("review_notes", ""))
        self.stop_audio()

    def save_form_into_row(self) -> None:
        row = self.current_row()
        row["review_status"] = REVIEW_STATUS_VALUES.get(self.review_status_var.get(), self.review_status_var.get())
        row["usable_for_fixed_eval"] = BOOL_VALUES.get(self.usable_var.get(), self.usable_var.get())
        row["content_ok"] = BOOL_VALUES.get(self.content_ok_var.get(), self.content_ok_var.get())
        row["noise_issue"] = ISSUE_VALUES.get(self.noise_issue_var.get(), self.noise_issue_var.get())
        row["reverb_issue"] = ISSUE_VALUES.get(self.reverb_issue_var.get(), self.reverb_issue_var.get())
        row["clipping_audible"] = ISSUE_VALUES.get(self.clipping_audible_var.get(), self.clipping_audible_var.get())
        row["accompaniment_issue"] = ISSUE_VALUES.get(self.accompaniment_issue_var.get(), self.accompaniment_issue_var.get())
        row["pronunciation_or_lyric_issue"] = ISSUE_VALUES.get(self.pronunciation_issue_var.get(), self.pronunciation_issue_var.get())
        row["speaker_or_gender_bucket_ok"] = BOOL_VALUES.get(self.speaker_bucket_ok_var.get(), self.speaker_bucket_ok_var.get())
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

    def audio_path(self) -> Path:
        return resolve_path(self.current_row()["path_raw"])

    def ensure_audio_loaded(self) -> None:
        if self.current_audio is not None and self.current_sr is not None:
            return
        audio, sr = sf.read(self.audio_path(), always_2d=False)
        audio = np.asarray(audio, dtype=np.float32)
        if audio.ndim == 2:
            audio = audio.mean(axis=1)
        peak = np.max(np.abs(audio))
        if peak > 1.0:
            audio = audio / peak
        self.current_audio = audio
        self.current_sr = sr

    def toggle_play(self) -> None:
        if self.is_playing:
            self.stop_audio()
            return
        self.ensure_audio_loaded()
        if self.current_audio is None or self.current_sr is None:
            return
        sd.play(self.current_audio, self.current_sr)
        self.is_playing = True

    def stop_audio(self) -> None:
        sd.stop()
        self.is_playing = False
        self.current_audio = None
        self.current_sr = None

    def quick_mark(self, usable: str) -> None:
        self.review_status_var.set(REVIEW_STATUS_LABELS["reviewed"])
        self.usable_var.set(BOOL_LABELS[usable])
        if not self.content_ok_var.get():
            self.content_ok_var.set(BOOL_LABELS["yes"])

    def mark_keep(self) -> None:
        self.quick_mark("yes")
        self.next_row()

    def mark_maybe(self) -> None:
        self.quick_mark("maybe")
        self.next_row()

    def mark_reject(self) -> None:
        self.quick_mark("no")
        self.next_row()


def main() -> None:
    args = parse_args()
    csv_path = resolve_path(args.csv)
    root = tk.Tk()
    app = ReviewApp(root, csv_path)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.save_form_into_row(), app.save_rows(), app.stop_audio(), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main()
