// RahulCoolGram phone UI: an inbox, one chat with the store, and an account switcher.
// New messages arrive by polling the API every 1.5 seconds.

const POLL_MS = 1500;
const GROUP_GAP_MS = 60 * 1000; // messages closer than this are grouped
const DIVIDER_GAP_MS = 15 * 60 * 1000; // show a time divider after a 15 minute gap
const STORE_LOGO = "/static/brand/logo-128.png";

// Generic line icons (lucide-style), drawn inline.
const ICONS = {
  chevronDown: '<path d="m6 9 6 6 6-6"/>',
  chevronLeft: '<path d="m15 18-6-6 6-6"/>',
  video: '<path d="m16 13 5.2 3.5a.5.5 0 0 0 .8-.4V7.9a.5.5 0 0 0-.8-.4L16 11"/><rect x="2" y="6" width="14" height="12" rx="2"/>',
  edit: '<path d="M12 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.4 2.6a2.1 2.1 0 1 1 3 3L12 15l-4 1 1-4Z"/>',
  search: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
  home: '<path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1Z"/>',
  reels: '<rect x="3" y="3" width="18" height="18" rx="4"/><path d="M3 8h18M8 3l3 5M14 3l3 5"/><path d="m10 11.5 4.5 2.5-4.5 2.5Z"/>',
  bag: '<path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><path d="M3 6h18M16 10a4 4 0 0 1-8 0"/>',
  phone: '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2Z"/>',
  info: '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>',
  camera: '<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3Z"/><circle cx="12" cy="13" r="3"/>',
  mic: '<rect x="9" y="2" width="6" height="12" rx="3"/><path d="M19 10v1a7 7 0 0 1-14 0v-1M12 18v4"/>',
  image: '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.1-3.1a2 2 0 0 0-2.8 0L6 21"/>',
  smile: '<circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01"/>',
};

// Chats that only exist to make the inbox look real; tapping them shows a hint.
const DECORATIVE_CHATS = [
  { name: "everest.trekkers", preview: "Sent a reel by @nepal.trails", time: "2h" },
  { name: "momo.house.ktm", preview: "Thanks for visiting! 🥟", time: "1d" },
];

const $ = (id) => document.getElementById(id);

const state = {
  customers: [],
  store: null,
  me: null, // the customer persona we are playing
  messages: [],
  threadOpen: false,
};

// ---------- small helpers ----------

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (key === "class") node.className = value;
    else if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
    else node.setAttribute(key, value);
  }
  for (const child of children) if (child != null) node.append(child);
  return node;
}

function icon(name) {
  const span = el("span", { class: "icon" });
  span.innerHTML = svg(ICONS[name]);
  return span;
}

function svg(paths) {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${paths}</svg>`;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) throw new Error(`${response.status} ${await response.text()}`);
  return response.json();
}

function storage(key, value) {
  try {
    if (value === undefined) return localStorage.getItem(key);
    localStorage.setItem(key, value);
  } catch {
    return null; // storage can be blocked; the app still works without it
  }
}

function shortAgo(iso) {
  const seconds = Math.max(0, (Date.now() - new Date(iso)) / 1000);
  if (seconds < 60) return "now";
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`;
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d`;
  return `${Math.floor(seconds / 604800)}w`;
}

function dividerTime(iso) {
  const date = new Date(iso);
  const time = date.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
  const sameDay = date.toDateString() === new Date().toDateString();
  return sameDay ? time : `${date.toLocaleDateString([], { weekday: "short" })} ${time}`;
}

function initialsAvatar(name) {
  const hue = [...name].reduce((sum, c) => sum + c.charCodeAt(0), 0) % 360;
  const letter = name[0].toUpperCase();
  const image = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96"><rect width="96" height="96" fill="hsl(${hue} 45% 55%)"/><text x="48" y="60" font-family="sans-serif" font-size="40" fill="#fff" text-anchor="middle">${letter}</text></svg>`;
  return `data:image/svg+xml,${encodeURIComponent(image)}`;
}

