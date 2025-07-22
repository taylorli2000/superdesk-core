# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import os
from typing import Any
from hachoir.stream import InputIOStream
from hachoir.parser import guessParser
from hachoir.metadata import extractMetadata
from flask import json
import logging
from superdesk.media.image import PhotoMetadata


logger = logging.getLogger(__name__)


def get_meta(filestream):
    metadata = {}

    try:
        filestream.seek(0)
        stream = InputIOStream(filestream, None, tags=[])
        parser = guessParser(stream)
        if not parser:
            return metadata

        tags = extractMetadata(parser).exportPlaintext(human=False, line_prefix="")
        for text in tags:
            try:
                json.dumps(text)
                key, value = text.split(":", maxsplit=1)
                key, value = key.strip(), value.strip()
                if key and value:
                    metadata.update({key: value})
            except Exception as ex:
                logger.exception(ex)
    except Exception as ex:
        logger.exception(ex)
        return metadata
    return metadata


def write_meta(input: bytes, metadata: PhotoMetadata):
    """
    write XMP metadata to video

    @param input: bytes
    @param metadata: PhotoMetadata
    """

    exiftool_args = convert_xmp_to_args(get_xmp_tags(metadata))
    return write_xmp_with_exiftool(input, exiftool_args)

def get_xmp_tags(metadata: PhotoMetadata):
    """
    get XMP tags for exiftool

    @param metadata: PhotoMetadata
    """
    xmp = {
        "Description": metadata.get("Description"),
        "CaptionWriter": metadata.get("DescriptionWriter"),
        "Headline": metadata.get("Headline"),
        "Instructions": metadata.get("Instructions"),
        "TransmissionReference": metadata.get("JobId"),
        "Title": metadata.get("Title"),
        "Creator": metadata.get("Creator"),
        "AuthorsPosition": metadata.get("CreatorsJobtitle"),
        "Rights": metadata.get("CopyrightNotice"),
        "City": metadata.get("City"),
        "Country": metadata.get("Country"),
        "CountryCode": metadata.get("CountryCode"),
        "Credit": metadata.get("CreditLine"),
        "State": metadata.get("ProvinceState"),
    }
    xmp = {k: v for k, v in xmp.items() if v}
    return xmp

def convert_xmp_to_args(xmp: dict[str, Any]):
    """
    convert XMP tags to exiftool args

    @param xmp: dict[str, Any]
    """
    args = [f"-{key}={value}" for key, value in xmp.items()]
    args.append("-overwrite_original")
    return args

def write_xmp_with_exiftool(original: bytes, args: dict[str, Any]):
    """
    write xmp tags to temp file using exiftool

    @param original: bytes
    @param args: dict[str, Any]
    """

    import tempfile
    from exiftool import ExifToolHelper
    from exiftool.exceptions import ExifToolExecuteError

    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(original)
        temp.flush()
        temp_path = temp.name

    try:
        with ExifToolHelper() as et:
            et.execute(*args, temp_path)

        with open(temp_path, "rb") as updated:
            return updated.read()
    except ExifToolExecuteError as e:
        logger.exception(e.stderr)
        return original
    finally:
        os.remove(temp_path)
    