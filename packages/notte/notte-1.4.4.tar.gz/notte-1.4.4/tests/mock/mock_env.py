import datetime as dt
from typing import final

from notte_browser.session import NotteSession
from notte_core.actions.base import Action
from notte_core.actions.space import ActionSpace
from notte_core.browser.observation import Observation
from notte_core.browser.snapshot import SnapshotMetadata, ViewportData
from typing_extensions import override


@final
class MockNotteSession(NotteSession):
    """A mock version of NotteSession that returns constant values for testing"""

    def __init__(self) -> None:
        super().__init__(headless=True)
        self._mock_action = Action(description="Mock action", id="mock_id", category="mock", status="valid")
        self._mock_action_space = ActionSpace(
            raw_actions=[self._mock_action],
            description="Mock action space",
        )
        self._mock_observation = Observation(
            metadata=SnapshotMetadata(
                url="https://mock.url",
                title="Mock title",
                timestamp=dt.datetime.now(),
                viewport=ViewportData(
                    scroll_x=0,
                    scroll_y=0,
                    viewport_width=1000,
                    viewport_height=1000,
                    total_width=1000,
                    total_height=1000,
                ),
                tabs=[],
            ),
            space=self._mock_action_space,
        )

    @override
    async def observe(self, url: str | None = None) -> Observation:
        """Mock observe method that returns a constant observation"""
        return self._mock_observation

    @override
    async def step(
        self,
        action_id: Action | str,
        params: dict[str, str] | str | None = None,
        enter: bool | None = None,
    ) -> Observation:
        """Mock step method that returns a constant observation"""
        return self._mock_observation
