"""
PPT Generator Module
Generates .pptx files from JSON structure using python-pptx.
"""

import json
from pathlib import Path
from typing import Any
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE


def _fix_unescaped_quotes(json_str: str) -> str:
    """
    Fix unescaped quotes inside JSON string values.
    This is a heuristic approach - we try to identify quotes that are likely
    inside string values (not JSON delimiters) and escape them.
    """
    result = []
    in_string = False
    escape_next = False
    
    i = 0
    while i < len(json_str):
        c = json_str[i]
        
        if escape_next:
            result.append(c)
            escape_next = False
            i += 1
            continue
            
        if c == '\\':
            result.append(c)
            escape_next = True
            i += 1
            continue
            
        if c == '"':
            if not in_string:
                # Starting a string
                in_string = True
                result.append(c)
            else:
                # We're in a string and see a quote
                # Check if this looks like an internal quote or string end
                # Look ahead: if next non-space char is : or , or } or ], it's likely string end
                rest = json_str[i+1:].lstrip()
                if rest and rest[0] in ':,}]':
                    # This is likely the end of the string
                    in_string = False
                    result.append(c)
                else:
                    # This is likely an internal quote - escape it
                    result.append('\\"')
            i += 1
            continue
        
        result.append(c)
        i += 1
    
    return ''.join(result)


