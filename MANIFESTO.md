The "DX12 is experimental" excuse is a smokescreen. Here's the proof.

Let me be clear from the start: I'm not here to ask for a new engine. I'm not here to demand a finished DX12 renderer tomorrow. I'm here because the same non-answer keeps coming back every time someone reports a real problem, and I'm tired of pretending it's a valid response.

I've spent weeks instrumenting the DX12 path in 1.61.1.1. I traced a reproducible stall on the draw thread directly to cold PSO compilation happening synchronously, and I found that the engine already has an async PSO preparation path that simply isn't being used. 27 out of 27 slow PSOs reached their first synchronous use without ever going through it.

That's not "DX12 isn't ready". That's a specific, traceable bug. One is a missing feature. The other is a wiring problem in the code that already exists.

The answer I got was, essentially, "we're still on DX11, we never said DX12 was ready." Which might be true as a statement about the transition. But it doesn't answer the question. The question was never when the new renderer is coming. The question is why the existing async system isn't wired into the draw flow. That's a bug report, and "it's experimental" is not a fix.

And here's the part that really gets me. This isn't an isolated incident. This is a pattern, and the evidence is everywhere.

Exhibit A: SCS admits the engine is the bottleneck.

In their own "Road to Consoles" dev talk, SCS's Console Producer Jakub Mráz stated plainly that the engine has been in development for almost 30 years and that "throughout all these years you make tiny little shortcuts in development because you need to ship content... and after 30 years it kind of adds up".

SCS co-owner and Rendering Programmer Petr Šebor added that "our technical debt had grown so massive that we were facing two possible routes: either rewrite everything from scratch or try to move forward through smaller, incremental changes that would keep the game alive".

They know. They've admitted it publicly. And yet, when a specific, traceable bug is reported on the current path, the answer is to point at the future renderer. That's not an answer. That's a deflection.

Exhibit B: The player base has been saying this for years.

This isn't a new complaint from a small group of people. Go to any forum, any Steam discussion, any Reddit thread. The language is always the same.

On Steam, a player with an i7-13700KF and RTX 4070Ti wrote: "The game engine can't keep up in certain circumstances, it has little to do with your hardware specs, the bottleneck is in the game software".

In the same thread, another user pointed out: "Certain parts of the game is not optimized well. It's up to SCS to fix it. Currently many limit the game to 60fps to avoid stutters".

On the official SCS forum, a player with a Ryzen 9 9950X3D and RTX 40-series GPU reported: "I believe the issue lies in the game engine itself, especially with DX11... The engine is simply too old to reliably deliver 100+ FPS".

Another Steam thread: "The game engine is not very well optimized and since 1.50 SCS has added more effects and better graphics making the game heavier. But the game engine itself is not yet at a point where it runs effectively with these new additions on all systems, even with hardware specs well above requirements".

And another: "The game engine can't keep up in certain circumstances... I think there will be certain times and places on the map when it will still happen".

These aren't isolated cases. Similar reports keep appearing even from players with hardware well above the game's requirements.

Exhibit C: The engine is still heavily main-thread / single-thread bottlenecked.

This is one of the most damning pieces of evidence, and it's been known for years. Multiple sources describe ETS2 and ATS as being heavily limited by single-thread performance, especially in CPU-heavy scenes.

A post on TruckersMP: "ETS2 uses an old, single-threaded engine. It cannot scale well with modern hardware, so FPS tanks in crowded areas regardless of your GPU".

On Steam: "It comes down to single core processing power, this game is very single core CPU heavy and can cause bottlenecks".

On the SCS forum: "It uses only one core, so in the cities, where there's more traffic and more buildings, the CPU becomes the bottleneck and the GPU waits, which is why the GPU utilization goes down".

A game still heavily constrained by single-thread performance in 2026. On hardware with 16, 24, or 32 threads. And the answer is still "we're working on it."

Exhibit D: The "it's experimental" excuse is used to shut down reports.

This is the part that is genuinely infuriating. Look at the official SCS forum thread about the DX12 engine upgrade. When people complained, a forum veteran replied: "Whoever who would expect the game to have all of a sudden graphics like a triple-A blockbuster are delusional... it's a waste of time to explain anything to them because at the end they just want an excuse to complain about".

And on Steam: "The game doesn't support DX12 yet... You can force the game to start in DX12, but it's not advisable at all. The game isn't optimized for DX12, thus regardless of your computer specs you might have problems".

So the community has internalized the excuse. "It's experimental" has become a shield that protects the engine from any and all criticism. Report a bug? "It's experimental." Ask for a fix? "It's experimental." Point out that the async PSO path exists but isn't wired in? "It's experimental."

Exhibit E: The business model rewards this.

I'm not going to accuse SCS of malice. I'm going to state a fact. DLC has a clear, measurable return on investment. A renderer rewrite does not. Nobody buys "Renderer Rewrite DLC." So the content keeps coming, and the infrastructure keeps getting pushed back. Maps, trucks, paint jobs, tuning packs. And meanwhile, the engine continues to crumble under its own weight.

So here's my question.

If SCS knows the engine is a problem, if the community has been reporting it for years, and if the technical debt has grown "so massive" that they've said so publicly, then why does every specific bug report get met with "it's experimental"?

The answer is simple. Because "it's experimental" is not a technical response. It's a PR response. It's a way to close the thread without fixing anything. And as long as the DLC keeps selling, there's no incentive to change that.

I'm not asking for a new engine. I'm asking for an honest answer. If you're not going to fix the current DX12 path, say so. If you're not going to address the async PSO coverage gap, say so. But don't tell me it's experimental. I already know. I measured it.