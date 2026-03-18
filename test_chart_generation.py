"""
Test chart generation in PPT
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tech_report_agent.ppt_generator import PPTGenerator, generate_ppt


def test_column_chart():
    """Test column chart generation"""
    print("Testing column chart...")
    
    ppt_structure = {
        "slides": [
            {
                "slide_number": 1,
                "type": "title",
                "title": "Chart Test",
                "content": ["PPT Chart Generation Test", "InsightForge 2026"]
            },
            {
                "slide_number": 2,
                "type": "chart",
                "title": "Market Size Growth",
                "chart_type": "column",
                "chart_data": {
                    "categories": ["2022", "2023", "2024", "2025", "2026"],
                    "series": [
                        {"name": "GenAI Market ($B)", "values": [40, 65, 110, 180, 290]}
                    ]
                },
                "content": [
                    "CAGR: 65% year-over-year growth",
                    "Video generation: Third largest segment"
                ]
            },
            {
                "slide_number": 3,
                "type": "chart",
                "title": "Cost Reduction by Industry",
                "chart_type": "bar",
                "chart_data": {
                    "categories": ["Video Production", "Content Creation", "Marketing", "Game Dev"],
                    "series": [
                        {"name": "Cost Reduction (%)", "values": [92, 85, 78, 65]}
                    ]
                },
                "content": [
                    "Video production sees highest impact",
                    "Content creation close second"
                ]
            },
            {
                "slide_number": 4,
                "type": "chart",
                "title": "Technology Adoption Trend",
                "chart_type": "line",
                "chart_data": {
                    "categories": ["Q1", "Q2", "Q3", "Q4"],
                    "series": [
                        {"name": "Enterprise Adoption", "values": [15, 28, 45, 68]},
                        {"name": "Consumer Adoption", "values": [22, 35, 52, 78]}
                    ]
                },
                "content": [
                    "Steady growth in both segments",
                    "Consumer adoption leads enterprise"
                ]
            },
            {
                "slide_number": 5,
                "type": "chart",
                "title": "Market Share Distribution",
                "chart_type": "pie",
                "chart_data": {
                    "categories": ["OpenAI", "Google", "Anthropic", "Meta", "Others"],
                    "series": [
                        {"name": "Market Share", "values": [35, 28, 18, 12, 7]}
                    ]
                },
                "content": [
                    "OpenAI leads with 35% market share",
                    "Top 3 players control 81% of market"
                ]
            },
            {
                "slide_number": 6,
                "type": "closing",
                "title": "Thank You",
                "content": ["InsightForge Test Report", "2026-03-18"]
            }
        ]
    }
    
    output_path = Path(__file__).parent / "test_output" / "presentations" / "test_charts.pptx"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    result = generate_ppt(ppt_structure, output_path, theme="tech_blue")
    print(f"Generated: {result}")
    return result


def test_all_themes_with_charts():
    """Test charts with all themes"""
    print("\nTesting charts with all themes...")
    
    ppt_structure = {
        "slides": [
            {
                "slide_number": 1,
                "type": "chart",
                "title": "Performance Metrics",
                "chart_type": "column",
                "chart_data": {
                    "categories": ["Accuracy", "Speed", "Cost", "Quality"],
                    "series": [
                        {"name": "Before AI", "values": [65, 40, 80, 70]},
                        {"name": "After AI", "values": [92, 95, 25, 88]}
                    ]
                },
                "content": [
                    "AI improves accuracy by 42%",
                    "Processing speed up 2.4x"
                ]
            }
        ]
    }
    
    themes = ["tech_blue", "business_gray", "minimal_white", "nature_green"]
    output_dir = Path(__file__).parent / "test_output" / "presentations"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for theme in themes:
        output_path = output_dir / f"test_chart_{theme}.pptx"
        generate_ppt(ppt_structure, output_path, theme=theme)
        print(f"  {theme}: {output_path}")


if __name__ == "__main__":
    print("=" * 60)
    print("  PPT Chart Generation Test")
    print("=" * 60)
    
    try:
        test_column_chart()
        test_all_themes_with_charts()
        print("\n" + "=" * 60)
        print("  All tests passed!")
        print("=" * 60)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()