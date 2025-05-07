# -*- coding: utf-8 -*-

# Standard library imports
import json
import locale # <-- 加入這一行
import logging
import os
import queue
import re
import sys
import threading
import time
import tkinter as tk
import traceback
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from typing import Any, Dict, List, Optional, Tuple, Union

# Third-party imports
try:
    import requests
except ImportError:
    messagebox.showerror(
        "Missing Dependency",
        "The 'requests' library is required for the AI Assistant plugin. "
        "Please install it (Tools > Manage plug-ins...).",
    )
    # Optionally disable the plugin entirely here
    requests = None  # type: ignore

try:
    from markdown_it import MarkdownIt
    from markdown_it.token import Token
    from markdown_it.utils import read_fixture_file
except ImportError:
    messagebox.showerror(
        "Missing Dependency",
        "The 'markdown-it-py' library is required for the AI Assistant plugin. "
        "Please install it (Tools > Manage plug-ins...).",
    )
    MarkdownIt = None  # type: ignore
    Token = None  # type: ignore

# Thonny imports
from thonny import get_runner, get_shell, get_workbench, THONNY_USER_DIR, ui_utils, languages
from thonny.config_ui import ConfigurationPage
from thonny.languages import tr
from thonny.misc_utils import running_on_mac_os, running_on_windows
from thonny.editors import EditorCodeViewText
from thonny.shell import ShellMenu, ShellText # For potential monkey-patching

# Setup logging
logger = logging.getLogger(__name__)

# --- Constants ---
ASSISTANT_USER_DIR = os.path.join(THONNY_USER_DIR, "ai_assistant")
HISTORY_FILE = os.path.join(ASSISTANT_USER_DIR, "history.json")
MAX_HISTORY = 50 # Maximum number of messages (user + assistant) to keep and send

# --- Configuration Page ---

