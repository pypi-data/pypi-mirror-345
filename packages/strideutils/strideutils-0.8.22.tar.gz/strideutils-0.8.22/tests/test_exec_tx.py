import json
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
from unittest.mock import MagicMock, patch

from strideutils.exec_tx import TxResponse, execute_tx

# Test constants
MOCK_TX_HASH = "ABC123"
MOCK_COMMAND = "stride tx bank send addr1 addr2 1000ustrd"
MOCK_API_ENDPOINT = "http://api.stride.test"

# Mock response types
MockCommandOutput = Dict[str, str]


@dataclass
class MockTxResponse:
    data: dict[str, Any]
    status_code: int = 200

    def json(self):
        return self.data


# Mock successful command output
MOCK_SUCCESS_STDOUT: MockCommandOutput = {
    "txhash": MOCK_TX_HASH,
    "other_data": "some_value",
}

# Mock successful tx response
MOCK_SUCCESS_TX_RESPONSE = MockTxResponse(
    data={
        "tx_response": {
            "code": 0,
            "raw_log": "transaction successful",
        }
    },
    status_code=200,
)

# Mock failed tx response
MOCK_FAILED_TX_RESPONSE = MockTxResponse(
    data={
        "tx_response": {
            "code": 1,
            "raw_log": "transaction failed",
        }
    },
    status_code=200,
)


def test_execute_tx_success() -> None:
    """Test successful transaction execution."""
    with patch("subprocess.run") as mock_run, patch("strideutils.stride_requests.requests.get") as mock_get_tx:
        # Mock subprocess.run
        mock_process = MagicMock()
        mock_process.stdout = json.dumps(MOCK_SUCCESS_STDOUT)
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        # Mock get_tx response
        mock_get_tx.return_value = MOCK_SUCCESS_TX_RESPONSE

        # Execute transaction
        response = execute_tx(MOCK_COMMAND, MOCK_API_ENDPOINT)

        # Verify command was called with correct arguments
        mock_run.assert_called_once_with(
            f"{MOCK_COMMAND} -y --output json",
            shell=True,
            capture_output=True,
            text=True,
        )

        # Verify response
        assert response.success is True
        assert response.tx_hash == MOCK_TX_HASH
        assert response.code == 0
        assert response.raw_log == "transaction successful"
        assert response.stderr == ""


def test_execute_tx_failure() -> None:
    """Test failed transaction execution."""
    with patch("subprocess.run") as mock_run, patch("strideutils.stride_requests.requests.get") as mock_get_tx:
        # Mock subprocess.run
        mock_process = MagicMock()
        mock_process.stdout = json.dumps(MOCK_SUCCESS_STDOUT)
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        # Mock get_tx response with failure
        mock_get_tx.return_value = MOCK_FAILED_TX_RESPONSE

        # Execute transaction
        response = execute_tx(MOCK_COMMAND, MOCK_API_ENDPOINT)

        # Verify response indicates failure
        assert response.success is False
        assert response.tx_hash == MOCK_TX_HASH
        assert response.code == 1
        assert response.raw_log == "transaction failed"


def test_execute_tx_subprocess_error() -> None:
    """Test handling of subprocess execution error."""
    with patch("subprocess.run") as mock_run:
        # Mock subprocess.run with stderr
        mock_process = MagicMock()
        mock_process.stdout = ""
        mock_process.stderr = "Command execution failed"
        mock_run.return_value = mock_process

        # Execute transaction
        response = execute_tx(MOCK_COMMAND, MOCK_API_ENDPOINT)

        # Verify response
        assert response.success is False
        assert response.tx_hash == ""
        assert response.stderr == "Command execution failed"
        assert response.raw_log == "Command execution failed"


def test_execute_tx_missing_hash() -> None:
    """Test handling of missing transaction hash."""
    with patch("subprocess.run") as mock_run:
        # Mock subprocess.run with stdout missing txhash
        mock_process = MagicMock()
        mock_process.stdout = json.dumps({"other_data": "value"})
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        # Execute transaction
        response = execute_tx(MOCK_COMMAND, MOCK_API_ENDPOINT)

        # Verify response
        assert response.success is False
        assert response.tx_hash == ""
        assert response.raw_log == "Tx hash not found after running tx"


