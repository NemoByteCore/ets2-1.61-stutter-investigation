from __future__ import annotations

import argparse
import csv
import hashlib
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Iterable, Sequence

VERSION = "1.0.0"
RG_NAME = "NemoChainProbe161_v03_rg.csv"
FRAME_NAME = "NemoFrameLogger_v4_frames.csv"

RG_COLUMNS = [
    "event_seq", "rg_call_seq", "qpc_start", "qpc_end",
    "duration_ticks", "duration_us", "thread_id",
]
FRAME_COLUMNS = [
    "event_seq", "frame_seq", "segment_id", "qpc_start", "qpc_end",
    "duration_ticks", "duration_us", "thread_id",
]

class IntegrityError(RuntimeError):
    pass

@dataclass(frozen=True)
class RGEvent:
    event_seq: int
    call_seq: int
    start: int
    end: int
    duration_ticks: int
    duration_us: int
    thread_id: int

@dataclass(frozen=True)
class FrameEvent:
    event_seq: int
    frame_seq: int
    segment_id: int
    start: int
    end: int
    duration_ticks: int
    duration_us: int
    thread_id: int

@dataclass(frozen=True)
class OverlapItem:
    call_seq: int
    rg_duration_us: int
    overlap_ticks: int
    overlap_us: float
    thread_id: int

@dataclass(frozen=True)
class FrameAnalysis:
    frame: FrameEvent
    segment_first: bool
    rg_overlap_count: int
    rg_overlap_union_ticks: int
    rg_overlap_union_us: float
    overlap_pct: float
    residual_us: float
    max_rg_call_seq: int | None
    max_rg_duration_us: int | None
    max_rg_overlap_us: float | None
    max_rg_thread_id: int | None
    all_rg_threads_match_frame: bool | None
    rg_calls: tuple[OverlapItem, ...]

@dataclass
class ParsedStream:
    comments: list[str]
    rows: list
    qpc_freq: int
    shutdown_events: int
    shutdown_lost: int
    shutdown_segments: int | None
    qpc_start_decreases: int
    qpc_end_decreases: int
    sha256: str
    size_bytes: int

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()

def parse_common(path: Path, expected_header: Sequence[str]) -> tuple[list[str], list[list[str]]]:
    comments: list[str] = []
    data_rows: list[list[str]] = []
    header: list[str] | None = None
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for raw in f:
            line = raw.rstrip("\r\n")
            if not line:
                continue
            if line.startswith("#"):
                comments.append(line)
                continue
            parsed = next(csv.reader([line]))
            if header is None:
                header = parsed
                continue
            data_rows.append(parsed)
    if header is None:
        raise IntegrityError(f"{path.name}: missing CSV header")
    if header != list(expected_header):
        raise IntegrityError(f"{path.name}: unexpected header expected={list(expected_header)} actual={header}")
    return comments, data_rows

def extract_single_int(comments: Iterable[str], pattern: str, label: str) -> int:
    rx = re.compile(pattern)
    values: list[int] = []
    for line in comments:
        m = rx.search(line)
        if m:
            values.append(int(m.group(1)))
    if not values:
        raise IntegrityError(f"missing {label}")
    if len(set(values)) != 1:
        raise IntegrityError(f"conflicting {label}: {values}")
    return values[-1]

