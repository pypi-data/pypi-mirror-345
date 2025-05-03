from climate_ref.executor.local import LocalExecutor
from climate_ref_core.executor import Executor


class TestLocalExecutor:
    def test_is_executor(self):
        executor = LocalExecutor()

        assert executor.name == "local"
        assert isinstance(executor, Executor)

    def test_run_metric(self, metric_definition, provider, mock_diagnostic, mocker, caplog):
        mock_handle_result = mocker.patch("climate_ref.executor.local.handle_execution_result")
        mock_execution_result = mocker.MagicMock()
        executor = LocalExecutor()

        executor.run(provider, mock_diagnostic, metric_definition, mock_execution_result)
        # This directory is created by the executor
        assert metric_definition.output_directory.exists()

        mock_handle_result.assert_called_once()
        config, db, metric_execution_result, result = mock_handle_result.call_args.args

        assert metric_execution_result == mock_execution_result
        assert result.successful
        assert result.output_bundle_filename == metric_definition.output_directory / "output.json"
        assert result.metric_bundle_filename == metric_definition.output_directory / "diagnostic.json"
        assert (metric_definition.output_directory / "out.log").exists()

    def test_raises_exception(self, mocker, provider, metric_definition, mock_diagnostic):
        mock_handle_result = mocker.patch("climate_ref.executor.local.handle_execution_result")
        mock_execution_result = mocker.MagicMock()

        executor = LocalExecutor()

        mock_diagnostic.run = lambda definition: 1 / 0

        executor.run(provider, mock_diagnostic, metric_definition, mock_execution_result)

        config, db, metric_execution_result, result = mock_handle_result.call_args.args
        assert result.successful is False
        assert result.output_bundle_filename is None
        assert result.metric_bundle_filename is None

    def test_join(self):
        executor = LocalExecutor()

        executor.join(1)
        # This method should return immediately