class AIAssistantConfigPage(ConfigurationPage):
    def __init__(self, master):
        super().__init__(master)
        self.dialog: Optional[ui_utils.CommonDialog] = None # Set by Thonny
        self._api_url_var = get_workbench().get_variable("ai_assistant.api_url")
        self._api_key_var = get_workbench().get_variable("ai_assistant.api_key")
        self._model_var = get_workbench().get_variable("ai_assistant.model")
        self._model_list_queue: queue.Queue = queue.Queue()

        # --- UI Elements (Manual Creation) ---
        pad_x = 10
        pad_y = 5
        label_width = 12

        # API URL
        api_url_label = ttk.Label(self, text=tr("API URL:"), width=label_width, anchor="w")
        api_url_label.grid(row=0, column=0, padx=(0, pad_x), pady=pad_y, sticky="w")
        self._api_url_entry = ttk.Entry(self, textvariable=self._api_url_var, width=50)
        self._api_url_entry.grid(row=0, column=1, pady=pad_y, sticky="ew")
        ui_utils.create_tooltip(self._api_url_entry, tr("Enter the base URL of the OpenAI-compatible API (e.g., http://localhost:8000/v1)"))

        # API Key
        api_key_label = ttk.Label(self, text=tr("API Key:"), width=label_width, anchor="w")
        api_key_label.grid(row=1, column=0, padx=(0, pad_x), pady=pad_y, sticky="w")
        self._api_key_entry = ttk.Entry(self, textvariable=self._api_key_var, show="*", width=50)
        self._api_key_entry.grid(row=1, column=1, pady=pad_y, sticky="ew")
        ui_utils.create_tooltip(self._api_key_entry, tr("Enter your API key (optional, depending on the server)"))

        # Model Selection
        model_label = ttk.Label(self, text=tr("Model:"), width=label_width, anchor="w")
        model_label.grid(row=2, column=0, padx=(0, pad_x), pady=pad_y, sticky="w")

        combobox_frame = ttk.Frame(self)
        combobox_frame.grid(row=2, column=1, pady=pad_y, sticky="ew")
        combobox_frame.columnconfigure(0, weight=1)

        self._model_combo = ttk.Combobox(
            combobox_frame,
            textvariable=self._model_var,
            state="readonly", # Important: use readonly, not disabled
            # width=40 # Let it expand
            values=[tr("<Click 'Fetch Models'>")] # Initial placeholder
        )
        self._model_combo.grid(row=0, column=0, sticky="ew", padx=(0, pad_x))
        ui_utils.create_tooltip(self._model_combo, tr("Select the AI model to use after fetching the list"))

        self._fetch_button = ttk.Button(
            combobox_frame,
            text=tr("Fetch Models"),
            command=self._start_fetch_models
        )
        self._fetch_button.grid(row=0, column=1, sticky="e")
        ui_utils.create_tooltip(self._fetch_button, tr("Fetch available models from the API URL"))

        # Make entry and combobox expand
        self.columnconfigure(1, weight=1)

        # Initial fetch if URL is present
        if self._api_url_var.get():
             self._start_fetch_models(show_error=False) # Don't show error on initial load


    def _start_fetch_models(self, show_error=True):
        if not requests:
            if show_error:
                messagebox.showerror(tr("Error"), tr("The 'requests' library is missing."), parent=self)
            return

        api_url = self._api_url_var.get().strip()
        if not api_url:
            if show_error:
                messagebox.showerror(tr("Error"), tr("API URL cannot be empty."), parent=self)
            return

        if not api_url.endswith("/"):
            api_url += "/"
        models_url = api_url + "models"
        api_key = self._api_key_var.get().strip()

        self._fetch_button.configure(state="disabled")
        self._model_combo.configure(values=[tr("<Fetching...>")])
        self.update_idletasks()

        thread = threading.Thread(target=self._fetch_models_thread, args=(models_url, api_key, show_error), daemon=True)
        thread.start()
        self._check_model_list_queue()

    def _fetch_models_thread(self, models_url: str, api_key: str, show_error: bool):
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            response = requests.get(models_url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()
            model_ids = sorted([model['id'] for model in data.get('data', []) if isinstance(model.get('id'), str)])
            if not model_ids:
                 model_ids = [tr("<No models found>")]
            self._model_list_queue.put({"success": True, "models": model_ids})
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch models from {models_url}: {e}", exc_info=True)
            self._model_list_queue.put({"success": False, "error": str(e), "show_error": show_error})
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching models: {e}", exc_info=True)
            self._model_list_queue.put({"success": False, "error": tr("An unexpected error occurred."), "show_error": show_error})

    def _check_model_list_queue(self):
        try:
            result = self._model_list_queue.get_nowait()
            self._fetch_button.configure(state="normal") # Re-enable button

            if result["success"]:
                models = result["models"]
                current_model = self._model_var.get()
                self._model_combo.configure(values=models)
                if current_model in models:
                    self._model_var.set(current_model) # Keep selection if valid
                elif models and models[0] != tr("<No models found>"):
                     self._model_var.set(models[0]) # Select first if none selected or invalid
                else:
                     self._model_var.set("") # Clear if no models found
            else:
                self._model_combo.configure(values=[tr("<Fetch failed>")])
                self._model_var.set("") # Clear selection on failure
                if result.get("show_error", True): # Check if error should be shown
                     messagebox.showerror(tr("Error Fetching Models"), result["error"], parent=self)

        except queue.Empty:
            self.after(100, self._check_model_list_queue) # Poll again

    def apply(self):
        # Thonny automatically saves variables bound to get_variable
        # We might do extra validation here if needed
        # If validation fails, return False
        # changed_options contains the names of options that were modified
        logger.debug("Applying AI Assistant settings. Changed", )
        return True # Return True if apply is successful

    def cancel(self):
        # Thonny automatically reverts variables bound to get_variable
        logger.debug("Cancelling AI Assistant settings")


# --- AI Assistant View ---

class AIAssistantView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self._message_queue: queue.Queue = queue.Queue()
        self._conversation_history: List[Dict[str, str]] = []
        self._current_ai_response = ""
        self._markdown = None
        if MarkdownIt:
            self._markdown = MarkdownIt() # Initialize Markdown parser
        self._cancel_requested = False # <--- 新增這個標誌

        self._load_history()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Conversation Display Area
        self._text_area = ScrolledText(
            self, wrap=tk.WORD, state="disabled", bd=0, padx=5, pady=5,
            font="TkDefaultFont" # Use default font initially
        )
        self._text_area.grid(row=0, column=0, sticky="nsew")
        self._setup_text_area_tags()
        self._render_history() # Render loaded history

        # Input Area Frame
        input_frame = ttk.Frame(self)
        input_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        input_frame.columnconfigure(0, weight=1)

        # Input Entry
        self._input_var = tk.StringVar()
        self._input_entry = ttk.Entry(input_frame, textvariable=self._input_var)
        self._input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self._input_entry.bind("<Return>", self._send_message)

        # Send Button
        self._send_button = ttk.Button(input_frame, text=tr("Send"), command=self._send_message)
        self._send_button.grid(row=0, column=1)

        # Clear Button
        self._clear_button = ttk.Button(input_frame, text=tr("Clear"), command=self._clear_conversation)
        self._clear_button.grid(row=0, column=2, padx=(5, 0))


        # Add TextMenu
        self._text_menu = ui_utils.TextMenu(self._text_area)
        self._text_area.bind(self._get_right_click_tag(), self._show_text_menu, True)

        self._check_queue() # Start polling the message queue


    def _get_right_click_tag(self):
        if running_on_mac_os():
            return "<Button-2>"
        else:
            return "<Button-3>"

    def _show_text_menu(self, event):
        self._text_menu.tk_popup(event.x_root, event.y_root)

    def _setup_text_area_tags(self):
        # Basic styles - adjust as needed
        default_font = tk.font.nametofont("TkDefaultFont")
        bold_font = default_font.copy()
        bold_font.configure(weight="bold")
        italic_font = default_font.copy()
        italic_font.configure(slant="italic")
        bold_italic_font = default_font.copy()
        bold_italic_font.configure(weight="bold", slant="italic")
        # Use a monospaced font for code - get it from Thonny's settings
        code_font_name = get_workbench().get_option("view.editor_font_family")
        code_font_size = get_workbench().get_option("view.editor_font_size") -1 # Slightly smaller
        try:
            code_font = tk.font.Font(family=code_font_name, size=code_font_size)
        except tk.TclError:
            logger.warning(f"Could not find font '{code_font_name}', using TkFixedFont")
            code_font = tk.font.nametofont("TkFixedFont")


        h1_font = default_font.copy()
        h1_font.configure(size=int(default_font.cget("size") * 1.5), weight="bold")
        h2_font = default_font.copy()
        h2_font.configure(size=int(default_font.cget("size") * 1.3), weight="bold")
        h3_font = default_font.copy()
        h3_font.configure(size=int(default_font.cget("size") * 1.1), weight="bold")

        self._text_area.tag_configure("h1", font=h1_font, spacing1=10, spacing3=5)
        self._text_area.tag_configure("h2", font=h2_font, spacing1=8, spacing3=4)
        self._text_area.tag_configure("h3", font=h3_font, spacing1=6, spacing3=3)
        self._text_area.tag_configure("bold", font=bold_font)
        self._text_area.tag_configure("italic", font=italic_font)
        self._text_area.tag_configure("bold_italic", font=bold_italic_font)
        self._text_area.tag_configure("code", font=code_font, background="#f0f0f0") # Inline code
        self._text_area.tag_configure("code_block", font=code_font, background="#f5f5f5",
                                        lmargin1=20, lmargin2=20, spacing1=5, spacing3=5,
                                        borderwidth=1, relief="sunken")
        self._text_area.tag_configure("list_item", lmargin1=20, lmargin2=20)
        self._text_area.tag_configure("user_message", foreground="blue", spacing3=5)
        self._text_area.tag_configure("assistant_message", foreground="black", spacing3=10)
        self._text_area.tag_configure("error_message", foreground="red", font=italic_font)
        self._text_area.tag_configure("hr", underline=True, spacing1=10, spacing3=10) # Simple horizontal rule

    def _clear_conversation(self):
        if messagebox.askyesno(tr("Clear Conversation"), tr("Are you sure you want to clear the conversation history?")):
            self._text_area.configure(state="normal")
            self._text_area.delete("1.0", tk.END)
            self._text_area.configure(state="disabled")
            self._conversation_history = []
            self._save_history()

    def _send_message(self, event=None):
        user_input = self._input_var.get().strip()
        if not user_input:
            return
        if not requests or not MarkdownIt:
             messagebox.showerror(tr("Error"), tr("Required libraries (requests, markdown-it-py) are missing."), parent=self)
             return

        api_url = get_workbench().get_option("ai_assistant.api_url")
        api_key = get_workbench().get_option("ai_assistant.api_key")
        model = get_workbench().get_option("ai_assistant.model")

        if not api_url or not model or model == tr("<Click 'Fetch Models'>") or model == tr("<Fetching...>") or model == tr("<Fetch failed>") or model == tr("<No models found>"):
            messagebox.showerror(tr("Configuration Error"), tr("Please configure API URL and select a model in Tools > Options > AI Assistant."), parent=self)
            return

        # Add user message to history and display
        self._add_message_to_history("user", user_input)
        self._render_message("user", user_input)

        self._input_var.set("")
        self._input_entry.configure(state="disabled")
        self._send_button.configure(state="disabled")
        self._text_area.see(tk.END) # Scroll down

        self._cancel_requested = False # <--- 重設取消標誌

        # Start background API call
        thread = threading.Thread(target=self._call_api_thread, args=(api_url, api_key, model), daemon=True)
        thread.start()

    def _add_message_to_history(self, role: str, content: str):
        self._conversation_history.append({"role": role, "content": content})
        # Limit history size
        if len(self._conversation_history) > MAX_HISTORY:
            # Keep system prompt + last MAX_HISTORY-1 messages
            self._conversation_history = [self._conversation_history[0]] + self._conversation_history[-(MAX_HISTORY-1):]
        self._save_history()


    def _render_message(self, role: str, content: str, is_error: bool = False):
        self._text_area.configure(state="normal")
        if is_error:
             self._text_area.insert(tk.END, f"{tr('Error')}:\n", ("error_message",))
             self._text_area.insert(tk.END, content + "\n", ("error_message",))
        elif role == "user":
            self._text_area.insert(tk.END, f"{tr('You')}:\n", ("user_message", "bold"))
            # User input doesn't need full Markdown rendering, just display it
            self._text_area.insert(tk.END, content + "\n\n", ("user_message",))
        elif role == "assistant":
            self._text_area.insert(tk.END, f"{tr('Assistant')}:\n", ("assistant_message", "bold"))
            self._render_markdown(content)
            self._text_area.insert(tk.END, "\n") # Add space after assistant message
        self._text_area.configure(state="disabled")
        self._text_area.see(tk.END)


    def _call_api_thread(self, base_url: str, api_key: str, model: str):
        self._current_ai_response = "" # Reset accumulator for streaming
        if not base_url.endswith("/"):
            base_url += "/"
        chat_url = base_url + "chat/completions"

        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        # --- 加入或修改 System Prompt ---
        # --- 加入或修改 System Prompt ---
        # 獲取作業系統預設語系 (使用推薦方法)
        os_language_code = None
        try:
            # 嘗試根據環境設定 LC_CTYPE
            # 注意：這可能會影響程式後續的區域設定行為，但在獨立執行緒中通常問題不大
            # 如果擔心影響主程式，可以考慮在執行緒開始時保存原始設定，結束時恢復
            # original_locale = locale.getlocale(locale.LC_CTYPE) # 保存 (如果需要恢復)
            locale.setlocale(locale.LC_CTYPE, '') # 使用 OS 預設
            # 獲取設定後的語言代碼和編碼
            os_locale_tuple = locale.getlocale(locale.LC_CTYPE)

            if os_locale_tuple and os_locale_tuple[0]:
                os_language_code = os_locale_tuple[0] # 提取語言代碼部分
            else:
                 # 如果 getlocale 返回 None 或語言碼為 None/空
                 logger.warning("locale.getlocale(LC_CTYPE) returned None or empty code after setting default locale.")
                 os_language_code = "en" # 預設為英文

            # 可選：恢復原始 locale (如果擔心副作用)
            # locale.setlocale(locale.LC_CTYPE, original_locale)

        except locale.Error as e:
            # 如果系統不支援空字串 locale 或設定失敗
            logger.error(f"Could not set/get OS default locale using setlocale/getlocale: {e}", exc_info=True)
            os_language_code = "en" # 出錯時預設為英文
        except Exception as e:
            # 捕捉其他意外錯誤
            logger.error("An unexpected error occurred while getting OS locale", exc_info=e)
            os_language_code = "en"

        # 使用作業系統語系代碼
        system_prompt = f"Respond in the language identified by the OS locale code: {os_language_code}"

        # 使用有限的歷史記錄副本進行操作
        messages_to_send = list(self._conversation_history[-MAX_HISTORY:]) # 創建副本

        if not messages_to_send or messages_to_send[0].get("role") != "system":
            # 如果歷史為空或第一條不是 system prompt，則插入
            messages_to_send.insert(0, {"role": "system", "content": system_prompt})
            logger.debug(f"Prepended system prompt: {system_prompt}")
        elif messages_to_send[0].get("role") == "system":
             # 如果已經有 system prompt，附加語言要求 (檢查關鍵字避免重複)
             original_system_content = messages_to_send[0].get("content", "")
             # 檢查一個獨特的子字串
             if f"language identified by the code:" not in original_system_content:
                 messages_to_send[0]["content"] = original_system_content + "\n" + system_prompt
                 logger.debug(f"Appended language requirement to existing system prompt.")
             else:
                 # 如果已存在類似要求，可以考慮更新語言碼或保持不變
                 # 這裡選擇保持不變，避免複雜化
                 logger.debug("Language requirement already seems to exist in system prompt.")

        payload = {
            "model": model,
            "messages": messages_to_send,
            "stream": True
        }

        full_response_content = ""
        try:
            logger.debug("Sending API request to %s with model %s", chat_url, model)
            logger.debug("payload: %s", payload)
            with requests.post(chat_url, headers=headers, json=payload, stream=True, timeout=120) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    # if self._message_queue.get("cancelled", False): # Check for cancellation
                    if self._cancel_requested:                     # <--- 改成檢查這個標誌
                        logger.info("API call cancelled by user.")
                        self._message_queue.put({"type": "cancelled"})
                        return

                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith("data: "):
                            json_str = decoded_line[len("data: "):]
                            if json_str.strip() == "[DONE]":
                                break
                            try:
                                chunk = json.loads(json_str)
                                delta = chunk.get('choices', [{}])[0].get('delta', {})
                                content_part = delta.get('content')
                                if content_part:
                                    full_response_content += content_part
                                    # No UI update here, accumulate first
                            except json.JSONDecodeError:
                                logger.warning(f"Could not decode stream JSON: {json_str}")
                                continue # Ignore malformed lines
                        elif decoded_line.strip(): # Handle potential non-event stream lines / errors
                             logger.warning(f"Received unexpected line from stream: {decoded_line}")


            logger.debug("API stream finished.")
            if full_response_content:
                 self._message_queue.put({"type": "response", "content": full_response_content})
            else:
                 # Handle cases where the stream finishes without content (e.g., API errors before stream starts properly)
                 logger.warning("API stream finished but no content was received.")
                 self._message_queue.put({"type": "error", "content": tr("Received an empty response from the AI.")})


        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}", exc_info=True)
            self._message_queue.put({"type": "error", "content": f"{tr('API request failed')}: {e}"})
        except Exception as e:
             logger.error(f"An unexpected error occurred during API call: {e}", exc_info=True)
             self._message_queue.put({"type": "error", "content": f"{tr('An unexpected error occurred')}: {e}"})

    def _check_queue(self):
        try:
            message = self._message_queue.get_nowait()
            if message["type"] == "response":
                self._input_entry.configure(state="normal")
                self._send_button.configure(state="normal")
                assistant_response = message["content"]
                self._add_message_to_history("assistant", assistant_response)
                self._render_message("assistant", assistant_response)
                self._current_ai_response = "" # Clear accumulator
            elif message["type"] == "error":
                self._input_entry.configure(state="normal")
                self._send_button.configure(state="normal")
                self._render_message("error", message["content"], is_error=True)
                self._current_ai_response = "" # Clear accumulator
            elif message["type"] == "cancelled":
                 self._input_entry.configure(state="normal")
                 self._send_button.configure(state="normal")
                 self._current_ai_response = "" # Clear accumulator
                 # Optionally display a "Cancelled" message

        except queue.Empty:
            pass
        except Exception as e:
            logger.error(f"Error processing message queue: {e}", exc_info=True)
            # Ensure UI is re-enabled even if queue processing fails
            if self._input_entry and self._input_entry.winfo_exists():
                 self._input_entry.configure(state="normal")
            if self._send_button and self._send_button.winfo_exists():
                 self._send_button.configure(state="normal")

        self.after(100, self._check_queue) # Continue polling


    def _render_markdown(self, md_text: str):
        if not self._markdown:
            # Fallback to plain text if markdown-it is not available
            self._text_area.insert(tk.END, md_text)
            return

        self._text_area.configure(state="normal")
        try:
            tokens = self._markdown.parse(md_text)
            logger.debug("Markdown Tokens: %s", tokens)

            active_tags = []
            list_level = 0
            list_bullet = "*" # Default bullet

            for token in tokens:
                tag_to_add = None
                content_to_insert = token.content if token.content else ""
                pop_tag = False

                # Block tags
                if token.type == "heading_open":
                    tag_to_add = f"h{token.tag[1]}"
                elif token.type == "heading_close":
                    pop_tag = True
                    content_to_insert = "\n"
                elif token.type == "paragraph_open":
                     # Add spacing before paragraph unless it's inside a list
                     if list_level == 0:
                          self._text_area.insert(tk.END, "\n", ("spacing_paragraph",))
                     pass # No specific tag needed unless for spacing maybe
                elif token.type == "paragraph_close":
                    content_to_insert = "\n"
                elif token.type == "bullet_list_open":
                     list_level += 1
                     list_bullet = "* "
                elif token.type == "ordered_list_open":
                     list_level += 1
                     list_bullet = f"{token.info}. " # Start number
                elif token.type == "list_item_open":
                     # Add bullet/number before the item content
                     prefix = "  " * (list_level - 1) + list_bullet
                     self._text_area.insert(tk.END, prefix, ("list_item",))
                     tag_to_add = "list_item"
                     if token.type == "ordered_list_open": # Increment number for next item
                          list_bullet = f"{int(list_bullet[:-2]) + 1}. "
                elif token.type == "list_item_close":
                     pop_tag = True
                     content_to_insert = "\n"
                elif token.type in ("bullet_list_close", "ordered_list_close"):
                     list_level -= 1
                     content_to_insert = "\n" if list_level == 0 else "" # Add space after top-level list
                elif token.type == "fence":
                    # Code block
                    lang = token.info.strip() if token.info else "code"
                    code_content = token.content.strip("\n") # Remove surrounding newlines added by parser
                    start_index = self._text_area.index(tk.INSERT)
                    self._text_area.insert(tk.END, code_content + "\n", ("code_block", f"lang_{lang}"))
                    end_index = self._text_area.index(tk.INSERT + "-1c") # Before the last newline
                    self._add_code_buttons(start_index, end_index, code_content)
                    content_to_insert = "" # Already inserted
                elif token.type == "hr":
                     # Insert a simple line - could use image or canvas later
                     self._text_area.insert(tk.END, "_" * 40 + "\n", ("hr",))
                     content_to_insert = ""

                # Inline tags
                elif token.type == "strong_open":
                    tag_to_add = "bold"
                elif token.type == "strong_close":
                    pop_tag = True
                elif token.type == "em_open":
                    tag_to_add = "italic"
                elif token.type == "em_close":
                    pop_tag = True
                elif token.type == "code_inline":
                    # Apply code tag directly to content
                    self._text_area.insert(tk.END, token.content, tuple(active_tags + ["code"]))
                    content_to_insert = ""
                elif token.type == "text":
                    pass # Just insert the content
                elif token.type.endswith("_close"): # Generic close for inline elements if needed
                     pop_tag = True
                # Ignore other token types for now (like html_inline, etc.)

                # Apply tags and insert content
                if content_to_insert:
                    self._text_area.insert(tk.END, content_to_insert, tuple(active_tags))

                if tag_to_add:
                    active_tags.append(tag_to_add)
                if pop_tag and active_tags:
                    # Handle potential mismatches gracefully
                    try:
                         active_tags.pop()
                    except IndexError:
                         logger.warning("Markdown tag pop error: No active tags left.")


        except Exception as e:
             logger.error(f"Error rendering Markdown: {e}", exc_info=True)
             # Fallback to plain text on error
             self._text_area.insert(tk.END, "\n" + md_text) # Insert original on error
        finally:
             # Ensure correct state even if errors occurred
             self._text_area.configure(state="disabled")
             self._text_area.see(tk.END)

    def _add_code_buttons(self, start_index: str, end_index: str, code_content: str):
        # Use window_create to add buttons below the code block
        # Create a small frame to hold the buttons
        button_frame = ttk.Frame(self._text_area) # Parent is the text area

        copy_button = ttk.Button(
            button_frame,
            text=tr("Copy"),
            command=lambda c=code_content: self._copy_code(c),
            width=5 # Make buttons small
        )
        copy_button.pack(side=tk.LEFT, padx=(0, 5))

        insert_button = ttk.Button(
            button_frame,
            text=tr("Insert"),
            command=lambda c=code_content: self._insert_code(c),
             width=6
        )
        insert_button.pack(side=tk.LEFT)

        # Add a newline before creating the window to ensure it's on its own line
        self._text_area.insert(tk.END, "\n")
        # Place the frame in the text widget right after the code block's newline
        self._text_area.window_create(tk.INSERT + "-1c", window=button_frame, padx=20, pady=3, align="bottom") # Align to left margin
        # Add another newline for spacing after the buttons
        self._text_area.insert(tk.END, "\n")


    def _copy_code(self, code_content: str):
        logger.debug("Copying code to clipboard")
        self.clipboard_clear()
        self.clipboard_append(code_content)
        # Maybe show a brief confirmation?

    def _insert_code(self, code_content: str):
        logger.debug("Inserting code into editor")
        editor = get_workbench().get_editor_notebook().get_current_editor()
        if editor:
            text_widget = editor.get_text_widget()
            try:
                text_widget.insert(tk.INSERT, code_content)
                editor.focus_set() # Focus the editor after inserting
            except tk.TclError as e:
                 logger.error(f"Failed to insert code: {e}")
                 messagebox.showerror(tr("Error"), tr("Could not insert code into the editor."), parent=self)
        else:
            messagebox.showwarning(tr("No Active Editor"), tr("Please open or focus an editor tab first."), parent=self)


    def _save_history(self):
        try:
            os.makedirs(ASSISTANT_USER_DIR, exist_ok=True)
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self._conversation_history, f, ensure_ascii=False, indent=2)
            logger.debug("Conversation history saved.")
        except Exception as e:
            logger.error(f"Failed to save conversation history: {e}", exc_info=True)

    def _load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    self._conversation_history = json.load(f)
                # Ensure loaded history is a list of dicts
                if not isinstance(self._conversation_history, list) or \
                   not all(isinstance(msg, dict) and 'role' in msg and 'content' in msg for msg in self._conversation_history):
                    logger.warning("Invalid history file format. Starting fresh.")
                    self._conversation_history = []
                    self._save_history() # Overwrite invalid file

                logger.debug(f"Loaded {len(self._conversation_history)} messages from history.")
                # Limit loaded history as well
                if len(self._conversation_history) > MAX_HISTORY:
                     self._conversation_history = self._conversation_history[-MAX_HISTORY:]

            except Exception as e:
                logger.error(f"Failed to load conversation history: {e}", exc_info=True)
                self._conversation_history = [] # Start fresh on error
        else:
             self._conversation_history = []
             logger.debug("No conversation history file found.")

    def _render_history(self):
         self._text_area.configure(state="normal")
         self._text_area.delete("1.0", tk.END)
         for message in self._conversation_history:
              role = message.get("role")
              content = message.get("content")
              if role and content:
                   self._render_message(role, content)
         self._text_area.configure(state="disabled")
         self._text_area.see(tk.END)


    def ask_ai_to_explain(self, text_to_explain: str):
        """Public method to trigger explanation from external commands."""
        logger.debug("Received request to explain: %s", text_to_explain[:100] + "...")
        prompt = f"{tr('Explain the following code or text')}:\n\n```\n{text_to_explain}\n```"

        # Directly add the synthesized "user" prompt to history and display
        # We don't want the user to manually type this.
        self._add_message_to_history("user", prompt)
        self._render_message("user", prompt)

        # Now trigger the API call
        api_url = get_workbench().get_option("ai_assistant.api_url")
        api_key = get_workbench().get_option("ai_assistant.api_key")
        model = get_workbench().get_option("ai_assistant.model")

        if not api_url or not model:
             messagebox.showerror(tr("Configuration Error"), tr("Please configure API URL and select a model first."), parent=self)
             return

        self._input_entry.configure(state="disabled")
        self._send_button.configure(state="disabled")

        thread = threading.Thread(target=self._call_api_thread, args=(api_url, api_key, model), daemon=True)
        thread.start()


