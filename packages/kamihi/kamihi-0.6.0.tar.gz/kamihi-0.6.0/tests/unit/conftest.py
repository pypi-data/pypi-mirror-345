"""
Unit testing configuration and common fixtures.

License:
    MIT

"""

from unittest.mock import Mock, AsyncMock

import pytest
from telegram import Update, Bot, Message


@pytest.fixture
def mock_update():
    """Fixture to provide a mock Update instance."""
    update = Mock(spec=Update)
    update.effective_message = Mock()
    update.effective_message.chat_id = 123456
    update.effective_message.message_id = 789
    return update


@pytest.fixture
def mock_context():
    """Fixture to provide a mock CallbackContext."""
    context = Mock()
    context.bot = Mock(spec=Bot)
    context.bot.send_message = AsyncMock(return_value=Mock(spec=Message))
    return context
