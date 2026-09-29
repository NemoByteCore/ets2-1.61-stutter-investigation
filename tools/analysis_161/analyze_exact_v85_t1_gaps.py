from __future__ import annotations

import argparse
import csv
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path

VERSION="1.0.0"
RG_NAME="NemoChainProbe161_v05_rg.csv"
FRAME_NAME="NemoFrameLogger_v4_frames.csv"

RG_HEADER=[
    "event_seq","rg_call_seq","qpc_start","qpc_end","duration_ticks","duration_us",
    "thread_id","t1_count","t1_ticks","t1_us","t1_max_ticks","t1_max_us",
    "pre_t1_ticks","pre_t1_us","inter_t1_gap_ticks","inter_t1_gap_us",
    "max_t1_gap_us","max_t1_gap_after_index","post_t1_ticks","post_t1_us",
    "outside_t1_ticks","outside_t1_us"
]
FRAME_HEADER=[
    "event_seq","frame_seq","segment_id","qpc_start","qpc_end",
    "duration_ticks","duration_us","thread_id"
]

class IntegrityError(RuntimeError):
    pass

@dataclass(frozen=True)
class RG:
    event_seq:int
    call_seq:int
    start:int
    end:int
    ticks:int
    us:int
    tid:int
    t1_count:int
    t1_ticks:int
    t1_us:int
    t1_max_ticks:int
    t1_max_us:int
    pre_t1_ticks:int
    pre_t1_us:int
    inter_gap_ticks:int
    inter_gap_us:int
    max_gap_us:int
    max_gap_after_index:int
    post_t1_ticks:int
    post_t1_us:int
    outside_t1_ticks:int
    outside_t1_us:int

@dataclass(frozen=True)
class Frame:
    event_seq:int
    frame_seq:int
    segment_id:int
    start:int
    end:int
    ticks:int
    us:int
    tid:int

def read_csv(path:Path, expected_header:list[str], stream:str):
    comments=[]
    rows=[]
    header=None
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        for raw in f:
            line=raw.rstrip("\r\n")
            if not line:
                continue
            if line.startswith("#"):
                comments.append(line)
                continue
            vals=next(csv.reader([line]))
            if header is None:
                header=vals
            else:
                rows.append(vals)
    if header!=expected_header:
        raise IntegrityError(f"{stream}: unexpected header {header}")
    return comments,rows

def get_freq(comments,stream):
    vals=[]
    for line in comments:
        m=re.search(r"\bqpc_freq=(\d+)\b",line)
        if m:
            vals.append(int(m.group(1)))
    if not vals:
        raise IntegrityError(f"{stream}: missing qpc_freq")
    if len(set(vals))!=1:
        raise IntegrityError(f"{stream}: conflicting qpc_freq {vals}")
    return vals[-1]

def parse_rg(path:Path):
    comments,raw=read_csv(path,RG_HEADER,"RG")
    freq=get_freq(comments,"RG")
    shutdown=None
    for line in comments:
        m=re.match(r"^# SHUTDOWN rg_events=(\d+) rg_lost=(\d+)$",line)
        if m:
            shutdown=(int(m.group(1)),int(m.group(2)))
    if shutdown is None:
        raise IntegrityError("RG: missing shutdown")
    if shutdown[1]!=0:
        raise IntegrityError(f"RG: rg_lost={shutdown[1]}")

    out=[]
    expected=1
    for vals in raw:
        if len(vals)!=len(RG_HEADER):
            raise IntegrityError(f"RG: malformed row expected seq={expected}")
        try:
            x=[int(v) for v in vals]
        except ValueError as exc:
            raise IntegrityError(f"RG: non-integer row expected seq={expected}") from exc
        e=RG(*x)
        if e.event_seq!=expected:
            raise IntegrityError(f"RG: event_seq expected={expected} got={e.event_seq}")
        if e.end-e.start!=e.ticks:
            raise IntegrityError(f"RG {e.event_seq}: duration ticks mismatch")
        if e.us!=(e.ticks*1_000_000)//freq:
            raise IntegrityError(f"RG {e.event_seq}: duration_us mismatch")
        if e.t1_us!=(e.t1_ticks*1_000_000)//freq:
            raise IntegrityError(f"RG {e.event_seq}: t1_us mismatch")
        if e.t1_max_us!=(e.t1_max_ticks*1_000_000)//freq:
            raise IntegrityError(f"RG {e.event_seq}: t1_max_us mismatch")
        if e.pre_t1_us!=(e.pre_t1_ticks*1_000_000)//freq:
            raise IntegrityError(f"RG {e.event_seq}: pre_t1_us mismatch")
        if e.inter_gap_us!=(e.inter_gap_ticks*1_000_000)//freq:
            raise IntegrityError(f"RG {e.event_seq}: inter_t1_gap_us mismatch")
        if e.post_t1_us!=(e.post_t1_ticks*1_000_000)//freq:
            raise IntegrityError(f"RG {e.event_seq}: post_t1_us mismatch")
        if e.outside_t1_us!=(e.outside_t1_ticks*1_000_000)//freq:
            raise IntegrityError(f"RG {e.event_seq}: outside_t1_us mismatch")
        if e.t1_count==0:
            if any((e.t1_ticks,e.t1_max_ticks,e.pre_t1_ticks,e.inter_gap_ticks,e.max_gap_us,e.post_t1_ticks)):
                raise IntegrityError(f"RG {e.event_seq}: nonzero T1 topology with t1_count=0")
        else:
            topo=e.pre_t1_ticks+e.inter_gap_ticks+e.post_t1_ticks
            delta=abs(topo-e.outside_t1_ticks)
            if delta>10:
                raise IntegrityError(
                    f"RG {e.event_seq}: topology mismatch outside={e.outside_t1_ticks} components={topo}"
                )
        out.append(e)
        expected+=1

    if len(out)!=shutdown[0]:
        raise IntegrityError(f"RG: rows={len(out)} shutdown={shutdown[0]}")
    return out,freq,shutdown

