# YouTube script — ETS2 1.61 DX12 stutter investigation

**Approximate length:** 8–12 minutes  
**Original technical investigation:** NemoByteCore  
**Purpose:** creator-ready community script; adapt freely, but preserve the scope and caveats.

> Before publishing, verify the current repository in case NemoByteCore has updated wording, evidence or conclusions.

## 0:00–0:45 — Hook

**Visual:** normal ETS2 driving, FPS counter looking stable; then show a frametime spike / hitch.

**Narration:**

Euro Truck Simulator 2 can look like it is running at 60 FPS and still feel as if it freezes for a fraction of a second. Those hitches are often described as “stutter”, but that word covers many different problems.

One player, NemoByteCore, decided not to guess. He instrumented the DX12 rendering path in ETS2 1.61.1.1, correlated frame-time spikes through the renderer, and found one specific engine-side stall that he could measure and reproduce.

And the important part is this: this video is **not** claiming that he found the cause of every stutter in ETS2 or ATS. He found one concrete cause in one documented renderer path — and the evidence is public.

## 0:45–2:10 — What a PSO is and why frame time matters

**Visual:** simple diagram: frame budget 16.67 ms at 60 FPS; PSO preparation inserted in the middle.

**Narration:**

The problem involves something called a graphics Pipeline State Object, or PSO. In simple terms, a PSO packages configuration the GPU needs for a particular kind of draw operation.

If the game already has the PSO ready, that part can move quickly. But if the PSO is cold and the game creates it at the exact moment the frame needs it, that work can become expensive.

NemoByteCore localized a path where a cold PSO reaches the draw path and the game calls the creation routine with a synchronous wait.

The investigation repeatedly measured cold-PSO stalls around 10 to more than 40 milliseconds.

At 60 FPS, the entire frame budget is only 16.67 milliseconds. So a 20, 30 or 40 millisecond blocking operation can produce a visible hitch even if your average FPS counter still looks fine.

## 2:10–3:20 — The documented path

**Visual:** show the function chain from the repository.

```text
FUN_1402A06D0
  -> FUN_1402AAA60
      -> FUN_14029DD00(..., wait=1)
```

**Narration:**

This is the relevant path NemoByteCore documented in ETS2 1.61.1.1. The names are reverse-engineering identifiers, not official SCS function names.

The key detail is `wait=1`. On a cache miss, the draw path waits for the PSO task to finish before it can continue.

But then NemoByteCore found something even more interesting: the same executable already contains another route that requests PSO preparation without blocking the caller.

```text
FUN_14029E0F0
  -> FUN_14029DD00(..., wait=0)
```

So the next question became obvious: are the PSOs that later cause the slow synchronous stalls being prepared through that async route beforehand?

## 3:20–4:30 — The 27/27 result

**Visual:** large “27 / 27” and the four counters.

```text
async_total = 0
slow_total  = 27
slow_seen   = 0
slow_unseen = 27
```

**Narration:**

In the accepted final coverage run, NemoByteCore recorded 27 slow PSOs on the synchronous path.

All 27 were unseen by the monitored async preparation route before first use.

That is the 27 out of 27 result you may see people quoting.

It does **not** mean every PSO in ETS2 is affected. It means that in this measured run, every slow PSO that hit this stall path arrived there without prior observed coverage from the built-in async route.

## 4:30–5:35 — The test that looks like a fix, but is not

**Visual:** `wait=1` changes to `wait=0`; then show black-flash / missing-rendering description.

**Narration:**

NemoByteCore tested the obvious idea. What if you simply stop waiting?

He changed the relevant call from synchronous `wait=1` to asynchronous `wait=0`.

The large synchronous stalls disappeared.

But rendering broke. Cold PSOs could still be pending when the game needed them, so some drawing was skipped, producing missing rendering and black flashes.

That is why this is not a one-line player patch.

The experiment tells us something more useful: the expensive work can happen asynchronously, but it has to start early enough that the PSO is ready **before its first draw**.

## 5:35–6:25 — What is proven, and what is not

**Visual:** split screen “PROVEN / NOT PROVEN”.

**Narration:**

Here is the most important caveat.

The evidence supports a specific conclusion: NemoByteCore demonstrated an engine-side DX12 stutter class in ETS2 1.61.1.1 where cold PSO creation synchronously blocks the draw path.

The evidence does not prove that every ETS2 hitch is this bug. It does not prove ATS behaves identically. It does not prove DX11 has the same root cause. And it does not prove every performance complaint in the community comes from this one path.

That limitation does not weaken the finding. It makes it precise.

## 6:25–7:35 — The SCS forum response

**Visual:** archived forum screenshots and repository forum-evidence link.

**Narration:**

NemoByteCore then brought the investigation to the official SCS forum.

The discussion eventually focused on the absence of a game log, the thread was locked, and its title was marked “NOT A BUG”. The repository preserves screenshots and an archived copy of the exchange.

A game log can be very useful for hardware, configuration, mod and script troubleshooting. But it does not contain the profiler correlations, render-thread timings or async-coverage instrumentation used here.

So the reasonable request is not “stop asking for logs”. It is: when somebody brings function-level profiling and controlled experiments, evaluate that evidence at the technical level it was produced.

## 7:35–9:00 — What should SCS investigate?

**Visual:** quote the project’s central engineering question.

**Narration:**

At this point the engineering question is no longer simply “where does the hitch happen?”

It is: why are graphics PSOs reaching the synchronous draw path cold, while an existing asynchronous preparation mechanism is not covering those PSOs before first use?

The investigation suggests several directions SCS can evaluate internally: earlier PSO discovery and warm-up, broader use of the existing async path, persistent caching if the architecture supports it, and avoiding render-thread waits for cold PSO creation during normal driving.

The exact solution is SCS’s job because only SCS controls the engine.

## 9:00–10:10 — The wider issue

**Visual:** ETS2/ATS evolution, graphics updates, Prism3D references.

**Narration:**

This is also why the story matters beyond one DX12 code path.

SCS has publicly acknowledged the age and accumulated technical debt of its engine. That does not prove that every performance problem is caused by the same architecture, but it does make renderer modernization and frame-time consistency legitimate questions for the future of ETS2 and ATS.

The community does not need SCS to agree with every interpretation in this repository. A useful technical response could reproduce the result, refute it with evidence, fix the preparation path, or explain how the renderer is being changed.

What matters is that technical evidence receives a technical answer.

## 10:10–end — Closing and credit

**Visual:** NemoByteCore GitHub repository, evidence folders, QR/link.

**Narration:**

The original investigation was performed by NemoByteCore. His repository contains the measurements, instrumentation notes, runtime evidence, failed approaches and the exact scope of the result.

If you want to judge the case for yourself, do not rely only on this video. Read the repository.

And remember the conclusion accurately: NemoByteCore did not prove the cause of every ETS2 stutter. He demonstrated one measurable engine-side stutter class in ETS2 1.61.1.1 under DX12 — and left enough evidence for SCS, or anyone else working on the same build, to examine it.

The link to the original investigation is in the description.

---

## Description credit block

> **Original technical investigation:** NemoByteCore  
> Repository: `NemoByteCore/ets2-1.61-stutter-investigation`  
> This video/script is a community-made explanation of the public research. The repository remains the canonical technical source.
