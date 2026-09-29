from __future__ import annotations
import argparse,csv,re,sys
from pathlib import Path

VERSION="1.0.0"
RG_NAME="NemoChainProbe161_v06_rg.csv"
FRAME_NAME="NemoFrameLogger_v4_frames.csv"

RG_HEADER=[
"event_seq","rg_call_seq","qpc_start","qpc_end","duration_ticks","duration_us","thread_id",
"t1_count","t1_ticks","t1_us","t1_max_ticks","t1_max_us","pre_t1_ticks","pre_t1_us",
"inter_t1_gap_ticks","inter_t1_gap_us","max_t1_gap_us","max_t1_gap_after_index",
"post_t1_ticks","post_t1_us","outside_t1_ticks","outside_t1_us",
"v160_count","v160_ticks","v160_us","v120_count","v120_ticks","v120_us",
"d0_count","d0_ticks","d0_us","v108_count","v108_ticks","v108_us",
"v110_count","v110_ticks","v110_us","v118_count","v118_ticks","v118_us",
"tail_union_ticks","tail_union_us"]
FRAME_HEADER=["event_seq","frame_seq","segment_id","qpc_start","qpc_end","duration_ticks","duration_us","thread_id"]
PHASES=["v160","v120","d0","v108","v110","v118"]

class IntegrityError(RuntimeError): pass

def load(path,header,name):
    comments=[]; rows=[]; got=None
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        for raw in f:
            line=raw.rstrip("\r\n")
            if not line: continue
            if line.startswith("#"):
                comments.append(line); continue
            vals=next(csv.reader([line]))
            if got is None: got=vals
            else: rows.append(vals)
    if got!=header: raise IntegrityError(f"{name}: bad header")
    freq=None
    for c in comments:
        m=re.search(r"\bqpc_freq=(\d+)\b",c)
        if m: freq=int(m.group(1))
    if not freq: raise IntegrityError(f"{name}: missing qpc_freq")
    return comments,rows,freq

def parse_rg(path):
    comments,raw,freq=load(path,RG_HEADER,"RG")
    shut=None
    for c in comments:
        m=re.match(r"^# SHUTDOWN rg_events=(\d+) rg_lost=(\d+)$",c)
        if m: shut=(int(m.group(1)),int(m.group(2)))
    if not shut or shut[1]!=0: raise IntegrityError(f"RG shutdown={shut}")
    out=[]; expected=1
    for vals in raw:
        if len(vals)!=len(RG_HEADER): raise IntegrityError(f"RG malformed seq={expected}")
        try: x={k:int(v) for k,v in zip(RG_HEADER,vals)}
        except ValueError as e: raise IntegrityError(f"RG noninteger seq={expected}") from e
        if x["event_seq"]!=expected: raise IntegrityError(f"RG seq expected={expected} got={x['event_seq']}")
        if x["qpc_end"]-x["qpc_start"]!=x["duration_ticks"]: raise IntegrityError(f"RG duration ticks seq={expected}")
        for ticks,us in [
            ("duration_ticks","duration_us"),("t1_ticks","t1_us"),("t1_max_ticks","t1_max_us"),
            ("pre_t1_ticks","pre_t1_us"),("inter_t1_gap_ticks","inter_t1_gap_us"),
            ("post_t1_ticks","post_t1_us"),("outside_t1_ticks","outside_t1_us"),
            ("v160_ticks","v160_us"),("v120_ticks","v120_us"),("d0_ticks","d0_us"),
            ("v108_ticks","v108_us"),("v110_ticks","v110_us"),("v118_ticks","v118_us"),
            ("tail_union_ticks","tail_union_us")]:
            if x[us]!=(x[ticks]*1_000_000)//freq:
                raise IntegrityError(f"RG {expected}: {us} mismatch")
        if x["t1_count"]==0:
            if x["tail_union_ticks"]!=0 or any(x[p+"_count"] or x[p+"_ticks"] for p in PHASES):
                raise IntegrityError(f"RG {expected}: tail data without T1")
        if x["tail_union_ticks"]>x["post_t1_ticks"]+100:
            raise IntegrityError(f"RG {expected}: tail union exceeds post-T1")
        out.append(x); expected+=1
    if len(out)!=shut[0]: raise IntegrityError(f"RG rows={len(out)} shutdown={shut[0]}")
    return out,freq,shut

def parse_frame(path):
    comments,raw,freq=load(path,FRAME_HEADER,"FRAME")
    shut=None
    for c in comments:
        m=re.match(r"^# SHUTDOWN frame_events=(\d+) frame_lost=(\d+) segments=(\d+)$",c)
        if m: shut=(int(m.group(1)),int(m.group(2)),int(m.group(3)))
    if not shut or shut[1]!=0: raise IntegrityError(f"FRAME shutdown={shut}")
    out=[]; expected=1
    for vals in raw:
        if len(vals)!=len(FRAME_HEADER): raise IntegrityError(f"FRAME malformed seq={expected}")
        x={k:int(v) for k,v in zip(FRAME_HEADER,vals)}
        if x["event_seq"]!=expected: raise IntegrityError(f"FRAME seq expected={expected} got={x['event_seq']}")
        if x["qpc_end"]-x["qpc_start"]!=x["duration_ticks"]: raise IntegrityError(f"FRAME ticks seq={expected}")
        if x["duration_us"]!=(x["duration_ticks"]*1_000_000)//freq: raise IntegrityError(f"FRAME us seq={expected}")
        out.append(x); expected+=1
    if len(out)!=shut[0]: raise IntegrityError("FRAME row count mismatch")
    if len({x["segment_id"] for x in out})!=shut[2]: raise IntegrityError("FRAME segment mismatch")
    return out,freq,shut