def parse_frame(path:Path):
    comments,raw=read_csv(path,FRAME_HEADER,"FRAME")
    freq=get_freq(comments,"FRAME")
    shutdown=None
    for line in comments:
        m=re.match(r"^# SHUTDOWN frame_events=(\d+) frame_lost=(\d+) segments=(\d+)$",line)
        if m:
            shutdown=(int(m.group(1)),int(m.group(2)),int(m.group(3)))
    if shutdown is None:
        raise IntegrityError("FRAME: missing shutdown")
    if shutdown[1]!=0:
        raise IntegrityError(f"FRAME: frame_lost={shutdown[1]}")

    out=[]
    expected=1
    for vals in raw:
        if len(vals)!=len(FRAME_HEADER):
            raise IntegrityError(f"FRAME: malformed row expected seq={expected}")
        try:
            e=Frame(*(int(v) for v in vals))
        except ValueError as exc:
            raise IntegrityError(f"FRAME: non-integer row expected seq={expected}") from exc
        if e.event_seq!=expected:
            raise IntegrityError(f"FRAME: event_seq expected={expected} got={e.event_seq}")
        if e.end-e.start!=e.ticks:
            raise IntegrityError(f"FRAME {e.event_seq}: duration ticks mismatch")
        if e.us!=(e.ticks*1_000_000)//freq:
            raise IntegrityError(f"FRAME {e.event_seq}: duration_us mismatch")
        out.append(e)
        expected+=1

    if len(out)!=shutdown[0]:
        raise IntegrityError(f"FRAME: rows={len(out)} shutdown={shutdown[0]}")
    if len({x.segment_id for x in out})!=shutdown[2]:
        raise IntegrityError("FRAME: segment count mismatch")
    return out,freq,shutdown

def overlap(a0,a1,b0,b1):
    return max(0,min(a1,b1)-max(a0,b0))

