# They spent years selling you DLC for an engine they refuse to fix. And when I proved it, they locked the thread and tagged it [NOT A BUG].

This is not a bug report. This is a story about what happens when a player does the work the developers should have done, hands them the results for free, and gets a green stamp and a locked thread in return.

If you play Euro Truck Simulator 2 or American Truck Simulator, this concerns you, even if you have never opened a config file in your life. So let me start with the simple version. No jargon, no function names. Just what happened.

## The short version

ETS2 stutters. Not for everyone, but for a lot of people, especially on newer hardware. The game can show 60 FPS and still hitch visibly every few seconds. It feels like micro-freezes when you drive. You are cruising along, and suddenly the game freezes for a fraction of a second. You cannot steer, you cannot brake, you just wait for it to come back. It happens again a minute later. And again. And again.

For some people, it is bad enough that the game is unplayable. For others, it is "just" annoying. But it is there, it is reproducible, and it has been reported for years.

I spent weeks investigating why. Not guessing from Task Manager. Not blaming my own hardware. Actually investigating. I instrumented the DX12 render path in ETS2 1.61.1.1, correlated frame-time spikes down through the render graph, and traced the dominant stall class to a specific piece of code.

What I found was this: the game engine compiles shaders in a way that blocks the main render thread. In plain English, the game stops everything it is doing to prepare graphics for the next frame, and it does this while you are driving, causing a visible hitch every single time.

I did not stop there. I measured it. I documented it. I found that the engine already has a system for preparing shaders in the background, before they are needed. That system exists in the game right now. But it is not being used for the shaders that cause the stutter. I measured 27 out of 27 slow shader compilations reaching the first frame they were needed on without ever going through the existing background system. So they blocked the render thread instead.

I tried the obvious fix. Changing the synchronous wait to asynchronous removed the big stalls, but caused missing frames and black flashes. So the answer is not a config tweak. The answer is to wire the existing background system into the path that needs it. Which is an engine-side job.

Then I posted everything on the official SCS forum.

SCS's response, in order:

1. A developer, MichaelKey, said "we never said DX12 was ready" (which does not address the finding).
2. Then asked for a `game.log` file, which physically cannot contain the data needed to diagnose this kind of bug.
3. Then a green moderator note appeared under the post: **"No Game Log, No bug. Other users can play the game with no stutters, so the game log is crucial in determining why they occur in your particular setup."**
4. Then the thread was locked.
5. Then the thread title was edited to include **[NOT A BUG]**.

Sources:
- Official SCS thread / MichaelKey replies: https://forum.scssoft.com/viewtopic.php?p=2163002
- Official SCS thread: https://forum.scssoft.com/viewtopic.php?t=354183
- Archived forum screenshots, including the moderator note / locked state: https://github.com/NemoByteCore/ets2-1.61-stutter-investigation/tree/main/evidence/forum
- Independent Wayback snapshot: https://web.archive.org/web/20261002223936/https://forum.scssoft.com/viewtopic.php?t=354183

So I did weeks of unpaid engineering work, gave SCS a full diagnosis with a named function and measured timings, and was told "no log, no bug" before the thread was locked behind me.

That is what happened. Now here is why it matters.

## The slightly longer version

My investigation found something specific. The engine already has a system for preparing graphics asynchronously. In plain English, it has a way to prepare shaders in the background, before they are needed. That system exists in the game right now.

But it is not being used for the shaders that cause the stutter. I measured it. 27 out of 27 slow shader compilations reached the first frame they were needed on without ever going through the existing background system. So they blocked the render thread instead.

That is not "DX12 is unfinished". That is a wiring bug in a system that already exists.

And the fix is not "flip a switch". I tested that. Changing the synchronous wait to asynchronous removed the big stalls, but caused missing frames and black flashes. So the answer is not a config tweak. The answer is to wire the existing background system into the path that needs it. Which is an engine-side job.

## How SCS handled it

SCS never addressed the async coverage gap. Not once. Not in the thread, not in the green note, not in any private message.

What they did instead was:

- Redirect the conversation to DX11, which is unplayable for some of the people reporting the bug.
- Ask for a log file that cannot contain the evidence.
- Add a green stamp saying "No Game Log, No bug".
- Lock the thread.
- Tag it **[NOT A BUG]**.

