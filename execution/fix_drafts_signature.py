"""
Update Gmail drafts to include HTML body + signature.
Converts plain text body to HTML and appends the user's Gmail signature.

SETUP: Replace SIGNATURE_HTML below with your own email signature.
You can get it from Gmail Settings > General > Signature, or inspect
the HTML source of a sent email.
"""
import json
import sys

# TODO: Replace with your own HTML signature
SIGNATURE_HTML = """<div dir="ltr">
<table cellpadding="0" cellspacing="0">
<tbody>
<tr>
<td style="vertical-align:middle">
<h3 style="margin:0;color:rgb(0,0,0)">
<font face="tahoma, sans-serif" size="2">[TU_NOMBRE]</font>
</h3>
<h3 style="margin:0;color:rgb(0,0,0)">
<span style="font-weight:normal;font-family:tahoma,sans-serif;font-size:small">[TU_CARGO]</span>
</h3>
</td>
</tr>
<tr>
<td>
<font size="2" face="tahoma, sans-serif">[TU_EMAIL]</font>
</td>
</tr>
<tr>
<td>
<a href="[TU_WEBSITE]"><font face="tahoma, sans-serif">[TU_WEBSITE]</font></a>
</td>
</tr>
<tr>
<td>
<font face="tahoma, sans-serif"><span style="font-size:12px">[TU_DIRECCIÓN]</span></font>
</td>
</tr>
</tbody>
</table>
</div>"""


# Email template — customize for your product/company
TEMPLATE = """{greeting}, cómo va todo?

Me recomendaron hablar contigo porque mi empresa, [TU_EMPRESA], tiene un producto muy ganador que te puede interesar.

[DESCRIPCIÓN_SENSORIAL_DE_TU_PRODUCTO]. Eso es [TU_PRODUCTO], un [CATEGORÍA] premium que ha conquistado [ALCANCE] y estoy seguro encajaría perfecto en {company}.

Me encantaría presentarte el producto. Es un best seller en {channel_ref} y estoy seguro que te va a sorprender.

Avísame y lo coordinamos.

Saludos."""

CHANNEL_REFS = {
    "channel_1": "[REFERENCIA_DE_CLIENTE_EXISTENTE_CANAL_1]",
    "channel_2": "[REFERENCIA_DE_CLIENTE_EXISTENTE_CANAL_2]",
    "channel_3": "[REFERENCIA_DE_CLIENTE_EXISTENTE_CANAL_3]",
}

# TODO: Populate with your actual drafts when ready to batch-update
DRAFTS = [
    # {"draft_id": "r-example123", "name": "Contact Name", "company": "Company", "channel": "channel_1"},
]


def text_to_html(text):
    """Convert plain text to HTML, preserving paragraph breaks."""
    import html as html_mod
    text = html_mod.escape(text)
    paragraphs = text.split("\n\n")
    html_parts = []
    for p in paragraphs:
        lines = p.split("\n")
        html_parts.append("<br>".join(lines))
    return "<br><br>".join(html_parts)


def build_html_body(draft):
    greeting = draft["name"] if draft["name"] else "Hola"
    channel_ref = CHANNEL_REFS[draft["channel"]]
    plain = TEMPLATE.format(
        greeting=greeting,
        company=draft["company"],
        channel_ref=channel_ref,
    )
    body_html = text_to_html(plain)
    return f'<div dir="ltr">{body_html}<br><br>-- <br>{SIGNATURE_HTML}</div>'


def main():
    dry_run = "--dry-run" in sys.argv
    mode = "DRY RUN" if dry_run else "LIVE"
    print(f"=== {mode} — Processing {len(DRAFTS)} drafts with HTML + signature ===\n")

    if not DRAFTS:
        print("No drafts configured. Add entries to the DRAFTS list.")
        return

    for i, draft in enumerate(DRAFTS, 1):
        html_body = build_html_body(draft)
        print(f"[{i}/{len(DRAFTS)}] {draft['company']} — HTML length: {len(html_body)} chars")
        if not dry_run:
            print(json.dumps({"company": draft["company"], "html_preview": html_body[:200]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
