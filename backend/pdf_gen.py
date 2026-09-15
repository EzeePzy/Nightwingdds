"""Generate a professional Kundali PDF report for Rashisense."""
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
)

GOLD = colors.HexColor("#B8860B")
INDIGO = colors.HexColor("#13102B")
DARK = colors.HexColor("#0B0D1B")
MUTED = colors.HexColor("#555555")


def _styles():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle("RSTitle", parent=ss["Title"], fontName="Helvetica-Bold",
                          fontSize=26, textColor=INDIGO, spaceAfter=2))
    ss.add(ParagraphStyle("RSSub", parent=ss["Normal"], fontName="Helvetica",
                          fontSize=10, textColor=MUTED, spaceAfter=10))
    ss.add(ParagraphStyle("RSH2", parent=ss["Heading2"], fontName="Helvetica-Bold",
                          fontSize=14, textColor=GOLD, spaceBefore=12, spaceAfter=6))
    ss.add(ParagraphStyle("RSBody", parent=ss["Normal"], fontName="Helvetica",
                          fontSize=10, textColor=colors.HexColor("#222222"), leading=15))
    ss.add(ParagraphStyle("RSLabel", parent=ss["Normal"], fontName="Helvetica-Bold",
                          fontSize=10, textColor=INDIGO))
    return ss


def _kv_table(rows):
    t = Table(rows, colWidths=[45 * mm, 120 * mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), INDIGO),
        ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#222222")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#E5E5E5")),
    ]))
    return t


def _grid_table(header, data, col_widths):
    rows = [header] + data
    t = Table(rows, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INDIGO),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAF6EC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#222222")),
    ]))
    return t


def generate_kundali_pdf(reading: dict) -> bytes:
    inp = reading.get("input", {})
    chart = reading.get("chart", {})
    gem = reading.get("gemstone", {})
    read = reading.get("reading", {})
    ss = _styles()
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=18 * mm, bottomMargin=16 * mm,
                            leftMargin=18 * mm, rightMargin=18 * mm, title="Rashisense Kundali")
    E = []

    E.append(Paragraph("RASHISENSE", ss["RSTitle"]))
    E.append(Paragraph("Vedic Janma Kundali &amp; Gemstone Report", ss["RSSub"]))
    E.append(HRFlowable(width="100%", thickness=1.2, color=GOLD, spaceAfter=10))

    # Birth details
    E.append(Paragraph("Birth Details", ss["RSH2"]))
    loc = chart.get("birth_location", {})
    E.append(_kv_table([
        ["Name", inp.get("name", "-")],
        ["Gender", inp.get("gender", "-")],
        ["Date of Birth", inp.get("dob", "-")],
        ["Time of Birth (24h)", inp.get("time", "-")],
        ["Place", f"{inp.get('place', '-')}  ({loc.get('matched', '')})"],
        ["Ayanamsa", f"Lahiri {chart.get('ayanamsa', '')}\u00b0"],
    ]))

    # Core signs
    E.append(Paragraph("Rashi &amp; Lagna", ss["RSH2"]))
    ms = chart.get("moon_sign", {})
    su = chart.get("sun_sign", {})
    asc = chart.get("ascendant", {})
    ws = chart.get("western_sun_sign", {})
    E.append(_kv_table([
        ["Rashi (Moon Sign)", f"{ms.get('sa','')} ({ms.get('en','')})"],
        ["Nakshatra / Pada", f"{chart.get('nakshatra','')}  ·  Pada {chart.get('pada','')}"],
        ["Lagna (Ascendant)", f"{asc.get('sa','')} ({asc.get('en','')})"],
        ["Vedic Sun Sign", f"{su.get('sa','')} ({su.get('en','')})"],
        ["Western Sun Sign", ws.get("en", "-")],
        ["Ruling Planet", chart.get("ruling_planet", "-")],
    ]))

    # Planetary positions
    E.append(Paragraph("Planetary Positions (Rashi Chart)", ss["RSH2"]))
    pp = chart.get("planet_positions", {})
    pd = chart.get("planet_degrees", {})
    nav = chart.get("navamsa_positions", {})
    order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    rows = [[p, pp.get(p, "-"), f"{pd.get(p, '-')}\u00b0", nav.get(p, "-")] for p in order if p in pp]
    E.append(_grid_table(["Planet", "Rashi (D1)", "Degree", "Navamsa (D9)"], rows,
                         [40 * mm, 45 * mm, 35 * mm, 45 * mm]))
    navasc = chart.get("navamsa_ascendant", {})
    if navasc:
        E.append(Spacer(1, 4))
        E.append(Paragraph(f"<b>Navamsa Lagna (D9 Ascendant):</b> {navasc.get('sa','')} ({navasc.get('en','')})", ss["RSBody"]))

    # Vimshottari Dasha
    E.append(Paragraph("Vimshottari Dasha (Mahadasha)", ss["RSH2"]))
    dasha = reading.get("chart", {}).get("dasha", []) or []
    drows = []
    for d in dasha[:9]:
        cur = "  (current)" if d.get("is_current") else ""
        drows.append([d.get("planet", ""), d.get("start", ""), d.get("end", ""), f"{d.get('years','')} yrs{cur}"])
    if drows:
        E.append(_grid_table(["Planet", "From", "To", "Duration"], drows,
                             [40 * mm, 40 * mm, 40 * mm, 45 * mm]))
    cd = chart.get("current_dasha")
    if cd:
        ad = cd.get("antardasha")
        ad_txt = f" · Antardasha: {ad['planet']} (till {ad['end']})" if ad else ""
        E.append(Spacer(1, 4))
        E.append(Paragraph(f"<b>Running now:</b> {cd['planet']} Mahadasha ({cd['start']} to {cd['end']}){ad_txt}", ss["RSBody"]))

    # Gemstone
    E.append(Paragraph("Recommended Gemstone", ss["RSH2"]))
    E.append(_kv_table([
        ["Gemstone", f"{gem.get('name','')} ({gem.get('name_sa','')})"],
        ["Planet", gem.get("planet", "-")],
        ["Metal", gem.get("metal", "-")],
        ["Finger", gem.get("finger", "-")],
        ["Day to wear", gem.get("day", "-")],
        ["Weight", gem.get("weight", "-")],
        ["Mantra", gem.get("mantra", "-")],
    ]))
    if read.get("gemstone_reason"):
        E.append(Spacer(1, 4))
        E.append(Paragraph(read["gemstone_reason"], ss["RSBody"]))

    # Reading
    E.append(Paragraph("Personalised Reading", ss["RSH2"]))
    for key, label in [("summary", "Overview"), ("career", "Career &amp; Finance"),
                       ("love", "Love &amp; Relationships"), ("health", "Health &amp; Energy"),
                       ("wealth", "Wealth"), ("spiritual", "Spiritual Guidance")]:
        if read.get(key):
            E.append(Paragraph(f"<b>{label}:</b> {read[key]}", ss["RSBody"]))
            E.append(Spacer(1, 3))

    E.append(Spacer(1, 10))
    E.append(HRFlowable(width="100%", thickness=0.8, color=GOLD))
    E.append(Paragraph("Generated by Rashisense · Swiss Ephemeris (Lahiri Ayanamsa). For guidance only.", ss["RSSub"]))

    doc.build(E)
    return buf.getvalue()
