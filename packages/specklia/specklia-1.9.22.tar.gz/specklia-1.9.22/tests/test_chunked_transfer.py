"""Unit tests for chunked_transfer.py."""
from http import HTTPStatus
import struct
from unittest.mock import call, MagicMock, patch

import pandas as pd

from specklia import chunked_transfer


def test_split_into_chunks():
    assert chunked_transfer.split_into_chunks(b'abcdefghijklmnop', chunk_size=5) == [
        (1, b'abcde'), (2, b'fghij'), (3, b'klmno'), (4, b'p')]


def test_merge_from_chunks():
    assert chunked_transfer.merge_from_chunks([
        (1, b'abcde'), (2, b'fghij'), (3, b'klmno'), (4, b'p')]) == b'abcdefghijklmnop'


def test_upload_chunks():
    with patch('specklia.chunked_transfer.requests.post') as mock_post:
        mock_post.return_value.status_code = HTTPStatus.OK
        mock_post.return_value.json.return_value = {'chunk_set_uuid': 'cheese'}

        assert chunked_transfer.upload_chunks(
            api_address='wibble', chunks=[(1, b'a'), (2, b'b')], logger=MagicMock(name="mock_logger")) == 'cheese'

        mock_post.assert_has_calls([
            call('wibble/chunk/upload/1-of-2', data=b'a'),
            call().json(),
            call().json(),
            call('wibble/chunk/upload/cheese/2-of-2', data=b'b')])


def test_download_chunks():
    with patch('specklia.chunked_transfer.requests.get') as mock_get:
        mock_get.side_effect = [
            MagicMock(name="mock_response_1", status_code=HTTPStatus.OK, content=struct.pack('i', 1) + b'wibble'),
            MagicMock(name="mock_response_2", status_code=HTTPStatus.OK, content=struct.pack('i', 2) + b'wobble'),
            MagicMock(name="mock_response_3", status_code=HTTPStatus.NO_CONTENT, content=b'')]

        assert chunked_transfer.download_chunks(
            api_address='wibble', chunk_set_uuid='rawr', logger=MagicMock(name="mock_logger")) == [
            (1, b'wibble'), (2, b'wobble')]


def test_serialise_dataframe_roundtrip():
    df = pd.DataFrame({'a': [1, 1, 2, 3], 'b': ['alfred', 'dave', 'ken', 'sally'], 'c': [1, 2, 4, 4.4]})

    pd.testing.assert_frame_equal(
        df, chunked_transfer.deserialise_dataframe(chunked_transfer.serialise_dataframe(df)))
