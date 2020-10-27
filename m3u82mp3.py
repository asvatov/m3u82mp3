# -*- coding: utf-8 -*-

"""Converter m3u8 audio stream to mp3 file.

Parse all audio sources chunks, decrypt data, collect it and save as complete audio file.

Example:
    You can use module as a script

        $ python m3u82mp3.py -i input.m3u8 -o output.mp3

.. _Github page:
   https://github.com/asvatov/m3u82mp3

"""

import argparse
import os
import binascii
import m3u8
import sys

from Crypto.Cipher import AES
from urllib.parse import urlparse
from urllib.request import urlopen


def is_valid(url, qualifying=None):
    """Check if string arg `url` is a legit url.

    Args:
        url (str): String argument to be checked.
        qualifying (iterable): Optional variable, that contains iterable object with desired strings to be found
            in parsed url string. By default it is 'scheme' and 'netloc'.

    Returns:
        Boolean value if argument `url` seems like a legit url.
    """

    min_attributes = ('scheme', 'netloc')

    qualifying = qualifying or min_attributes
    token = urlparse(url)

    return all([getattr(token, qualifying_attr)
                for qualifying_attr in qualifying])


def read_bytes(path, silent = True):
    """Read bytes from a file.

    Args:
        path (str): File path can be both url and local os path.

    Returns:
        Bytes content of the file.
    """

    content = b""

    is_url = is_valid(path)
    if is_url:
        if not silent:
            print(path)
        data_response = urlopen(path)
        content = data_response.read()
    else:
        with open(path, "rb") as fp:
            content = fp.read()

    return content


def save_converted_mp3(output, content):
    """Save mp3 file from bytes.

    Args:
        output (file object): File path to save.
        content (bytes): Bytes content to write.

    Raises:
        TypeError: An error occurred trying to write None to mp3 file.
    """

    if content is None:
        raise TypeError("Empty mp3 content to save.")

    output.write(content)


def get_host_uri(m3u8_obj):
    """Save mp3 file from bytes.

    Args:
        m3u8_obj (M3U8 obj): M3U8 object that contains parsed data from m3u8 file.

    Returns:
        Host URI string of audio chunks from m3u8 file. None if this data is missed.
    """

    host_uri = None

    media_sequence = m3u8_obj.media_sequence

    for i in range(media_sequence):
        try:
            key_uri = m3u8_obj.keys[i].uri
            host_uri = "/".join(key_uri.split("/")[:-1])

            return host_uri
        except AttributeError:
            continue

    return host_uri


def get_ts_from_m3u8(input, host_uri=None):
    """Get audio bytes from stream audio file `m3u8_filepath`.

    Iterate through all audio sources chunks, read data, decrypt it if needed and return full audio bytes.

    Args:
        m3u8_filepath (file object): File path to m3u8 file.
        host_uri (str): Optional variable, that contains host of all audio chunks sources from m3u8 file.

    Returns:
        Audio bytes of complete audio file.

    Raises:
        ValueError: An error occurred trying to load m3u8 object from file `m3u8_filepath`.
        TypeError: An error occurred if base URI is not set.
    """

    m3u8_obj = m3u8.loads(input.read())
    media_sequence = m3u8_obj.media_sequence

    host_uri = host_uri or get_host_uri(m3u8_obj)
    if host_uri is None:
        raise TypeError("Host URL is not set.")

    ts_content = b""
    key = None

    for i, segment in enumerate(m3u8_obj.segments):
        decrypt_func = lambda x: x

        if segment.key.method == "AES-128":
            if not key:
                key_uri = segment.key.uri
                key = read_bytes(key_uri)

            ind = i + media_sequence
            iv = binascii.a2b_hex('%032x' % ind)
            cipher = AES.new(key, AES.MODE_CBC, iv=iv)
            decrypt_func = cipher.decrypt

        ts_url = os.path.join(host_uri, segment.uri)
        data = read_bytes(ts_url)
        ts_content += decrypt_func(data)

    return ts_content


def convert(input, output):
    """Get mp3 file from m3u8 audio stream and save it to file system.

    Args:
        input (file object): IO to read m3u8 from.
        output (file object): IO to write mp3 into.

    Raises:
        ValueError: An error occurred trying to load m3u8 object from file `input`.
        TypeError: An error occurred if base URI is not set.
    """

    ts_bytes = get_ts_from_m3u8(input)
    save_converted_mp3(output, ts_bytes)


def parse_command_line_args():
    """Parse command line to retrieve file paths to input and output files.

    Returns:
        input_filepath (str): File path to input m3u8 file.
        output_filepath (str): File path to outpur mp3 file.
    """

    ap = argparse.ArgumentParser(description='Command line converter from input_file.m3u8 to output_file.mp3',
                                 epilog="That's all folks")
    ap.add_argument("-i", "--input", required=False,
                    help="path to input m3u8 file to be converted")
    ap.add_argument("-o", "--output", required=False,
                    help="path to output mp3 file")
    args = vars(ap.parse_args())

    input_filepath = args["input"]
    output_filepath = args["output"]

    return input_filepath, output_filepath


def run_from_cmd():
    """Run converter from command line."""

    input_filepath, output_filepath = parse_command_line_args()

    if input_filepath:
        input = open(input_filepath, 'r')
    else:
        input = sys.stdin

    if output_filepath:
        output = open(output_filepath, 'wb')
    else:
        output = sys.stdout.buffer

    convert(input, output)


if __name__ == "__main__":
    run_from_cmd()
