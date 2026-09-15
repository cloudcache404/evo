# ================================================================
#                 NOTESWALLAH BUDDY (EVO STUDY BUDDY)
#           Next-Gen Student AI Assistant for Telegram
# ================================================================
#
# Features:
#   • 🤖 Multi-Model AI Engine (Qwen 2.5, Llama 3.3, Nemotron, Auto)
#   • 📷 Vision AI for Handwritten & Printed Doubts
#   • 📚 Modes: Ask, Explain, Smart Notes, Quiz Master
#   • 🌐 Bilingual (English + Hinglish Romanized)
#   • ⚡ PHP Telemetry & Live Web Monitor Integration
#   • 🛟 Built-in Support & Ticket Routing to Owner
#   • 👑 Owner Control Center with Broadcast & Live Metrics
#   • 🎨 Premium Typography, Glassmorphic formatting & UI
#
# ================================================================

import asyncio
import base64
import html
import json
import logging
import os
import platform
import re
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests

try:
    import psutil
except ImportError:
    psutil = None

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    User,
)
from telegram.constants import ChatAction, ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ================================================================
# CONFIGURATION (100% SELF-CONTAINED — NO .ENV / YAML REQUIRED)
# ================================================================

BOT_NAME = "NotesWallah Buddy"
BOT_VERSION = "2.4.0 (Autonomous Edition)"
BOT_ENV = "Cloud Production"

# ----------------------------------------------------------------
# YOUR TELEGRAM BOT TOKEN
# ----------------------------------------------------------------
BOT_TOKEN ="YOUR_TELEGRAM_BOT_TOKEN"

# ----------------------------------------------------------------
# YOUR TELEGRAM NUMERIC USER ID (For Owner /admin & Support Alerts)
# ----------------------------------------------------------------
OWNER_ID = 123456789

# ----------------------------------------------------------------
# OPENROUTER AI API KEY
# ----------------------------------------------------------------
OPENROUTER_API_KEY = "YOU_OPEN_ROUTER_APIKEY"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# ----------------------------------------------------------------
# PHP TELEMETRY & WEB DASHBOARD ENDPOINT
# Point this to your live website (e.g., https://noteswallah.xyz/api/bot_telemetry.php)
# or localhost if testing locally.
# ----------------------------------------------------------------
PHP_MONITOR_URL = "https://example.com/api/bot_telemetry.php"

PHP_API_SECRET = "NW_BOT_SECRET_2026_KEY"

ENABLE_PHP_TELEMETRY = True

# ----------------------------------------------------------------
# Bot Tuning & Assets
# ----------------------------------------------------------------
LOGO_FILE = os.path.join(os.path.dirname(__file__), "logo.png")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
LOCAL_STATS_FILE = os.path.join(DATA_DIR, "stats.json")
LOCAL_USERS_FILE = os.path.join(DATA_DIR, "users.json")

SUPPORT_ENABLED = True
MAX_HISTORY_MESSAGES = 14
MAX_SUPPORT_LENGTH = 3500

# Bot start timestamp for uptime calculation
BOT_START_TIME = time.time()

# Ensure local data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# ================================================================
# AI MODELS CATALOG (EXACT ALIGNED WITH NotesWallah ai.php)
# ================================================================

MODELS = {
    "qwen": {
        "name": "⚡ Qwen 2.5 7B",
        "badge": "Fast & Concise",
        "id": "qwen/qwen-2.5-7b-instruct",
        "description": "Ultra fast, brilliant for instant doubts and formulas.",
    },
    "llama": {
        "name": "🦙 Llama 3.3 70B",
        "badge": "High Intelligence",
        "id": "meta-llama/llama-3.3-70b-instruct",
        "description": "Deep reasoning, step-by-step proofs and complex code.",
    },
    "nemotron_super": {
        "name": "🟢 Nemotron 3 Super",
        "badge": "NVIDIA Free Tier",
        "id": "nvidia/nemotron-3-super-120b-a12b:free",
        "description": "Generates structured diagrams, summaries, and exam tables.",
    },
    "nemotron_vision": {
        "name": "👁️ Nemotron Omni Vision",
        "badge": "Multimodal Vision",
        "id": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
        "description": "Specialized in analyzing diagrams, handwritten math & questions.",
    },
    "auto": {
        "name": "🔄 OpenRouter Auto",
        "badge": "Smart Auto-Routing",
        "id": "openrouter/auto",
        "description": "Automatically selects the best and most available model.",
    },
}

DEFAULT_MODEL = "qwen"

# ================================================================
# LOGGING SETUP
# ================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger("NotesWallahBuddy")

# ================================================================
# TELEMETRY & STATS ENGINE
# ================================================================