And here is the part that makes it worse. The green note also said "other users can play the game with no stutters". That is the "works on my machine" argument, but coming from the company itself. A bug affecting a subset of users is still a bug. If it affected everyone, they would have fixed it already. The fact that it does not affect everyone is not proof that it is not real. It just makes it easier to ignore.

And the request for a `game.log` is a red herring. A `game.log.txt` in ETS2 contains CPU/GPU info, config settings, mod list and script errors. It does not contain render thread call stacks, shader compilation timings, or async coverage data. Asking for it to diagnose a threading bug is not a technical request. It is a way to close the thread without addressing the report. I explained, in detail, why the log cannot contain the evidence. And the response was a green stamp and a lock.

## They know the engine is the problem. They said so themselves.

In SCS's own "Road to Consoles" dev talk, Console Producer Jakub Mráz said the engine has been in development for almost 30 years, and that "throughout all these years you make tiny little shortcuts in development because you need to ship content... and after 30 years it kind of adds up".

Co-owner and Rendering Programmer Petr Šebor added that "our technical debt had grown so massive that we were facing two possible routes: either rewrite everything from scratch or try to move forward through smaller, incremental changes that would keep the game alive".

Sources:
- Official SCS Software "Road to Consoles Dev Talk #2": https://blog.scssoft.com/2026/04/scs-software-road-to-consoles-dev-talk-2.html
- Official SCS video embedded in that post: https://www.youtube.com/watch?v=HDohGbLom_Y
- Transcript/report reproducing the Jakub Mráz and Petr Šebor quotes: https://traxion.gg/why-porting-american-truck-simulator-and-euro-truck-simulator-2-to-console-is-a-superhuman-task/

They know. They have said it publicly. And yet the response to a specific, traceable bug is "send a game.log" and a locked thread.

That is not an accident. That is a policy. When the engine is held together with duct tape, you cannot fix every report. So you close the threads, lock them, tag them, and move on. Because the alternative is admitting that the foundation is rotten, and that would cost money.

## The pattern: DLC over engine

Here is the part that really matters, and it is not about this one bug. It is about the priorities.

SCS has released dozens of paid DLCs over the years. Maps, trucks, paint jobs, tuning packs, cargo packs, radio icons. Every single one of them has a clear, measurable return on investment. You make content, you sell it, you get money.

Rewriting the renderer does not have that. Nobody buys "Renderer Rewrite DLC". So the content keeps coming, and the infrastructure keeps getting pushed back.

This is not a conspiracy theory. It is a business model. And it leads to a very specific behaviour: when a real bug is reported, the priority is not to fix it. The priority is to close the thread. Because closing the thread costs nothing, and fixing the renderer costs years.

The result is what we see today. The engine is held together with duct tape and thirty years of shortcuts, DLC keeps shipping, and anyone who points out the problem gets a green stamp and a locked thread.

And the players feel it. On Steam, on Reddit, on the SCS forum, the same complaints keep coming back. A player with an i7-13700KF and RTX 4070Ti wrote: "The game engine can't keep up in certain circumstances, it has little to do with your hardware specs, the bottleneck is in the game software". Another added: "Certain parts of the game is not optimized well. It's up to SCS to fix it. Currently many limit the game to 60fps to avoid stutters". On the SCS forum, a player with a Ryzen 9 9950X3D and RTX 40-series reported: "I believe the issue lies in the game engine itself, especially with DX11. The engine is simply too old to reliably deliver 100+ FPS". Another Steam thread: "The game engine is not very well optimized and since 1.50 SCS has added more effects and better graphics making the game heavier. But the game engine itself is not yet at a point where it runs effectively with these new additions on all systems, even with hardware specs well above requirements".

Sources:
- Steam — "Stuttering" (contains the i7-13700KF / RTX 4070 Ti comments): https://steamcommunity.com/app/227300/discussions/0/786567268147491294/
- SCS forum — "ETS2 1.57 version 100% GPU usage" (Ryzen 9 9950X3D quote): https://forum.scssoft.com/viewtopic.php?p=2088185
- Steam — "And the stutter is back…": https://steamcommunity.com/app/227300/discussions/0/600767061860296699/