def parse_rg(path: Path) -> ParsedStream:
    comments, raw_rows = parse_common(path, RG_COLUMNS)
    freq = extract_single_int(comments, r"\bqpc_freq=(\d+)\b", "RG qpc_freq")
    shutdown = None
    rx = re.compile(r"^# SHUTDOWN rg_events=(\d+) rg_lost=(\d+)$")
    for line in comments:
        m = rx.match(line)
        if m:
            shutdown = (int(m.group(1)), int(m.group(2)))
    if shutdown is None:
        raise IntegrityError("RG: missing clean shutdown marker")

    rows: list[RGEvent] = []
    expected_seq = 1
    prev_start = None
    prev_end = None
    start_dec = 0
    end_dec = 0

    for values in raw_rows:
        if len(values) != len(RG_COLUMNS):
            raise IntegrityError(f"RG: malformed row at expected event_seq={expected_seq}")
        try:
            event = RGEvent(
                event_seq=int(values[0]),
                call_seq=int(values[1]),
                start=int(values[2]),
                end=int(values[3]),
                duration_ticks=int(values[4]),
                duration_us=int(values[5]),
                thread_id=int(values[6]),
            )
        except ValueError as e:
            raise IntegrityError(f"RG: non-integer field at expected event_seq={expected_seq}") from e
        if event.event_seq != expected_seq:
            raise IntegrityError(f"RG: event_seq discontinuity expected={expected_seq} got={event.event_seq}")
        if event.end < event.start:
            raise IntegrityError(f"RG event {event.event_seq}: qpc_end < qpc_start")
        if event.duration_ticks != event.end - event.start:
            raise IntegrityError(f"RG event {event.event_seq}: duration_ticks mismatch")
        expected_us = event.duration_ticks * 1_000_000 // freq
        if event.duration_us != expected_us:
            raise IntegrityError(f"RG event {event.event_seq}: duration_us mismatch stored={event.duration_us} expected={expected_us}")
        if prev_start is not None and event.start < prev_start:
            start_dec += 1
        if prev_end is not None and event.end < prev_end:
            end_dec += 1
        prev_start = event.start
        prev_end = event.end
        rows.append(event)
        expected_seq += 1

    shutdown_events, shutdown_lost = shutdown
    if shutdown_lost != 0:
        raise IntegrityError(f"RG: rg_lost={shutdown_lost}")
    if len(rows) != shutdown_events:
        raise IntegrityError(f"RG: row count {len(rows)} != shutdown rg_events {shutdown_events}")

    return ParsedStream(
        comments=comments,
        rows=rows,
        qpc_freq=freq,
        shutdown_events=shutdown_events,
        shutdown_lost=shutdown_lost,
        shutdown_segments=None,
        qpc_start_decreases=start_dec,
        qpc_end_decreases=end_dec,
        sha256=sha256_file(path),
        size_bytes=path.stat().st_size,
    )

def parse_frame(path: Path) -> ParsedStream:
    comments, raw_rows = parse_common(path, FRAME_COLUMNS)
    freq = extract_single_int(comments, r"\bqpc_freq=(\d+)\b", "frame qpc_freq")
    shutdown = None
    rx = re.compile(r"^# SHUTDOWN frame_events=(\d+) frame_lost=(\d+) segments=(\d+)$")
    for line in comments:
        m = rx.match(line)
        if m:
            shutdown = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    if shutdown is None:
        raise IntegrityError("FRAME: missing clean shutdown marker")

    rows: list[FrameEvent] = []
    expected_seq = 1
    prev_start = None
    prev_end = None
    start_dec = 0
    end_dec = 0

    for values in raw_rows:
        if len(values) != len(FRAME_COLUMNS):
            raise IntegrityError(f"FRAME: malformed row at expected event_seq={expected_seq}")
        try:
            event = FrameEvent(
                event_seq=int(values[0]),
                frame_seq=int(values[1]),
                segment_id=int(values[2]),
                start=int(values[3]),
                end=int(values[4]),
                duration_ticks=int(values[5]),
                duration_us=int(values[6]),
                thread_id=int(values[7]),
            )
        except ValueError as e:
            raise IntegrityError(f"FRAME: non-integer field at expected event_seq={expected_seq}") from e
        if event.event_seq != expected_seq:
            raise IntegrityError(f"FRAME: event_seq discontinuity expected={expected_seq} got={event.event_seq}")
        if event.end < event.start:
            raise IntegrityError(f"FRAME event {event.event_seq}: qpc_end < qpc_start")
        if event.duration_ticks != event.end - event.start:
            raise IntegrityError(f"FRAME event {event.event_seq}: duration_ticks mismatch")
        expected_us = event.duration_ticks * 1_000_000 // freq
        if event.duration_us != expected_us:
            raise IntegrityError(f"FRAME event {event.event_seq}: duration_us mismatch stored={event.duration_us} expected={expected_us}")
        if prev_start is not None and event.start < prev_start:
            start_dec += 1
        if prev_end is not None and event.end < prev_end:
            end_dec += 1
        prev_start = event.start
        prev_end = event.end
        rows.append(event)
        expected_seq += 1

    shutdown_events, shutdown_lost, shutdown_segments = shutdown
    if shutdown_lost != 0:
        raise IntegrityError(f"FRAME: frame_lost={shutdown_lost}")
    if len(rows) != shutdown_events:
        raise IntegrityError(f"FRAME: row count {len(rows)} != shutdown frame_events {shutdown_events}")
    observed_segments = len({x.segment_id for x in rows})
    if observed_segments != shutdown_segments:
        raise IntegrityError(f"FRAME: observed segment count {observed_segments} != shutdown segments {shutdown_segments}")

    return ParsedStream(
        comments=comments,
        rows=rows,
        qpc_freq=freq,
        shutdown_events=shutdown_events,
        shutdown_lost=shutdown_lost,
        shutdown_segments=shutdown_segments,
        qpc_start_decreases=start_dec,
        qpc_end_decreases=end_dec,
        sha256=sha256_file(path),
        size_bytes=path.stat().st_size,
    )

