"""Tests for QR code generation."""

import pytest
from pathlib import Path
from PIL import Image
import qrcode


@pytest.fixture
def qr_output_dir():
    """Get the QR code output directory."""
    return Path("figures/main")


@pytest.fixture
def expected_qr_codes():
    """Expected QR code files and their URLs."""
    return {
        "qr_lablink.png": "https://github.com/talmolab/lablink",
        "qr_lablink-template.png": "https://github.com/talmolab/lablink-template",
    }


def test_qr_code_files_exist(qr_output_dir, expected_qr_codes):
    """Test that QR code PNG files were generated."""
    for filename in expected_qr_codes.keys():
        file_path = qr_output_dir / filename
        assert file_path.exists(), f"QR code file {filename} not found"


def test_qr_code_pdfs_exist(qr_output_dir, expected_qr_codes):
    """Test that QR code PDF files were generated."""
    for filename in expected_qr_codes.keys():
        pdf_filename = filename.replace('.png', '.pdf')
        pdf_path = qr_output_dir / pdf_filename
        assert pdf_path.exists(), f"QR code PDF {pdf_filename} not found"


def test_qr_code_dimensions(qr_output_dir, expected_qr_codes):
    """Test that QR codes have expected dimensions."""
    for filename in expected_qr_codes.keys():
        file_path = qr_output_dir / filename
        img = Image.open(file_path)

        # QR codes should be at least 100x100 pixels
        assert img.size[0] >= 100, f"{filename} width too small"
        assert img.size[1] >= 100, f"{filename} height too small"

        # QR codes should be square
        assert img.size[0] == img.size[1], f"{filename} is not square"


def test_qr_code_format(qr_output_dir, expected_qr_codes):
    """Test that QR codes are valid images."""
    for filename in expected_qr_codes.keys():
        file_path = qr_output_dir / filename
        img = Image.open(file_path)

        # Should be a valid image mode
        assert img.mode in ['1', 'L', 'RGB', 'RGBA'], f"{filename} has invalid image mode"


def test_qr_code_generation_consistency(expected_qr_codes):
    """Test that regenerating QR codes produces consistent results."""
    for url in expected_qr_codes.values():
        qr1 = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=20,
            border=2,
        )
        qr1.add_data(url)
        qr1.make(fit=True)
        img1 = qr1.make_image(fill_color="black", back_color="white")

        qr2 = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=20,
            border=2,
        )
        qr2.add_data(url)
        qr2.make(fit=True)
        img2 = qr2.make_image(fill_color="black", back_color="white")

        # Same dimensions
        assert img1.size == img2.size, f"Inconsistent QR code size for {url}"


def test_qr_code_file_sizes(qr_output_dir, expected_qr_codes):
    """Test that QR code files have reasonable sizes."""
    for filename in expected_qr_codes.keys():
        file_path = qr_output_dir / filename
        file_size = file_path.stat().st_size

        # PNG should be between 100 bytes and 100KB
        assert 100 < file_size < 100_000, f"{filename} has unexpected file size: {file_size}"

        # PDF should exist and be larger than 100 bytes
        pdf_path = qr_output_dir / filename.replace('.png', '.pdf')
        pdf_size = pdf_path.stat().st_size
        assert pdf_size > 100, f"PDF {pdf_path.name} is too small: {pdf_size}"
