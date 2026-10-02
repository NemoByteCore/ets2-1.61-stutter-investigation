# The SCS Software Playbook: Deflect, Stamp, Lock. A Case Study in Engine Debt and Forum Nepotism.

This is not a bug report. This is a record of what happens when you do the work SCS Software should have done internally, hand them the results for free, and then get told "No Game Log, No bug" before the thread is locked and the topic is marked as "[NOT A BUG]".

Let me start with the technical part, because without it, everything else is just an opinion.

## 1. The technical evidence

I spent weeks instrumenting the DX12 render path in Euro Truck Simulator 2 version 1.61.1.1. I traced a reproducible stall on the draw thread to cold PSO compilation happening synchronously. I found that the engine already has an async PSO preparation path that simply is not being used. I measured it. 27 out of 27 slow PSOs reached their first synchronous use without ever going through it.

The full public investigation is here: [LINK DO REPO]

Build investigated: ETS2 1.61.1.1, revision `6949e633e77902f7e023819d3131cc6ccce3707f`, EXE SHA-256 `EB17944139BE4DE3D70D0CD57CDAA7C52C9E326ECF2D0DD3EA2F806545C74A53`, DX12.

The relevant call path is `FUN_1402A06D0` → `FUN_1402AAA60` → `FUN_14029DD00(..., wait=1)` on a cold PSO cache miss.

Measured individual cold-PSO stalls landed in the 10–40+ ms range. The final coverage run included synchronous stalls of 9.958 ms, 10.331 ms, 11.247 ms, 11.617 ms, 11.990 ms, 12.821 ms, 13.303 ms, 14.674 ms, 16.416 ms, 19.936 ms and 22.351 ms.

I also tested `wait=0`. The large synchronous stalls disappeared, but the cold async request returns `0xFFFF` while compilation is pending, so the current draw gets skipped and you get black flashes. The answer is not "flip `wait=1` to `wait=0`". The PSO has to be compiled before the first draw needs it. And the engine already has a path to do that: `FUN_14029E0F0` → `FUN_14029DD00(..., wait=0)`. I built a probe to compare. `async_total = 0`, `slow_total = 27`, `slow_unseen = 27`. Not one of the 27 slow PSOs ever went through the existing async path before blocking the draw thread.

That is the bug. Not "DX12 is unfinished". The async system already exists. It just is not wired into the draw flow.

## 2. What happened when I posted this on the official SCS forum

You can read the full thread here: [LINK DO WĄTKU]

### 2.1. The first deflection

SCS developer MichaelKey replied that "No one said that DX12 is ready. We're still running on DX11." Which is true, but does not answer the report. The report is not "DX12 is unfinished". The report is "the async path that already exists is not wired in". MichaelKey did not address that. He moved the conversation to DX11.

### 2.2. The second deflection: "send a game.log"

I pointed out that DX11 is unplayable for me and DX12 is the only path that runs, and that the async coverage gap is a bug, not a missing feature. MichaelKey replied:

> "Let's focus on this, because DX11 is the version we support now, and it should work for everyone. So far, you've been describing it in very general terms. Send your game.log here. Maybe we'll find something in it that explains why it's stuttering so much."

Two problems with that.

First, a `game.log.txt` in ETS2 contains CPU/GPU info, config settings, mod list and script errors. It does not contain render thread call stacks, PSO compilation timings, or async coverage data. Asking for it to diagnose a DX12 threading bug is not a technical request. It is a way to close the thread without addressing the report.

Second, "you've been describing it in very general terms" is not true. I gave the build revision, the EXE hash, the exact call path, and a measured coverage gap of 27/27. That is as specific as a bug report can get. Calling it "general" is gaslighting.

### 2.3. The green stamp

After I posted a full reply, a green moderator note was added underneath:

> "No Game Log, No bug. Other users can play the game with no stutters, so the game log is crucial in determining why they occur in your particular setup."