class TelemetryEngine:
    """Manages local metrics and communicates with PHP backend."""

    def __init__(self):
        self.stats: Dict[str, Any] = self._load_local_stats()
        self.known_users: Dict[str, Any] = self._load_known_users()

    def _load_local_stats(self) -> Dict[str, Any]:
        if os.path.exists(LOCAL_STATS_FILE):
            try:
                with open(LOCAL_STATS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "images_processed": 0,
            "support_tickets": 0,
            "modes_used": {"normal": 0, "simple": 0, "notes": 0, "quiz": 0},
            "models_used": {k: 0 for k in MODELS.keys()},
            "languages_used": {"english": 0, "hinglish": 0},
            "total_latency_ms": 0,
            "latencies": [],
        }

    def _save_local_stats(self):
        try:
            with open(LOCAL_STATS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save local stats: {e}")

    def _load_known_users(self) -> Dict[str, Any]:
        if os.path.exists(LOCAL_USERS_FILE):
            try:
                with open(LOCAL_USERS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_known_users(self):
        try:
            with open(LOCAL_USERS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.known_users, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save known users: {e}")

    def touch_user(self, user: User, mode: str, model: str, language: str):
        uid = str(user.id)
        now_iso = datetime.now(timezone.utc).isoformat()
        if uid not in self.known_users:
            self.known_users[uid] = {
                "id": user.id,
                "first_name": user.first_name or "",
                "username": user.username or "",
                "first_seen": now_iso,
                "last_seen": now_iso,
                "query_count": 0,
                "preferred_mode": mode,
                "preferred_model": model,
                "preferred_language": language,
            }
        self.known_users[uid]["last_seen"] = now_iso
        self.known_users[uid]["query_count"] += 1
        self.known_users[uid]["preferred_mode"] = mode
        self.known_users[uid]["preferred_model"] = model
        self.known_users[uid]["preferred_language"] = language
        self._save_known_users()

    def record_query(
        self,
        user: User,
        mode: str,
        model: str,
        language: str,
        latency_ms: float,
        success: bool = True,
        is_image: bool = False,
    ):
        self.touch_user(user, mode, model, language)
        self.stats["total_requests"] += 1
        if success:
            self.stats["successful_requests"] += 1
        else:
            self.stats["failed_requests"] += 1

        if is_image:
            self.stats["images_processed"] += 1

        self.stats["modes_used"][mode] = self.stats["modes_used"].get(mode, 0) + 1
        self.stats["models_used"][model] = self.stats["models_used"].get(model, 0) + 1
        self.stats["languages_used"][language] = self.stats["languages_used"].get(language, 0) + 1

        self.stats["total_latency_ms"] += latency_ms
        self.stats["latencies"].append(round(latency_ms, 2))
        if len(self.stats["latencies"]) > 500:
            self.stats["latencies"] = self.stats["latencies"][-500:]

        self._save_local_stats()

        # Asynchronously send telemetry to PHP backend
        if ENABLE_PHP_TELEMETRY:
            asyncio.create_task(
                self._send_php_telemetry({
                    "action": "log_usage",
                    "secret": PHP_API_SECRET,
                    "event": {
                        "user_id": user.id,
                        "username": user.username or "Anonymous",
                        "full_name": user.full_name or "Student",
                        "mode": mode,
                        "model": model,
                        "language": language,
                        "latency_ms": round(latency_ms, 2),
                        "is_image": is_image,
                        "success": success,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                })
            )

    def record_support_ticket(self, user: User, report_text: str):
        self.stats["support_tickets"] += 1
        self._save_local_stats()

        if ENABLE_PHP_TELEMETRY:
            asyncio.create_task(
                self._send_php_telemetry({
                    "action": "log_support",
                    "secret": PHP_API_SECRET,
                    "ticket": {
                        "user_id": user.id,
                        "username": user.username or "",
                        "full_name": user.full_name or "Student",
                        "report": report_text,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                })
            )

    def get_system_metrics(self) -> Dict[str, Any]:
        uptime_sec = int(time.time() - BOT_START_TIME)
        days = uptime_sec // 86400
        hours = (uptime_sec % 86400) // 3600
        minutes = (uptime_sec % 3600) // 60
        seconds = uptime_sec % 60
        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s" if days > 0 else f"{hours}h {minutes}m {seconds}s"

        ram_mb = 0.0
        cpu_pct = 0.0
        if psutil:
            try:
                proc = psutil.Process()
                ram_mb = proc.memory_info().rss / (1024 * 1024)
                cpu_pct = psutil.cpu_percent(interval=None)
            except Exception:
                pass

        avg_latency = 0.0
        if self.stats["successful_requests"] > 0:
            avg_latency = self.stats["total_latency_ms"] / self.stats["successful_requests"]

        return {
            "uptime_seconds": uptime_sec,
            "uptime_formatted": uptime_str,
            "ram_mb": round(ram_mb, 2),
            "cpu_percent": round(cpu_pct, 1),
            "python_version": platform.python_version(),
            "total_users": len(self.known_users),
            "total_requests": self.stats["total_requests"],
            "successful_requests": self.stats["successful_requests"],
            "failed_requests": self.stats["failed_requests"],
            "avg_latency_ms": round(avg_latency, 2),
            "support_tickets": self.stats["support_tickets"],
            "modes_breakdown": self.stats["modes_used"],
            "models_breakdown": self.stats["models_used"],
        }

    async def _send_php_telemetry(self, payload: Dict[str, Any]):
        """Non-blocking telemetry POST to PHP endpoint."""
        def _post():
            try:
                requests.post(
                    PHP_MONITOR_URL,
                    json=payload,
                    timeout=5,
                    headers={"Content-Type": "application/json", "X-Bot-Client": "NotesWallah-Telegram-Bot"}
                )
            except Exception:
                # Silently ignore if PHP webserver is offline
                pass

        await asyncio.to_thread(_post)

    async def send_heartbeat_pulse(self):
        """Sends periodic heartbeat to PHP server."""
        while True:
            try:
                metrics = self.get_system_metrics()
                payload = {
                    "action": "heartbeat",
                    "secret": PHP_API_SECRET,
                    "bot_name": BOT_NAME,
                    "version": BOT_VERSION,
                    "status": "online",
                    "metrics": metrics,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                await self._send_php_telemetry(payload)
            except Exception as e:
                logger.debug(f"Heartbeat pulse error: {e}")
            await asyncio.sleep(45)  # pulse every 45s


telemetry = TelemetryEngine()

# ================================================================
# AESTHETIC TEXT FORMATTERS & TEMPLATES
# ================================================================

def format_telegram_html(text: str) -> str:
    """
    Converts standard Markdown formatting (bold, italics, code blocks)
    to Telegram safe HTML to ensure pristine rendering without parse errors.
    """
    if not text:
        return ""

    # Preserve markdown code blocks ```lang ... ```
    blocks = []
    def save_code_block(match):
        lang = match.group(1) or ""
        code = match.group(2)
        escaped_code = html.escape(code.strip())
        blocks.append(f"<pre><code>{escaped_code}</code></pre>")
        return f"__CODE_BLOCK_{len(blocks)-1}__"

    text = re.sub(r"```([a-zA-Z0-9_-]*)\n?(.*?)```", save_code_block, text, flags=re.DOTALL)

    # Preserve inline `code`
    inline_codes = []
    def save_inline_code(match):
        code = match.group(1)
        inline_codes.append(f"<code>{html.escape(code)}</code>")
        return f"__INLINE_CODE_{len(inline_codes)-1}__"

    text = re.sub(r"`([^`\n]+)`", save_inline_code, text)

    # Basic text escaping for remaining characters
    text = html.escape(text)

    # Convert markdown **bold** to <b>bold</b>
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    # Convert markdown *italic* or _italic_ to <i>italic</i>
    text = re.sub(r"(?<!\w)\*([^*]+)\*(?!\w)", r"<i>\1</i>", text)
    text = re.sub(r"(?<!\w)_([^_]+)_(?!\w)", r"<i>\1</i>", text)

    # Restore code blocks
    for i, block in enumerate(blocks):
        text = text.replace(f"__CODE_BLOCK_{i}__", block)
    for i, icode in enumerate(inline_codes):
        text = text.replace(f"__INLINE_CODE_{i}__", icode)

    return text.strip()


WELCOME_BANNER = """
✨ <b>NotesWallah Buddy</b> • <i>AI Study Companion</i>
━━━━━━━━━━━━━━━━━━━━━━━━━━━

👋 <b>Welcome, scholar!</b> I am your personal 24/7 AI tutor designed specifically for CBSE, ICSE, College & Competitive prep.

🎯 <b>Choose your Study Mode:</b>
• 📚 <b>Ask:</b> Direct answers & step-by-step math solver
• 🧠 <b>Explain:</b> Deep simplified concepts with real-world analogies
• 📝 <b>Notes:</b> Exam-ready crisp revision points & formulas
• ❓ <b>Quiz:</b> Interactive topic quiz master to test your memory

📷 <b>Got a hard question?</b> Snap a photo and send it directly!
━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

BETA_NOTICE = """
🧪 <b>NotesWallah Buddy — Architecture & Beta</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━
• <b>Engine:</b> OpenRouter Unified Neural Routing
• <b>Vision:</b> NVIDIA Nemotron Omni 30B Vision
• <b>State Management:</b> Zero-bloat Async Context
• <b>Server Sync:</b> Live Telemetry to NotesWallah Admin

<i>Some bleeding-edge free models may occasionally experience high load. If an answer takes longer, you can switch models in <b>⚙️ Settings</b>.</i>
"""

# ================================================================
# USER SETTINGS HELPERS
# ================================================================

def get_language(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("language", "english")

def get_mode(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("mode", "normal")

def get_model(context: ContextTypes.DEFAULT_TYPE) -> str:
    model = context.user_data.get("model", DEFAULT_MODEL)
    return model if model in MODELS else DEFAULT_MODEL

def get_history(context: ContextTypes.DEFAULT_TYPE) -> List[Dict[str, str]]:
    return context.user_data.setdefault("history", [])

def language_name(language: str) -> str:
    return "🇮🇳 Hinglish" if language == "hinglish" else "🇬🇧 English"

def mode_name(mode: str) -> str:
    names = {
        "normal": "📚 Ask Doubt",
        "simple": "🧠 Concept Explain",
        "notes": "📝 Revision Notes",
        "quiz": "❓ Quiz Master",
    }
    return names.get(mode, "📚 Ask Doubt")

def model_name(model: str) -> str:
    return MODELS.get(model, MODELS[DEFAULT_MODEL])["name"]

def is_owner(update: Update) -> bool:
    user = update.effective_user
    return bool(user and OWNER_ID and user.id == OWNER_ID)

# ================================================================
# KEYBOARDS & UI BUILDERS
# ================================================================

def start_keyboard(context: ContextTypes.DEFAULT_TYPE) -> InlineKeyboardMarkup:
    cur_mode = get_mode(context)
    cur_model = get_model(context)
    cur_lang = get_language(context)

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                ("✨ " if cur_mode == "normal" else "") + "📚 Ask Doubt",
                callback_data="mode:normal"
            ),
            InlineKeyboardButton(
                ("✨ " if cur_mode == "simple" else "") + "🧠 Deep Explain",
                callback_data="mode:simple"
            ),
        ],
        [
            InlineKeyboardButton(
                ("✨ " if cur_mode == "notes" else "") + "📝 Smart Notes",
                callback_data="mode:notes"
            ),
            InlineKeyboardButton(
                ("✨ " if cur_mode == "quiz" else "") + "❓ Quiz Master",
                callback_data="mode:quiz"
            ),
        ],
        [
            InlineKeyboardButton(f"🤖 Model: {MODELS[cur_model]['name']}", callback_data="menu:model"),
        ],
        [
            InlineKeyboardButton(f"🌐 Language: {language_name(cur_lang)}", callback_data="menu:language"),
            InlineKeyboardButton("📊 My Stats", callback_data="user:stats"),
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="menu:settings"),
            InlineKeyboardButton("🛟 Help / Support", callback_data="menu:support"),
        ],
    ])


def settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 Switch AI Model", callback_data="menu:model")],
        [InlineKeyboardButton("🌐 Change Output Language", callback_data="menu:language")],
        [InlineKeyboardButton("🎯 Choose Study Mode", callback_data="menu:mode")],
        [InlineKeyboardButton("🧹 Clear Conversation Memory", callback_data="action:clear_history")],
        [InlineKeyboardButton("🧪 System & Beta Info", callback_data="menu:beta")],
        [InlineKeyboardButton("🏠 Back to Home", callback_data="home")],
    ])


def model_keyboard(context: ContextTypes.DEFAULT_TYPE) -> InlineKeyboardMarkup:
    current = get_model(context)
    rows = []
    for key, data in MODELS.items():
        label = f"✓ {data['name']} ({data['badge']})" if key == current else f"{data['name']} ({data['badge']})"
        rows.append([InlineKeyboardButton(label, callback_data=f"model:{key}")])
    rows.append([InlineKeyboardButton("‹ Back to Settings", callback_data="menu:settings")])
    return InlineKeyboardMarkup(rows)


def language_keyboard(context: ContextTypes.DEFAULT_TYPE) -> InlineKeyboardMarkup:
    current = get_language(context)
    eng_label = "✓ 🇬🇧 English (Academic & Clear)" if current == "english" else "🇬🇧 English (Academic & Clear)"
    hing_label = "✓ 🇮🇳 Hinglish (Natural Roman Hindi)" if current == "hinglish" else "🇮🇳 Hinglish (Natural Roman Hindi)"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(eng_label, callback_data="language:english")],
        [InlineKeyboardButton(hing_label, callback_data="language:hinglish")],
        [InlineKeyboardButton("‹ Back to Settings", callback_data="menu:settings")],
    ])


def mode_keyboard(context: ContextTypes.DEFAULT_TYPE) -> InlineKeyboardMarkup:
    current = get_mode(context)
    modes = [
        ("📚 Ask (Fast answers & problem solving)", "normal"),
        ("🧠 Deep Explain (Concepts, analogies, 'why')", "simple"),
        ("📝 Revision Notes (Bullets, formulas, summaries)", "notes"),
        ("❓ Quiz Master (Test yourself interactively)", "quiz"),
    ]
    rows = []
    for label, val in modes:
        display = f"✓ {label}" if current == val else label
        rows.append([InlineKeyboardButton(display, callback_data=f"mode:{val}")])
    rows.append([InlineKeyboardButton("‹ Back to Settings", callback_data="menu:settings")])
    return InlineKeyboardMarkup(rows)


def support_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Submit Feedback / Bug Report", callback_data="support:start")],
        [InlineKeyboardButton("🏠 Back to Home", callback_data="home")],
    ])


def admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊 Live Bot Health", callback_data="admin:status"),
            InlineKeyboardButton("⚡ PHP Sync Pulse", callback_data="admin:sync_php"),
        ],
        [
            InlineKeyboardButton(
                "🔴 Disable Support" if SUPPORT_ENABLED else "🟢 Enable Support",
                callback_data="admin:toggle_support"
            ),
            InlineKeyboardButton("📢 Broadcast Info", callback_data="admin:broadcast_help"),
        ],
        [
            InlineKeyboardButton("🔄 Refresh Dashboard", callback_data="admin:status"),
        ]
    ])

# ================================================================
# SYSTEM PROMPT BUILDER
# ================================================================

def build_system_prompt(context: ContextTypes.DEFAULT_TYPE) -> str:
    language = get_language(context)
    mode = get_mode(context)

    if language == "hinglish":
        lang_instruction = """
OUTPUT LANGUAGE:
Respond in natural, engaging Indian Hinglish (English mixed with conversational Hindi written in Roman script).
Example: "Iska core logic ye hai ki jab temperature increase hota hai toh particles ki kinetic energy badh jaati hai..."
Use clean formatting with bullet points and bold highlights.
"""
    else:
        lang_instruction = """
OUTPUT LANGUAGE:
Respond in crisp, student-friendly, and academically rigorous English.
"""

    if mode == "simple":
        mode_instruction = """
MODE: DEEP CONCEPT EXPLAINER
• Break down tricky topics into intuitive, easy-to-digest steps.
• Use relatable everyday analogies and real-world examples.
• Explain the fundamental "WHY" before the "HOW".
• Avoid overly complex mathematical jargon unless necessary.
"""
    elif mode == "notes":
        mode_instruction = """
MODE: SMART EXAM REVISION NOTES
• Format answers as high-yield, structured revision sheets.
• Include: 📌 Key Definitions, ⚡ Core Formulas, 🔍 Crucial Diagrams/Points, 💡 Exam Watchouts.
• Use bullet points, bold key terms, and numbered step breakdowns.
"""
    elif mode == "quiz":
        mode_instruction = """
MODE: ADAPTIVE QUIZ MASTER
• Formulate 1 to 3 targeted multiple-choice or short concept questions based on the topic.
• Do NOT provide the final answers immediately unless the student specifically asks for solutions.
• Encourage the student to try, then evaluate their answers with helpful explanations and scorecards.
"""
    else:
        mode_instruction = """
MODE: DIRECT PROBLEM SOLVER (ASK)
• Provide direct, accurate, step-by-step solutions to questions.
• For math and science equations, clearly state given parameters, formula used, calculations, and final highlighted answer with units.
"""

    return f"""You are NotesWallah Buddy, an elite, friendly, and empowering AI study assistant created for students.

CORE CAPABILITIES:
• Mathematics, Physics, Chemistry, Biology, Social Sciences
• Computer Science, Coding (Python, C++, Java, Web Dev, SQL)
• Exam Preparation & Doubt Clearing

{lang_instruction}
{mode_instruction}

STRICT GUIDELINES:
1. Always maintain factual and academic precision.
2. If equations are used, format them cleanly with standard symbols.
3. Keep explanations structured, motivating, and neatly formatted.
4. If code is requested, provide well-commented, modern code snippets.
"""

# ================================================================
# OPENROUTER AI CLIENT
# ================================================================

def request_openrouter(messages: List[Dict[str, Any]], model_key: str) -> (str, float):
    """
    Sends request to OpenRouter API and returns (response_text, latency_ms).
    """
    if not OPENROUTER_API_KEY or "YOUR_" in OPENROUTER_API_KEY:
        return (
            "⚠️ <b>OpenRouter API Key is missing.</b>\n\n"
            "Please configure your valid API key in <code>bot.py</code>.",
            0.0,
        )

    if model_key not in MODELS:
        model_key = DEFAULT_MODEL

    model_id = MODELS[model_key]["id"]

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://noteswallah.xyz",
        "X-Title": "NotesWallah Buddy Bot",
    }

    payload = {
        "model": model_id,
        "messages": messages,
        "temperature": 0.35,
    }

    start_t = time.time()
    try:
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=80,
        )
        latency_ms = (time.time() - start_t) * 1000

        response.raise_for_status()
        data = response.json()
        choices = data.get("choices", [])

        if not choices:
            return ("⚠️ <b>No response received from the AI model.</b> Please try again.", latency_ms)

        msg_obj = choices[0].get("message", {})
        content = msg_obj.get("content")

        if isinstance(content, list):
            parts = [item.get("text", "") for item in content if isinstance(item, dict) and item.get("type") == "text"]
            content = "\n".join(parts)

        if not content:
            return ("⚠️ <i>The model returned an empty response. Please rephrase your doubt.</i>", latency_ms)

        return (str(content).strip(), latency_ms)

    except requests.exceptions.Timeout:
        return ("⏳ <b>Request timed out.</b> The AI model is experiencing heavy traffic. Please try switching models in <code>/start</code>.", 80000.0)
    except requests.exceptions.HTTPError as he:
        latency_ms = (time.time() - start_t) * 1000
        try:
            err_json = response.json()
            err_msg = err_json.get("error", {}).get("message", str(he))
        except Exception:
            err_msg = str(he)
        return (f"⚠️ <b>AI Service Notice:</b>\n<code>{html.escape(str(err_msg)[:350])}</code>\n\nTry selecting another model via <code>/start</code>.", latency_ms)
    except Exception as e:
        latency_ms = (time.time() - start_t) * 1000
        logger.exception("Unexpected error in OpenRouter query")
        return (f"⚠️ <b>Network / Service Glitch:</b> <code>{html.escape(str(e)[:250])}</code>", latency_ms)

# ================================================================
# TEXT & VISION AI DISPATCHERS
# ================================================================

def generate_text_answer(context: ContextTypes.DEFAULT_TYPE, user_text: str) -> (str, float, str, str, str):
    history = get_history(context)
    mode = get_mode(context)
    model = get_model(context)
    language = get_language(context)

    messages = [{"role": "system", "content": build_system_prompt(context)}]
    messages.extend(history[-MAX_HISTORY_MESSAGES:])
    messages.append({"role": "user", "content": user_text})

    raw_answer, latency_ms = request_openrouter(messages, model)

    if raw_answer and not raw_answer.startswith("⚠️") and not raw_answer.startswith("⏳"):
        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": raw_answer})
        if len(history) > MAX_HISTORY_MESSAGES:
            del history[:-MAX_HISTORY_MESSAGES]

    return raw_answer, latency_ms, mode, model, language


def generate_vision_answer(context: ContextTypes.DEFAULT_TYPE, image_base64: str, caption: str) -> (str, float, str, str, str):
    mode = get_mode(context)
    model = "nemotron_vision"
    language = get_language(context)

    system_prompt = build_system_prompt(context)
    prompt_text = caption if caption else "Examine this study image/problem carefully. Identify all text, diagrams, or equations, and solve or explain it thoroughly in student-friendly format."

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt_text},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
            ],
        },
    ]

    raw_answer, latency_ms = request_openrouter(messages, model)
    return raw_answer, latency_ms, mode, model, language

# ================================================================
# BOT COMMAND HANDLERS
# ================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Initialize defaults
    context.user_data.setdefault("language", "english")
    context.user_data.setdefault("mode", "normal")
    context.user_data.setdefault("model", DEFAULT_MODEL)
    context.user_data.setdefault("history", [])
    context.user_data["waiting_for_support"] = False

    user = update.effective_user
    if user:
        telemetry.touch_user(user, get_mode(context), get_model(context), get_language(context))

    message = update.effective_message
    cur_model_name = model_name(get_model(context))
    cur_mode_name = mode_name(get_mode(context))
    cur_lang_name = language_name(get_language(context))

    caption_text = (
        WELCOME_BANNER +
        f"🤖 <b>Active Model:</b> <code>{cur_model_name}</code>\n"
        f"🎯 <b>Active Mode:</b> <code>{cur_mode_name}</code>\n"
        f"🌐 <b>Language:</b> <code>{cur_lang_name}</code>\n\n"
        "<i>Select an option below or type your doubt right away! 👇</i>"
    )

    kb = start_keyboard(context)

    try:
        if os.path.isfile(LOGO_FILE):
            with open(LOGO_FILE, "rb") as logo:
                await message.reply_photo(
                    photo=logo,
                    caption=caption_text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=kb,
                )
        else:
            await message.reply_text(
                caption_text,
                parse_mode=ParseMode.HTML,
                reply_markup=kb,
            )
    except Exception as e:
        logger.warning(f"Fallback to plain text start screen: {e}")
        await message.reply_text(caption_text, parse_mode=ParseMode.HTML, reply_markup=kb)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📖 <b>NotesWallah Buddy Guide & Commands</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>✨ Available Study Modes:</b>
• 📚 <b>Ask Doubt (/mode):</b> Fast step-by-step problem solver.
• 🧠 <b>Deep Explain:</b> In-depth concept intuition & analogies.
• 📝 <b>Smart Notes:</b> High-yield exam cheat-sheets & summaries.
• ❓ <b>Quiz Master:</b> Test your knowledge with instant feedback.

<b>📷 Vision Doubt Solving:</b>
• Take a photo of your textbook, whiteboard, or assignment and send it directly!

<b>⚡ Quick Bot Commands:</b>
• <code>/start</code> — Open main control dashboard
• <code>/mode</code> — Switch current study mode
• <code>/model</code> — Choose AI engine
• <code>/stats</code> — View your personal and server usage stats
• <code>/clear</code> — Reset conversation memory
• <code>/support</code> — Open direct ticket with the creator
• <code>/help</code> — Show this manual
━━━━━━━━━━━━━━━━━━━━━━━━━━━
<i>Empowering your learning journey at NotesWallah.</i> 🚀
"""
    await update.effective_message.reply_text(help_text, parse_mode=ParseMode.HTML)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id) if user else ""
    user_info = telemetry.known_users.get(uid, {})
    q_count = user_info.get("query_count", 0)

    sys_m = telemetry.get_system_metrics()

    stats_card = f"""
📊 <b>NotesWallah Buddy Live Telemetry</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 <b>Student:</b> {html.escape(user.full_name or 'Scholar')}
🆔 <b>User ID:</b> <code>{user.id}</code>
📈 <b>Your Queries:</b> <code>{q_count}</code>
🎯 <b>Current Mode:</b> <code>{mode_name(get_mode(context))}</code>
🤖 <b>Current Model:</b> <code>{model_name(get_model(context))}</code>
🌐 <b>Language:</b> <code>{language_name(get_language(context))}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ <b>GLOBAL SYSTEM VITALS</b>
⏱️ <b>Uptime:</b> <code>{sys_m['uptime_formatted']}</code>
🌐 <b>Total Students:</b> <code>{sys_m['total_users']}</code>
🚀 <b>Total AI Queries:</b> <code>{sys_m['total_requests']}</code>
⚡ <b>Avg AI Latency:</b> <code>{sys_m['avg_latency_ms']} ms</code>
🧠 <b>Memory (RAM):</b> <code>{sys_m['ram_mb']} MB</code>
🟢 <b>Status:</b> <code>Online & Healthy</code>
━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh Stats", callback_data="user:stats")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="home")],
    ])
    await update.effective_message.reply_text(stats_card, parse_mode=ParseMode.HTML, reply_markup=kb)


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["history"] = []
    await update.effective_message.reply_text(
        "🧹 <b>Memory Cleared!</b>\n\nYour previous context has been refreshed. What would you like to learn next?",
        parse_mode=ParseMode.HTML,
    )


async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not SUPPORT_ENABLED:
        await update.effective_message.reply_text(
            "🛟 <b>Support is temporarily under maintenance.</b>\nPlease check back shortly.",
            parse_mode=ParseMode.HTML,
        )
        return

    context.user_data["waiting_for_support"] = True
    text = """
🛟 <b>NotesWallah Helpdesk & Bug Report</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Encountered an issue, incorrect solution, or have a feature idea?

📝 <b>Simply type and send your message now in ONE single text.</b>
Our team reads every report to enhance NotesWallah Buddy.

<i>(Tip: To cancel, just send <code>/start</code>)</i>
"""
    await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)


# ================================================================
# OWNER ADMIN CONSOLE & BROADCAST
# ================================================================

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        await update.effective_message.reply_text("⛔ <b>Access Denied:</b> Owner clearance required.", parse_mode=ParseMode.HTML)
        return

    m = telemetry.get_system_metrics()
    status_emoji = "🟢" if SUPPORT_ENABLED else "🔴"

    admin_panel_text = f"""
👑 <b>NOTESWALLAH BUDDY OWNER CONSOLE</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 <b>Bot:</b> {BOT_NAME} <code>v{BOT_VERSION}</code>
⚡ <b>Status:</b> <code>ONLINE & POLLING</code>
⏱️ <b>Uptime:</b> <code>{m['uptime_formatted']}</code>
👥 <b>Total Users:</b> <code>{m['total_users']}</code>
💬 <b>Total Requests:</b> <code>{m['total_requests']}</code>
🛟 <b>Support Status:</b> {status_emoji} (<code>{m['support_tickets']}</code> tickets)
📈 <b>Avg Latency:</b> <code>{m['avg_latency_ms']} ms</code>
💻 <b>Host RAM:</b> <code>{m['ram_mb']} MB</code> (CPU: {m['cpu_percent']}%)
🔗 <b>PHP Monitor URL:</b> <code>{PHP_MONITOR_URL}</code>
━━━━━━━━━━━━━━━━━━━━━━━━━━━
<i>Broadcast: <code>/broadcast [Message]</code></i>
"""
    await update.effective_message.reply_text(admin_panel_text, parse_mode=ParseMode.HTML, reply_markup=admin_keyboard())


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        return

    if not context.args:
        await update.effective_message.reply_text(
            "📢 <b>Broadcast Usage:</b>\n<code>/broadcast Your message here...</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    broadcast_msg = " ".join(context.args)
    user_ids = list(telemetry.known_users.keys())

    if not user_ids:
        await update.effective_message.reply_text("⚠️ No registered users found yet.")
        return

    progress_msg = await update.effective_message.reply_text(f"🚀 Broadcasting to {len(user_ids)} users...")

    sent = 0
    failed = 0
    formatted_msg = f"📢 <b>NotesWallah Announcement</b>\n━━━━━━━━━━━━━━━━━━━━\n\n{format_telegram_html(broadcast_msg)}\n\n━━━━━━━━━━━━━━━━━━━━"

    for uid in user_ids:
        try:
            await context.bot.send_message(chat_id=int(uid), text=formatted_msg, parse_mode=ParseMode.HTML)
            sent += 1
            await asyncio.sleep(0.05)  # Telegram rate limit compliance
        except Exception:
            failed += 1

    await progress_msg.edit_text(
        f"✅ <b>Broadcast Completed</b>\n\n• Successfully Delivered: <code>{sent}</code>\n• Failed/Blocked: <code>{failed}</code>",
        parse_mode=ParseMode.HTML,
    )

# ================================================================
# MESSAGE & PHOTO HANDLERS
# ================================================================

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    user = update.effective_user
    if not message or not message.photo:
        return

    await message.chat.send_action(ChatAction.TYPING)

    status_note = await message.reply_text("🔍 <i>Analyzing image with Nemotron Vision AI...</i>", parse_mode=ParseMode.HTML)

    try:
        photo = message.photo[-1]
        telegram_file = await context.bot.get_file(photo.file_id)
        image_bytes = await telegram_file.download_as_bytearray()
        image_base64 = base64.b64encode(bytes(image_bytes)).decode("utf-8")
        caption = (message.caption or "").strip()

        answer_raw, latency_ms, mode, model, lang = await asyncio.to_thread(
            generate_vision_answer, context, image_base64, caption
        )

        telemetry.record_query(user, mode, model, lang, latency_ms, success=True, is_image=True)

        formatted_answer = format_telegram_html(answer_raw)
        footer = f"\n\n━━━━━━━━━━━━━━━━━━━━\n👁️ <i>Nemotron Omni Vision • {latency_ms/1000:.1f}s</i>"

        await status_note.delete()

        try:
            await message.reply_text(formatted_answer + footer, parse_mode=ParseMode.HTML)
        except Exception:
            await message.reply_text(answer_raw + f"\n\n[Vision processed in {latency_ms/1000:.1f}s]")

    except Exception as e:
        logger.exception("Failed image analysis")
        telemetry.record_query(user, "normal", "nemotron_vision", "english", 0.0, success=False, is_image=True)
        await status_note.edit_text("⚠️ <b>Could not analyze the image.</b> Please make sure the photo is clear and try again.", parse_mode=ParseMode.HTML)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    user = update.effective_user
    if not message or not message.text:
        return

    user_text = message.text.strip()
    if not user_text:
        return

    # Handle Support Ticket Submission
    if context.user_data.get("waiting_for_support", False):
        context.user_data["waiting_for_support"] = False

        if len(user_text) > MAX_SUPPORT_LENGTH:
            await message.reply_text(f"⚠️ Report exceeds max length ({MAX_SUPPORT_LENGTH} chars). Please shorten and submit again.")
            return

        telemetry.record_support_ticket(user, user_text)

        # Notify Owner directly on Telegram
        owner_ticket = (
            "🚨 <b>NEW NOTESWALLAH SUPPORT TICKET</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>From:</b> {html.escape(user.full_name or 'Unknown')} (@{user.username or 'None'})\n"
            f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
            f"🕒 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 <b>Report:</b>\n{html.escape(user_text)}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        try:
            await context.bot.send_message(chat_id=OWNER_ID, text=owner_ticket, parse_mode=ParseMode.HTML)
        except Exception as oe:
            logger.error(f"Failed sending support notification to owner: {oe}")

        await message.reply_text(
            "✅ <b>Report Submitted Successfully!</b>\n\nThank you for helping us improve NotesWallah Buddy. Our team has received your ticket.",
            parse_mode=ParseMode.HTML,
        )
        return

    # Normal AI Query
    await message.chat.send_action(ChatAction.TYPING)

    try:
        answer_raw, latency_ms, mode, model, lang = await asyncio.to_thread(
            generate_text_answer, context, user_text
        )

        telemetry.record_query(user, mode, model, lang, latency_ms, success=True, is_image=False)

        formatted_answer = format_telegram_html(answer_raw)

        # Aesthetic footer badge
        m_info = MODELS.get(model, {"name": model})
        footer = f"\n\n━━━━━━━━━━━━━━━━━━━━\n🤖 <i>{m_info['name']} • {latency_ms/1000:.1f}s</i>"

        try:
            await message.reply_text(formatted_answer + footer, parse_mode=ParseMode.HTML)
        except Exception:
            # Fallback in case of unexpected HTML parsing quirks
            await message.reply_text(answer_raw + f"\n\n[{m_info['name']} • {latency_ms/1000:.1f}s]")

    except Exception as e:
        logger.exception("Text processing error")
        telemetry.record_query(user, get_mode(context), get_model(context), get_language(context), 0.0, success=False)
        await message.reply_text("⚠️ <b>Something went wrong while formulating the answer.</b> Please try again or switch model with <code>/start</code>.", parse_mode=ParseMode.HTML)

# ================================================================
# CALLBACK QUERY ROUTER
# ================================================================

async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return

    data = query.data or ""
    user = update.effective_user

    # HOME / MAIN MENU
    if data == "home":
        await query.answer()
        cur_model_name = model_name(get_model(context))
        cur_mode_name = mode_name(get_mode(context))
        cur_lang_name = language_name(get_language(context))

        caption_text = (
            WELCOME_BANNER +
            f"🤖 <b>Active Model:</b> <code>{cur_model_name}</code>\n"
            f"🎯 <b>Active Mode:</b> <code>{cur_mode_name}</code>\n"
            f"🌐 <b>Language:</b> <code>{cur_lang_name}</code>\n\n"
            "<i>Select an option below or type your doubt right away! 👇</i>"
        )
        try:
            await query.edit_message_text(caption_text, parse_mode=ParseMode.HTML, reply_markup=start_keyboard(context))
        except Exception:
            await query.message.reply_text(caption_text, parse_mode=ParseMode.HTML, reply_markup=start_keyboard(context))
        return

    # USER STATS
    if data == "user:stats":
        await query.answer()
        uid = str(user.id) if user else ""
        user_info = telemetry.known_users.get(uid, {})
        q_count = user_info.get("query_count", 0)
        sys_m = telemetry.get_system_metrics()

        stats_card = f"""
📊 <b>NotesWallah Buddy Live Telemetry</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 <b>Student:</b> {html.escape(user.full_name or 'Scholar')}
🆔 <b>User ID:</b> <code>{user.id}</code>
📈 <b>Your Queries:</b> <code>{q_count}</code>
🎯 <b>Current Mode:</b> <code>{mode_name(get_mode(context))}</code>
🤖 <b>Current Model:</b> <code>{model_name(get_model(context))}</code>
🌐 <b>Language:</b> <code>{language_name(get_language(context))}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ <b>GLOBAL SYSTEM VITALS</b>
⏱️ <b>Uptime:</b> <code>{sys_m['uptime_formatted']}</code>
🌐 <b>Total Students:</b> <code>{sys_m['total_users']}</code>
🚀 <b>Total AI Queries:</b> <code>{sys_m['total_requests']}</code>
⚡ <b>Avg AI Latency:</b> <code>{sys_m['avg_latency_ms']} ms</code>
🧠 <b>Memory:</b> <code>{sys_m['ram_mb']} MB</code>
🟢 <b>Status:</b> <code>Online & Synchronized</code>
━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Refresh Stats", callback_data="user:stats")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="home")],
        ])
        await query.edit_message_text(stats_card, parse_mode=ParseMode.HTML, reply_markup=kb)
        return

    # SETTINGS MENU
    if data == "menu:settings":
        await query.answer()
        settings_text = f"""
⚙️ <b>Buddy Control Center & Preferences</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 <b>Model:</b> {model_name(get_model(context))}
🌐 <b>Language:</b> {language_name(get_language(context))}
🎯 <b>Mode:</b> {mode_name(get_mode(context))}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
<i>Customize your personal learning environment:</i>
"""
        await query.edit_message_text(settings_text, parse_mode=ParseMode.HTML, reply_markup=settings_keyboard())
        return

    # MODEL SELECTION MENU
    if data == "menu:model":
        await query.answer()
        m_text = f"""
🤖 <b>Select AI Brain</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Currently Active: <b>{model_name(get_model(context))}</b>

<i>Choose the neural engine tailored to your subject:</i>
"""
        await query.edit_message_text(m_text, parse_mode=ParseMode.HTML, reply_markup=model_keyboard(context))
        return

    # MODEL CHOSEN
    if data.startswith("model:"):
        await query.answer("Model selected!")
        model_key = data.split(":", 1)[1]
        if model_key in MODELS:
            context.user_data["model"] = model_key
            if user:
                telemetry.touch_user(user, get_mode(context), model_key, get_language(context))

        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(
            f"✅ <b>Switched to {model_name(model_key)}</b>\n\n{MODELS[model_key]['description']}\n\nYou can continue chatting now! 🚀",
            parse_mode=ParseMode.HTML,
        )
        return

    # LANGUAGE MENU
    if data == "menu:language":
        await query.answer()
        l_text = f"""
🌐 <b>Choose Response Language</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Currently Active: <b>{language_name(get_language(context))}</b>

<i>Select how you want NotesWallah Buddy to explain concepts:</i>
"""
        await query.edit_message_text(l_text, parse_mode=ParseMode.HTML, reply_markup=language_keyboard(context))
        return

    # LANGUAGE CHOSEN
    if data.startswith("language:"):
        await query.answer("Language updated!")
        lang_key = data.split(":", 1)[1]
        if lang_key in ("english", "hinglish"):
            context.user_data["language"] = lang_key
            if user:
                telemetry.touch_user(user, get_mode(context), get_model(context), lang_key)

        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(
            f"✅ <b>Language set to {language_name(lang_key)}</b>\n\nReady to assist! Ask your doubt whenever you like.",
            parse_mode=ParseMode.HTML,
        )
        return

    # MODE MENU
    if data == "menu:mode":
        await query.answer()
        mo_text = f"""
🎯 <b>Select Study Mode</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Currently Active: <b>{mode_name(get_mode(context))}</b>

<i>Choose the teaching format best suited for your study session:</i>
"""
        await query.edit_message_text(mo_text, parse_mode=ParseMode.HTML, reply_markup=mode_keyboard(context))
        return

    # MODE CHOSEN
    if data.startswith("mode:"):
        await query.answer("Mode updated!")
        mode_val = data.split(":", 1)[1]
        allowed = ("normal", "simple", "notes", "quiz")
        if mode_val in allowed:
            context.user_data["mode"] = mode_val
            if user:
                telemetry.touch_user(user, mode_val, get_model(context), get_language(context))

        await query.edit_message_reply_markup(reply_markup=None)
        mode_descriptions = {
            "normal": "Direct answers, formulas, step-by-step problem solver.",
            "simple": "Deep concept explanations with clear everyday analogies.",
            "notes": "Exam-ready revision points, cheat-sheets, and bullet summaries.",
            "quiz": "Interactive quiz master to test your memory and score your answers.",
        }
        await query.message.reply_text(
            f"✅ <b>{mode_name(mode_val)} Enabled</b>\n\n<i>{mode_descriptions.get(mode_val, '')}</i>\n\nSend your topic or question now! 📚",
            parse_mode=ParseMode.HTML,
        )
        return

    # CLEAR HISTORY
    if data == "action:clear_history":
        await query.answer("Memory reset!")
        context.user_data["history"] = []
        await query.edit_message_text(
            "🧹 <b>Conversation history cleared.</b>\n\nBuddy has reset context memory for fresh topics.",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Back to Home", callback_data="home")]])
        )
        return

    # BETA INFO
    if data == "menu:beta":
        await query.answer()
        await query.edit_message_text(
            BETA_NOTICE,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("‹ Back to Settings", callback_data="menu:settings")]])
        )
        return

    # SUPPORT MENU
    if data == "menu:support":
        await query.answer()
        sup_text = """
🛟 <b>NotesWallah Buddy Helpdesk</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Need assistance or found a bug?
Our support system directly routes your ticket to the development team.

• 🐛 Bug reports & UI feedback
• ⚡ Model availability questions
• 💡 Feature suggestions
━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        await query.edit_message_text(sup_text, parse_mode=ParseMode.HTML, reply_markup=support_keyboard())
        return

    # START SUPPORT TICKET
    if data == "support:start":
        await query.answer()
        context.user_data["waiting_for_support"] = True
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(
            "📝 <b>Please type and send your feedback/issue in ONE message now.</b>\n\n<i>(Type <code>/start</code> to cancel)</i>",
            parse_mode=ParseMode.HTML
        )
        return

    # ADMIN ACTIONS
    if data.startswith("admin:"):
        if not is_owner(update):
            await query.answer("⛔ Owner clearance required.", show_alert=True)
            return

        action = data.split(":", 1)[1]
        global SUPPORT_ENABLED

        if action == "toggle_support":
            SUPPORT_ENABLED = not SUPPORT_ENABLED
            await query.answer(f"Support {'Enabled' if SUPPORT_ENABLED else 'Disabled'}")
        elif action == "sync_php":
            metrics = telemetry.get_system_metrics()
            asyncio.create_task(telemetry._send_php_telemetry({
                "action": "heartbeat",
                "secret": PHP_API_SECRET,
                "bot_name": BOT_NAME,
                "version": BOT_VERSION,
                "status": "online",
                "metrics": metrics,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }))
            await query.answer("PHP Pulse sent!", show_alert=True)
        elif action == "broadcast_help":
            await query.answer("Use command: /broadcast <message>", show_alert=True)
            return
        else:
            await query.answer("Refreshed.")

        m = telemetry.get_system_metrics()
        status_emoji = "🟢" if SUPPORT_ENABLED else "🔴"
        admin_panel_text = f"""
