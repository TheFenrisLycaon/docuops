"""
docx_table.py — Populate a DOCX Table from Excel Data
=======================================================
Reads an Excel file with pandas and renders its rows into a ``docxtpl``
Word template that contains a ``{{ tbl_contents }}`` context variable.

Public API
----------
    populate_table(excel_path, template_path, output_path)

Dependencies
------------
    pandas   (pip)
    openpyxl (pip, required by pandas for ``.xlsx`` files)
    docxtpl  (pip)
"""

import pandas as pd
from docxtpl import DocxTemplate


def populate_table(
    excel_path: str,
    template_path: str,
    output_path: str,
) -> None:
    """Read *excel_path* and render its rows into a DOCX table template.

    The template at *template_path* must contain a Jinja2 loop over
    ``tbl_contents``, where each item has a ``cols`` key::

        {% for row in tbl_contents %}
        {% for col in row.cols %}{{ col }} {% endfor %}
        {% endfor %}

    Args:
        excel_path: Path to the source ``.xlsx`` (or ``.xls``) file.
        template_path: Path to the ``.docx`` template file.
        output_path: Destination path for the rendered ``.docx`` file.

    Example::

        from docuops.docx_table import populate_table

        populate_table(
            excel_path="data/table.xlsx",
            template_path="templates/sample.docx",
            output_path="output/table_filled.docx",
        )
    """
    data = pd.read_excel(excel_path)

    context: dict = {"tbl_contents": []}
    for _, row in data.iterrows():
        context["tbl_contents"].append({"cols": list(row)})

    tpl = DocxTemplate(template_path)
    tpl.render(context)
    tpl.save(output_path)

    print(f"  Saved: {output_path}")