# --- Editor / Shell Integration ---

def _get_ai_assistant_view() -> Optional[AIAssistantView]:
    try:
        # Access the view instance through the workbench's view records
        # This assumes the view has been created and shown at least once
        view_instance = get_workbench().get_view("AIAssistantView", create=True) # Create if not exists
        if isinstance(view_instance, AIAssistantView):
            get_workbench().show_view("AIAssistantView") # Make sure it's visible
            return view_instance
        else:
            logger.error("AI Assistant View instance is not of the expected type.")
            return None
    except Exception as e:
        logger.error(f"Could not get AI Assistant view: {e}", exc_info=True)
        return None


def _explain_editor_selection():
    editor = get_workbench().get_editor_notebook().get_current_editor()
    if not editor:
        return
    text_widget = editor.get_text_widget()
    try:
        selected_text = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
        if selected_text:
            view = _get_ai_assistant_view()
            if view:
                view.ask_ai_to_explain(selected_text)
    except tk.TclError:
        # No selection
        pass
    except Exception as e:
        logger.error(f"Error explaining editor selection: {e}", exc_info=True)
        messagebox.showerror(tr("Error"), tr("Could not send text to AI Assistant."), parent=get_workbench())

def _editor_selection_exists():
    editor = get_workbench().get_editor_notebook().get_current_editor()
    if not editor:
        return False
    text_widget = editor.get_text_widget()
    try:
        return bool(text_widget.tag_ranges(tk.SEL))
    except tk.TclError:
        return False


