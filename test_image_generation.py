"""
Test image insertion in PPT
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tech_report_agent.ppt_generator import generate_ppt


def test_image_slide():
    """Test image slide generation"""
    print("Testing image slide...")
    
    # Create a simple test image (1x1 pixel PNG)
    test_image_dir = Path(__file__).parent / "test_output" / "images"
    test_image_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a simple test image using PIL if available
    try:
        from PIL import Image
        img = Image.new('RGB', (800, 600), color=(52, 73, 94))
        img.save(test_image_dir / "test_image.png")
        print(f"Created test image: {test_image_dir / 'test_image.png'}")
        has_test_image = True
    except ImportError:
        print("PIL not available, skipping local image test")
        has_test_image = False
    
    ppt_structure = {
        "slides": [
            {
                "slide_number": 1,
                "type": "title",
                "title": "Image Test",
                "content": ["PPT Image Insertion Test", "InsightForge 2026"]
            },
            {
                "slide_number": 2,
                "type": "image",
                "title": "Architecture Diagram",
                "image": str(test_image_dir / "test_image.png") if has_test_image else "https://via.placeholder.com/800x600/34495e/ffffff?text=Architecture+Diagram",
                "content": [
                    "Core components of the system",
                    "Data flows from input to output"
                ]
            },
            {
                "slide_number": 3,
                "type": "image",
                "title": "URL Image Test",
                "image": {
                    "path": "https://via.placeholder.com/800x400/1a1a2e/e94560?text=Sora+Architecture",
                    "alt_text": "Sora Architecture Diagram",
                    "position": "center",
                    "width": 10.0,
                    "height": 5.0
                },
                "content": [
                    "Diffusion Transformer (DiT) architecture",
                    "Spacetime patches for video processing"
                ]
            },
            {
                "slide_number": 4,
                "type": "diagram",
                "title": "Value Chain Transformation",
                "image": "https://via.placeholder.com/900x500/27ae60/ffffff?text=Value+Chain+Before+and+After+Sora",
                "content": [
                    "Traditional: 8 steps",
                    "Sora-enabled: 4 steps",
                    "50% reduction in process complexity"
                ]
            },
            {
                "slide_number": 5,
                "type": "closing",
                "title": "Thank You",
                "content": ["Image Test Complete"]
            }
        ]
    }
    
    output_path = Path(__file__).parent / "test_output" / "presentations" / "test_images.pptx"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    result = generate_ppt(ppt_structure, output_path, theme="tech_blue")
    print(f"Generated: {result}")
    return result


if __name__ == "__main__":
    print("=" * 60)
    print("  PPT Image Insertion Test")
    print("=" * 60)
    
    try:
        test_image_slide()
        print("\n" + "=" * 60)
        print("  Test passed!")
        print("=" * 60)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()