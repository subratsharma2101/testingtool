import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from selenium.common.exceptions import WebDriverException

from smart_test_engine import SmartTestEngine


class RecordingSession:
    """Represents a manual recording session."""

    def __init__(self, website_url: str):
        self.website_url = website_url
        self.engine: Optional[SmartTestEngine] = None
        self.driver = None
        self.started_at = datetime.utcnow()
        self.events: List[Dict[str, Any]] = []
        self.steps: List[Dict[str, Any]] = []
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._step_counter = 0

    def start(self):
        """Launch Chrome and begin polling for recorded events."""
        self.engine = SmartTestEngine(self.website_url, "", "", headed=True)
        self.driver = self.engine.initialize_driver()
        self.driver.get(self.website_url)
        time.sleep(2)
        self._inject_recorder()
        self._thread = threading.Thread(target=self._poll_events, daemon=True)
        self._thread.start()

    def stop(self) -> Dict[str, Any]:
        """Stop recording and close resources."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        if self.engine:
            self.engine.close()
        script = self.build_python_script()
        return {
            "steps": self.steps,
            "python_script": script,
            "started_at": self.started_at.isoformat(),
            "stopped_at": datetime.utcnow().isoformat(),
        }

    def _inject_recorder(self):
        """Injects JavaScript listeners into the page to track interactions."""
        script = """
            (function() {
                if (window.__mobiliseRecorderInitialized) {
                    return;
                }
                window.__mobiliseRecorderInitialized = true;
                window.__recordedEvents = [];

                function getCssSelector(element) {
                    if (!element) { return ''; }
                    if (element.id) {
                        return '#' + element.id;
                    }
                    var parts = [];
                    while (element && element.nodeType === 1) {
                        var selector = element.nodeName.toLowerCase();
                        if (element.className) {
                            var classes = element.className.trim().split(/\\s+/).slice(0, 3);
                            if (classes.length) {
                                selector += '.' + classes.join('.');
                            }
                        }
                        var sibling = element;
                        var nth = 1;
                        while (sibling = sibling.previousElementSibling) {
                            if (sibling.nodeName === element.nodeName) {
                                nth++;
                            }
                        }
                        selector += ':nth-of-type(' + nth + ')';
                        parts.unshift(selector);
                        element = element.parentElement;
                        if (selector.indexOf('#') === 0) {
                            break;
                        }
                    }
                    return parts.join(' > ');
                }

                function recordEvent(event) {
                    try {
                        var target = event.target || event.srcElement;
                        if (!target) { return; }
                        var selector = getCssSelector(target);
                        var data = {
                            timestamp: Date.now(),
                            type: event.type,
                            selector: selector,
                            tag: (target.tagName || '').toLowerCase(),
                            value: target.value || '',
                            text: target.innerText || target.textContent || '',
                            key: event.key || '',
                            url: window.location.href
                        };
                        window.__recordedEvents.push(data);
                    } catch (err) {
                        console.error('Recorder error', err);
                    }
                }

                ['click', 'change', 'input', 'submit', 'keydown'].forEach(function(type) {
                    document.addEventListener(type, function(event) {
                        recordEvent(event);
                    }, true);
                });
            })();
        """
        self.driver.execute_script(script)

    def _poll_events(self):
        """Continuously pulls recorded events from the browser."""
        while not self._stop_event.is_set():
            try:
                events = self.driver.execute_script(
                    """
                    if (!window.__recordedEvents) { return []; }
                    const events = window.__recordedEvents.slice();
                    window.__recordedEvents = [];
                    return events;
                    """
                )
            except WebDriverException:
                break

            if events:
                self._process_events(events)

            time.sleep(0.5)

    def _process_events(self, events: List[Dict[str, Any]]):
        with self._lock:
            for event in events:
                step = self._convert_event_to_step(event)
                if step:
                    self.steps.append(step)
            self.events.extend(events)

    def _convert_event_to_step(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        event_type = event.get("type")
        selector = event.get("selector")

        if not selector:
            return None

        action = None
        value = event.get("value") or ""

        if event_type == "click":
            action = "click"
        elif event_type in {"input", "change"}:
            action = "type"
        elif event_type == "submit":
            action = "submit"
        elif event_type == "keydown" and event.get("key") == "Enter":
            action = "press_enter"
        else:
            return None

        if action == "type":
            last_step = self.steps[-1] if self.steps else None
            if last_step and last_step["action"] == "type" and last_step["selector"] == selector:
                last_step["value"] = value
                last_step["updated_at"] = datetime.utcnow().isoformat()
                return None

        self._step_counter += 1
        step = {
            "step_id": f"REC_STEP_{self._step_counter:03d}",
            "action": action,
            "selector": selector,
            "value": value,
            "timestamp": event.get("timestamp"),
            "tag": event.get("tag"),
            "url": event.get("url"),
            "text": event.get("text", ""),
        }
        return step

    def build_python_script(self) -> str:
        """Generate a Selenium Python script from recorded steps."""
        lines = [
            "from selenium import webdriver",
            "from selenium.webdriver.common.by import By",
            "from selenium.webdriver.common.keys import Keys",
            "",
            "options = webdriver.ChromeOptions()",
            "options.add_argument('--start-maximized')",
            "driver = webdriver.Chrome(options=options)",
            f"driver.get('{self.website_url}')",
            "",
        ]

        for step in self.steps:
            selector = self._escape(step["selector"])
            value = self._escape(step.get("value", ""))

            lines.append(f"element = driver.find_element(By.CSS_SELECTOR, \"{selector}\")")
            if step["action"] == "click":
                lines.append("element.click()")
            elif step["action"] == "type":
                lines.append("element.clear()")
                lines.append(f"element.send_keys(\"{value}\")")
            elif step["action"] == "submit":
                lines.append("element.submit()")
            elif step["action"] == "press_enter":
                lines.append("element.send_keys(Keys.ENTER)")
            lines.append("")

        lines.append("driver.quit()")
        return "\n".join(lines)

    @staticmethod
    def _escape(value: str) -> str:
        return value.replace("\\", "\\\\").replace('"', '\\"')


class RecordingManager:
    """Singleton-style manager for handling recording sessions."""

    def __init__(self):
        self._session: Optional[RecordingSession] = None
        self._lock = threading.Lock()

    def start_session(self, website_url: str) -> Dict[str, Any]:
        with self._lock:
            if self._session:
                self._session.stop()
            self._session = RecordingSession(website_url)
            self._session.start()
            return {
                "active": True,
                "website_url": website_url,
                "started_at": self._session.started_at.isoformat(),
            }

    def stop_session(self) -> Dict[str, Any]:
        with self._lock:
            if not self._session:
                return {"active": False, "message": "No active recording session"}
            result = self._session.stop()
            self._session = None
            result["active"] = False
            return result

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            if not self._session:
                return {
                    "active": False,
                    "steps": [],
                    "python_script": "",
                }
            return {
                "active": True,
                "website_url": self._session.website_url,
                "started_at": self._session.started_at.isoformat(),
                "steps": self._session.steps,
                "python_script": self._session.build_python_script(),
            }

    def is_active(self) -> bool:
        return self._session is not None


