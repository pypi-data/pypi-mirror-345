# SPDX-License-Identifier: Apache-2.0

# Standard
from unittest.mock import Mock, patch
import pathlib
import typing

# Third Party
import git
import pytest
import yaml

# First Party
from instructlab import utils
from instructlab.utils import Message, MessageSample
from tests.test_backends import create_safetensors_or_bin_model_files


class TestUtils:
    """Test collection in instructlab.utils."""

    @patch(
        "instructlab.utils.git_clone_checkout",
        return_value=Mock(
            spec=git.Repo, working_dir="tests/testdata/temp_taxonomy_repo"
        ),
    )
    def test_validate_documents(self, git_clone_checkout):
        with open(
            "tests/testdata/knowledge_valid.yaml", "r", encoding="utf-8"
        ) as qnafile:
            utils._validate_documents(
                source=yaml.safe_load(qnafile).get("document"),
                skip_checkout=True,
            )
            git_clone_checkout.assert_called_once()

    def test_convert_to_legacy_from_pretraining_messages(
        self,
    ):
        new_dataset: typing.List[MessageSample] = [
            {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a friendly assistant",
                    },
                    {
                        "role": "pretraining",
                        "content": "<|user|>What is 2+2?<|assistant|>2+2=4",
                    },
                ],
                "group": " test",
                "dataset": "test-dataset",
                "metadata": "test",
            }
        ]
        legacy = utils.ensure_legacy_dataset(new_dataset)
        assert len(legacy) == 1
        assert legacy[0]["system"] == "You are a friendly assistant"
        assert legacy[0]["user"] == "What is 2+2?"
        assert legacy[0]["assistant"] == "2+2=4"

    @pytest.mark.parametrize(
        "content,exception,match",
        [
            ("<|user|>What is 2+2? 2+2=4", ValueError, "<|assistant|>"),
            ("<|assistant|>2+2=4", ValueError, "<|user|>"),
            ("<|user|>what is 2+2?<|assistant|>2+2=4", None, ""),
        ],
    )
    def test_invalid_pretraining_messages(
        self, content: str, exception: Exception | None, match: str
    ):
        new_dataset: typing.List[MessageSample] = [
            {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a friendly assistant",
                    },
                    {
                        "role": "pretraining",
                        "content": content,
                    },
                ],
                "group": " test",
                "dataset": "test-dataset",
                "metadata": "test",
            }
        ]
        if exception:
            with pytest.raises(ValueError, match=match):
                utils.ensure_legacy_dataset(new_dataset)
        else:
            utils.ensure_legacy_dataset(new_dataset)

    def test_pretraining_messages_without_system(self):
        new_dataset: typing.List[MessageSample] = [
            {
                "messages": [
                    {
                        "role": "pretraining",
                        "content": "<|user|>What is 2+2?<|assistant|>2+2=4",
                    },
                ],
                "group": " test",
                "dataset": "test-dataset",
                "metadata": "test",
            }
        ]
        legacy = utils.ensure_legacy_dataset(new_dataset)
        assert len(legacy) == 1
        assert legacy[0]["system"] == ""

    def test_convert_to_legacy_from_messages(self):
        messages: typing.List[MessageSample] = [
            {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a friendly assistant",
                    },
                    {"role": "user", "content": "Who is pickle rick?"},
                    {
                        "role": "assistant",
                        "content": "As an AI language model, I have absolutely no idea.",
                    },
                ],
                "group": " test",
                "dataset": "test-dataset",
                "metadata": "test",
            }
        ]
        legacy = utils.ensure_legacy_dataset(messages)
        assert len(legacy) == 1
        sample = legacy[0]
        assert sample["system"] == "You are a friendly assistant"
        assert sample["user"] == "Who is pickle rick?"
        assert (
            sample["assistant"] == "As an AI language model, I have absolutely no idea."
        )

    @pytest.mark.parametrize(
        "system,user,assistant",
        [
            (None, None, None),
            ("You are a friendly assistant trained by ACME corp", None, None),
            (None, "Who is pickle rick?", None),
            (
                "You are a friendly assistant trained by ACME corp",
                "Who is pickle rick?",
                None,
            ),
            (None, None, "As an AI language model, I have absolutely no idea."),
            (
                "You are a friendly assistant trained by ACME corp",
                None,
                "As an AI language model, I have absolutely no idea.",
            ),
            (
                None,
                "Who is pickle rick?",
                "As an AI language model, I have absolutely no idea.",
            ),
        ],
    )
    def test_invalid_datasets(
        self, system: str | None, user: str | None, assistant: str | None
    ):
        messages: typing.List[Message] = []
        if system:
            messages.append({"content": system, "role": "system"})
        if user:
            messages.append({"content": user, "role": "user"})
        if assistant:
            messages.append({"content": assistant, "role": "assistant"})
        dataset: typing.List[MessageSample] = [
            {
                "messages": messages,
                "group": "ACME",
                "dataset": "The Pickle Rick Collection",
                "metadata": "{{ pickle: rick, }}",
            }
        ]
        with pytest.raises(ValueError):
            utils.ensure_legacy_dataset(dataset)