def main():
    ap=argparse.ArgumentParser(description="ETS2 v0.5 exact RG/T1-gap analyzer")
    ap.add_argument("--capture",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    ap.add_argument("--long-ms",type=float,default=25.0)
    args=ap.parse_args()

    cap=args.capture.resolve()
    out=args.output.resolve()
    if not cap.is_dir():
        raise IntegrityError(f"capture missing: {cap}")
    if out.exists():
        raise IntegrityError(f"output exists: {out}")

    rg,freq,rgsh=parse_rg(cap/RG_NAME)
    frames,ffreq,fsh=parse_frame(cap/FRAME_NAME)
    if freq!=ffreq:
        raise IntegrityError(f"QPC mismatch RG={freq} FRAME={ffreq}")

    first={}
    for f in frames:
        first.setdefault(f.segment_id,f.event_seq)

    rg_sorted=sorted(rg,key=lambda x:(x.start,x.end,x.event_seq))
    threshold=int(round(args.long_ms*1000))
    rows=[]
    j=0
    for f in sorted(frames,key=lambda x:x.start):
        if f.us<threshold:
            continue
        while j<len(rg_sorted) and rg_sorted[j].end<=f.start:
            j+=1
        k=j
        while k<len(rg_sorted) and rg_sorted[k].start<f.end:
            r=rg_sorted[k]
            ot=overlap(f.start,f.end,r.start,r.end)
            if ot>0:
                rows.append({
                    "frame_seq":f.frame_seq,
                    "segment_id":f.segment_id,
                    "segment_first":str(f.event_seq==first[f.segment_id]).lower(),
                    "frame_us":f.us,
                    "frame_tid":f.tid,
                    "rg_call_seq":r.call_seq,
                    "rg_us":r.us,
                    "rg_overlap_us":ot*1_000_000/freq,
                    "rg_overlap_pct":100.0*(ot*1_000_000/freq)/f.us,
                    "rg_tid":r.tid,
                    "t1_count":r.t1_count,
                    "t1_us":r.t1_us,
                    "t1_max_us":r.t1_max_us,
                    "pre_t1_us":r.pre_t1_us,
                    "inter_t1_gap_us":r.inter_gap_us,
                    "max_t1_gap_us":r.max_gap_us,
                    "max_t1_gap_after_index":r.max_gap_after_index,
                    "post_t1_us":r.post_t1_us,
                    "outside_t1_us":r.outside_t1_us,
                })
            k+=1

    out.mkdir(parents=True)
    csv_path=out/"RESULTS_T1_GAPS.csv"
    md_path=out/"SUMMARY_T1_GAPS.md"

    fields=[
        "frame_seq","segment_id","segment_first","frame_us","frame_tid",
        "rg_call_seq","rg_us","rg_overlap_us","rg_overlap_pct","rg_tid",
        "t1_count","t1_us","t1_max_us","pre_t1_us","inter_t1_gap_us",
        "max_t1_gap_us","max_t1_gap_after_index","post_t1_us","outside_t1_us"
    ]
    with csv_path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        for x in rows:
            y=dict(x)
            y["rg_overlap_us"]=f"{x['rg_overlap_us']:.3f}"
            y["rg_overlap_pct"]=f"{x['rg_overlap_pct']:.3f}"
            w.writerow(y)

    lines=[
        "# ETS2 v0.5 exact RG / T1-gap analysis","",
        f"Analyzer version: {VERSION}",
        f"Capture: {cap}","",
        "## Integrity","",
        f"- RG events: {len(rg)}; lost: {rgsh[1]}",
        f"- FRAME events: {len(frames)}; lost: {fsh[1]}",
        f"- QPC frequency: {freq}","",
        f"## Frame intervals >= {args.long_ms:g} ms","",
        "| Frame | Seg | First | Frame ms | RG call | RG ms | RG overlap % | T1 count | T1 ms | Max T1 ms | Pre-T1 ms | Inter-T1 gaps ms | Max gap ms | Gap after T1 # | Post-T1 ms | Outside T1 ms |",
        "| ---: | ---: | :---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"
    ]
    for x in sorted(rows,key=lambda z:z["frame_us"],reverse=True):
        lines.append(
            f"| {x['frame_seq']} | {x['segment_id']} | {x['segment_first']} | "
            f"{x['frame_us']/1000:.3f} | {x['rg_call_seq']} | {x['rg_us']/1000:.3f} | "
            f"{x['rg_overlap_pct']:.2f} | {x['t1_count']} | {x['t1_us']/1000:.3f} | "
            f"{x['t1_max_us']/1000:.3f} | {x['pre_t1_us']/1000:.3f} | "
            f"{x['inter_t1_gap_us']/1000:.3f} | {x['max_t1_gap_us']/1000:.3f} | "
            f"{x['max_t1_gap_after_index']} | {x['post_t1_us']/1000:.3f} | "
            f"{x['outside_t1_us']/1000:.3f} |"
        )
    lines += [
        "",
        "Interpretation guide:",
        "- pre-T1 = RG start to first T1 start.",
        "- inter-T1 gaps = total elapsed time between consecutive T1 calls.",
        "- max gap = largest single interval between T1 calls.",
        "- post-T1 = last T1 end to RG end.",
        "- outside T1 = full RG elapsed minus exact T1 elapsed.",
        "- these are wall-time intervals; a gap can contain CPU work, waits, synchronization or preemption."
    ]
    md_path.write_text("\n".join(lines)+"\n",encoding="utf-8")

    print(f"OK RG={len(rg)} FRAME={len(frames)} LONG_ROWS={len(rows)}")
    print(f"RESULTS={csv_path}")
    print(f"SUMMARY={md_path}")

if __name__=="__main__":
    try:
        main()
    except IntegrityError as exc:
        print(f"INTEGRITY_ERROR: {exc}",file=sys.stderr)
        raise SystemExit(2)