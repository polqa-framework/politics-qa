from pathlib import Path
from typing import Dict
from jinja2 import Template

def generate_report(run_summary: Dict, output_path: str = "results/report.html"):
    template_path = Path("polqa/reporting/templates/report.html.j2")
    styles_path = Path("polqa/reporting/templates/styles.css")
    html = Template(template_path.read_text(encoding="utf-8")).render(
        summary=run_summary, styles=styles_path.read_text(encoding="utf-8")
    )
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return str(out)
