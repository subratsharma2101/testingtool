import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from smart_test_engine import SmartTestEngine


class RecordingSession:
    """Represents a manual recording session."""

    def __init__(self, website_url: str):
        self.website_url = website_url
        self.engine: Optional[SmartTestEngine] = None
        self.page = None
        self.started_at = datetime.utcnow()
        self.events: List[Dict[str, Any]] = []
        self.steps: List[Dict[str, Any]] = []
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._step_counter = 0
        self.screenshots: List[Dict[str, str]] = []  # Store screenshots with step IDs
        self.wait_times: Dict[str, float] = {}  # Track wait times between steps

    def start(self):
        """Launch Chrome and begin polling for recorded events."""
        self.engine = SmartTestEngine(self.website_url, "", "", headed=True)
        self.page = self.engine.initialize_driver()
        self.page.goto(self.website_url, wait_until='domcontentloaded')
        self.page.wait_for_load_state('networkidle')
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
                    
                    // Prefer ID
                    if (element.id) {
                        return '#' + element.id;
                    }
                    
                    // Try data-testid or data-test
                    if (element.getAttribute('data-testid')) {
                        return '[data-testid="' + element.getAttribute('data-testid') + '"]';
                    }
                    if (element.getAttribute('data-test')) {
                        return '[data-test="' + element.getAttribute('data-test') + '"]';
                    }
                    
                    // Try name attribute
                    if (element.name) {
                        if (element.tagName.toLowerCase() === 'input' || element.tagName.toLowerCase() === 'select') {
                            return element.tagName.toLowerCase() + '[name="' + element.name + '"]';
                        }
                    }
                    
                    // Try role and accessible name
                    if (element.getAttribute('role')) {
                        var role = element.getAttribute('role');
                        var ariaLabel = element.getAttribute('aria-label');
                        if (ariaLabel) {
                            return '[role="' + role + '"][aria-label="' + ariaLabel + '"]';
                        }
                    }
                    
                    // Build path selector
                    var parts = [];
                    while (element && element.nodeType === 1) {
                        var selector = element.nodeName.toLowerCase();
                        if (element.className) {
                            var classes = element.className.trim().split(/\\s+/).slice(0, 2);
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
                        
                        // Stop at body or if we found a good selector
                        if (!element || element.nodeName === 'BODY' || element.nodeName === 'HTML') {
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
                            url: window.location.href,
                            href: target.href || '',
                            checked: target.checked !== undefined ? target.checked : null,
                            selected: target.selected !== undefined ? target.selected : null,
                            disabled: target.disabled !== undefined ? target.disabled : null
                        };
                        window.__recordedEvents.push(data);
                    } catch (err) {
                        console.error('Recorder error', err);
                    }
                }
                
                // Record navigation events
                window.addEventListener('popstate', function(event) {
                    recordEvent({type: 'navigation', target: window, timestamp: Date.now()});
                });
                
                // Record URL changes
                var lastUrl = window.location.href;
                setInterval(function() {
                    if (window.location.href !== lastUrl) {
                        lastUrl = window.location.href;
                        recordEvent({
                            type: 'navigation',
                            target: window,
                            timestamp: Date.now(),
                            url: window.location.href
                        });
                    }
                }, 100);

                ['click', 'change', 'input', 'submit', 'keydown', 'focus', 'blur'].forEach(function(type) {
                    document.addEventListener(type, function(event) {
                        recordEvent(event);
                    }, true);
                });
            })();
        """
        self.page.evaluate(script)

    def _poll_events(self):
        """Continuously pulls recorded events from the browser."""
        while not self._stop_event.is_set():
            try:
                events = self.page.evaluate(
                    """
                    if (!window.__recordedEvents) { return []; }
                    const events = window.__recordedEvents.slice();
                    window.__recordedEvents = [];
                    return events;
                    """
                )
            except Exception:
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

        action = None
        value = event.get("value") or ""
        
        # Handle different event types
        if event_type == "click":
            action = "click"
        elif event_type in {"input", "change"}:
            action = "type"
        elif event_type == "submit":
            action = "submit"
        elif event_type == "keydown" and event.get("key") == "Enter":
            action = "press_enter"
        elif event_type == "navigation":
            action = "navigate"
            selector = event.get("url", "")
        elif event_type == "focus":
            action = "focus"
        elif event_type == "change" and event.get("tag") == "select":
            action = "select"
        elif event_type == "change" and event.get("tag") in ["input"] and event.get("checked") is not None:
            action = "check" if event.get("checked") else "uncheck"
        else:
            return None

        # Merge typing events for the same field
        if action == "type":
            last_step = self.steps[-1] if self.steps else None
            if last_step and last_step["action"] == "type" and last_step["selector"] == selector:
                last_step["value"] = value
                last_step["updated_at"] = datetime.utcnow().isoformat()
                return None

        # Calculate wait time since last step
        wait_time = 0
        if self.steps:
            last_timestamp = self.steps[-1].get("timestamp", 0)
            current_timestamp = event.get("timestamp", 0)
            wait_time = max(0, (current_timestamp - last_timestamp) / 1000.0)  # Convert to seconds

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
            "wait_time": wait_time,
            "href": event.get("href", ""),
            "checked": event.get("checked"),
            "selected": event.get("selected"),
            "disabled": event.get("disabled")
        }
        
        # Store wait time if significant (>0.5 seconds)
        if wait_time > 0.5:
            self.wait_times[step["step_id"]] = wait_time
        
        return step

    def build_python_script(self) -> str:
        """Generate a Playwright Python script from recorded steps."""
        lines = [
            "from playwright.sync_api import sync_playwright",
            "",
            "with sync_playwright() as p:",
            "    browser = p.chromium.launch(headless=False)",
            "    context = browser.new_context()",
            "    page = context.new_page()",
            f"    page.goto('{self.website_url}')",
            "",
        ]

        for step in self.steps:
            selector = self._escape(step["selector"])
            value = self._escape(step.get("value", ""))

            # Add wait if significant wait time detected
            wait_time = step.get("wait_time", 0)
            if wait_time > 1.0:
                lines.append(f"    page.wait_for_timeout({int(wait_time * 1000)})  # Wait {wait_time:.1f}s")
            
            if step["action"] == "navigate":
                lines.append(f"    page.goto(\"{selector}\")")
                lines.append("    page.wait_for_load_state('networkidle')")
            elif step["action"] == "click":
                lines.append(f"    element = page.locator(\"{selector}\").first")
                lines.append("    element.click()")
                if wait_time > 0.5:
                    lines.append("    page.wait_for_load_state('networkidle')")
            elif step["action"] == "type":
                lines.append(f"    element = page.locator(\"{selector}\").first")
                lines.append(f"    element.fill(\"{value}\")")
            elif step["action"] == "select":
                lines.append(f"    element = page.locator(\"{selector}\").first")
                lines.append(f"    element.select_option(\"{value}\")")
            elif step["action"] == "check":
                lines.append(f"    element = page.locator(\"{selector}\").first")
                lines.append("    element.check()")
            elif step["action"] == "uncheck":
                lines.append(f"    element = page.locator(\"{selector}\").first")
                lines.append("    element.uncheck()")
            elif step["action"] == "submit":
                lines.append(f"    element = page.locator(\"{selector}\").first")
                lines.append("    element.press('Enter')")
            elif step["action"] == "press_enter":
                lines.append(f"    element = page.locator(\"{selector}\").first")
                lines.append("    element.press('Enter')")
            elif step["action"] == "focus":
                lines.append(f"    element = page.locator(\"{selector}\").first")
                lines.append("    element.focus()")
            lines.append("")

        lines.extend([
            "    browser.close()",
            ""
        ])
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


