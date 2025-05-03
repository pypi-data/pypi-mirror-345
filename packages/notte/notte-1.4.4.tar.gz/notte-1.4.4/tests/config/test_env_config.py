from notte_browser.scraping.pipe import ScrapingType
from notte_browser.session import NotteSessionConfig
from notte_browser.tagging.action.pipe import ActionSpaceType
from notte_sdk.types import DEFAULT_MAX_NB_STEPS


def test_notte_session_config_initialization():
    config = NotteSessionConfig()
    assert config.verbose is False
    assert config.max_steps == DEFAULT_MAX_NB_STEPS


def test_dev_mode():
    config = NotteSessionConfig()
    updated_config = config.dev_mode()
    assert updated_config.verbose is True


def test_user_mode():
    config = NotteSessionConfig()
    updated_config = config.user_mode()
    assert updated_config.verbose is True
    assert updated_config.window.verbose is True
    assert updated_config.action.verbose is True


def test_groq():
    config = NotteSessionConfig()
    updated_config = config.groq()
    assert updated_config.perception_model == "groq/llama-3.3-70b-versatile"


def test_openai():
    config = NotteSessionConfig()
    updated_config = config.openai()
    assert updated_config.perception_model == "openai/gpt-4o"


def test_cerebras():
    config = NotteSessionConfig()
    updated_config = config.cerebras()
    assert updated_config.perception_model == "cerebras/llama-3.3-70b"


def test_steps():
    config = NotteSessionConfig()
    updated_config = config.steps(20)
    assert updated_config.max_steps == 20


def test_headless():
    config = NotteSessionConfig()
    updated_config = config.headless(True)
    assert updated_config.window.headless is True


def test_not_headless():
    config = NotteSessionConfig()
    updated_config = config.not_headless()
    assert updated_config.window.headless is False


def test_cdp():
    config = NotteSessionConfig()
    updated_config = config.cdp("ws://example.com")
    assert updated_config.window.cdp_url == "ws://example.com"


def test_llm_action_tagging():
    config = NotteSessionConfig().disable_perception()
    updated_config = config.llm_action_tagging()
    assert config.action.type is ActionSpaceType.SIMPLE
    assert updated_config.action.type is ActionSpaceType.LLM_TAGGING


def test_llm_data_extract():
    config = NotteSessionConfig().disable_perception()
    updated_config = config.llm_data_extract()
    assert config.scraping.type is ScrapingType.SIMPLE
    assert updated_config.scraping.type == ScrapingType.LLM_EXTRACT


def test_disable_web_security():
    config = NotteSessionConfig()
    updated_config = config.disable_web_security()
    assert config.window.web_security is False
    assert updated_config.window.web_security is False


def test_enable_web_security():
    config = NotteSessionConfig().disable_web_security()
    updated_config = config.enable_web_security()
    assert config.window.web_security is False
    assert updated_config.window.web_security is True
