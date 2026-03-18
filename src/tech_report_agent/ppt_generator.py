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
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION


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


# Theme configurations
THEMES = {
    "tech_blue": {
        "name": "科技蓝",
        "title_bg": RGBColor(26, 26, 46),      # Deep navy
        "accent": RGBColor(233, 69, 96),       # Coral red
        "text_light": RGBColor(255, 255, 255),  # White
        "text_dark": RGBColor(51, 51, 51),      # Dark gray
        "content_bg": RGBColor(248, 249, 250),  # Light gray
        "header_bg": RGBColor(52, 73, 94),      # Steel blue
    },
    "business_gray": {
        "name": "商务灰",
        "title_bg": RGBColor(45, 52, 54),       # Charcoal
        "accent": RGBColor(0, 184, 148),        # Teal
        "text_light": RGBColor(255, 255, 255),
        "text_dark": RGBColor(45, 52, 54),
        "content_bg": RGBColor(245, 246, 250),
        "header_bg": RGBColor(99, 110, 114),
    },
    "minimal_white": {
        "name": "简约白",
        "title_bg": RGBColor(255, 255, 255),    # White
        "accent": RGBColor(0, 123, 255),         # Blue
        "text_light": RGBColor(51, 51, 51),      # Dark for white bg
        "text_dark": RGBColor(51, 51, 51),
        "content_bg": RGBColor(255, 255, 255),
        "header_bg": RGBColor(240, 240, 240),
    },
    "nature_green": {
        "name": "自然绿",
        "title_bg": RGBColor(39, 174, 96),       # Green
        "accent": RGBColor(243, 156, 18),        # Orange
        "text_light": RGBColor(255, 255, 255),
        "text_dark": RGBColor(45, 52, 54),
        "content_bg": RGBColor(245, 250, 245),
        "header_bg": RGBColor(46, 204, 113),
    },
}


