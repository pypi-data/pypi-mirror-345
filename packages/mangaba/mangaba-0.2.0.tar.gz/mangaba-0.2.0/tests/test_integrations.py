import pytest
from unittest.mock import Mock, patch
from mangaba.integrations import SlackIntegration, GitHubIntegration, JiraIntegration, DiscordIntegration

class TestSlackIntegration:
    @pytest.fixture
    def slack_integration(self):
        return SlackIntegration(
            bot_token="test-token",
            app_token="test-app-token",
            channel_id="test-channel"
        )

    def test_send_message(self, slack_integration):
        with patch('slack_sdk.WebClient') as mock_client:
            mock_client.return_value.chat_postMessage.return_value = {"ok": True}
            result = slack_integration.send_message("Test message")
            assert result["ok"] is True

class TestGitHubIntegration:
    @pytest.fixture
    def github_integration(self):
        return GitHubIntegration(
            token="test-token",
            repo_owner="test-owner",
            repo_name="test-repo"
        )

    def test_create_issue(self, github_integration):
        with patch('github.Github') as mock_github:
            mock_repo = Mock()
            mock_github.return_value.get_repo.return_value = mock_repo
            mock_repo.create_issue.return_value = Mock(number=1)
            result = github_integration.create_issue("Test issue", "Test body")
            assert result.number == 1

class TestJiraIntegration:
    @pytest.fixture
    def jira_integration(self):
        return JiraIntegration(
            server="https://test.atlassian.net",
            email="test@email.com",
            api_token="test-token"
        )

    def test_create_issue(self, jira_integration):
        with patch('jira.JIRA') as mock_jira:
            mock_issue = Mock(key="TEST-1")
            mock_jira.return_value.create_issue.return_value = mock_issue
            result = jira_integration.create_issue("Test issue", "Test description")
            assert result.key == "TEST-1"

class TestDiscordIntegration:
    @pytest.fixture
    def discord_integration(self):
        return DiscordIntegration(
            token="test-token",
            guild_id="test-guild"
        )

    def test_send_message(self, discord_integration):
        with patch('discord.Client') as mock_client:
            mock_channel = Mock()
            mock_client.return_value.get_channel.return_value = mock_channel
            mock_channel.send.return_value = Mock(id=123)
            result = discord_integration.send_message("test-channel", "Test message")
            assert result.id == 123 