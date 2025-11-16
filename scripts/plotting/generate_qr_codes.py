"""Generate QR codes for LabLink GitHub repositories for poster."""

import qrcode
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as pdf_backend

# Output directory
OUTPUT_DIR = Path("figures/main")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# GitHub repository URLs
REPOS = {
    "lablink": "https://github.com/talmolab/lablink",
    "lablink-template": "https://github.com/talmolab/lablink-template",
}

def generate_qr_code(url: str, output_path: Path, box_size: int = 20, border: int = 2):
    """
    Generate a high-resolution QR code for poster printing.

    Args:
        url: The URL to encode in the QR code
        output_path: Path to save the QR code image
        box_size: Size of each box in pixels (default 20 for high resolution)
        border: Size of border in boxes (default 2, minimum is 4 per QR spec)
    """
    qr = qrcode.QRCode(
        version=1,  # Auto-adjust size
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction (30%)
        box_size=box_size,
        border=border,
    )

    qr.add_data(url)
    qr.make(fit=True)

    # Create image with high resolution
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)

    print(f"Generated QR code: {output_path}")
    print(f"  URL: {url}")
    print(f"  Size: {img.size}")


def generate_pdf_from_png(png_path: Path, pdf_path: Path):
    """
    Convert PNG QR code to PDF format for poster printing.

    Args:
        png_path: Path to the PNG file
        pdf_path: Path to save the PDF file
    """
    # Read the PNG image
    img = Image.open(png_path)

    # Create a figure with the exact size of the image
    dpi = 300  # High DPI for poster quality
    fig_width = img.size[0] / dpi
    fig_height = img.size[1] / dpi

    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)
    ax.imshow(img, cmap='gray')
    ax.axis('off')

    # Remove all margins and padding
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0, hspace=0)

    # Save as PDF
    plt.savefig(pdf_path, format='pdf', dpi=dpi, bbox_inches='tight', pad_inches=0)
    plt.close()

    print(f"Generated PDF: {pdf_path}")


def main():
    """Generate QR codes for all repositories."""
    for repo_name, url in REPOS.items():
        # Generate PNG
        png_path = OUTPUT_DIR / f"qr_{repo_name}.png"
        generate_qr_code(url, png_path)

        # Generate PDF
        pdf_path = OUTPUT_DIR / f"qr_{repo_name}.pdf"
        generate_pdf_from_png(png_path, pdf_path)
        print()


if __name__ == "__main__":
    main()
