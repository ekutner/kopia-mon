import pytest
from datetime import datetime, timezone
from kopiaapi import KopiaApi, SnapshotVerifyResult

def test_snapshot_verify_with_errors(mocker):
    # Mock response from kopia command
    with open("tests/snapshot_verify_output_with_errors.txt", 'r', encoding="utf-8") as file:
        mock_response = file.read()
    # x= """
    # Listed 100 blobs
    # Processed 50/100...
    # Processed 100/100...
    # Finished processing 100 objects
    # ERROR Invalid checksum for blob abc123
    # ERROR Missing data in blob def456
    # """

    mock_command = mocker.Mock(return_value=mock_response)

    # Initialize API with mock command
    api = KopiaApi("test.config", mock_command)

    # Call the method
    result = api.snapshot_verify(percent=0.5, file_parallelism=5, parallel=5)

    # Verify the mock was called with correct arguments
    mock_command.assert_called_once_with(
        ["snapshot", "verify", "--verify-files-percent=0.5", "--file-parallelism=5", "--parallel=5"],
        json_result=False
    )

    # Verify result properties
    assert isinstance(result, SnapshotVerifyResult)
    assert result.blob_count == 100482
    assert result.processed_count == 289957
    assert result.error_count == 2
    assert len(result.errors) == 2
    assert result.errors[0] == "error processing eran@homepc:C:\\Users\\eran@2025-02-01 01:59:58 IST/AppData/Local/Google/DriveFS/Logs/drive_fs_232.txt: error reading object 5f0e8088163c1b71075bfa540ddacb95: unable to open object 5f0e8088163c1b71075bfa540ddacb95: unexpected content error: invalid checksum at p8dec91ff45a45091b370164a6a27dc89-s6ab50597524a9eca12b offset 8534285 length 36352/36352: decrypt: Error computing ECC: no shard data"
    assert result.errors[1] == "error reading object 5f0e8088163c1b71075bfa540ddacb95: unable to open object 5f0e8088163c1b71075bfa540ddacb95: unexpected content error: invalid checksum at p8dec91ff45a45091b370164a6a27dc89-s6ab50597524a9eca12b offset 8534285 length 36352/36352: decrypt: Error computing ECC: no shard data"
    assert result.timestamp.tzinfo == timezone.utc
    assert result.run_time >= 0

def test_snapshot_verify_no_errors(mocker):
    # Mock response from kopia command
    with open("tests/snapshot_verify_output_no_errors.txt", 'r', encoding="utf-8") as file:
        mock_response = file.read()

    mock_command = mocker.Mock(return_value=mock_response)

    # Initialize API with mock command
    api = KopiaApi("test.config", mock_command)

    # Call the method
    result = api.snapshot_verify(percent=0.5, file_parallelism=5, parallel=5)

    # Verify the mock was called with correct arguments
    mock_command.assert_called_once_with(
        ["snapshot", "verify", "--verify-files-percent=0.5", "--file-parallelism=5", "--parallel=5"],
        json_result=False
    )

    # Verify result properties
    assert isinstance(result, SnapshotVerifyResult)
    assert result.blob_count == 100482
    assert result.processed_count == 310570
    assert result.error_count == 0
    assert len(result.errors) == 0
    assert result.timestamp.tzinfo == timezone.utc
    assert result.run_time >= 0