function showToast(text) {
  const toast = $("toast");
  toast.textContent = text;
  toast.classList.remove("hidden");
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => toast.classList.add("hidden"), 2200);
}

// ---------- persona (who am I?) ----------

function setMe(customer) {
  state.me = customer;
  storage("rcg.me", customer.id);
  $("my-username").textContent = customer.username;
  $("nav-avatar").src = customer.avatar;
  $("my-note-avatar").src = customer.avatar;
  state.messages = [];
  refresh();
}

function openSwitcher() {
  $("account-list").replaceChildren(
    ...state.customers.map((c) =>
      el(
        "li",
        {},
        el(
          "button",
          {
            class: `account${c.id === state.me.id ? " current" : ""}`,
            onclick: () => {
              closeSwitcher();
              if (c.id !== state.me.id) setMe(c);
            },
          },
          el("img", { src: c.avatar, alt: "" }),
          el("div", {}, el("strong", {}, c.username), el("small", {}, c.name)),
          el("span", { class: "radio" }),
        ),
      ),
    ),
  );
  $("sheet-backdrop").classList.remove("hidden");
}

function closeSwitcher() {
  $("sheet-backdrop").classList.add("hidden");
}

// ---------- inbox ----------

function lastSeenKey() {
  return `rcg.lastSeen.${state.me.id}`;
}

function renderInbox() {
  const last = state.messages.at(-1);
  const lastSeen = storage(lastSeenKey()) || "";
  const unread = last && last.sender === "store" && last.sent_at > lastSeen;

  let preview = "Tap to chat";
  if (last) preview = last.sender === "customer" ? `You: ${last.text}` : last.text;

  const storeChat = el(
    "button",
    { class: `chat${unread ? " unread" : ""}`, onclick: openThread },
    el("span", { class: "ring" }, el("img", { src: STORE_LOGO, alt: "" })),
    el(
      "span",
      { class: "chat-text" },
      el("span", { class: "chat-name" }, state.store.name),
      el(
        "span",
        { class: "chat-preview" },
        el("span", { class: "preview-text" }, preview),
        last ? el("span", {}, `· ${shortAgo(last.sent_at)}`) : null,
      ),
    ),
    unread ? el("span", { class: "unread-dot" }) : el("span", { class: "camera-hint" }, icon("camera")),
  );

  const decorative = DECORATIVE_CHATS.map((chat) =>
    el(
      "li",
      {},
      el(
        "button",
        { class: "chat", onclick: () => showToast("Only Himal Luggage Co. is connected in this demo.") },
        el("span", { class: "no-ring" }, el("img", { src: initialsAvatar(chat.name), alt: "" })),
        el(
          "span",
          { class: "chat-text" },
          el("span", { class: "chat-name" }, chat.name),
          el(
            "span",
            { class: "chat-preview" },
            el("span", { class: "preview-text" }, chat.preview),
            el("span", {}, `· ${chat.time}`),
          ),
        ),
        el("span", { class: "camera-hint" }, icon("camera")),
      ),
    ),
  );

  $("chat-list").replaceChildren(el("li", {}, storeChat), ...decorative);
}

// ---------- thread ----------

function openThread() {
  state.threadOpen = true;
  $("inbox-screen").classList.add("hidden");
  $("thread-screen").classList.remove("hidden");
  renderThread();
  $("text").focus();
}

function closeThread() {
  state.threadOpen = false;
  $("thread-screen").classList.add("hidden");
  $("inbox-screen").classList.remove("hidden");
  renderInbox();
}