class PPTGenerator:
    """Generate PowerPoint presentations from JSON structure."""

    SLIDE_TYPES = {
        "title": "_create_title_slide",
        "agenda": "_create_content_slide",
        "key_findings": "_create_content_slide",
        "methodology": "_create_content_slide",
        "analysis": "_create_content_slide",
        "diagram": "_create_content_slide",
        "chart": "_create_chart_slide",
        "data": "_create_chart_slide",  # data 类型也用图表
        "conclusion": "_create_content_slide",
        "recommendations": "_create_content_slide",
        "closing": "_create_closing_slide",
    }

    def __init__(self, theme: str = "tech_blue"):
        """Initialize PPT Generator with theme.
        
        Args:
            theme: Theme name (tech_blue, business_gray, minimal_white, nature_green)
        """
        self.theme_name = theme
        self.theme = THEMES.get(theme, THEMES["tech_blue"])
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
                first_newline = content.find("\n")
                if first_newline != -1:
                    content = content[first_newline + 1:]
            if content.rstrip().endswith("```"):
                content = content.rstrip()[:-3].rstrip()
            # Fix unescaped quotes in JSON
            content = _fix_unescaped_quotes(content)
            try:
                ppt_structure = json.loads(content)
            except json.JSONDecodeError as e:
                import re
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
        shape.fill.fore_color.rgb = self.theme["title_bg"]
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
            p.font.color.rgb = self.theme["text_light"]
            p.alignment = PP_ALIGN.CENTER

            # Subtitle
            if len(content) > 1:
                p = tf.add_paragraph()
                p.text = content[1]
                p.font.size = Pt(24)
                p.font.color.rgb = self.theme["text_light"]
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
                p.font.color.rgb = self.theme["text_light"]
                p.alignment = PP_ALIGN.CENTER

    def _create_content_slide(self, slide_data: dict) -> None:
        """Create content slide with title and bullet points."""
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])  # Blank

        # Add header bar
        header = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, 0, 0, self.prs.slide_width, Inches(1.2)
        )
        header.fill.solid()
        header.fill.fore_color.rgb = self.theme["header_bg"]
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
            p.font.color.rgb = self.theme["text_light"]

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
                
                p.text = "\u2022 " + item
                p.font.size = Pt(20)
                p.font.color.rgb = self.theme["text_dark"]
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
            p.font.color.rgb = self.theme["text_dark"]
            p.alignment = PP_ALIGN.RIGHT

    def _create_closing_slide(self, slide_data: dict) -> None:
        """Create closing slide (thank you page)."""
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])  # Blank

        # Add background
        shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, 0, 0, self.prs.slide_width, self.prs.slide_height
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = self.theme["title_bg"]
        shape.line.fill.background()

        # Add thank you text
        thank_box = slide.shapes.add_textbox(
            Inches(0.5), Inches(2.5), Inches(12.333), Inches(2)
        )
        tf = thank_box.text_frame
        p = tf.paragraphs[0]
        p.text = "Thank You"
        p.font.size = Pt(60)
        p.font.bold = True
        p.font.color.rgb = self.theme["text_light"]
        p.alignment = PP_ALIGN.CENTER

        # Add contact info
        content = slide_data.get("content", [])
        if content:
            contact_box = slide.shapes.add_textbox(
                Inches(0.5), Inches(4.5), Inches(12.333), Inches(1)
            )
            tf = contact_box.text_frame
            for i, item in enumerate(content):
                if i == 0:
                    p = tf.paragraphs[0]
                else:
                    p = tf.add_paragraph()
                p.text = item
                p.font.size = Pt(18)
                p.font.color.rgb = self.theme["text_light"]
                p.alignment = PP_ALIGN.CENTER

    def _create_chart_slide(self, slide_data: dict) -> None:
        """Create slide with chart visualization.
        
        Expected slide_data format:
        {
            "type": "chart",
            "title": "Chart Title",
            "chart_type": "bar" | "column" | "line" | "pie",
            "chart_data": {
                "categories": ["Cat1", "Cat2", "Cat3"],
                "series": [
                    {"name": "Series 1", "values": [10, 20, 30]},
                    {"name": "Series 2", "values": [15, 25, 35]}
                ]
            },
            "content": ["Additional bullet points"]  # optional
        }
        """
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])  # Blank

        # Add header bar
        header = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, 0, 0, self.prs.slide_width, Inches(1.2)
        )
        header.fill.solid()
        header.fill.fore_color.rgb = self.theme["header_bg"]
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
            p.font.color.rgb = self.theme["text_light"]

        # Check if chart_data exists
        chart_data = slide_data.get("chart_data")
        if chart_data:
            chart_type = slide_data.get("chart_type", "column")
            self._add_chart(slide, chart_type, chart_data)

        # Add bullet points if provided (below chart or as main content)
        content = slide_data.get("content", [])
        if content:
            # Position below chart or full height if no chart
            top = Inches(4.8) if chart_data else Inches(1.5)
            height = Inches(2.2) if chart_data else Inches(5.5)
            
            content_box = slide.shapes.add_textbox(
                Inches(0.7), top, Inches(11.933), height
            )
            tf = content_box.text_frame
            tf.word_wrap = True

            for i, item in enumerate(content):
                if i == 0:
                    p = tf.paragraphs[0]
                else:
                    p = tf.add_paragraph()
                
                p.text = "\u2022 " + item
                p.font.size = Pt(16) if chart_data else Pt(20)
                p.font.color.rgb = self.theme["text_dark"]
                p.space_after = Pt(8)
                p.level = 0

    def _add_chart(self, slide, chart_type: str, chart_data: dict) -> None:
        """Add a chart to the slide.
        
        Args:
            slide: The slide to add chart to
            chart_type: Type of chart (bar, column, line, pie)
            chart_data: Chart data with categories and series
        """
        # Prepare chart data
        data = CategoryChartData()
        data.categories = chart_data.get("categories", [])
        
        series_list = chart_data.get("series", [])
        for series in series_list:
            data.add_series(series.get("name", ""), series.get("values", []))

        # Map chart type to python-pptx chart type
        chart_type_map = {
            "bar": XL_CHART_TYPE.BAR_CLUSTERED,
            "column": XL_CHART_TYPE.COLUMN_CLUSTERED,
            "line": XL_CHART_TYPE.LINE,
            "pie": XL_CHART_TYPE.PIE,
        }
        
        xl_chart_type = chart_type_map.get(chart_type, XL_CHART_TYPE.COLUMN_CLUSTERED)
        
        # Add chart to slide
        x, y, cx, cy = Inches(0.7), Inches(1.5), Inches(11.933), Inches(3.2)
        chart = slide.shapes.add_chart(
            xl_chart_type, x, y, cx, cy, data
        ).chart

        # Style the chart
        chart.has_legend = True
        chart.legend.position = XL_LEGEND_POSITION.BOTTOM
        chart.legend.include_in_layout = False
        
        # Style plot area
        plot = chart.plots[0]
        plot.has_data_labels = True
        
        # For pie charts, show percentages
        if chart_type == "pie":
            plot.data_labels.show_percentage = True
            plot.data_labels.show_value = False
        else:
            plot.data_labels.show_value = True
            plot.data_labels.show_percentage = False


def generate_ppt(ppt_structure: dict | str, output_path: str | Path, theme: str = "tech_blue") -> str:
    """
    Convenience function to generate PPT.

    Args:
        ppt_structure: JSON structure dict or path to JSON file
        output_path: Output path for the .pptx file
        theme: Theme name (tech_blue, business_gray, minimal_white, nature_green)

    Returns:
        Path to generated PPT file
    """
    generator = PPTGenerator(theme=theme)
    return generator.generate(ppt_structure, output_path)