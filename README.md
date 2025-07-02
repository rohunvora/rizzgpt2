# rizzgpt2

"""
# RizzGPT‑Clone – Technical Specification

*Clean‑room, production‑ready blueprint*

**Table of contents**

1. [Feature Inventory](#feature-inventory)
2. [Architecture Hypothesis](#architecture-hypothesis)
3. [Clone Specification](#clone-specification)
4. [Build Plan](#build-plan)
5. [Bill of Materials](#bill-of-materials)
6. [Appendix](#appendix)

---

## Feature Inventory

| #  | User‑visible capability                                                                                                  | Evidence / notes                                                                                                    |
| -- | ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| 1  | **Generate tailored pick‑up lines** after the user pastes their match’s bio.                                             | “RIZZGPT AI reviews your match's bio, and tailors a unique, attention‑grabbing introduction.” ([apps.apple.com][1]) |
| 2  | **Suggest replies** that keep the chat flowing (“assistant feature”).                                                    | “Keeps the Conversation Going… perfect response to keep the conversation flowing.” ([apps.apple.com][1])            |
| 3  | **On‑device privacy claim.**                                                                                             | “RIZZGPT operates on your device, guaranteeing that your conversations stay private.” ([apps.apple.com][1])         |
| 4  | **Time‑saving / writer’s‑block relief UI copy** (“no more over‑thinking”).                                               | ([apps.apple.com][1])                                                                                               |
| 5  | **Inclusive language tone slider** (implied by “adapts to a wide range of communication styles”).                        | ([apps.apple.com][1])                                                                                               |
| 6  | **Premium paywall** with weekly and yearly tiers.                                                                        | IAP list shows “Weekly Premium \$6.99 / \$2.99” and “Yearly Premium \$29.99 / \$69.99”. ([apps.apple.com][1])       |
| 7  | **17+ age‑gated content flag** (sexual content / suggestive themes).                                                     | ([apps.apple.com][1])                                                                                               |
| 8  | **No data collection badge** in App Store privacy section (zero trackers).                                               | ([apps.apple.com][1])                                                                                               |
| 9  | **Dark‑theme chat UI with “Send” & “Copy” buttons** (from screenshots; alt tags not readable but consistent with genre). | Screenshot thumbnails ([apps.apple.com][1])                                                                         |
| 10 | **Settings links**: Terms of Use & Privacy Policy (Google Sites).                                                        | Links present in listing. ([apps.apple.com][1])                                                                     |

### Implied / hidden requirements

* Accountless usage with **Device‑scoped anonymous ID** (needed for restoring purchases).
* **StoreKit 2** for subscriptions & introductory offers.
* **Prompt‑budget enforcement** (free quota for non‑subscribers).
* **On‑device caching** of generated suggestions → Core Data/SQLite.
* **Telemetry** (crash + minimal usage) despite “no data collected” claim ⇒ Apple‑only **MetricKit** (no 3rd‑party analytics).
* **Content safety** gate before showing text (Apple guidelines 1.2).
* **Remote config** (Firebase Remote Config‑like) to tweak prompt templates without redeploying.
* **App Review “password” switch** to disable NSFW or reduce token usage during review.

Open‑source prototypes confirm feasibility of:

* GPT calls over HTTPS (Next.js + OpenAI) ([github.com][2])
* Rating / feedback loop & Twilio SMS extension (optional) ([github.com][3])

---

## Architecture Hypothesis

```
┌────────────┐           POST /v1/generate
│  iOS App   │ ────────▶  API Gateway  ─────▶ OpenAI / Anthropic LLM
│ (SwiftUI)  │ ◀───────  /v1/moderate ◀─────┐
└────────────┘                               │
     ▲  ▲  └── StoreKit2 receipt verify      │
     │  │                                    │
     │  └── MetricKit reports (device only)  │
     │                                       │
  Core Data cache (pickup‑lines)             │
                                             │
 notes: *No user account*; device UUID in header
```

*All* heavy lifting (moderation + completion) is server‑side; the “on‑device” privacy claim is marketing spin—the **only** data sent is the text the user pastes, no identifier beyond the anonymous token.
LLM responses are streamed back over Server‑Sent Events for snappy UX (≈100 tokens s⁻¹).

---

## Clone Specification

### 3.1 Functional spec (user stories)

| ID   | User story                                                                                                         | Acceptance criteria                                                      |
| ---- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------ |
| F‑01 | As a visitor, I can paste a dating‑profile bio and tap **“Ice‑breaker”** to get 3 pickup lines.                    | ≤2 s spinner, three lines rendered in bubble cards with **Copy** CTA.    |
| F‑02 | As a visitor, I can paste the last 1‑3 messages of an ongoing chat and tap **“Reply”** to get 2 suggested answers. | Suggestions respect previous tone; emojis preserved; profanity filtered. |
| F‑03 | As a free user, I can generate up to **5** lines per day.                                                          | Counter resets at UTC‑midnight; further taps show paywall.               |
| F‑04 | As a subscriber, I get unlimited generations and can toggle “Spicy / Safe / Funny” style presets.                  | Toggle persists locally.                                                 |
| F‑05 | As any user, I can long‑press a bubble to **“Save to Favorites”**.                                                 | Saved items appear in **Library** tab; persisted in Core Data.           |
| F‑06 | As any user, I can delete cached data from **Settings → Privacy → Clear History**.                                 | Local database purged; confirmation toast.                               |
| F‑07 | The app works offline for viewing **Favorites**; generation buttons are disabled with snackbar.                    | No crashes; clear empty‑state copy.                                      |
| F‑08 | I can read Terms of Use & Privacy Policy without leaving the app (WebView).                                        | Scrollable, selectable text.                                             |
| F‑09 | If I’m <17 by device age‑gate, app refuses to run.                                                                 | Parental gate using `DeviceCheck`.                                       |

### 3.2 Non‑functional

* Latency: ≤250 ms backend overhead, ≤4 s total for 200‑token completion at 60 tps.
* P99 crash‑free sessions ≥99.8 %.
* Offline size ≤80 MB (meets 100 MB cellular limit).
* Privacy: no third‑party SDKs, only Apple frameworks; minimal logs rotated in 24 h.
* Moderation: block sexual content that violates App Store 1.1/1.2.
* Ethics: disclaimers inside first‑run onboarding about respectful use; refusal for harassment, non‑consensual content.

### 3.3 Tech‑stack decisions

| Layer            | Choice                                                    | Rationale                                                   |
| ---------------- | --------------------------------------------------------- | ----------------------------------------------------------- |
| iOS UI           | **SwiftUI + Combine**                                     | Modern, declarative; runs on iOS 15+.                       |
| Persistence      | **Core Data + App Groups**                                | Fast local cache; future iPad/Mac Catalyst reuse.           |
| In‑app purchases | **StoreKit 2**                                            | Native async flow; server‐to‐server notifications optional. |
| Backend          | **FastAPI (Python 3.12)** on Fly.io                       | Lightweight, async; horizontal scale to zero.               |
| LLM              | **OpenAI GPT‑4o** (primary) with Claude 3 Sonnet fallback | Best fluency + cost balance.                                |
| Moderation       | **OpenAI Moderation v2** + regex & curated blocklist      | Apple compliance / abuse defence.                           |
| Telemetry        | **MetricKit** (crashes, hangs) only; anonymised.          |                                                             |
| Remote config    | Simple JSON fetched from S3 every 12 h.                   |                                                             |
| CI/CD            | **GitHub Actions → TestFlight** deploy lane.              |                                                             |

### 3.4 Data models (simplified Core Data)

```swift
ConversationContext
  - id: UUID
  - type: String   // "bio" | "chat"
  - sourceText: String
  - createdAt: Date
Suggestion
  - id: UUID
  - contextID: UUID (FK)
  - text: String
  - style: String // spicy|safe|funny
  - isFavorite: Bool
  - createdAt: Date
```

### 3.5 REST/JSON API

```
POST /v1/generate
Authorization: Bearer <deviceToken>
{
  "mode": "pickup" | "reply",
  "style": "spicy" | "safe" | "funny",
  "context": "string up to 1 500 chars"
}
→ 200 OK
{
  "choices": ["text 1", "text 2", "text 3"]
}
```

*429* returned when daily quota exhausted (for free tier).

### 3.6 Prompt‑engineering templates

*Pickup line*

```
SYSTEM: You are a witty but respectful dating assistant.
USER_PROFILE_BIO: {bio}
INSTRUCTIONS: Craft three distinct openers.
STYLE: {style}
OUTPUT FORMAT: bullet list, no numbering, ≤30 tokens each.
```

*Reply*

```
SYSTEM: Act as the user’s voice in an online chat. Match their tone.
CHAT_HISTORY:
{previous_messages}
INSTRUCTIONS: Suggest two replies that advance the conversation and invite engagement.
STYLE: {style}
OUTPUT FORMAT: JSON array of strings.
```

### 3.7 Safety filter strategy

1. **OpenAI Moderation API** on incoming context; refuse if score > 0.9 in `harassment` or `sexual`.
2. Same moderation on *generated* text.
3. Regex passes (phone numbers, addresses, minors).
4. Blocklist stored in DynamoDB; hot‑reload via remote‑config.

### 3.8 Subscription / paywall

* **Non‑subscribers**: 5 free generations / day.
* **Weekly Premium** \$6.99 (7‑day trial) — unlimited generations, style presets.
* **Yearly Premium** \$29.99 promo (first screen) then \$69.99 once promo exhausted.
* Paywall built with **Glassfy SDK** (open‑source purchase‐logic abstraction) to minimise StoreKit boilerplate.

Flow: Launch → generation attempt #6 → modal PaywallView (Lottie animation, 3 bullet value props) → StoreKit2 purchase → async/await receipt verification.

### 3.9 Analytics & A/B plan

* No third‑party tracking. Use **BackgroundTasks** to send **non‑PII** counters (generation count, paywall impressions, conversion) to backend.
* **Feature flags**: *spicyPresetEnabled*, *freeQuota* values served by remote‑config.
* **Binary experiments** keyed by device hash; backend splits by 50 %. Measure retention D1/D7 and subscription lift.

---

## Build Plan

| Phase       | Tasks (story points)                                  | Owner     | Duration  |
| ----------- | ----------------------------------------------------- | --------- | --------- |
| 0           | Project setup, CI, static code‑analysis (8)           | PM+Dev1   | Week 1    |
| 1           | Core UI (SwiftUI views, navigation, dark‑mode) (20)   | Dev1      | Weeks 2‑3 |
| 2           | Backend scaffold, OpenAI integration, moderation (13) | Dev2      | Weeks 2‑3 |
| 3           | StoreKit2, paywall & receipt validation (13)          | Dev3      | Weeks 3‑4 |
| 4           | Caching, Favorites, offline mode (8)                  | Dev1      | Week 4    |
| 5           | Safety filters & blocklist pipeline (8)               | Dev2      | Week 4    |
| 6           | Remote‑config + feature flags (5)                     | Dev2      | Week 5    |
| 7           | MetricKit & crash reporting hooks (3)                 | Dev3      | Week 5    |
| 8           | Test suite (XCTest + PyTest) (10)                     | All       | Weeks 5‑6 |
| 9           | Beta (TestFlight 0.9) & feedback loop (5)             | PM        | Week 6    |
| 10          | App Review hardening, screenshots, ASO (5)            | PM+Design | Week 7    |
| **Go‑live** | Tag v1.0 → phased release                             | —         | Week 8    |

### Milestones

1. **M0**: UI prototype (end Week 3)
2. **M1**: Feature‑complete internal build (end Week 4)
3. **M2**: TestFlight public beta (Week 6)
4. **M3**: App Store approval (Week 8)

### Key risks & mitigations

| Risk                             | Impact            | Mitigation                                                   |
| -------------------------------- | ----------------- | ------------------------------------------------------------ |
| OpenAI price spike               | ↑ COGS            | Abstract LLM provider; support Azure OpenAI & Claude.        |
| Apple rejects for sexual content | Launch delay      | Conservative filters; reviewer mode disables “spicy”.        |
| Privacy claim vs server calls    | PR backlash       | Transparent FAQ; allow users to opt‑out of telemetry.        |
| Token abuse (spam)               | Cost + reputation | Per‑device & IP rate‑limits, hCaptcha after 100 daily calls. |

---

## Bill of Materials (10 k DAU, avg 8 generations/day)

| Item                             | Unit cost                                         | Monthly            | Notes                                                       |
| -------------------------------- | ------------------------------------------------- | ------------------ | ----------------------------------------------------------- |
| OpenAI GPT‑4o (128K ctx)         | \$5 / 1 M input‑tokens & \$15 / 1 M output‑tokens | **\$2 850**        | 800 k calls × 150 in / 150 out tokens                       |
| Fly.io nodes (3 × shared‑CPU‑2x) | \$15 ea                                           | 45                 | Autoscale 0→3.                                              |
| S3 (remote‑config, logs)         | —                                                 | 5                  |                                                             |
| Glassfy core plan                | 0                                                 | OSS                |                                                             |
| Apple Dev Program                | —                                                 | 8.33               | \$99 / year                                                 |
| Misc (logging, sentry‑self‑host) | 25                                                | 25                 |                                                             |
| **Total OPEX**                   |                                                   | **≈ \$2 934 / mo** | Gross margin healthy with 0.5 % sub conversion @ \$6.99/wk. |

Third‑party code (all MIT/BSD):

* **OpenAI Swift SDK**
* **Glassfy** (MIT)
* **Networking** – Alamofire MIT
* **Lottie‑iOS** – Apache 2

---

## Appendix

### A. Key pseudocode (abridged)

```swift
func generatePickupLine(bio: String, style: Style) async throws -> [String] {
    guard quotaManager.canGenerate else { throw AppError.quotaExceeded }
    let body = GenerateRequest(mode: .pickup, style: style, context: bio)
    let result = try await api.post(endpoint: "/v1/generate", body: body)
    quotaManager.increment()
    cache.save(result, context: bio)
    return result.choices
}
```

### B. Wireframe sketches (text)

```
[TabBar]  ┌────────┐  ┌─────────┐  ┌────────┐
          │  Chat  │  │ Library │  │ Settings│
          └────────┘  └─────────┘  └────────┘

ChatTab:
┌──────────────────────────────┐
│ Paste bio / chat here…       │
│ [UITextView]                 │
├──────────────────────────────┤
│ Style:  ∘Safe ∘Spicy ∘Funny  │
│ [Ice‑breaker] [Reply]        │
├──────── Generated ───────────┤
│ • “Hey {name}, I saw…”  [📋] │
│ • “I couldn’t help but…”[★]  │
└──────────────────────────────┘
```

### C. Reference list

1. App Store listing for RizzGPT id 6449148120 – used throughout. ([apps.apple.com][1])
2. **monocle‑rizz** README – Next.js + OpenAI architecture inspiration. ([github.com][2])
3. **Dru‑O7/RizzGPT** README – rating & Twilio features evidence. ([github.com][3])
4. **chensterman/RizzGPT** repository – confirms browser‐automation + agent variation (architecture diversity). ([github.com][4])

---

*Prepared by: veteran mobile architect & PM*

[1]: https://apps.apple.com/us/app/rizzgpt-pick-up-lines-rizz/id6449148120 "
      ‎RizzGPT: Pick Up Lines & Rizz on the App Store
    "
[2]: https://github.com/acui51/monocle-rizz "GitHub - acui51/monocle-rizz: rizzGPT"
[3]: https://github.com/Dru-O7/RizzGPT "GitHub - Dru-O7/RizzGPT: RizzGPT: The ultimate wingman that will rate your pick-up line."
[4]: https://github.com/chensterman/RizzGPT?utm_source=chatgpt.com "chensterman/RizzGPT: Using AI to absolutely ruin the dating market.""""