These are not isolated cases. Similar reports keep appearing even from players with hardware well above the game's requirements. And the answer is always the same. "Send a log." "It's experimental." "Works on my machine."

## The "it's experimental" excuse is used to shut down reports

Look at the official SCS forum thread about the DX12 engine upgrade. When people complained, a forum veteran replied: "Whoever who would expect the game to have all of a sudden graphics like a triple-A blockbuster are delusional... it's a waste of time to explain anything to them because at the end they just want an excuse to complain about".

Source:
https://forum.scssoft.com/viewtopic.php?p=1862668

And on Steam: "The game doesn't support DX12 yet... You can force the game to start in DX12, but it's not advisable at all. The game isn't optimized for DX12, thus regardless of your computer specs you might have problems".

Source:
https://steamcommunity.com/app/227300/discussions/0/596260689262273412/

So the community has internalized the excuse. "It's experimental" has become a shield that protects the engine from any and all criticism. Report a bug? "It's experimental." Ask for a fix? "It's experimental." Point out that the async PSO path exists but isn't wired in? "It's experimental."

And the company lets them do it. Because as long as the community polices itself, SCS does not have to. The players who defend SCS are not employees. They are players. But they behave like a shield. They tell you "it's experimental", "just use DX11", "works on my machine", "you're just complaining". They are not paid to do this. They do it for free. And SCS lets them. Because as long as the community polices itself, SCS does not have to.

This is not unique to SCS. But it is particularly visible here because the evidence is so one-sided. I gave them a stack trace, a named function, a measured coverage gap, and a public repo. They gave me a green stamp, a locked thread, and a "[NOT A BUG]" tag.

## The technical evidence

Everything is public. Nothing here is speculation.

**Build investigated:** ETS2 1.61.1.1

**Revision:** `6949e633e77902f7e023819d3131cc6ccce3707f`

**EXE SHA-256:** `EB17944139BE4DE3D70D0CD57CDAA7C52C9E326ECF2D0DD3EA2F806545C74A53`

**Renderer:** DX12

**The relevant call path is:**

`FUN_1402A06D0` -> `FUN_1402AAA60` -> `FUN_14029DD00(..., wait=1)` on a cold PSO cache miss.

Measured individual cold-PSO stalls repeatedly landed in roughly the 10-40+ ms range. The final coverage run included synchronous stalls of 9.958 ms, 10.331 ms, 11.247 ms, 11.617 ms, 11.990 ms, 12.821 ms, 13.303 ms, 14.674 ms, 16.416 ms, 19.936 ms and 22.351 ms.

I tested `wait=0`. The large synchronous stalls disappeared. But the cold async request returns `0xFFFF` while compilation is still pending, so the current draw gets skipped and you get black flashes. So the answer is not "flip wait=1 to wait=0". The PSO has to be compiled before the first draw needs it.

And the engine already has a path to do that: `FUN_14029E0F0` -> `FUN_14029DD00(..., wait=0)`. I built a probe to compare. `async_total = 0`, `slow_total = 27`, `slow_seen = 0`, `slow_unseen = 27`. Not one of the 27 slow PSOs ever went through the existing async path before blocking the draw thread.

That is the bug. Not "DX12 is unfinished". The async system already exists. It just is not wired into the draw flow.

## The evidence

Everything is public. Nothing here is speculation.

Public repository with the full investigation:\
https://github.com/NemoByteCore/ets2-1.61-stutter-investigation

Official SCS forum thread (locked and tagged [NOT A BUG]):\
https://forum.scssoft.com/viewtopic.php?t=354183

Independent Wayback Machine snapshot of the locked thread:\
https://web.archive.org/web/20261002223936/https://forum.scssoft.com/viewtopic.php?t=354183

The repository contains the full technical investigation, the exact build revision, the executable hash, the call path, the measured stall timings, the async coverage result, the locked forum exchange, the green moderator note, and screenshots of the entire thread. It also contains a chronological screenshot archive of the entire relevant forum exchange, numbered 01-09.

## Why "just use DX11" does not answer the report

