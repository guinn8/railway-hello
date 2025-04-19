Below is a **step‐wise development roadmap** that moves from the tiniest proof‑of‑concept to the full “living net‑art” piece you described. Each stage ends with one or two **checkpoints** so we can be sure the idea in your head made it into code before moving on.

---

## Stage 0 Bootstrap (½ day)

| Task | Notes |
|------|-------|
| **0‑1 Repo skeleton** | `src/` with `main.py`, `requirements.txt`, `README.md`. |
| **0‑2 Railway dev env** | Pin Python 3.11, set `OPENAI_API_KEY`, `PORT`. |
| **Checkpoint 0** | `curl https://<railway‑dev‑url>` returns “Hello prototype”. |

---

## Stage 1 *Bare‑bones LLM‑authored page* (1 day)  
*Goal: prove the function‑calling round‑trip works; no ads, no cache, no images.*

| Task | Deliverable |
|------|-------------|
| **1‑1 Define function schema** | Only **one** function: `create_page(title, body_html)`. |
| **1‑2 FastAPI route `/`** | Calls OpenAI with the function schema, streams HTML straight to client. |
| **1‑3 Guardrails** | Strip `<script>` tags for now; warn in console if found. |
| **Checkpoint 1** | Refreshing the page shows a *different* LLM‑generated layout every time. |

---

## Stage 2 *Slot + ad generation* (1 day)

| Task | Deliverable |
|------|-------------|
| **2‑1 Add `make_ad(html)` function** | LLM can embed `{{CALL:make_ad}}` placeholders inside its `body_html`. |
| **2‑2 Recursive resolver** | Walk the HTML string, detect placeholders, asynchronously fetch ad fragments via another LLM call. |
| **Checkpoint 2** | Page contains 3–10 unique ads each refresh; view‑source shows they came from separate calls. |

---

## Stage 3 *Images* (1–2 days)

| Task | Deliverable |
|------|-------------|
| **3‑1 Extend schema with `make_image(prompt)`** | LLM returns `{ "url": "data:image/png;base64,…" }` (DALL·E or placeholder). |
| **3‑2 Image budget toggle** | Env var `ENABLE_IMAGES`; off in dev to save tokens, on in prod/gallery. |
| **Checkpoint 3** | At least one ad per page displays a generated image when images are enabled. |

---

## Stage 4 *Goal link & session path* (1 day)

| Task | Deliverable |
|------|-------------|
| **4‑1 Add `goal_link(html)` function** | The model must call it exactly **once** per top‑level page. |
| **4‑2 Session logic** | Simple cookie with `session_id`; depth increments via `/page/{n}` route chosen by the LLM. |
| **Checkpoint 4** | Clicking the rare goal link leads to `/download/treasure.zip` (dummy file). |

---

## Stage 5 *Caching abstraction* (2 days)

| Task | Deliverable |
|------|-------------|
| **5‑1 `ContentStore` class** | Same interface we sketched, but **read/write only**, no fallback logic yet. |
| **5‑2 Integrate store** | All function calls route through `ContentStore.get()`. |
| **Checkpoint 5** | Refreshing an already‑visited page is instant (cache hit shown in logs). |

---

## Stage 6 *Budget & fallback logic* (½–1 day)

| Task | Deliverable |
|------|-------------|
| **6‑1 Token counter** | `api_calls` persisted in SQLite row; env var `API_BUDGET`. |
| **6‑2 Fallback strategy** | On miss+budget‑exhausted, return random cached artifact of that function. |
| **Checkpoint 6** | Set `API_BUDGET=1`, hit the site twice: first call hits OpenAI, second delivers cached/random content with **no** new API usage. |

---

## Stage 7 Polish / gallery readiness (open‑ended)

*   Add easter‑egg pop‑ups, sound bytes, hall‑of‑fame table, etc.  
*   Decide whether to allow `<script>` to run (full artistic chaos) or keep sandboxed.

---

### Testing approach at each checkpoint

* **Unit** – pytest cases for `ContentStore.get()`, placeholder resolver.  
* **Smoke** – GitHub Action that boots FastAPI, hits `/`, asserts `<html>` appears.  
* **Manual** – We (or gallery staff) open the Railway preview link, verify behaviour live.