def test_get_sysprompt():
    arch = "llama"
    assert (
        utils.get_sysprompt(arch)
        == "I am, Red Hat® Instruct Model based on Granite 7B, an AI language model developed by Red Hat and IBM Research, based on the Granite-7b-base language model. My primary function is to be a chat assistant."
    )

    arch = "granite"
    assert (
        utils.get_sysprompt(arch)
        == "I am a Red Hat® Instruct Model, an AI language model developed by Red Hat and IBM Research based on the granite-3.0-8b-base model. My primary role is to serve as a chat assistant."
    )

    arch = "granite-3.1"
    assert (
        utils.get_sysprompt(arch)
        == "I am a Red Hat® Instruct Model, an AI language model developed by Red Hat and IBM Research based on the granite-3.1-8b-base model. My primary role is to serve as a chat assistant."
    )

    arch = "random"
    assert (
        utils.get_sysprompt(arch)
        == "I am an advanced AI language model designed to assist you with a wide range of tasks and provide helpful, clear, and accurate responses. My primary role is to serve as a chat assistant, engaging in natural, conversational dialogue, answering questions, generating ideas, and offering support across various topics."
    )


def test_get_model_arch_granite():
    mock_path = pathlib.Path("/path/to/mock/granite/model")
    mock_config = {
        "model_type": "granite",
        "max_position_embeddings": 32768,  # Less than 131072
    }

    with (
        patch("instructlab.utils.is_model_safetensors", return_value=True),
        patch("instructlab.utils.get_config_file_from_model", return_value=mock_config),
    ):
        result = utils.get_model_arch(mock_path)
        assert result == "granite"


def test_get_model_arch_granite_3_1():
    mock_path = pathlib.Path("/path/to/mock/granite-3.1/model")
    mock_config = {"model_type": "granite", "max_position_embeddings": 131072}

    with (
        patch("instructlab.utils.is_model_safetensors", return_value=True),
        patch("instructlab.utils.get_config_file_from_model", return_value=mock_config),
    ):
        result = utils.get_model_arch(mock_path)
        assert result == "granite-3.1"


def test_get_model_template_from_tokenizer(tmp_path: pathlib.Path):
    model_path = tmp_path / "tmp_model"
    create_safetensors_or_bin_model_files(model_path, "safetensors", True)

    tmpl, eos, bos = utils.get_model_template_from_tokenizer(model_path)
    assert tmpl == "test-chat-template"
    assert eos == "<|end_of_text|>"
    assert bos == "<|beginning_of_text|>"


def test_use_legacy_pretraining_format(tmp_path: pathlib.Path):
    model_path = tmp_path / "tmp_model"
    model_arch = "llama"
    test_json_config = {
        "model_type": "granite",
    }
    test_json_tokeninzer_config = {
        "bos_token": "<|begginingoftext|>",
        "eos_token": "<|endoftext|>",
    }
    # llama tokens, should return true
    create_safetensors_or_bin_model_files(
        model_path,
        "safetensors",
        True,
        test_config=test_json_config,
        test_tokenizer_config=test_json_tokeninzer_config,
    )
    assert utils.use_legacy_pretraining_format(model_path, model_arch)

    model_path = tmp_path / "tmp_model"
    model_arch = "llama"
    test_json_config = {
        "model_type": "granite",
    }
    test_json_tokeninzer_config = {
        "bos_token": "<|begginingoftext|>",
    }
    # invalid tokens, should default to checking arch and return true
    create_safetensors_or_bin_model_files(
        model_path,
        "safetensors",
        True,
        test_config=test_json_config,
        test_tokenizer_config=test_json_tokeninzer_config,
    )
    assert utils.use_legacy_pretraining_format(model_path, model_arch)

    model_path = tmp_path / "tmp_model-2"
    model_arch = "llama"
    # granite tokens, should return false
    create_safetensors_or_bin_model_files(model_path, "safetensors", True)
    assert not utils.use_legacy_pretraining_format(model_path, model_arch)