def _explain_shell_selection():
    shell = get_shell()
    if not shell:
        return
    text_widget = shell.text # Assuming 'text' is the attribute for the Text widget
    try:
        selected_text = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
        # Shell often includes prompts or output markers, try to clean it
        selected_text = re.sub(r"^>>>\s*|^...\s*|^\%?\w+.*\n?", "", selected_text, flags=re.MULTILINE).strip()

        if selected_text:
            view = _get_ai_assistant_view()
            if view:
                view.ask_ai_to_explain(selected_text)
    except tk.TclError:
        # No selection
        pass
    except Exception as e:
        logger.error(f"Error explaining shell selection: {e}", exc_info=True)
        messagebox.showerror(tr("Error"), tr("Could not send text to AI Assistant."), parent=get_workbench())

def _shell_selection_exists():
    shell = get_shell()
    if not shell:
        return False
    text_widget = shell.text
    try:
        return bool(text_widget.tag_ranges(tk.SEL))
    except tk.TclError:
        return False


# --- Plugin Loading ---

def load_plugin():
    if requests is None or MarkdownIt is None:
         logger.warning("AI Assistant plugin disabled due to missing dependencies.")
         # Maybe show a message in the UI?
         return

    wb = get_workbench()

    # Default Settings
    wb.set_default("ai_assistant.api_url", "http://localhost:8081/v1") # Example default
    wb.set_default("ai_assistant.api_key", "")
    wb.set_default("ai_assistant.model", "") # No default model initially

    # Register View
    wb.add_view(AIAssistantView, tr("AI Assistant"), "w") # 'w' for west pane

    # Register Configuration Page
    # Use a high order number to place it towards the end
    wb.add_configuration_page("AI Assistant", tr("AI Assistant"), AIAssistantConfigPage, 90)

    # Add Editor Context Menu Command
    # Group 150 is typically for external tools/actions
    wb.add_command(
        command_id="explain_editor_selection_with_ai",
        menu_name="edit", # Add to Edit menu for context
        command_label=tr("Explain with AI Assistant"),
        handler=_explain_editor_selection,
        tester=_editor_selection_exists,
        group=150,
         # Define accelerator if desired, e.g.:
         # default_sequence=select_sequence("<Control-Alt-E>", "<Command-Alt-E>")
    )
    # Add to editor context menu explicitly (needed for Text widgets)

    # Hacky way: Find the Text widget's context menu if Thonny creates one,
    # or bind directly to the Text class tag if that's feasible.
    # Standard way: Thonny currently doesn't have a dedicated API for editor context menu.
    # We rely on the command being available in the main Edit menu when text is selected.


    # Add Shell Context Menu Command (Integration Challenge)
    # Create the command first
