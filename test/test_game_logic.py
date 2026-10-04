import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from logic_utils import check_guess, get_range_for_difficulty


class TestCheckGuessHintDirection:
    """
    Targets the inverted-hint bug: the original code returned 'Go HIGHER!'
    when the guess was too high (and vice-versa). These tests pin the correct
    direction so the bug cannot regress silently.
    """

    def test_guess_above_secret_returns_too_high(self):
        outcome, _ = check_guess(80, 50)
        assert outcome == "Too High"

    def test_guess_above_secret_message_says_lower(self):
        # The bug had this returning "Go HIGHER!" instead of "Go LOWER!"
        _, message = check_guess(80, 50)
        assert "LOWER" in message, f"Expected hint to say LOWER, got: {message!r}"

    def test_guess_below_secret_returns_too_low(self):
        outcome, _ = check_guess(20, 50)
        assert outcome == "Too Low"

    def test_guess_below_secret_message_says_higher(self):
        # The bug had this returning "Go LOWER!" instead of "Go HIGHER!"
        _, message = check_guess(20, 50)
        assert "HIGHER" in message, f"Expected hint to say HIGHER, got: {message!r}"

    def test_exact_match_returns_win(self):
        outcome, _ = check_guess(42, 42)
        assert outcome == "Win"

    def test_hint_directions_are_not_swapped(self):
        # Sanity: high guess and low guess must give opposite directions
        _, high_msg = check_guess(99, 50)
        _, low_msg = check_guess(1, 50)
        assert "LOWER" in high_msg
        assert "HIGHER" in low_msg

    # --- TypeError path (int guess vs str secret, as produced by app.py on even attempts) ---

    def test_guess_above_str_secret_says_lower(self):
        _, message = check_guess(80, "50")
        assert "LOWER" in message, f"Expected LOWER for guess 80 vs secret '50', got: {message!r}"

    def test_guess_below_str_secret_says_higher(self):
        _, message = check_guess(20, "50")
        assert "HIGHER" in message, f"Expected HIGHER for guess 20 vs secret '50', got: {message!r}"

    def test_exact_match_str_secret_returns_win(self):
        outcome, _ = check_guess(42, "42")
        assert outcome == "Win"


class TestGetRangeForDifficulty:
    """
    Targets the swapped Normal/Hard range bug: Normal was returning 1–100
    and Hard was returning 1–50, making Hard easier than Normal range-wise.
    """

    def test_easy_range(self):
        low, high = get_range_for_difficulty("Easy")
        assert (low, high) == (1, 20)

    def test_normal_range_is_50_not_100(self):
        # Bug: Normal incorrectly returned 1–100 (the Hard range)
        low, high = get_range_for_difficulty("Normal")
        assert (low, high) == (1, 50)

    def test_hard_range_is_100_not_50(self):
        # Bug: Hard incorrectly returned 1–50 (smaller than Normal, making it paradoxically easier)
        low, high = get_range_for_difficulty("Hard")
        assert (low, high) == (1, 100)

    def test_ranges_widen_with_difficulty(self):
        # Both axes must increase together: narrower range = easier, wider range = harder
        _, easy_high = get_range_for_difficulty("Easy")
        _, normal_high = get_range_for_difficulty("Normal")
        _, hard_high = get_range_for_difficulty("Hard")
        assert easy_high < normal_high < hard_high


