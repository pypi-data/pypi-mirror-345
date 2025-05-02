# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import uuid
from azuresphere_imagemetadata.image import Image
from azuresphere_imagemetadata.metadata_sections.abi import (
    ABIProvidesSection,
    ABIDependsSection,
)
from azuresphere_imagemetadata.metadata_sections.compression import CompressionSection
from azuresphere_imagemetadata.metadata_sections.debug import DebugSection
from azuresphere_imagemetadata.metadata_sections.identity import IdentitySection
from azuresphere_imagemetadata.metadata_sections.image_policy import ImagePolicySection
from azuresphere_imagemetadata.metadata_sections.required_offset import (
    RequiredOffsetSection,
)
from azuresphere_imagemetadata.metadata_sections.revocation import RevocationSection
from azuresphere_imagemetadata.metadata_sections.signature import SignatureSection
from azuresphere_imagemetadata.metadata_sections.temporary_image import (
    TempImageMetadataSection,
)

from azuresphere_imagemetadata.metadata_sections.compression import CompressionType
from lzma import LZMACompressor, LZMADecompressor, FORMAT_ALONE

IMAGEPACKAGE_PATH = os.path.join(
    ".", "tests", "test_files", "applications", "HelloWorld_HighLevelApp.imagepackage"
)

COMPRESSED_SAMPLE_APP = os.path.join(
    ".", "tests", "test_files", "compressed", "io-hello-world-update.bin.lzma"
)

class LZMACompressorDecompressor:

    def compress(self, data: bytearray, compression_type: CompressionType) -> bytearray:
        assert compression_type.compression_type == CompressionType.Lzma, "Only LZMA is supported"
        lzma_compressor = LZMACompressor(format=FORMAT_ALONE)
        return lzma_compressor.compress(data) + lzma_compressor.flush()

    def decompress(self, data: bytearray, compression_type: CompressionType) -> bytearray:
        assert compression_type.compression_type == CompressionType.Lzma, "Only LZMA is supported"
        lzma_decompressor = LZMADecompressor(format=FORMAT_ALONE)
        return lzma_decompressor.decompress(data)


def test_known_guids(test_logger):
    logger = test_logger()
    logger.info("Beginning test_known_guids")

    with open(IMAGEPACKAGE_PATH, "rb") as f:
        image = Image(f.read())
        assert (
            image.metadata.identity.image_uid == "3b912ace-ecd2-49a5-ab84-9de7521106e9"
        )
        assert (
            image.metadata.identity.component_uid
            == "1689d8b2-c835-2e27-27ad-e894d6d15fa9"
        )


def test_update_uids(test_logger):
    logger = test_logger()
    logger.info("Beginning test_update_uids")

    with open(IMAGEPACKAGE_PATH, "rb") as f:
        image = Image(f.read())
        set_uuid = uuid.uuid4()
        image.metadata.identity.image_uid = set_uuid.hex
        assert image.metadata.identity.image_uid.replace("-", "") == set_uuid.hex

        set_uuid = uuid.uuid4()
        image.metadata.identity.component_uid = set_uuid.hex
        assert image.metadata.identity.component_uid.replace("-", "") == set_uuid.hex


def test_serialize_fixed_size(test_logger):
    logger = test_logger()
    logger.info("Beginning test_serialize_fixed_size")

    file_len = os.path.getsize(IMAGEPACKAGE_PATH)
    new_file = IMAGEPACKAGE_PATH + ".new"

    with open(IMAGEPACKAGE_PATH, "rb") as f:
        image = Image(f.read())

        with open(new_file, "wb") as f:
            f.write(image.serialize(fixed_size=file_len + 8096))

    assert os.path.getsize(new_file) == file_len + 8096


def test_deserialization(test_logger):
    logger = test_logger()
    logger.info("Beginning test_deserialization")

    with open(IMAGEPACKAGE_PATH, "rb") as f:
        image = Image(f.read())

        assert image.metadata is not None
        assert image.signature is not None
        assert image.data is not None
        assert image.metadata.signature_size == len(image.signature)

    logger.info("Finishing test_deserialization")


def test_serialization(test_logger):
    logger = test_logger()
    logger.info("Beginning test_serialization")

    with open(IMAGEPACKAGE_PATH, "rb") as f:
        data = f.read()
        image = Image(data)

        # check all sections serialize the same way they are parsed
        for s in image.metadata.sections:
            assert s.serialize() in data

        new_data = image.serialize(include_signature=False)
        original_data_no_sig = data[: -image.metadata.signature_size]
        assert len(original_data_no_sig) == len(new_data)

        assert original_data_no_sig == new_data
    logger.info("Finishing test_serialization")


def test_section_serialization(test_logger):
    logger = test_logger()
    logger.info("Beginning test_section_serialization")
    # all sections should handle no data parameter
    # and should produce serialized data the same length as their size
    sections = [
        ABIProvidesSection(),
        ABIDependsSection(),
        CompressionSection(),
        DebugSection(),
        IdentitySection(),
        ImagePolicySection(),
        RequiredOffsetSection(),
        RevocationSection(),
        SignatureSection(),
        TempImageMetadataSection(),
    ]

    for sec in sections:
        assert sec.serialize() is not None
        assert len(sec.serialize()) == sec.size()
    logger.info("Finishing test_section_serialization")


def test_open_compressed_no_compressor(test_logger):
    logger = test_logger()
    logger.info("Beginning test_open_compressed_no_compressor")

    with open(COMPRESSED_SAMPLE_APP, "rb") as f:
        image = Image(f.read())
        assert image.metadata.compression_info is not None
        assert image.is_compressed() is True

    logger.info("Finishing test_open_compressed_no_compressor")

def test_open_compressed_with_compressor(test_logger):
    logger = test_logger()
    logger.info("Beginning test_open_compressed_with_compressor")

    with open(COMPRESSED_SAMPLE_APP, "rb") as f:
        image = Image(f.read(), compressor=LZMACompressorDecompressor())
        assert image.metadata.compression_info is not None
        assert image.metadata.compression_info.uncompressed_size == len(image.data)
        assert image.is_compressed() is False

    logger.info("Finishing test_open_compressed_with_compressor")

def test_open_compressed_with_compressor_check_compressed(test_logger):
    logger = test_logger()
    logger.info("Beginning test_open_compressed_with_compressor_check_compressed")

    with open(COMPRESSED_SAMPLE_APP, "rb") as f:
        image = Image(f.read(), compressor=LZMACompressorDecompressor())
        assert image.metadata.compression_info is not None
        assert image.metadata.compression_info.uncompressed_size == len(image.data)
        assert image.is_compressed() is False
        image.serialize()
        assert image.is_compressed() is True
    logger.info("Finishing test_open_compressed_with_compressor_check_compressed")


def test_decompress_compress(test_logger):
    logger = test_logger()
    logger.info("Beginning test_decompress_compress")

    new_name = COMPRESSED_SAMPLE_APP + ".new"

    with open(COMPRESSED_SAMPLE_APP, "rb") as f:
        image = Image(f.read(), compressor=LZMACompressorDecompressor())

        assert image.metadata.compression_info is not None
        uncompressed_size = image.metadata.compression_info.uncompressed_size

        with open(new_name, "wb") as f:
            f.write(image.serialize())

        with open(new_name, "rb") as f:
            new_image = Image(f.read(), compressor=LZMACompressorDecompressor())

            assert len(new_image.data) == uncompressed_size

    logger.info("Finishing test_decompress_compress")