def overlap(a0,a1,b0,b1): return max(0,min(a1,b1)-max(a0,b0))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--capture",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    ap.add_argument("--long-ms",type=float,default=25.0)
    args=ap.parse_args()
    cap=args.capture.resolve(); out=args.output.resolve()
    if not cap.is_dir(): raise IntegrityError(f"capture missing: {cap}")
    if out.exists(): raise IntegrityError(f"output exists: {out}")

    rg,freq,rgsh=parse_rg(cap/RG_NAME)
    frames,ffreq,fsh=parse_frame(cap/FRAME_NAME)
    if freq!=ffreq: raise IntegrityError("QPC mismatch")
    first={}
    for f in frames: first.setdefault(f["segment_id"],f["event_seq"])
    rs=sorted(rg,key=lambda x:(x["qpc_start"],x["qpc_end"],x["event_seq"]))
    threshold=int(round(args.long_ms*1000))
    rows=[]; j=0
    for f in sorted(frames,key=lambda x:x["qpc_start"]):
        if f["duration_us"]<threshold: continue
        while j<len(rs) and rs[j]["qpc_end"]<=f["qpc_start"]: j+=1
        k=j
        while k<len(rs) and rs[k]["qpc_start"]<f["qpc_end"]:
            q=rs[k]; ot=overlap(f["qpc_start"],f["qpc_end"],q["qpc_start"],q["qpc_end"])
            if ot>0:
                phase_ticks={p:q[p+"_ticks"] for p in PHASES}
                dominant=max(PHASES,key=lambda p:phase_ticks[p])
                residual=max(0,q["post_t1_ticks"]-q["tail_union_ticks"])
                row={
                    "frame_seq":f["frame_seq"],"segment_id":f["segment_id"],
                    "segment_first":str(f["event_seq"]==first[f["segment_id"]]).lower(),
                    "frame_us":f["duration_us"],"frame_tid":f["thread_id"],
                    "rg_call_seq":q["rg_call_seq"],"rg_us":q["duration_us"],
                    "rg_overlap_us":ot*1_000_000/freq,
                    "rg_overlap_pct":100.0*(ot*1_000_000/freq)/f["duration_us"],
                    "rg_tid":q["thread_id"],"t1_us":q["t1_us"],"post_t1_us":q["post_t1_us"],
                    "tail_union_us":q["tail_union_us"],"tail_residual_us":residual*1_000_000//freq,
                    "dominant_phase":dominant,"dominant_us":q[dominant+"_us"],
                }
                for p in PHASES:
                    row[p+"_count"]=q[p+"_count"]; row[p+"_us"]=q[p+"_us"]
                rows.append(row)
            k+=1

    out.mkdir(parents=True)
    csvp=out/"RESULTS_DX11_TAIL.csv"; mdp=out/"SUMMARY_DX11_TAIL.md"
    fields=["frame_seq","segment_id","segment_first","frame_us","frame_tid","rg_call_seq","rg_us",
            "rg_overlap_us","rg_overlap_pct","rg_tid","t1_us","post_t1_us",
            "v160_count","v160_us","v120_count","v120_us","d0_count","d0_us",
            "v108_count","v108_us","v110_count","v110_us","v118_count","v118_us",
            "tail_union_us","tail_residual_us","dominant_phase","dominant_us"]
    with csvp.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for x in rows:
            y=dict(x); y["rg_overlap_us"]=f"{x['rg_overlap_us']:.3f}"; y["rg_overlap_pct"]=f"{x['rg_overlap_pct']:.3f}"
            w.writerow(y)

    lines=["# ETS2 v0.6 DX11 post-T1 tail analysis","",f"Analyzer version: {VERSION}",f"Capture: {cap}","",
           "## Integrity","",f"- RG events: {len(rg)}; lost: {rgsh[1]}",f"- FRAME events: {len(frames)}; lost: {fsh[1]}",
           f"- QPC frequency: {freq}","",
           f"## Frame intervals >= {args.long_ms:g} ms","",
           "| Frame | Seg | Frame ms | RG ms | RG % | T1 ms | Post-T1 ms | V160 | V120 | D0 | V108 | V110 | V118 | Tail union | Tail residual | Dominant |",
           "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |"]
    for x in sorted(rows,key=lambda z:z["frame_us"],reverse=True):
        lines.append(f"| {x['frame_seq']} | {x['segment_id']} | {x['frame_us']/1000:.3f} | {x['rg_us']/1000:.3f} | {x['rg_overlap_pct']:.2f} | {x['t1_us']/1000:.3f} | {x['post_t1_us']/1000:.3f} | {x['v160_us']/1000:.3f} | {x['v120_us']/1000:.3f} | {x['d0_us']/1000:.3f} | {x['v108_us']/1000:.3f} | {x['v110_us']/1000:.3f} | {x['v118_us']/1000:.3f} | {x['tail_union_us']/1000:.3f} | {x['tail_residual_us']/1000:.3f} | {x['dominant_phase']} |")
    lines += ["","Notes:",
              "- Phase totals are elapsed wall time in six validated DX11 vtable methods after the final T1 candidate.",
              "- tail_union is the union of instrumented phase intervals and avoids nested double counting.",
              "- tail_residual = post-T1 elapsed time minus tail_union.",
              "- elapsed time can include execution, synchronization, waits, or scheduler preemption."]
    mdp.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(f"OK RG={len(rg)} FRAME={len(frames)} LONG_ROWS={len(rows)}")
    print(f"RESULTS={csvp}"); print(f"SUMMARY={mdp}")

if __name__=="__main__":
    try: main()
    except IntegrityError as e:
        print("INTEGRITY_ERROR:",e,file=sys.stderr); raise SystemExit(2)