Whether DX11 is the currently supported renderer is a product-support question. The existence of a measurable engine-side failure in the DX12 path is a technical question. Those are not mutually exclusive.

SCS can legitimately say: DX12 is experimental / unsupported. That does not make a reproducible defect inside that implementation cease to exist.

And in my case, DX11 was not a practical fallback because its stutter behavior was bad enough that DX12 was the usable path. The investigation therefore focused on the renderer I could actually use and on a mechanism that could be measured.

So telling me to "just use DX11" did not work. And telling me DX12 is experimental did not help either, because for some of us DX12 is the only path that runs at all, and it still stutters.

## Why I am not continuing to patch it

I tested the obvious external directions. Forced async removes the large PSO wait but skips rendering while a pipeline is pending. Static PSO-key prewarm fails because future drives encounter different cold keys. Synchronous prewarm can simply move a 35 ms compile stall somewhere else. Triggering prewarm too early can hit dependencies that do not exist yet.

The engine already contains the machinery needed for asynchronous preparation. At this point the correct fix needs knowledge and control available inside the engine: what PSOs will be needed, when their dependencies become valid, when to enqueue them, how to persist and cache them, and how to guarantee completion before draw-time use.

That is not something I am going to keep reverse-engineering and reconstructing externally for free.

## Why the repository remains public

I bought Euro Truck Simulator 2 to play it.

I did not buy it so that I could reverse-engineer Prism3D, build telemetry DLLs, recover call graphs, trace command-stream execution, measure PSO creation, experiment with synchronization, build multiple generations of runtime probes, perform whole-binary version comparisons, and debug the renderer for free.

The repository remains public because the work already exists and may be useful. Everything needed to understand the finding is there.

The investigation is closed.

Not because there was no evidence. Because the remaining work belongs to the people who own the renderer.

## The final engine-level conclusion

If the problem is simply missing coverage of the existing asynchronous preparation system, SCS should fix that path.

If the renderer architecture cannot reliably keep cold PSO creation away from the latency-critical draw path, then another external workaround is not the answer. The graphics layer needs deeper work.

Modern APIs should not be treated as a thin compatibility layer over assumptions inherited from a much older rendering architecture.

In plain terms: if this is architectural, stop polishing the fossil and fix or replace the renderer underneath it.

## And yes, this is personal

I am not going to pretend this is purely academic. It is not. I spent weeks of my own time on this. I bought the game to play it, not to do unpaid renderer engineering for a commercial studio. I did the work because nobody else was going to, and because the stutter was making the game unplayable on the only path that runs on my machine.

And when I handed them the results, they gave me a green stamp, a locked thread, and a "[NOT A BUG]" tag. They never once addressed the actual finding. They never explained why `FUN_14029E0F0` with `wait=0` is not covering the PSOs that later stall through `FUN_1402AAA60` with `wait=1`. They never engaged with the 27/27 measurement. They just closed the thread and moved on to the next DLC announcement.

So yes, this is also a personal grudge. I am not going to pretend otherwise. I did the work, I got dismissed, and I am documenting it publicly. If that bothers SCS, good. Maybe it will motivate them to actually respond next time someone hands them a diagnosis for free.

## SCS, stop with the excuses and fix your engine

You know the engine is the problem. You said so yourselves, publicly, in your own dev talk. You called the technical debt "massive". You said you were facing a choice between rewriting everything from scratch or moving forward through incremental changes. You admitted that thirty years of shortcuts "adds up".

So stop telling people "No Game Log, No bug". Stop tagging reproducible, documented, measured bugs as "[NOT A BUG]". Stop locking threads when someone does your job for you. Stop hiding behind "DX12 is experimental" when the async preparation system already exists in your own code and simply is not wired into the draw flow.

And stop selling DLC for an engine you refuse to fix.

Either wire the existing asynchronous preparation into the missing paths so cold PSOs stop blocking the draw thread, or admit that the architecture cannot support it and do the renderer-level work. But pick one. Stop pretending this is not a real problem.

The evidence is public. The call path is named. The coverage gap is measured. The forum handling is archived. The ball is in your court.

SCS: finish with the excuses and fix your engine.