def merge_intervals(intervals: list[tuple[int, int]]) -> int:
    if not intervals:
        return 0
    intervals.sort()
    total = 0
    cur_s, cur_e = intervals[0]
    for s, e in intervals[1:]:
        if s <= cur_e:
            cur_e = max(cur_e, e)
        else:
            total += cur_e - cur_s
            cur_s, cur_e = s, e
    total += cur_e - cur_s
    return total

def analyze_frames(frames: list[FrameEvent], rg_events: list[RGEvent], freq: int) -> list[FrameAnalysis]:
    frames_sorted = sorted(frames, key=lambda x: (x.start, x.end, x.event_seq))
    rg_sorted = sorted(rg_events, key=lambda x: (x.start, x.end, x.event_seq))
    first_event_by_segment: dict[int, int] = {}
    for f in frames:
        first_event_by_segment.setdefault(f.segment_id, f.event_seq)

    out: list[FrameAnalysis] = []
    rg_floor = 0
    for f in frames_sorted:
        while rg_floor < len(rg_sorted) and rg_sorted[rg_floor].end <= f.start:
            rg_floor += 1
        idx = rg_floor
        clipped: list[tuple[int, int]] = []
        items: list[OverlapItem] = []
        while idx < len(rg_sorted) and rg_sorted[idx].start < f.end:
            r = rg_sorted[idx]
            overlap_start = max(f.start, r.start)
            overlap_end = min(f.end, r.end)
            if overlap_end > overlap_start:
                ticks = overlap_end - overlap_start
                clipped.append((overlap_start, overlap_end))
                items.append(OverlapItem(
                    call_seq=r.call_seq,
                    rg_duration_us=r.duration_us,
                    overlap_ticks=ticks,
                    overlap_us=ticks * 1_000_000.0 / freq,
                    thread_id=r.thread_id,
                ))
            idx += 1

        union_ticks = merge_intervals(clipped)
        union_us = union_ticks * 1_000_000.0 / freq
        overlap_pct = (100.0 * union_us / f.duration_us) if f.duration_us > 0 else 0.0
        residual_us = max(0.0, f.duration_us - union_us)

        if items:
            max_item = max(items, key=lambda x: (x.rg_duration_us, x.overlap_ticks))
            all_match = all(x.thread_id == f.thread_id for x in items)
            max_call = max_item.call_seq
            max_duration = max_item.rg_duration_us
            max_overlap_us = max(x.overlap_us for x in items)
            max_tid = max_item.thread_id
        else:
            all_match = None
            max_call = None
            max_duration = None
            max_overlap_us = None
            max_tid = None

        out.append(FrameAnalysis(
            frame=f,
            segment_first=(f.event_seq == first_event_by_segment[f.segment_id]),
            rg_overlap_count=len(items),
            rg_overlap_union_ticks=union_ticks,
            rg_overlap_union_us=union_us,
            overlap_pct=overlap_pct,
            residual_us=residual_us,
            max_rg_call_seq=max_call,
            max_rg_duration_us=max_duration,
            max_rg_overlap_us=max_overlap_us,
            max_rg_thread_id=max_tid,
            all_rg_threads_match_frame=all_match,
            rg_calls=tuple(items),
        ))
    return sorted(out, key=lambda x: x.frame.event_seq)

