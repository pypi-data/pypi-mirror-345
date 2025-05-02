# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
# --------------------------------------------------------------------------------------------

from .exceptions import (
    ImageMetadataDeserializationError,
    ImageMetadataSerializationError,
)
from .image_metadata import ImageMetadata
from .metadata_sections.identity import ImageType
from .metadata_sections import SignatureSection
from .signing.app_development import AppDevelopmentSigner
from .signing.der_encoded import DEREncodedSignature
from .signing.signer import SigningType, Signer
from hashlib import sha256
from typing import Optional, List, Tuple
from .metadata_sections.compression import CompressionType

_KNOWN_SIGNERS = [AppDevelopmentSigner()]


class ImageCompressorDecompressor:
    def __init__():
        pass

    def compress(
        self,
        data: bytearray,
        # default to invalid compression type
        compression_type: CompressionType = CompressionType(None),
    ) -> bytearray:
        raise NotImplementedError(
            "Compress is not implemented in this class. Please subclass and implement compress/decompress"
        )

    def decompress(
        self,
        data: bytearray,
        # default to invalid compression type
        compression_type: CompressionType = CompressionType(None),
    ) -> bytearray:
        raise NotImplementedError(
            "Decompress is not implemented in this class. Please subclass and implement compress/decompress"
        )