#     wb.add_command(
#         command_id="explain_shell_selection_with_ai",
#         menu_name="edit", # Also add to main Edit menu as fallback
#         command_label=tr("Explain with AI Assistant (Shell)"), # Differentiate label slightly
#         handler=_explain_shell_selection,
#         tester=_shell_selection_exists,
#         group=151, # Slightly different group
#     )

    # TODO: Integrate into Shell's actual context menu.
    # This requires modifying ShellMenu or finding a hook.
    # Example monkey-patch (use with caution, might break):
    # original_add_extra_items = ShellMenu.add_extra_items
    # def patched_add_extra_items(self):
    #     original_add_extra_items(self)
    #     self.add_separator()
    #     self.add_command(label=tr("Explain with AI Assistant"),
    #                      command=_explain_shell_selection,
    #                      state="disabled" if not _shell_selection_exists() else "normal")
    # ShellMenu.add_extra_items = patched_add_extra_items
    # logger.info("Attempted to patch ShellMenu for AI Assistant.")
    logger.warning("Shell context menu integration for 'Explain with AI' is not fully implemented.")


    # --- Monkey Patch ShellMenu ---
    # Make sure ShellMenu is imported: from thonny.shell import ShellMenu
    
    original_add_extra_items = ShellMenu.add_extra_items

    def patched_add_extra_items(shell_menu_instance):
        # Call the original method first
        original_add_extra_items(shell_menu_instance)

        # Add our command specifically for the Shell menu
        try:
            shell_menu_instance.add_separator() # Add a separator before our item
            shell_menu_instance.add_command(
                label=tr("Explain with AI Assistant"), # Use a clean label now
                command=_explain_shell_selection,
                # The tester will be called dynamically by MenuEx logic
                tester=_shell_selection_exists
            )
            # Note: We don't need state here, MenuEx's postcommand handles it via tester
        except Exception as e:
            logger.error("Error patching ShellMenu", exc_info=e)

    # Apply the patch
    ShellMenu.add_extra_items = patched_add_extra_items
    logger.info("Patched ShellMenu.add_extra_items to include AI Assistant.")

    # --- Remove the redundant global command for shell explanation ---
    # Find the command dictionary for 'explain_shell_selection_with_ai' and remove it
    # This requires iterating wb._commands or modifying how commands are added initially.
    # A simpler approach for now: Comment out the wb.add_command call for it earlier.

    # --- Comment out or delete this block earlier in load_plugin ---
    # wb.add_command(
    #     command_id="explain_shell_selection_with_ai",
    #     menu_name="edit", # Problem: This puts it in the main Edit menu
    #     command_label=tr("Explain with AI Assistant (Shell)"), # Differentiate label slightly
    #     handler=_explain_shell_selection,
    #     tester=_shell_selection_exists,
    #     group=151, # Slightly different group
    # )
    # --- End of block to remove ---


    logger.info("AI Assistant plugin loaded.")