def test_execute_tx_timeout() -> None:
    """Test handling of transaction timeout."""
    with (
        patch("subprocess.run") as mock_run,
        patch("strideutils.stride_requests.requests.get") as mock_get_tx,
        patch("time.sleep") as mock_sleep,
    ):  # Added sleep mock
        # Mock subprocess.run
        mock_process = MagicMock()
        mock_process.stdout = json.dumps(MOCK_SUCCESS_STDOUT)
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        # Mock get_tx response without tx_response field
        mock_get_tx.return_value = MockTxResponse(data={}, status_code=200)

        # Execute transaction
        response = execute_tx(MOCK_COMMAND, MOCK_API_ENDPOINT)

        # Verify response
        assert response.success is False
        assert response.tx_hash == MOCK_TX_HASH
        assert response.raw_log == "Transaction not found on chain after one minute"

        # Verify sleep was called correctly
        assert mock_sleep.call_count == 30  # Verifying that all retries happened
        mock_sleep.assert_called_with(2)  # Verifying the sleep duration was 2 seconds


def test_execute_tx_not_found() -> None:
    """Test handling of transaction where the tx was not found and returned a non-200 status code"""
    with (
        patch("subprocess.run") as mock_run,
        patch("strideutils.stride_requests.requests.get") as mock_get_tx,
        patch("time.sleep") as mock_sleep,
    ):  # Added sleep mock
        # Mock subprocess.run
        mock_process = MagicMock()
        mock_process.stdout = json.dumps(MOCK_SUCCESS_STDOUT)
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        # Mock get_tx response without tx_response field
        mock_get_tx.return_value = MockTxResponse(data={}, status_code=404)

        # Execute transaction
        response = execute_tx(MOCK_COMMAND, MOCK_API_ENDPOINT)

        # Verify response
        assert response.success is False
        assert response.tx_hash == MOCK_TX_HASH
        assert response.raw_log == "Transaction not found on chain after one minute"

        # Verify sleep was called correctly
        assert mock_sleep.call_count == 30  # Verifying that all retries happened
        mock_sleep.assert_called_with(2)  # Verifying the sleep duration was 2 seconds


def test_execute_tx_auto_append_flags() -> None:
    """Test auto-appending of -y and --output json flags."""
    with patch("subprocess.run") as mock_run:
        # Mock subprocess.run
        mock_process = MagicMock()
        mock_process.stdout = ""
        mock_process.stderr = "some error"
        mock_run.return_value = mock_process

        # Test commands with different combinations of flags
        test_cases: List[Tuple[str, str]] = [
            ("base command", "base command -y --output json"),
            ("base command -y", "base command -y --output json"),
            ("base command --output json", "base command --output json -y --output json"),
        ]

        for input_cmd, expected_cmd in test_cases:
            execute_tx(input_cmd, MOCK_API_ENDPOINT)
            mock_run.assert_called_with(
                expected_cmd,
                shell=True,
                capture_output=True,
                text=True,
            )


def test_tx_response_dataclass() -> None:
    """Test TxResponse dataclass initialization and defaults."""
    # Test default initialization
    response = TxResponse(stdout={}, stderr="")
    assert response.success is False
    assert response.tx_hash == ""
    assert response.code is None
    assert response.tx_response is None
    assert response.raw_log is None

    # Test with all fields
    response = TxResponse(
        stdout={"data": "test"},
        stderr="error",
        tx_hash="hash123",
        success=True,
        code=0,
        tx_response={"key": "value"},
        raw_log="log message",
    )
    assert response.stdout == {"data": "test"}
    assert response.stderr == "error"
    assert response.tx_hash == "hash123"
    assert response.success is True
    assert response.code == 0
    assert response.tx_response == {"key": "value"}
    assert response.raw_log == "log message"