function renderThread() {
  const box = $("messages");
  const nearBottom = box.scrollHeight - box.scrollTop - box.clientHeight < 80;
  const nodes = [profileIntro()];

  state.messages.forEach((message, i) => {
    const prev = state.messages[i - 1];
    const next = state.messages[i + 1];
    const time = new Date(message.sent_at);

    if (!prev || time - new Date(prev.sent_at) > DIVIDER_GAP_MS) {
      nodes.push(el("div", { class: "time-divider" }, dividerTime(message.sent_at)));
    }
    const startsGroup = !prev || prev.sender !== message.sender || time - new Date(prev.sent_at) > GROUP_GAP_MS;
    const endsGroup = !next || next.sender !== message.sender || new Date(next.sent_at) - time > GROUP_GAP_MS;
    nodes.push(messageRow(message, startsGroup, endsGroup));
  });

  const last = state.messages.at(-1);
  if (last?.sender === "customer") nodes.push(el("div", { class: "status" }, "Sent"));

  box.replaceChildren(...nodes);
  if (nearBottom || !renderThread.done) box.scrollTop = box.scrollHeight;
  renderThread.done = true;

  // Everything on screen counts as seen.
  const lastStore = state.messages.findLast((m) => m.sender === "store");
  if (lastStore) storage(lastSeenKey(), lastStore.sent_at);
}

function messageRow(message, startsGroup, endsGroup) {
  const mine = message.sender === "customer";
  const classes = ["row", mine ? "mine" : "theirs"];
  if (startsGroup) classes.push("group-start");
  if (endsGroup) classes.push("group-end");

  const row = el("div", { class: classes.join(" ") });
  if (!mine) {
    // The store's avatar sits next to the last bubble of each group.
    row.append(
      endsGroup ? el("img", { class: "mini-avatar", src: STORE_LOGO, alt: "" }) : el("span", { class: "avatar-space" }),
    );
  }
  row.append(el("div", { class: "bubble", title: dividerTime(message.sent_at) }, message.text));
  return row;
}

function profileIntro() {
  return el(
    "div",
    { class: "profile-intro" },
    el("span", { class: "ring" }, el("img", { src: STORE_LOGO, alt: "" })),
    el("strong", {}, state.store.name),
    el("span", { class: "muted" }, `${state.store.username} · RahulCoolGram`),
    el("button", { class: "view-profile", type: "button" }, "View profile"),
  );
}

// ---------- sending ----------

async function send(event) {
  event.preventDefault();
  const input = $("text");
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  updateComposer();
  const message = await api(`/api/customers/${state.me.id}/messages`, {
    method: "POST",
    body: JSON.stringify({ text }),
  });
  state.messages.push(message);
  renderThread();
}

function updateComposer() {
  const hasText = $("text").value.trim().length > 0;
  $("send").classList.toggle("hidden", !hasText);
  $("composer-icons").classList.toggle("hidden", hasText);
}

// ---------- polling ----------

async function refresh() {
  if (!state.me) return;
  const customerId = state.me.id;
  try {
    const messages = await api(`/api/customers/${customerId}/messages`);
    if (customerId !== state.me.id) return; // persona changed while we were waiting
    const changed =
      messages.length !== state.messages.length || messages.at(-1)?.id !== state.messages.at(-1)?.id;
    state.messages = messages;
    if (state.threadOpen && changed) renderThread();
    if (!state.threadOpen) renderInbox();
  } catch (error) {
    console.warn("refresh failed", error);
  }
}

// ---------- start ----------

async function start() {
  document.querySelectorAll("[data-icon]").forEach((node) => {
    node.innerHTML = svg(ICONS[node.dataset.icon]);
  });
  [state.customers, state.store] = await Promise.all([api("/api/customers"), api("/api/store")]);
  $("store-name").textContent = state.store.name;
  $("store-username").textContent = state.store.username;

  $("composer").addEventListener("submit", send);
  $("text").addEventListener("input", updateComposer);
  $("back").addEventListener("click", closeThread);
  $("account-switch").addEventListener("click", openSwitcher);
  $("nav-profile").addEventListener("click", openSwitcher);
  $("sheet-backdrop").addEventListener("click", (e) => {
    if (e.target.id === "sheet-backdrop") closeSwitcher();
  });

  const saved = state.customers.find((c) => c.id === storage("rcg.me"));
  setMe(saved || state.customers[0]);
  setInterval(refresh, POLL_MS);
}

start();