class PPTGenerator:
    """Generate PowerPoint presentations from JSON structure."""

    # Color scheme (Tech Blue Professional Style)
    COLORS = {
        "primary": RGBColor(0, 82, 147),      # Deep Blue
        "secondary": RGBColor(0, 120, 215),    # Light Blue
        "accent": RGBColor(255, 153, 0),       # Orange Accent
        "text_dark": RGBColor(51, 51, 51),     # Dark Gray Text
        "text_light": RGBColor(255, 255, 255), # White Text
        "bg_light": RGBColor(240, 248, 255),   # Light Blue Background
    }

    SLIDE_TYPES = {
        "title": "_create_title_slide",
        "agenda": "_create_content_slide",
        "key_findings": "_create_content_slide",
        "methodology": "_create_content_slide",
        "analysis": "_create_content_slide",
        "diagram": "_create_content_slide",
        "chart": "_create_content_slide",
        "conclusion": "_create_content_slide",
        "recommendations": "_create_content_slide",
        "closing": "_create_closing_slide",
    }

    def __init__(self, theme: str = "tech_blue"):
        self.theme = theme
        self.prs = Presentation()
        self.prs.slide_width = Inches(13.333)  # 16:9 Widescreen
        self.prs.slide_height = Inches(7.5)

    def generate(self, ppt_structure: dict | str, output_path: str | Path) -> str:
        """
        Generate PPT from JSON structure.

        Args:
            ppt_structure: JSON structure dict or path to JSON file
            output_path: Output path for the .pptx file

        Returns:
            Path to generated PPT file
        """
        # Load structure if path provided
        if isinstance(ppt_structure, str):
            with open(ppt_structure, "r", encoding="utf-8") as f:
                content = f.read()
            # Remove markdown code block markers if present
            if content.startswith("```"):
                # Find the end of the first line
                first_newline = content.find("\n")
                if first_newline != -1:
                    content = content[first_newline + 1:]
            if content.rstrip().endswith("```"):
                # Remove trailing ``` marker
                content = content.rstrip()[:-3].rstrip()
            # Fix unescaped quotes in JSON
            content = _fix_unescaped_quotes(content)
            try:
                ppt_structure = json.loads(content)
            except json.JSONDecodeError as e:
                # Try to extract JSON from content
                import re
                # Find JSON object boundaries
                match = re.search(r'\{[\s\S]*\}', content)
                if match:
                    try:
                        ppt_structure = json.loads(match.group())
                    except:
                        raise ValueError(f"Failed to parse JSON structure: {e}")
                else:
                    raise ValueError(f"No valid JSON found in file: {e}")

        # Validate structure
        if "slides" not in ppt_structure:
            raise ValueError("Invalid PPT structure: missing 'slides' key")

        # Create slides
        for slide_data in ppt_structure["slides"]:
            self._create_slide(slide_data)

        # Save presentation
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.prs.save(str(output_path))

        return str(output_path)

    def _create_slide(self, slide_data: dict) -> None:
        """Create a single slide based on type."""
        slide_type = slide_data.get("type", "content")
        method_name = self.SLIDE_TYPES.get(slide_type, "_create_content_slide")
        method = getattr(self, method_name)
        method(slide_data)

    def _create_title_slide(self, slide_data: dict) -> None:
        """Create title slide (cover page)."""
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])  # Blank

        # Add background shape
        shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, 0, 0, self.prs.slide_width, self.prs.slide_height
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = self.COLORS["primary"]
        shape.line.fill.background()

        # Add title
        content = slide_data.get("content", [])
        if content:
            title_box = slide.shapes.add_textbox(
                Inches(0.5), Inches(2.5), Inches(12.333), Inches(1.5)
            )
            tf = title_box.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = content[0]
            p.font.size = Pt(44)
            p.font.bold = True
            p.font.color.rgb = self.COLORS["text_light"]
            p.alignment = PP_ALIGN.CENTER

            # Subtitle
            if len(content) > 1:
                p = tf.add_paragraph()
                p.text = content[1]
                p.font.size = Pt(24)
                p.font.color.rgb = self.COLORS["text_light"]
                p.alignment = PP_ALIGN.CENTER

            # Footer
            if len(content) > 2:
                footer_box = slide.shapes.add_textbox(
                    Inches(0.5), Inches(6), Inches(12.333), Inches(0.5)
                )
                tf = footer_box.text_frame
                p = tf.paragraphs[0]
                p.text = content[2]
                p.font.size = Pt(14)
                p.font.color.rgb = self.COLORS["text_light"]
                p.alignment = PP_ALIGN.CENTER

    def _create_content_slide(self, slide_data: dict) -> None:
        """Create content slide with title and bullet points."""
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])  # Blank

        # Add header bar
        header = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, 0, 0, self.prs.slide_width, Inches(1.2)
        )
        header.fill.solid()
        header.fill.fore_color.rgb = self.COLORS["primary"]
        header.line.fill.background()

        # Add title
        title = slide_data.get("title", "")
        if title:
            title_box = slide.shapes.add_textbox(
                Inches(0.5), Inches(0.25), Inches(12.333), Inches(0.7)
            )
            tf = title_box.text_frame
            p = tf.paragraphs[0]
            p.text = title
            p.font.size = Pt(32)
            p.font.bold = True
            p.font.color.rgb = self.COLORS["text_light"]

        # Add content
        content = slide_data.get("content", [])
        if content:
            content_box = slide.shapes.add_textbox(
                Inches(0.7), Inches(1.5), Inches(11.933), Inches(5.5)
            )
            tf = content_box.text_frame
            tf.word_wrap = True

            for i, item in enumerate(content):
                if i == 0:
                    p = tf.paragraphs[0]
                else:
                    p = tf.add_paragraph()
                
                # Use bullet character
                p.text = "\u2022 " + item
                p.font.size = Pt(20)
                p.font.color.rgb = self.COLORS["text_dark"]
                p.space_after = Pt(12)
                p.level = 0

        # Add slide number
        slide_num = slide_data.get("slide_number", "")
        if slide_num:
            num_box = slide.shapes.add_textbox(
                Inches(12.5), Inches(7), Inches(0.5), Inches(0.3)
            )
            tf = num_box.text_frame
            p = tf.paragraphs[0]
            p.text = str(slide_num)
            p.font.size = Pt(12)
            p.font.color.rgb = self.COLORS["text_dark"]
            p.alignment = PP_ALIGN.RIGHT

    def _create_closing_slide(self, slide_data: dict) -> None:
        """Create closing slide (thank you page)."""
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])  # Blank

        # Add background
        shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, 0, 0, self.prs.slide_width, self.prs.slide_height
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = self.COLORS["primary"]
        shape.line.fill.background()

        # Add thank you text
        content = slide_data.get("content", [])
        if content:
            # Main text
            title_box = slide.shapes.add_textbox(
                Inches(0.5), Inches(2.5), Inches(12.333), Inches(1)
            )
            tf = title_box.text_frame
            p = tf.paragraphs[0]
            p.text = content[0]
            p.font.size = Pt(48)
            p.font.bold = True
            p.font.color.rgb = self.COLORS["text_light"]
            p.alignment = PP_ALIGN.CENTER

            # Subtext
            if len(content) > 1:
                p = tf.add_paragraph()
                p.text = content[1]
                p.font.size = Pt(24)
                p.font.color.rgb = self.COLORS["text_light"]
                p.alignment = PP_ALIGN.CENTER

            if len(content) > 2:
                p = tf.add_paragraph()
                p.text = content[2]
                p.font.size = Pt(18)
                p.font.color.rgb = self.COLORS["text_light"]
                p.alignment = PP_ALIGN.CENTER


def generate_ppt(ppt_structure: dict | str, output_path: str | Path) -> str:
    """
    Convenience function to generate PPT.

    Args:
        ppt_structure: JSON structure dict or path to JSON file
        output_path: Output path for the .pptx file

    Returns:
        Path to generated PPT file
    """
    generator = PPTGenerator()
    return generator.generate(ppt_structure, output_path)


if __name__ == "__main__":
    # Test with sample structure
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ppt_generator.py <ppt_structure.json> [output.pptx]")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "output.pptx"
    
    result = generate_ppt(input_path, output_path)
    print(f"PPT generated: {result}")