That green note was placed directly under a post that explains why a `game.log` cannot contain the data needed to diagnose the bug. That is not a mistake. That is the whole point. It is a loop: ask for the log, the log cannot contain the evidence, declare the evidence missing, close the thread.

### 2.4. The thread got locked and marked

Shortly after, the thread was locked. Nobody can reply. The thread title was also edited to include "[NOT A BUG]". The evidence is still there, but no one can add to it. No one from SCS ever addressed the async coverage gap. No one from SCS ever commented on `FUN_14029E0F0` or the 27/27 measurement. They just closed the thread, stamped it, and moved on.

### 2.5. Meanwhile, the community does the same thing

In the same thread, another user suggested config tweaks. Another one said "DX11 is fine for me, I just get microstutters, I hope multicore and DX12 will fix it". The pattern is the same: deflect, downplay, hope for the future renderer. Nobody actually looks at the bug.

## 3. The nepotism pattern

This is the part that goes beyond a single bug report. This is a pattern of mutual protection between the company and a segment of its most vocal community members. It works like this:

A player reports a problem. A developer asks for a log. The player provides something better than a log. The developer ignores it. A forum veteran jumps in to defend the developer. The thread gets locked. The topic gets marked as "[NOT A BUG]". The player is left holding a bag of evidence that no one will look at, and the community moves on to the next DLC announcement.

The people who defend SCS in these threads are not employees. They are players. But they behave like a shield. They tell you "it's experimental", "just use DX11", "works on my machine", "you're just complaining". They are not paid to do this. They do it for free. And SCS lets them. Because as long as the community polices itself, SCS does not have to.

This is not unique to SCS. But it is particularly visible here because the evidence is so one-sided. I gave them a stack trace, a named function, a measured coverage gap, and a public repo. They gave me a green stamp, a locked thread, and a "[NOT A BUG]" tag.

## 4. They know the engine is the problem. They have said so themselves.

This is not speculation. In SCS's own "Road to Consoles" dev talk, Console Producer Jakub Mráz said the engine has been in development for almost 30 years and that "throughout all these years you make tiny little shortcuts in development because you need to ship content... and after 30 years it kind of adds up". Co-owner and Rendering Programmer Petr Šebor added that "our technical debt had grown so massive that we were facing two possible routes: either rewrite everything from scratch or try to move forward through smaller, incremental changes that would keep the game alive".

They know. They have said it publicly. And yet the response to a specific, traceable bug is "send a game.log", then a green stamp, then a locked thread with a "[NOT A BUG]" tag.

## 5. Why this pattern keeps happening

I am not going to accuse SCS of malice. I am going to state a fact. DLC has a clear, measurable return on investment. A renderer rewrite does not. Nobody buys "Renderer Rewrite DLC". So the content keeps coming: maps, trucks, paint jobs, tuning packs, radio icons. And the infrastructure keeps getting pushed back. Meanwhile, every specific bug report gets met with deflection, and the thread gets locked before anyone from the rendering team has to look at it.

## 6. So here is the point

This is not a bug report. This is a record. A record of what happened when someone did the work SCS should have done internally, handed them the results for free, and got a green stamp, a locked thread, and a "[NOT A BUG]" tag in return.

If SCS wants to fix this, everything they need is public. The repo is here: [LINK DO REPO]. The forum thread is here: [LINK DO WĄTKU]. The build is documented. The call path is named. The async coverage gap is measured. The green stamp is in the thread. The lock is on the thread. The "[NOT A BUG]" tag is on the thread.

If they do not want to fix it, that is their choice. But they should stop pretending they are investigating bug reports when what they are actually doing is closing threads and letting their community do the damage control for them.

I bought Euro Truck Simulator 2 to play it. I did not buy it so I could reverse-engineer Prism3D, write telemetry DLLs, trace command streams, locate PSO creation functions and test synchronization behaviour for free, only to be told "No Game Log, No bug" and have the thread locked behind me.

The renderer debt is theirs. The work was mine. The deflection is documented. The lock is documented. The green stamp is documented. The "[NOT A BUG]" tag is documented. Everything after this is on them.