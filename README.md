# NetShield

Domain filtering for Windows, built by intercepting and rewriting DNS traffic in user space instead of installing a proxy or editing the `hosts` file.

A desktop app manages the blocklist, a privileged background process rewrites DNS packets as they leave and re-enter the machine, and a separate server tier stores per-user settings behind a gRPC API.

I built it to understand DNS filtering end to end, and to practise keeping a privileged component small and isolated from the UI that drives it.

## Why filter at the DNS layer

This was a choice between four options, and the trade-offs are the interesting part:

| Approach | Why not |
| --- | --- |
| Edit the `hosts` file | Trivial to implement and trivial to bypass. No way to express "block ads" without shipping a list of a hundred thousand entries. |
| Local HTTP/S proxy | Requires installing a root certificate on the user's machine to see inside TLS. A much larger ask, and a much larger thing to get wrong. |
| Kernel driver | Highest fidelity, but signing and deployment are a real burden. I took that route on Linux in [My_Internet](https://github.com/pazMenachem/My_Internet); this project is the user-space answer on Windows. |
| **DNS interception (chosen)** | Sits below the browser, so it covers every application on the machine. No certificate, no kernel code, no proxy configuration. |

**The honest limitation of this choice:** DNS filtering is bypassable. DNS-over-HTTPS, an application with a hardcoded resolver, or a connection straight to a raw IP all go through untouched. This is a parental-control-grade control, not a security boundary, and it should not be described as one.

## Architecture

```
  ┌──────────────────────── client machine ────────────────────────┐
  │                                                                │
  │   GUI (Tkinter)                                                │
  │        │  HTTP  127.0.0.1:8000                                 │
  │        ▼                                                       │
  │   gateway (FastAPI)                                            │
  │        │  named pipe \\.\pipe\blocker_pipe                     │
  │        │  length-prefixed JSON frames                          │
  │        ▼                                                       │
  │   blocker (elevated)  ──── WinDivert ────►  DNS packets        │
  │        └─ BlockSettingsCache (in-memory, lock-guarded)         │
  └────────────────────────────────────────────────────────────────┘

  ┌──────────────────────── server tier ───────────────────────────┐
  │   Express gateway  ──── gRPC ────►  .NET 9 service  ──►  Postgres
  │   REST, validation                  EF Core, owns schema       │
  └────────────────────────────────────────────────────────────────┘
```

### Client

**`blocker`** — the only component that needs administrator rights, because WinDivert does. It runs two threads over shared state:

- a *control* thread draining the named pipe for settings changes
- a *data* thread sitting in the WinDivert loop on `udp.DstPort == 53 or udp.SrcPort == 53`

Keeping the privileged process this thin is the point of the split. It has no UI, no network listener and no database client — it accepts a fixed set of five message codes over a local pipe and nothing else.

**`gate_way`** — a FastAPI process exposing four local POST routes (`/add_domain`, `/remove_domain`, `/update_adult_ads`, `/init_blocker`) and translating each into a pipe message. It exists so the GUI never has to know about pipes or run elevated.

**`GUI`** — Tkinter. Blocking-mode radio buttons plus a domain list; every action is an HTTP call to the local gateway.

### What actually happens to a packet

On the way **out**, the destination address is rewritten to an upstream resolver chosen by the two filter toggles:

| adult | ads | resolver |
| --- | --- | --- |
| off | off | the machine's own default gateway (unchanged behaviour) |
| on | off | Cloudflare Family `1.1.1.3` |
| off | on | AdGuard `94.140.14.14` |
| on | on | AdGuard Family `94.140.14.15` |

Category blocking (ads, adult) is therefore delegated to resolvers that already maintain those lists. Maintaining my own would have been a data problem, not an engineering one.

On the way **in**, the payload is parsed with `dpkt`. If the queried name is on the user's blocklist and the record type is A or AAAA, the response is rewritten to deny it. Then the source address is rewritten back to the default gateway.

That last step is the non-obvious one. Because the outbound query was redirected to a resolver the operating system never chose, the reply arrives from an address the stub resolver is not expecting and would discard as unsolicited. Rewriting the source makes the reply appear to come from the resolver the machine thinks it is using.

### Control-plane design

Messages are integer codes (`200`–`204`) carrying a JSON body. `HandlerFactory` maps each code to an `IHandler` subclass, so a new control message is a new class plus one dictionary entry rather than another branch in a dispatch function. The same request-handler-factory shape appears in my [Trivia_Game](https://github.com/pazMenachem/Trivia_Game) server.

In fairness: with five handlers, a factory is arguably more structure than the problem needs. It earns its place only if the message set keeps growing.

`BlockSettingsCache` holds the blocklist as a `set` behind a `threading.Lock`, capped at 256 entries. The packet path runs per DNS query, so it reads from memory rather than crossing a process boundary or touching a database. The cost is that the cache is not persisted — restart the blocker and it is empty until the GUI replays `/init_blocker`.

Frames on the pipe are a 4-byte little-endian length prefix followed by UTF-8 JSON. The pipe is also created in `PIPE_TYPE_MESSAGE` mode, which already preserves message boundaries, so the prefix is belt-and-braces rather than strictly necessary.

### Server tier

Two services, split by responsibility:

- **`server/gateway`** (Node/Express) owns transport concerns — routing, email and domain validation middleware, error shaping, structured logging via Winston. It holds no schema knowledge.
- **`server/DbAPI`** (.NET 9) owns the data. It serves gRPC to the gateway and also exposes REST controllers with Swagger for manual inspection during development.

gRPC between them because the contract is generated from `.proto` files, so a Node client and a C# server stay in step without a hand-written DTO layer on each side.

Schema: `User` (GUID key, unique email) has a one-to-one `UserSettings` and many `BlockedDomain`s, with a unique index on `(UserId, DomainName)` and cascade delete on both relationships. The connection string is read from the `DB_CONNECTION_STRING` environment variable — deliberately not from `appsettings.json`, so nothing credential-shaped is ever tracked in git.

## Known limitations

Stated plainly, because they are the things I would ask about:

- **The client and the server tier are not wired together.** The GUI talks only to the local gateway on `127.0.0.1:8000`. The server stores per-user blocklists, but no client code calls it yet. Blocklists currently live and die with the blocker process.
- **There is no authentication anywhere.** Users are identified by an email string. `User.cs` carries a note to add a password hash and salt; the gateway's user routes carry a note that identification needs a token. Neither is done.
- **gRPC runs on insecure credentials**, which is fine on localhost and not fine anywhere else.
- **The Node gateway loads `.proto` files off the filesystem** from inside the .NET project directory. That coupling would not survive deploying the two services independently; the protos belong in a shared, versioned location.
- **The blocking response is internally inconsistent.** It sets `NXDOMAIN` *and* attaches an A record for `0.0.0.0`. Either alone is a valid way to deny a name; both together is not what the RFC describes, and it works only because resolvers are lenient.
- **The gateway's Windows Service wrapper is commented out**, so it runs as a console process and does not survive a reboot.
- **`client/App/gate_way/requirements.txt` is incomplete** — it lists `pydivert` and `pywin32` but not `fastapi`, `uvicorn` or `pydantic`.
- **There are no tests.**

## Running it

Windows only. WinDivert needs an elevated process and will install a driver.

```bash
# blocker — run from an Administrator shell
cd client/App/blocker
pip install pydivert dpkt pywin32 netifaces
python main.py

# local gateway — start after the blocker, it connects to the pipe on boot
cd client/App/gate_way
pip install fastapi uvicorn pydantic pywin32
python main.py

# GUI
cd client/GUI
pip install requests
python main.py
```

Server tier (optional — see limitations above):

```bash
# .NET service
cd server/DbAPI/DbAPI
export DB_CONNECTION_STRING="Host=localhost;Database=netshield;Username=...;Password=..."
dotnet ef database update
dotnet run

# Express gateway
cd server/gateway
npm install
npm run dev
```

## Stack

Python (pydivert, dpkt, FastAPI, Tkinter, pywin32) · Node.js (Express, gRPC, Winston) · C# / .NET 9 (gRPC, EF Core) · PostgreSQL · Protocol Buffers · Windows named pipes
