# SPDX-License-Identifier: Apache-2.0
# pylint: disable=duplicate-code

# Standard
from unittest.mock import MagicMock, patch
import os

# Third Party
from click.testing import CliRunner
from git import GitError

# First Party
from instructlab import lab
from instructlab.configuration import DEFAULTS, read_config


class TestLabInit:
    @patch(
        "torch.cuda.is_available",
        return_value=False,
    )
    @patch("instructlab.config.init.is_hpu_available", return_value=True)
    def test_is_hpu_available_true(
        self,
        is_hpu_available_mock,  # pylint: disable=unused-argument
        is_cuda_available_mock,  # pylint: disable=unused-argument
        cli_runner: CliRunner,
    ):
        result = cli_runner.invoke(lab.ilab, ["config", "init", "--interactive"])
        assert result.exit_code == 0, result.stdout

    @patch(
        "torch.cuda.is_available",
        return_value=True,
    )
    @patch("instructlab.config.init.is_hpu_available", return_value=False)
    def test_is_hpu_available_false(
        self,
        is_hpu_available_mock,  # pylint: disable=unused-argument
        is_cuda_available_mock,  # pylint: disable=unused-argument
        cli_runner: CliRunner,
    ):
        result = cli_runner.invoke(lab.ilab, ["config", "init", "--interactive"])
        assert result.exit_code == 0, result.stdout

    @patch("instructlab.config.init.is_hpu_available", return_value=False)
    @patch(
        "torch.cuda.is_available",
        return_value=True,
    )
    @patch(
        "torch.version.hip",
        "6.2.41134",
    )
    def test_hip_and_cuda_active(
        self,
        is_cuda_available_mock,  # pylint: disable=unused-argument
        is_hpu_available_mock,  # pylint: disable=unused-argument
        cli_runner: CliRunner,
    ):
        result = cli_runner.invoke(lab.ilab, ["config", "init", "--interactive"])
        assert result.exit_code == 0, result.stdout

    @patch(
        "instructlab.config.init.get_gpu_or_cpu",
        return_value=("nvidia a100", 0, 2),
    )
    def test_ilab_config_init_auto_detection_nvidia(
        self, convert_bytes_to_proper_mag_mock, cli_runner: CliRunner
    ):
        result = cli_runner.invoke(lab.ilab, ["config", "init", "--interactive"])
        assert result.exit_code == 0, result.stdout
        convert_bytes_to_proper_mag_mock.assert_called_once()
        assert (
            "We have detected the NVIDIA A100 X2 profile as an exact match for your system."
            in result.stdout
        )

    @patch(
        "torch.cuda.is_available",
        return_value=True,
    )
    @patch("torch.cuda.device_count", return_value=2)
    @patch(
        "instructlab.utils.get_cuda_device_properties",
        return_value=("nvidia-a100-sxm4-40gb", 40000),
    )
    def test_ilab_config_init_auto_detection_nvidia_a100(
        self,
        get_device_properties_mock,  # pylint: disable=unused-argument
        device_count_mock,  # pylint: disable=unused-argument
        is_cuda_available_mock,  # pylint: disable=unused-argument
        cli_runner: CliRunner,
    ):
        result = cli_runner.invoke(lab.ilab, ["config", "init", "--interactive"])
        assert result.exit_code == 0, result.stdout
        assert (
            "We have detected the NVIDIA A100 X2 profile as an exact match for your system."
            in result.stdout
        )

    @patch(
        "instructlab.config.init.get_gpu_or_cpu",
        return_value=("apple m3 max", 0, 0),
    )
    def test_ilab_config_init_auto_detection_mac(
        self, convert_bytes_to_proper_mag_mock, cli_runner: CliRunner
    ):
        result = cli_runner.invoke(lab.ilab, ["config", "init", "--interactive"])
        assert result.exit_code == 0, result.stdout
        convert_bytes_to_proper_mag_mock.assert_called_once()
        assert (
            "We have detected the APPLE M3 MAX profile as an exact match for your system."
            in result.stdout
        )

    @patch(
        "instructlab.config.init.get_gpu_or_cpu",
        return_value=("amd cpu", 0, 0),
    )
    def test_ilab_config_init_auto_detection_amd_cpu(
        self, convert_bytes_to_proper_mag_mock, cli_runner: CliRunner
    ):
        result = cli_runner.invoke(lab.ilab, ["config", "init", "--interactive"])
        assert result.exit_code == 0, result.stdout
        convert_bytes_to_proper_mag_mock.assert_called_once()
        assert (
            "We have detected the AMD CPU profile as an exact match for your system."
            in result.stdout
        )

    @patch(
        "instructlab.config.init.get_gpu_or_cpu",
        return_value=("intel cpu", 0, 0),
    )
    def test_ilab_config_init_auto_detection_intel_cpu(
        self, convert_bytes_to_proper_mag_mock, cli_runner: CliRunner
    ):
        result = cli_runner.invoke(lab.ilab, ["config", "init", "--interactive"])
        assert result.exit_code == 0, result.stdout
        convert_bytes_to_proper_mag_mock.assert_called_once()
        assert (
            "We have detected the INTEL CPU profile as an exact match for your system."
            in result.stdout
        )

    @patch(
        "instructlab.config.init.get_gpu_or_cpu",
        return_value=("intel gaudi 3", 0, 8),
    )
    def test_ilab_config_init_auto_detection_gaudi(
        self, convert_bytes_to_proper_mag_mock, cli_runner: CliRunner
    ):
        result = cli_runner.invoke(lab.ilab, ["config", "init", "--interactive"])
        assert result.exit_code == 0, result.stdout
        convert_bytes_to_proper_mag_mock.assert_called_once()
        assert (
            "We have detected the INTEL GAUDI X8 profile as an exact match for your system."
            in result.stdout
        )

    @patch(
        "instructlab.config.init.get_gpu_or_cpu",
        return_value=("nvidia h100 pcie", 0, 8),
    )
    def test_ilab_config_init_auto_detection_h100_pcie(
        self, convert_bytes_to_proper_mag_mock, cli_runner: CliRunner
    ):
        result = cli_runner.invoke(lab.ilab, ["config", "init", "--interactive"])
        assert result.exit_code == 0, result.stdout
        convert_bytes_to_proper_mag_mock.assert_called_once()
        assert (
            "We have detected the NVIDIA H100 X8 profile as an exact match for your system."
            in result.stdout
        )

    @patch(
        "instructlab.config.init.get_gpu_or_cpu",
        return_value=("nvidia h100 80gb hbm3", 0, 8),
    )
    def test_ilab_config_init_auto_detection_h100_hbm3(
        self, convert_bytes_to_proper_mag_mock, cli_runner: CliRunner
    ):
        result = cli_runner.invoke(lab.ilab, ["config", "init", "--interactive"])
        assert result.exit_code == 0, result.stdout
        convert_bytes_to_proper_mag_mock.assert_called_once()
        assert (
            "We have detected the NVIDIA H100 X8 profile as an exact match for your system."
            in result.stdout
        )

    @patch(
        "instructlab.config.init.get_gpu_or_cpu",
        return_value=("nvidia h100 nvl", 0, 8),
    )
    def test_ilab_config_init_auto_detection_h100_nvl(
        self, convert_bytes_to_proper_mag_mock, cli_runner: CliRunner
    ):
        result = cli_runner.invoke(lab.ilab, ["config", "init", "--interactive"])
        assert result.exit_code == 0, result.stdout
        convert_bytes_to_proper_mag_mock.assert_called_once()
        assert (
            "We have detected the NVIDIA H100 X8 profile as an exact match for your system."
            in result.stdout
        )

    # When using `from X import Y` you need to understand that Y becomes part
    # of your module, so you should use `my_module.Y`` to patch.
    # When using `import X`, you should use `X.Y` to patch.
    # https://docs.python.org/3/library/unittest.mock.html#where-to-patch?
    @patch("instructlab.cli.config.init.Repo.clone_from")
    def test_init_noninteractive(self, mock_clone_from, cli_runner: CliRunner):
        result = cli_runner.invoke(lab.ilab, ["config", "init", "--non-interactive"])
        assert result.exit_code == 0
        assert os.path.exists(DEFAULTS.CONFIG_FILE)
        assert "config.yaml" in os.listdir(DEFAULTS._config_dir)
        mock_clone_from.assert_called_once()

    @patch("instructlab.cli.config.init.Repo.clone_from")
    def test_init_interactive(self, mock_clone_from, cli_runner: CliRunner):
        result = cli_runner.invoke(lab.ilab, ["config", "init"], input="\nn")
        assert result.exit_code == 0
        assert "config.yaml" in os.listdir(DEFAULTS._config_dir)
        assert "taxonomy" not in os.listdir()
        mock_clone_from.assert_not_called()

    @patch(
        "instructlab.cli.config.init.Repo.clone_from",
        MagicMock(side_effect=GitError("Authentication failed")),
    )
    def test_init_interactive_git_error(self, cli_runner: CliRunner):
        result = cli_runner.invoke(lab.ilab, ["config", "init"], input="y\n\ny")
        assert result.exit_code == 1, "command finished with an unexpected exit code"
        assert "Failed to clone taxonomy repo: Authentication failed" in result.output
        assert "manually run" in result.output

    @patch("instructlab.cli.config.init.Repo.clone_from")
    def test_init_interactive_clone(self, mock_clone_from, cli_runner: CliRunner):
        result = cli_runner.invoke(lab.ilab, ["config", "init"], input="y\n\ny")
        assert result.exit_code == 0
        assert "config.yaml" in os.listdir(DEFAULTS._config_dir)
        mock_clone_from.assert_called_once()

    @patch("instructlab.cli.config.init.Repo.clone_from")
    def test_init_interactive_default_clone(
        self, mock_clone_from, cli_runner: CliRunner
    ):
        result = cli_runner.invoke(lab.ilab, ["config", "init"], input="\n")
        assert result.exit_code == 0
        assert "config.yaml" in os.listdir(DEFAULTS._config_dir)
        mock_clone_from.assert_called_once()

    @patch("instructlab.cli.config.init.Repo.clone_from")
    def test_init_interactive_with_preexisting_nonempty_taxonomy(
        self, mock_clone_from, cli_runner: CliRunner
    ):
        os.makedirs(f"{DEFAULTS.TAXONOMY_DIR}/contents")
        result = cli_runner.invoke(lab.ilab, ["config", "init"], input="\n\n")
        assert result.exit_code == 0
        assert "config.yaml" in os.listdir(DEFAULTS._config_dir)
        assert "taxonomy" in os.listdir(DEFAULTS._data_dir)
        mock_clone_from.assert_not_called()

    def test_init_interactive_with_preexisting_config(self, cli_runner: CliRunner):
        result = cli_runner.invoke(
            lab.ilab, ["config", "init"], input="non-default-taxonomy\nn"
        )
        assert result.exit_code == 0
        assert "config.yaml" in os.listdir(DEFAULTS._config_dir)
        config = read_config(DEFAULTS.CONFIG_FILE)
        assert config.generate.taxonomy_path == "non-default-taxonomy"

        # second invocation should ask if we want to overwrite - yes, and change taxonomy path
        result = cli_runner.invoke(
            lab.ilab, ["config", "init"], input="y\ny\ndifferent-taxonomy\nn"
        )
        assert result.exit_code == 0
        assert "config.yaml" in os.listdir(DEFAULTS._config_dir)
        config = read_config(DEFAULTS.CONFIG_FILE)
        assert config.generate.taxonomy_path == "different-taxonomy"

        # third invocation should again ask, but this time don't overwrite
        result = cli_runner.invoke(lab.ilab, ["config", "init"], input="n")
        assert result.exit_code == 0
        assert "config.yaml" in os.listdir(DEFAULTS._config_dir)
        config = read_config(DEFAULTS.CONFIG_FILE)
        assert config.generate.taxonomy_path == "different-taxonomy"

    def test_lab_init_with_profile(self, tmp_path_home, cli_runner: CliRunner):
        config_path = tmp_path_home / "config.yaml"
        with open(config_path, "w", encoding="utf-8") as config_file:
            config_file.write(
                """\
version: 1.0.0
chat:
  model: models/granite-7b-lab-Q4_K_M.gguf
generate:
  pipeline: simple
  model: models/granite-7b-lab-Q4_K_M.gguf
  taxonomy_base: upstream/main
  taxonomy_path: mytaxonomy
  teacher:
    model_path: models/granite-7b-lab-Q4_K_M.gguf
    chat_template: tokenizer
    llama_cpp:
      gpu_layers: 1
      max_ctx_size: 2048
      llm_family: ''
    vllm:
      gpus: 8
serve:
  model_path: models/granite-7b-lab-Q4_K_M.gguf
  chat_template: tokenizer
  llama_cpp:
    gpu_layers: 1
    max_ctx_size: 2048
    llm_family: ''
  vllm:
    gpus: 8
    vllm_args:
       - --dtype=auto
       - --enable-lora
evaluate:
  base_model: instructlab/granite-7b-lab
  gpus: 1
  mmlu:
    few_shots: 2
    batch_size: auto
  mmlu_branch:
    tasks_dir: /path/to/sdg
  mt_bench:
    judge_model: prometheus
    output_dir: /dir/to/output
    max_workers: auto
  mt_bench_branch:
    taxonomy_path: taxonomy
general:
  log_level: DEBUG
"""
            )
        # third invocation should again ask, but this time don't overwrite
        result = cli_runner.invoke(
            lab.ilab,
            ["config", "init", "--non-interactive", f"--profile={config_path}"],
        )
        assert result.exit_code == 0
