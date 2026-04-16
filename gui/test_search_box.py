"""
Test suite for SearchBox component
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from search_box import SearchBox


class TestSearchBox:
    """Test suite for SearchBox component"""

    def __init__(self):
        self.root = ctk.CTk()
        self.root.withdraw()  # Hide window during tests
        self.test_results = []

    def run_test(self, test_name, test_func):
        """Run a single test and record result"""
        try:
            test_func()
            self.test_results.append((test_name, "PASS", None))
            print(f"✓ {test_name}")
        except Exception as e:
            self.test_results.append((test_name, "FAIL", str(e)))
            print(f"✗ {test_name}: {e}")

    def test_initialization(self):
        """Test SearchBox initialization"""
        box = SearchBox(self.root)

        # Verify it's a CTkFrame
        assert isinstance(box, ctk.CTkFrame), "SearchBox should inherit from CTkFrame"

        # Verify entry exists
        assert hasattr(box, "_entry"), "SearchBox should have _entry attribute"
        assert hasattr(box, "_search_text"), (
            "SearchBox should have _search_text attribute"
        )

        # Verify placeholder text
        assert box.get_search_text() == "", "Initial search text should be empty"

        box.destroy()

    def test_search_callback(self):
        """Test search callback functionality"""
        callback_called = []

        def on_search(text):
            callback_called.append(text)

        box = SearchBox(self.root, search_callback=on_search)

        # Set some text
        box.set_search_text("test")

        # Callback should be called with the text
        assert len(callback_called) > 0, "Callback should be called when text changes"
        assert "test" in callback_called, "Callback should receive the search text"

        box.destroy()

    def test_get_search_text(self):
        """Test get_search_text method"""
        box = SearchBox(self.root)

        box.set_search_text("hello world")
        assert box.get_search_text() == "hello world", (
            "get_search_text should return current text"
        )

        box.clear()
        assert box.get_search_text() == "", "clear should reset text"

        box.destroy()

    def test_clear_method(self):
        """Test clear method"""
        box = SearchBox(self.root)

        box.set_search_text("text to clear")
        box.clear()

        assert box.get_search_text() == "", "clear should empty the search text"

        box.destroy()

    def test_enter_key_event(self):
        """Test Enter key triggers search callback"""
        callback_count = []

        def on_search(text):
            callback_count.append(1)

        box = SearchBox(self.root, search_callback=on_search)
        box.set_search_text("test")

        # Simulate Enter key press
        box._on_enter_pressed(None)

        assert len(callback_count) > 0, "Enter key should trigger search callback"

        box.destroy()

    def test_escape_key_event(self):
        """Test Escape key clears search"""
        box = SearchBox(self.root)
        box.set_search_text("text to clear")

        # Simulate Escape key press
        box._on_escape_pressed(None)

        assert box.get_search_text() == "", "Escape key should clear search text"

        box.destroy()

    def test_clear_button_appearance(self):
        """Test clear button appears when text is entered"""
        box = SearchBox(self.root)

        # Initially, clear button should be hidden (not in layout)
        clear_btn_initial = box._clear_button.winfo_viewable()

        # After entering text, clear button should be visible
        box.set_search_text("test")

        # Use winfo_exists() and check if button was packed (visible)
        assert box._clear_button.winfo_exists(), "Clear button should exist"
        # The button should now be visible after text is set
        # Force update to ensure layout is processed
        box.update_idletasks()
        # Check that clear button is now visible (not hidden with pack_forget)
        assert not (not box._clear_button.winfo_manager() == "none"), (
            "Clear button should be packed"
        )

        box.destroy()

    def test_search_button_state(self):
        """Test search button state changes based on text"""
        box = SearchBox(self.root)

        # Initially, search button should be disabled
        assert box._search_button.cget("state") == "disabled", (
            "Search button should be disabled initially"
        )

        # After entering text, search button should be enabled
        box.set_search_text("test")

        assert box._search_button.cget("state") == "normal", (
            "Search button should be enabled when text exists"
        )

        box.destroy()

    def test_configure_search_callback(self):
        """Test dynamic callback configuration"""
        callback1_called = []
        callback2_called = []

        def callback1(text):
            callback1_called.append(text)

        def callback2(text):
            callback2_called.append(text)

        box = SearchBox(self.root, search_callback=callback1)
        box.set_search_text("test1")

        # Change callback
        box.configure_search_callback(callback2)
        box.set_search_text("test2")

        # Only callback2 should have been called
        assert len(callback1_called) == 1, "Callback1 should be called once"
        assert len(callback2_called) == 1, "Callback2 should be called once"
        assert callback1_called[0] == "test1", "Callback1 should receive test1"
        assert callback2_called[0] == "test2", "Callback2 should receive test2"

        box.destroy()

    def run_all_tests(self):
        """Run all tests and print summary"""
        print("\n" + "=" * 50)
        print("SearchBox Test Suite")
        print("=" * 50 + "\n")

        self.run_test("Initialization", self.test_initialization)
        self.run_test("Search Callback", self.test_search_callback)
        self.run_test("Get Search Text", self.test_get_search_text)
        self.run_test("Clear Method", self.test_clear_method)
        self.run_test("Enter Key Event", self.test_enter_key_event)
        self.run_test("Escape Key Event", self.test_escape_key_event)
        self.run_test("Search Button State", self.test_search_button_state)
        self.run_test("Configure Search Callback", self.test_configure_search_callback)

        # Print summary
        print("\n" + "=" * 50)
        print("Test Summary")
        print("=" * 50)

        passed = sum(1 for _, result, _ in self.test_results if result == "PASS")
        failed = sum(1 for _, result, _ in self.test_results if result == "FAIL")

        print(f"Total: {len(self.test_results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")

        if failed > 0:
            print("\nFailed Tests:")
            for name, result, error in self.test_results:
                if result == "FAIL":
                    print(f"  - {name}: {error}")

        return failed == 0


if __name__ == "__main__":
    runner = TestSearchBox()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)