def percentile_floor(values: Sequence[float], p: float) -> float:
    if not values:
        return math.nan
    ordered = sorted(values)
    idx = math.floor((len(ordered) - 1) * p)
    return float(ordered[idx])

def fmt_ms_from_us(us: float) -> str:
    return f"{us / 1000.0:.3f}"

def fmt_num(value: float, digits: int = 3) -> str:
    if math.isnan(value):
        return "n/a"
    return f"{value:.{digits}f}"

def pearson(xs: Sequence[float], ys: Sequence[float]) -> float:
    if len(xs) != len(ys) or not xs:
        return math.nan
    mx = mean(xs)
    my = mean(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    sx = sum(x * x for x in dx)
    sy = sum(y * y for y in dy)
    if sx <= 0 or sy <= 0:
        return math.nan
    return sum(a * b for a, b in zip(dx, dy)) / math.sqrt(sx * sy)

def write_results(path: Path, analyses: list[FrameAnalysis], threshold_us: int) -> None:
    fields = [
        "event_seq","frame_seq","segment_id","segment_first","qpc_start","qpc_end",
        "frame_duration_ticks","frame_duration_us","frame_thread_id","rg_overlap_count",
        "rg_overlap_union_ticks","rg_overlap_union_us","overlap_pct","residual_us",
        "max_rg_call_seq","max_rg_duration_us","max_rg_overlap_us","max_rg_thread_id",
        "all_rg_threads_match_frame","rg_calls",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for a in analyses:
            if a.frame.duration_us < threshold_us:
                continue
            calls = ";".join(
                f"{x.call_seq}:{x.rg_duration_us}:{x.overlap_us:.3f}:{x.thread_id}"
                for x in a.rg_calls
            )
            writer.writerow({
                "event_seq": a.frame.event_seq,
                "frame_seq": a.frame.frame_seq,
                "segment_id": a.frame.segment_id,
                "segment_first": str(a.segment_first).lower(),
                "qpc_start": a.frame.start,
                "qpc_end": a.frame.end,
                "frame_duration_ticks": a.frame.duration_ticks,
                "frame_duration_us": a.frame.duration_us,
                "frame_thread_id": a.frame.thread_id,
                "rg_overlap_count": a.rg_overlap_count,
                "rg_overlap_union_ticks": a.rg_overlap_union_ticks,
                "rg_overlap_union_us": f"{a.rg_overlap_union_us:.3f}",
                "overlap_pct": f"{a.overlap_pct:.3f}",
                "residual_us": f"{a.residual_us:.3f}",
                "max_rg_call_seq": "" if a.max_rg_call_seq is None else a.max_rg_call_seq,
                "max_rg_duration_us": "" if a.max_rg_duration_us is None else a.max_rg_duration_us,
                "max_rg_overlap_us": "" if a.max_rg_overlap_us is None else f"{a.max_rg_overlap_us:.3f}",
                "max_rg_thread_id": "" if a.max_rg_thread_id is None else a.max_rg_thread_id,
                "all_rg_threads_match_frame": "" if a.all_rg_threads_match_frame is None else str(a.all_rg_threads_match_frame).lower(),
                "rg_calls": calls,
            })

def summarize_group(name: str, group: list[FrameAnalysis]) -> str:
    if not group:
        return f"| {name} | 0 | n/a | n/a | n/a | n/a |"
    frame_avg = mean(a.frame.duration_us for a in group)
    ov_avg = mean(a.rg_overlap_union_us for a in group)
    residual_avg = mean(a.residual_us for a in group)
    ge50 = sum(1 for a in group if a.overlap_pct >= 50.0)
    return f"| {name} | {len(group)} | {frame_avg/1000.0:.3f} | {ov_avg/1000.0:.3f} | {residual_avg/1000.0:.3f} | {ge50} |"

def write_summary(path: Path, capture: Path, rg: ParsedStream, frame: ParsedStream, analyses: list[FrameAnalysis], threshold_us: int, analyzer_sha: str) -> None:
    long_frames = [a for a in analyses if a.frame.duration_us >= threshold_us]
    ge33 = [a for a in analyses if a.frame.duration_us >= 33_000]
    ge50 = [a for a in analyses if a.frame.duration_us >= 50_000]
    ordinary = [a for a in analyses if a.frame.duration_us < 20_000]
    mid = [a for a in analyses if 20_000 <= a.frame.duration_us < 25_000]
    long_25_33 = [a for a in analyses if 25_000 <= a.frame.duration_us < 33_000]
    long_ge33 = [a for a in analyses if a.frame.duration_us >= 33_000]
    non_segment_first_long = [a for a in long_frames if not a.segment_first]
    first_by_segment = [a for a in analyses if a.segment_first]
    frame_us = [float(a.frame.duration_us) for a in analyses]
    overlap_us = [a.rg_overlap_union_us for a in analyses]
    residual_us = [a.residual_us for a in analyses]
    with_rg = [a for a in analyses if a.rg_overlap_count > 0]
    thread_match_count = sum(1 for a in with_rg if a.all_rg_threads_match_frame is True)
    multi_rg_count = sum(1 for a in analyses if a.rg_overlap_count > 1)
    ordinary_rg = [a.max_rg_duration_us for a in ordinary if a.max_rg_duration_us is not None]
    long_rg = [a.max_rg_duration_us for a in long_frames if a.max_rg_duration_us is not None]
    rg_duration_us = [float(x.duration_us) for x in rg.rows]

    lines: list[str] = []
    lines += ["# ETS2 exact frame/RG analysis", ""]
    lines += [f"Analyzer version: {VERSION}", f"Analyzer SHA-256: {analyzer_sha}", f"Capture: {capture}", ""]
    lines += ["## Integrity", "", "| Check | Result |", "| --- | --- |"]
    lines += [
        f"| RG SHA-256 | {rg.sha256} |",
        f"| Frame SHA-256 | {frame.sha256} |",
        f"| Shared QPC frequency | {rg.qpc_freq} |",
        f"| RG rows / shutdown events | {len(rg.rows)} / {rg.shutdown_events} |",
        f"| Frame rows / shutdown events | {len(frame.rows)} / {frame.shutdown_events} |",
        f"| RG lost | {rg.shutdown_lost} |",
        f"| Frame lost | {frame.shutdown_lost} |",
        f"| Segments | {frame.shutdown_segments} |",
        f"| RG qpc_start decreases in event_seq order | {rg.qpc_start_decreases} |",
        f"| RG qpc_end decreases in event_seq order | {rg.qpc_end_decreases} |",
        f"| Frame qpc_start decreases in event_seq order | {frame.qpc_start_decreases} |",
        f"| Frame qpc_end decreases in event_seq order | {frame.qpc_end_decreases} |",
        "",
        "All event_seq values are contiguous 1..N; row counts match clean shutdown counters; duration ticks and stored microseconds were validated against QPC.",
        "",
    ]
    lines += ["## Frame distribution", ""]
    lines += [
        f"- total frame intervals: {len(analyses)}",
        f"- >=25 ms: {len(long_frames)}",
        f"- >=33 ms: {len(ge33)}",
        f"- >=50 ms: {len(ge50)}",
        f"- p50: {fmt_ms_from_us(percentile_floor(frame_us, 0.50))} ms",
        f"- p95: {fmt_ms_from_us(percentile_floor(frame_us, 0.95))} ms",
        f"- p99: {fmt_ms_from_us(percentile_floor(frame_us, 0.99))} ms",
        "",
        "Percentiles use floor-index selection on the sorted sample: floor((N-1)*p).",
        "",
    ]
    lines += ["## RG timing", ""]
    lines += [
        f"- total RG calls: {len(rg.rows)}",
        f"- RG duration p50: {fmt_ms_from_us(percentile_floor(rg_duration_us, 0.50))} ms",
        f"- RG duration p95: {fmt_ms_from_us(percentile_floor(rg_duration_us, 0.95))} ms",
        f"- RG duration p99: {fmt_ms_from_us(percentile_floor(rg_duration_us, 0.99))} ms",
        f"- RG duration max: {fmt_ms_from_us(max(rg_duration_us))} ms",
        "",
        f"- frames with >=1 RG overlap: {len(with_rg)} / {len(analyses)}",
        f"- frames with >1 RG overlap: {multi_rg_count}",
        f"- matching frame/RG thread IDs when overlap exists: {thread_match_count} / {len(with_rg)}",
        f"- RG-overlap p50: {fmt_ms_from_us(percentile_floor(overlap_us, 0.50))} ms",
        f"- RG-overlap p95: {fmt_ms_from_us(percentile_floor(overlap_us, 0.95))} ms",
        f"- RG-overlap p99: {fmt_ms_from_us(percentile_floor(overlap_us, 0.99))} ms",
        f"- residual p50: {fmt_ms_from_us(percentile_floor(residual_us, 0.50))} ms",
        f"- residual p95: {fmt_ms_from_us(percentile_floor(residual_us, 0.95))} ms",
        f"- Pearson(frame duration, RG overlap): {fmt_num(pearson(frame_us, overlap_us), 4)}",
        f"- Pearson(frame duration, residual): {fmt_num(pearson(frame_us, residual_us), 4)}",
        "",
    ]
    lines += [
        "## Timing bins", "",
        "| Bin | N | Avg frame ms | Avg RG overlap ms | Avg residual ms | RG overlap >=50% |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
        summarize_group("<20 ms", ordinary),
        summarize_group("20-25 ms", mid),
        summarize_group("25-33 ms", long_25_33),
        summarize_group(">=33 ms", long_ge33),
        "",
    ]
    lines += ["## Ordinary vs long-frame RG", ""]
    if ordinary_rg:
        lines.append(
            f"- ordinary frames (<20 ms), overlapping RG call duration: p50 {fmt_ms_from_us(percentile_floor(ordinary_rg, 0.50))} ms, "
            f"p95 {fmt_ms_from_us(percentile_floor(ordinary_rg, 0.95))} ms, p99 {fmt_ms_from_us(percentile_floor(ordinary_rg, 0.99))} ms"
        )
    if long_rg:
        lines.append(
            f"- long frames (>=25 ms), overlapping RG call duration: p50 {fmt_ms_from_us(percentile_floor(long_rg, 0.50))} ms, "
            f"p95 {fmt_ms_from_us(percentile_floor(long_rg, 0.95))} ms, p99 {fmt_ms_from_us(percentile_floor(long_rg, 0.99))} ms"
        )
    lines += ["", "## First measured interval of each segment", ""]
    lines += ["| Segment | Frame seq | Duration ms | RG overlap ms | Residual ms |", "| ---: | ---: | ---: | ---: | ---: |"]
    for a in sorted(first_by_segment, key=lambda x: x.frame.segment_id):
        lines.append(
            f"| {a.frame.segment_id} | {a.frame.frame_seq} | {a.frame.duration_us/1000.0:.3f} | "
            f"{a.rg_overlap_union_us/1000.0:.3f} | {a.residual_us/1000.0:.3f} |"
        )
    lines += ["", "First-of-segment is a structural tag only. The analyzer does not automatically discard it.", ""]
    lines += [f"## All frame intervals >= {threshold_us/1000.0:.0f} ms", ""]
    lines += [
        "| Frame | Segment | First? | Frame ms | RG count | RG overlap ms | Overlap % | Residual ms | Max RG call | Max RG ms | Frame TID | RG TID |",
        "| ---: | ---: | :---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for a in sorted(long_frames, key=lambda x: x.frame.duration_us, reverse=True):
        lines.append(
            f"| {a.frame.frame_seq} | {a.frame.segment_id} | {'yes' if a.segment_first else 'no'} | "
            f"{a.frame.duration_us/1000.0:.3f} | {a.rg_overlap_count} | {a.rg_overlap_union_us/1000.0:.3f} | "
            f"{a.overlap_pct:.2f} | {a.residual_us/1000.0:.3f} | "
            f"{a.max_rg_call_seq if a.max_rg_call_seq is not None else ''} | {(a.max_rg_duration_us or 0)/1000.0:.3f} | "
            f"{a.frame.thread_id} | {a.max_rg_thread_id if a.max_rg_thread_id is not None else ''} |"
        )
    lines += ["", "## Threshold-only mechanical observations", ""]
    long_rg10 = [a for a in non_segment_first_long if (a.max_rg_duration_us or 0) >= 10_000]
    long_rg50pct = [a for a in non_segment_first_long if a.overlap_pct >= 50.0]
    lines += [
        f"- >=25 ms excluding first-of-segment: {len(non_segment_first_long)} intervals.",
        f"- among those, max overlapping RG >=10 ms: {len(long_rg10)} / {len(non_segment_first_long)}.",
        f"- among those, RG overlap >=50% of frame interval: {len(long_rg50pct)} / {len(non_segment_first_long)}.",
        "",
        "These are threshold counts, not causal labels. RG duration is elapsed wall time and may include execution, waiting, synchronization or scheduler preemption.",
        "",
        "## Output semantics", "",
        "RG overlap is the union of all RG intervals intersecting the frame interval. This avoids double-counting if overlapping or nested RG events ever occur.",
        "Residual = frame_start-to-frame_start duration minus RG-overlap union. It is not automatically equivalent to CPU execution outside RG.",
        "RESULTS.csv contains every frame interval at or above the configured threshold, with exact QPC overlap details and all overlapping RG call IDs.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic ETS2 exact frame/RG correlation analyzer.")
    parser.add_argument("--capture", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--long-ms", type=float, default=25.0)
    args = parser.parse_args()

    capture = args.capture.resolve()
    output = args.output.resolve()
    threshold_us = int(round(args.long_ms * 1000.0))

    if not capture.is_dir():
        raise IntegrityError(f"capture directory missing: {capture}")
    if output.exists():
        raise IntegrityError(f"output path already exists: {output}")

    rg_path = capture / RG_NAME
    frame_path = capture / FRAME_NAME
    if not rg_path.is_file():
        raise IntegrityError(f"missing {RG_NAME}")
    if not frame_path.is_file():
        raise IntegrityError(f"missing {FRAME_NAME}")

    rg = parse_rg(rg_path)
    frame = parse_frame(frame_path)
    if rg.qpc_freq != frame.qpc_freq:
        raise IntegrityError(f"QPC frequency mismatch RG={rg.qpc_freq} FRAME={frame.qpc_freq}")

    analyses = analyze_frames(list(frame.rows), list(rg.rows), rg.qpc_freq)

    output.mkdir(parents=True, exist_ok=False)
    results_path = output / "RESULTS.csv"
    summary_path = output / "SUMMARY.md"
    analyzer_sha = sha256_file(Path(__file__).resolve())

    write_results(results_path, analyses, threshold_us)
    write_summary(summary_path, capture, rg, frame, analyses, threshold_us, analyzer_sha)

    print(f"ANALYZER_VERSION={VERSION}")
    print(f"ANALYZER_SHA256={analyzer_sha}")
    print(f"CAPTURE={capture}")
    print(f"OUTPUT={output}")
    print(f"RG_EVENTS={len(rg.rows)}")
    print(f"FRAME_EVENTS={len(frame.rows)}")
    print(f"QPC_FREQ={rg.qpc_freq}")
    print(f"LONG_GE_{args.long_ms:g}MS={sum(1 for a in analyses if a.frame.duration_us >= threshold_us)}")
    print(f"RESULTS={results_path}")
    print(f"SUMMARY={summary_path}")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except IntegrityError as e:
        print(f"INTEGRITY_ERROR: {e}", file=sys.stderr)
        raise SystemExit(2)