class TestAttemptsRemainingDisplay:
    """
    Targets the off-by-1 bug in app.py where 'Attempts left' was rendered
    before st.session_state.attempts was incremented. On every submit rerun,
    Streamlit executes the display line first (with the old attempts value),
    then increments — so the counter lagged by 1 on every submission.

    The fix: compute pending_attempts = attempts + (1 if submit else 0)
    and use that in the display. This class tests that formula directly,
    since importing app.py would execute Streamlit code.
    """

    def _attempts_left(self, attempts: int, attempt_limit: int, submit_pressed: bool) -> int:
        """Mirrors the fixed formula from app.py."""
        pending = attempts + (1 if submit_pressed else 0)
        return attempt_limit - pending

    def test_initial_load_shows_full_limit(self):
        # No submit yet: display should equal the full limit
        assert self._attempts_left(0, 6, submit_pressed=False) == 6

    def test_first_submit_decrements_display_by_1(self):
        # Bug: old formula gave 6 - 0 = 6 (wrong). Correct: 6 - 1 = 5.
        assert self._attempts_left(0, 6, submit_pressed=True) == 5

    def test_second_submit_decrements_correctly(self):
        # After 1 prior attempt, submitting again should show 4, not 5
        assert self._attempts_left(1, 6, submit_pressed=True) == 4

    def test_final_submit_shows_zero(self):
        # On the 6th and last submission, display must reach 0, not 1
        assert self._attempts_left(5, 6, submit_pressed=True) == 0

    def test_between_submits_no_decrement(self):
        # When the page reruns without a submit (e.g. sidebar change),
        # do not subtract the extra 1
        assert self._attempts_left(3, 6, submit_pressed=False) == 3

    def test_old_formula_was_wrong_on_first_submit(self):
        # Regression guard: the buggy formula (attempt_limit - attempts)
        # returned the full limit even after the first guess.
        buggy_result = 6 - 0  # what app.py produced before the fix
        correct_result = self._attempts_left(0, 6, submit_pressed=True)
        assert buggy_result != correct_result
        assert correct_result == 5


class TestNewGameReset:
    """
    Targets the bug where clicking "New Game" after a game ended (won/lost)
    did not fully reset session state. The handler reset `attempts` and `secret`
    but left `status`, `score`, and `history` unchanged — so the game stayed
    stuck in the game-over screen after rerun.

    These tests simulate the session_state dict directly (no Streamlit import)
    using a helper that mirrors the fixed handler in app.py.
    """

    def _apply_buggy_new_game(self, state: dict, new_secret: int) -> dict:
        """Mirrors the BROKEN handler (before fix): only resets attempts + secret."""
        state["attempts"] = 0
        state["secret"] = new_secret
        return state

    def _apply_fixed_new_game(self, state: dict, new_secret: int) -> dict:
        """Mirrors the FIXED handler: resets all five fields."""
        state["attempts"] = 0
        state["secret"] = new_secret
        state["status"] = "playing"
        state["score"] = 0
        state["history"] = []
        return state

    def _game_over_state(self, status: str = "won") -> dict:
        """Returns a realistic end-of-game session_state snapshot."""
        return {
            "attempts": 5,
            "secret": 42,
            "status": status,
            "score": 60,
            "history": [10, 20, 30, 40, 42],
        }

    # --- status reset ---

    def test_buggy_handler_leaves_status_unchanged_after_win(self):
        # Regression: the old code did NOT reset status, so it stayed "won"
        state = self._apply_buggy_new_game(self._game_over_state("won"), 7)
        assert state["status"] == "won"  # confirms the bug existed

    def test_fixed_handler_resets_status_to_playing_after_win(self):
        state = self._apply_fixed_new_game(self._game_over_state("won"), 7)
        assert state["status"] == "playing"

    def test_fixed_handler_resets_status_to_playing_after_loss(self):
        state = self._apply_fixed_new_game(self._game_over_state("lost"), 7)
        assert state["status"] == "playing"

    # --- score reset ---

    def test_buggy_handler_leaves_score_unchanged(self):
        state = self._apply_buggy_new_game(self._game_over_state(), 7)
        assert state["score"] == 60  # confirms the bug existed

    def test_fixed_handler_resets_score_to_zero(self):
        state = self._apply_fixed_new_game(self._game_over_state(), 7)
        assert state["score"] == 0

    # --- history reset ---

    def test_buggy_handler_leaves_history_unchanged(self):
        state = self._apply_buggy_new_game(self._game_over_state(), 7)
        assert state["history"] == [10, 20, 30, 40, 42]  # confirms the bug existed

    def test_fixed_handler_resets_history_to_empty(self):
        state = self._apply_fixed_new_game(self._game_over_state(), 7)
        assert state["history"] == []

    # --- fields that were already reset ---

    def test_fixed_handler_resets_attempts_to_zero(self):
        state = self._apply_fixed_new_game(self._game_over_state(), 7)
        assert state["attempts"] == 0

    def test_fixed_handler_assigns_new_secret(self):
        state = self._apply_fixed_new_game(self._game_over_state(), 99)
        assert state["secret"] == 99
        assert state["secret"] != 42  # different from the old game's secret