class Image:
    def __init__(
        self,
        data: Optional[bytearray] = None,
        compressor: Optional[ImageCompressorDecompressor] = None,
    ):
        """
        Creates an Image object from the data (if provided).
        @param data: The image data to be deserialized. If None, the object will be created with no data.
        @param compressor: The optional compressor to be used for compressing/decompressing the image data.
                           If compressor is provided, the image will be automatically compressed/decompressed
                           during serialization and deserialization.
        """
        self.signature = None
        self.data = data
        self.metadata = ImageMetadata(None)
        self.compressor = compressor

        if data is not None:
            self.deserialize(data)

    def _verify_signature(self, with_signer: Signer):
        der_encoded = DEREncodedSignature.from_stored_signature(self.signature)

        return with_signer.verify(
            der_encoded,
            sha256(self.data + self.metadata.serialize()).digest(),
        )

    def has_valid_signature(self, known_signers: List[Signer] = _KNOWN_SIGNERS) -> bool:
        """
        Iterates over the provided list of signers `known_signers` until the signature is correctly verified.

        @returns True if the signature belongs to any of the `known_signers`
        """
        # no signature
        if len(self.signature) == 0:
            return False

        for signer in known_signers:
            result = self._verify_signature(signer)
            if result:
                return True

        return False

    def resolve_signer_and_type(
        self, known_signers: List[Signer] = _KNOWN_SIGNERS
    ) -> Tuple[Optional[Signer], Optional[SigningType]]:
        """
        Iterates over the provided list of signers `known_signers` until the signature is correctly verified.

        @returns If matched, returns the matching signer and signing type. Otherwise returns the tuple: None,None
        """
        signature = self.metadata.signature
        INVALID_SIG_RESULT = None, None

        if signature is None:
            return INVALID_SIG_RESULT

        sign_type = signature.signing_type.signing_type

        if sign_type == SigningType.Invalid:
            return INVALID_SIG_RESULT

        for signer in known_signers:
            result = self._verify_signature(signer)

            if result:
                return signer, sign_type

        return INVALID_SIG_RESULT

    def as_bytes(
        self,
        signer=AppDevelopmentSigner(),
        include_signature=False,
        fixed_size=None,
        signing_type: SigningType = SigningType.ECDsa256,
    ):
        """
        Serializes the current image and metadata to a byte array.

        If `include_signature` is True, the returned bytes will have a signature appended and the SignatureSection within the metadata
        will be rewritten per the provided `signer` and `signing_type`.

        If `include_signature` is False, the current metadata and image data will be returned without a signature. This output cannot be
        parsed again by this library as metadata is only valid with a signature.
        """
        new_data = self.data

        # Pad the data to a multiple of 4 bytes
        if len(new_data) % 4 != 0:
            new_data += b"\0" * (4 - len(new_data) % 4)

        if include_signature:
            self.metadata.remove_section(self.metadata.signature)

            # add a new signature metadata section from the provided signer
            new_sig_metadata = SignatureSection()
            new_sig_type = SigningType(None)

            new_sig_metadata.signing_cert_thumbprint = bytes(
                signer.thumbprint(signing_type=signing_type), encoding="utf-8"
            )

            new_sig_type.signing_type = signing_type
            new_sig_metadata.signing_type = new_sig_type

            self.metadata.add_section(new_sig_metadata)

        # 1BL special case when metadata does not specify fixed size, leave space for info structure
        # This will be the case of older 1BLs that did not have fixed size in their metadata
        if (
            fixed_size is None
            and self.metadata.identity is not None
            and self.metadata.identity.image_type == ImageType.OneBL
        ):
            fixed_size = 16 * 1024

        metadata_bytes = self.metadata.serialize()

        new_data += metadata_bytes
        total_size = len(new_data)

        if include_signature:
            # add the default signature size
            # note: as far can be determined, the only signature size in use is 64 bytes
            total_size += DEREncodedSignature.size()

        # if fixed_size is provided, then the file size must match the provided size.
        # the total file size is: data + metadata + signature
        # if the fixed size is smaller than the total size, then an exception is thrown
        if fixed_size is not None:
            if fixed_size < total_size:
                raise ImageMetadataSerializationError(
                    "Fixed size is smaller than the current file size. Will not shrink file content."
                )
            else:
                new_data += b"\0" * (fixed_size - total_size)

        if include_signature:
            self.signature = DEREncodedSignature.to_stored_signature(
                signer.sign_data(new_data, signing_type=signing_type)
            )
        else:
            self.signature = b""

        return new_data + self.signature

    def is_compressed(self):
        return (
            # if we have compression info
            self.metadata.compression_info is not None
            # and its size is not equal to the uncompressed size
            and self.metadata.compression_info.uncompressed_size != len(self.data)
            # the image is compressed!
        )

    def _decompress(self):
        if self.metadata.compression_info is not None and self.compressor is not None:
            if self.metadata.identity is None:
                raise ValueError("Provided image does not have an identity section!")

            if self.metadata.compression_info.uncompressed_size <= 0:
                raise ValueError(
                    f"Image has invalid uncompressed size: {self.metadata.compression_info.uncompressed_size}"
                )

            self.data = self.compressor.decompress(
                self.data, self.metadata.compression_info.compression_type
            )

            if len(self.data) != self.metadata.compression_info.uncompressed_size:
                raise ValueError(
                    f"Decompressed data size does not match uncompressed size: {len(self.data)} != {self.metadata.compression_info.uncompressed_size}"
                )

    def _compress(self):
        if self.metadata.compression_info is not None and self.compressor is not None:
            if self.metadata.identity is None:
                raise ValueError("Provided image does not have an identity section!")

            if self.metadata.compression_info.uncompressed_size <= 0:
                raise ValueError(
                    f"Image has invalid uncompressed size: {self.metadata.compression_info.uncompressed_size}"
                )

            self.data = self.compressor.compress(
                self.data, self.metadata.compression_info.compression_type
            )

    def deserialize(self, data):
        self.metadata = ImageMetadata(data)

        self.data = data[: self.metadata.start_of_metadata]
        self.signature = data[-self.metadata.signature_size :]

        self._decompress()

    def serialize(
        self,
        signer=AppDevelopmentSigner(),
        include_signature=True,
        fixed_size=None,
        signing_type: SigningType = SigningType.ECDsa256,
    ):
        self._compress()
        return self.as_bytes(
            signer, include_signature, fixed_size, signing_type=signing_type
        )