👑 <b>NOTESWALLAH BUDDY OWNER CONSOLE</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 <b>Bot:</b> {BOT_NAME} <code>v{BOT_VERSION}</code>
⚡ <b>Status:</b> <code>ONLINE & POLLING</code>
⏱️ <b>Uptime:</b> <code>{m['uptime_formatted']}</code>
👥 <b>Total Users:</b> <code>{m['total_users']}</code>
💬 <b>Total Requests:</b> <code>{m['total_requests']}</code>
🛟 <b>Support Status:</b> {status_emoji} (<code>{m['support_tickets']}</code> tickets)
📈 <b>Avg Latency:</b> <code>{m['avg_latency_ms']} ms</code>
💻 <b>Host RAM:</b> <code>{m['ram_mb']} MB</code> (CPU: {m['cpu_percent']}%)
🔗 <b>PHP Monitor URL:</b> <code>{PHP_MONITOR_URL}</code>
━━━━━━━━━━━━━━━━━━━━━━━━━━━
<i>Broadcast: <code>/broadcast [Message]</code></i>
"""
        await query.edit_message_text(admin_panel_text, parse_mode=ParseMode.HTML, reply_markup=admin_keyboard())
        return

# ================================================================
# ERROR HANDLER
# ================================================================

async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Global Telegram Unhandled Exception:", exc_info=context.error)

# ================================================================
# MAIN ENTRYPOINT
# ================================================================

async def post_init(application: Application):
    """Start background heartbeat pulse once application is running."""
    asyncio.create_task(telemetry.send_heartbeat_pulse())
    logger.info("✓ Telemetry heartbeat background task initiated")


def main():
    print("=" * 64)
    print("       ✨ NOTESWALLAH BUDDY — TELEGRAM AI COMPANION ✨")
    print("=" * 64)

    if not BOT_TOKEN or "YOUR_" in BOT_TOKEN:
        print("\n[ERROR] Telegram BOT_TOKEN is missing! Please configure it in bot.py.\n")
        sys.exit(1)

    print(f"• Name:        {BOT_NAME}")
    print(f"• Version:     {BOT_VERSION} ({BOT_ENV})")
    print(f"• Owner ID:    {OWNER_ID}")
    print(f"• PHP Monitor: {PHP_MONITOR_URL}")
    print(f"• Models:      {len(MODELS)} Neural Models Configured")
    print("=" * 64)
    print("Connecting to Telegram Bot API...")

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Command Handlers
    application.add_handler(CommandHandler(["start"], start_command))
    application.add_handler(CommandHandler(["help"], help_command))
    application.add_handler(CommandHandler(["stats", "monitor"], stats_command))
    application.add_handler(CommandHandler(["clear", "reset"], clear_command))
    application.add_handler(CommandHandler(["support", "feedback", "fd"], support_command))
    application.add_handler(CommandHandler(["admin"], admin_command))
    application.add_handler(CommandHandler(["broadcast"], broadcast_command))
    application.add_handler(CommandHandler(["mode"], lambda u, c: start_command(u, c)))

    # Callback Query Router
    application.add_handler(CallbackQueryHandler(callback_router))

    # Media & Text Handlers
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Error Handler
    application.add_error_handler(global_error_handler)

    print("✓ Polling started. Bot is LIVE and serving queries!")
    print("=" * 64)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
