def render_cv(template_name, data):
    name = str(data.get("name", "Name Not Found"))
    headline = str(data.get("headline", ""))
    contact = str(data.get("contact", ""))

    # Defensive type conversions
    skills_raw = data.get("skills", "")
    skills = [s.strip() for s in skills_raw.split(',')] if isinstance(skills_raw, str) else [str(s).strip() for s in skills_raw]
    skills = [s for s in skills if s]

    def to_html(val):
        if not val: return ""
        if isinstance(val, list):
            parts = []
            for item in val:
                if isinstance(item, dict):
                    lines = [f"<b>{str(k).replace('_',' ').title()}:</b> {str(v)}" for k, v in item.items()]
                    parts.append("<div style='margin-bottom:12px;'>" + "<br>".join(lines) + "</div>")
                else:
                    parts.append(f"<p>{str(item)}</p>")
            return "".join(parts)
        if isinstance(val, dict):
            lines = [f"<b>{str(k).replace('_',' ').title()}:</b> {str(v)}" for k, v in val.items()]
            return "<div>" + "<br>".join(lines) + "</div>"
        return str(val)

    experience   = to_html(data.get("experience", ""))
    education    = to_html(data.get("education", ""))
    certificates = to_html(data.get("certificates", ""))
    projects     = to_html(data.get("projects", ""))

    # Clean up bold job-title tags for scoped CSS classes
    for text in [experience, projects]:
        text = text.replace("<p><b>", "<div class='job-title'>").replace("</b></p>", "</div>")
    experience = experience.replace("<p><b>", "<div class='job-title'>").replace("</b></p>", "</div>")
    projects   = projects.replace("<p><b>", "<div class='job-title'>").replace("</b></p>", "</div>")

    has_edu  = bool(education and len(education) > 5)
    has_cert = bool(certificates and len(certificates) > 5)
    has_proj = bool(projects and len(projects) > 5)

    # =============================================
    # TEMPLATE 1 — Premium Two-Column (Navy & White)
    # Ref: Mariana Anderson
    # =============================================
    if template_name == "1. Premium Two-Column (Navy & White)":
        skill_li = "".join([f'<li class="sk">{s}</li>' for s in skills])
        return f"""<html><head>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}body{{font-family:'Inter',sans-serif;background:#dde1e7;}}
.cv{{max-width:900px;margin:24px auto;display:flex;background:#fff;box-shadow:0 10px 30px rgba(0,0,0,.15);min-height:1100px;}}
.lc{{width:33%;background:#2f3640;color:#fff;padding:36px 28px;}}
.rc{{width:67%;padding:40px 44px;}}
.lc h3{{font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:1.2px;border-bottom:1px solid #4a5463;padding-bottom:5px;margin:32px 0 14px;}}
.lc p,.lc li{{font-size:13px;color:#cbd5e1;line-height:1.6;}}
.sk{{list-style:none;padding-left:14px;position:relative;margin-bottom:7px;}}
.sk::before{{content:"•";position:absolute;left:0;color:#94a3b8;}}
.name{{font-size:36px;font-weight:700;color:#1e293b;letter-spacing:.5px;margin-bottom:4px;}}
.hl{{font-size:15px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-bottom:28px;}}
.sh{{font-size:16px;font-weight:700;color:#1e293b;border-bottom:2px solid #e2e8f0;padding-bottom:6px;margin:28px 0 16px;}}
.exp{{border-left:2px solid #cbd5e1;padding-left:18px;margin-left:6px;}}
.job-title{{font-size:14px;font-weight:700;color:#0f172a;position:relative;margin:20px 0 8px;}}
.job-title::before{{content:'';position:absolute;left:-26px;top:3px;width:10px;height:10px;background:#fff;border:2px solid #94a3b8;border-radius:50%;}}
.exp ul{{padding-left:18px;margin-top:4px;}}.exp li{{font-size:13px;color:#475569;line-height:1.6;margin-bottom:5px;}}
.std{{font-size:13px;color:#475569;line-height:1.6;}}
</style></head><body>
<div class="cv">
  <div class="lc">
    <h3>Contact</h3><p>{contact.replace(' | ','<br>')}</p>
    <h3>Skills</h3><ul class="sk-list">{"".join([f'<li class="sk">{s}</li>' for s in skills])}</ul>
    {"<h3>Education</h3><div class='std'>"+education+"</div>" if has_edu else ""}
    {"<h3>Certifications</h3><div class='std'>"+certificates+"</div>" if has_cert else ""}
  </div>
  <div class="rc">
    <div class="name">{name}</div>
    <div class="hl">{headline}</div>
    <div class="sh">Experience</div>
    <div class="exp">{experience}</div>
    {"<div class='sh'>Projects</div><div class='exp'>"+projects+"</div>" if has_proj else ""}
  </div>
</div></body></html>"""

    # =============================================
    # TEMPLATE 2 — Executive Corporate (Clean & Bold)
    # Ref: Ethan Smith
    # =============================================
    elif template_name == "2. Executive Corporate (Clean & Bold)":
        sk_str = ", ".join(skills)
        return f"""<html><head>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}body{{font-family:'Montserrat',sans-serif;background:#f0f2f5;}}
.cv{{max-width:900px;margin:30px auto;background:#fff;padding:50px;box-shadow:0 4px 12px rgba(0,0,0,.08);}}
.hdr{{border-bottom:3px solid #111;padding-bottom:18px;margin-bottom:28px;}}
.name{{font-size:38px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:#111;}}
.hl{{font-size:15px;font-weight:600;color:#3b82f6;margin:4px 0 12px;}}
.ct{{font-size:12px;color:#555;}}
.grid{{display:grid;grid-template-columns:2fr 1fr;gap:40px;}}
.sh{{font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#111;border-bottom:2px solid #111;padding-bottom:4px;margin:0 0 14px;}}
.job-title{{font-size:14px;font-weight:700;color:#111;margin:22px 0 6px;}}
.exp ul{{padding-left:18px;margin-top:4px;}}.exp li{{font-size:13px;color:#444;line-height:1.65;margin-bottom:5px;}}
.sb{{margin-bottom:32px;}}
.st{{font-size:13px;color:#444;line-height:1.65;}}
</style></head><body>
<div class="cv">
  <div class="hdr">
    <div class="name">{name}</div>
    <div class="hl">{headline}</div>
    <div class="ct">{contact.replace(' | ',' &bull; ')}</div>
  </div>
  <div class="grid">
    <div>
      <div class="sh">Professional Experience</div>
      <div class="exp">{experience}</div>
      {"<div class='sh' style='margin-top:28px;'>Projects</div><div class='exp'>"+projects+"</div>" if has_proj else ""}
    </div>
    <div>
      <div class="sb"><div class="sh">Core Competencies</div><div class="st">{sk_str}</div></div>
      {"<div class='sb'><div class='sh'>Education</div><div class='st'>"+education+"</div></div>" if has_edu else ""}
      {"<div class='sb'><div class='sh'>Certifications</div><div class='st'>"+certificates+"</div></div>" if has_cert else ""}
    </div>
  </div>
</div></body></html>"""

    # =============================================
    # TEMPLATE 3 — Creative Professional (Ribbons & Colors)
    # Ref: Steven Terry
    # =============================================
    elif template_name == "3. Creative Professional (Ribbons & Colors)":
        sk_pills = "".join([f'<span class="pill">{s}</span>' for s in skills])
        return f"""<html><head>
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}body{{font-family:'Roboto',sans-serif;background:#e0e7ff;}}
.cv{{max-width:860px;margin:30px auto;background:#fff;display:grid;grid-template-columns:2fr 3fr;min-height:1050px;box-shadow:0 10px 25px rgba(0,0,0,.15);}}
.lc{{border-right:1px solid #e5e7eb;padding:40px 0;display:flex;flex-direction:column;align-items:center;text-align:center;}}
.name{{font-size:26px;font-weight:900;letter-spacing:2px;text-transform:uppercase;color:#111;padding:0 18px;}}
.hl{{font-size:13px;color:#ef4444;font-weight:500;font-style:italic;margin:6px 0 28px;}}
.rib{{background:#fca5a5;color:#fff;text-transform:uppercase;font-weight:700;font-size:13px;letter-spacing:1px;padding:7px 14px;width:100%;text-align:left;margin:28px 0 14px;position:relative;}}
.rib::after{{content:'';position:absolute;right:-14px;top:0;border-top:16px solid transparent;border-bottom:16px solid transparent;border-left:14px solid #fca5a5;}}
.lt{{font-size:12.5px;color:#4b5563;line-height:1.6;padding:0 18px;text-align:left;width:100%;}}
.pw{{display:flex;flex-wrap:wrap;gap:7px;padding:0 18px;width:100%;justify-content:flex-start;}}
.pill{{font-size:11px;background:#e5e7eb;padding:3px 9px;border-radius:20px;color:#374151;font-weight:500;}}
.rc{{padding:36px 0;}}
.rbr{{background:#fca5a5;color:#fff;text-transform:uppercase;font-weight:700;font-size:13px;letter-spacing:1px;padding:7px 14px;width:93%;margin:0 0 16px 14px;clip-path:polygon(0 0,100% 0,96% 50%,100% 100%,0 100%);}}
.rt{{padding:0 28px 26px;}}
.job-title{{font-size:14px;font-weight:700;color:#111;margin:0 0 8px;}}
.rt ul{{padding-left:14px;margin-top:4px;}}.rt li{{font-size:13px;color:#4b5563;line-height:1.6;margin-bottom:7px;}}
</style></head><body>
<div class="cv">
  <div class="lc">
    <div class="name">{name}</div>
    <div class="hl">{headline}</div>
    <div class="rib">✒️ Contact</div>
    <div class="lt">{contact.replace(' | ','<br><br>')}</div>
    <div class="rib">🛠️ Skills</div>
    <div class="pw">{sk_pills}</div>
    {"<div class='rib'>🎓 Education</div><div class='lt'>"+education+"</div>" if has_edu else ""}
    {"<div class='rib'>📜 Certificates</div><div class='lt'>"+certificates+"</div>" if has_cert else ""}
  </div>
  <div class="rc">
    <div class="rbr">💼 Work Experience</div>
    <div class="rt">{experience}</div>
    {"<div class='rbr'>🚀 Projects</div><div class='rt'>"+projects+"</div>" if has_proj else ""}
  </div>
</div></body></html>"""

    # =============================================
    # TEMPLATE 4 — Minimalist Clean (Kinsley Morrison Ref)
    # =============================================
    elif template_name == "4. Minimalist Clean (Kinsley Morrison)":
        sk_list = "".join([f'<li class="sk">{s}</li>' for s in skills])
        return f"""<html><head>
<link href="https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}body{{font-family:'Raleway',sans-serif;background:#f5f5f5;}}
.cv{{max-width:860px;margin:24px auto;display:flex;background:#fff;box-shadow:0 6px 20px rgba(0,0,0,.08);min-height:1100px;}}
.lc{{width:30%;background:#f8f8f8;border-right:1px solid #e0e0e0;padding:40px 22px;}}
.rc{{width:70%;padding:40px 36px;}}
.bigname{{font-size:30px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#111;line-height:1.2;margin-bottom:20px;}}
.divider{{border:none;border-top:2px solid #111;margin:10px 0 20px;}}
.sh-left{{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#555;margin:28px 0 12px;}}
.sk{{list-style:none;font-size:13px;color:#333;margin-bottom:7px;}}
.lc p{{font-size:13px;color:#444;line-height:1.6;margin-bottom:8px;}}
.sh-right{{font-size:14px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#111;border-bottom:1px solid #e0e0e0;padding-bottom:5px;margin:26px 0 14px;}}
.job-title{{font-size:14px;font-weight:700;color:#111;margin:18px 0 6px;}}
.exp ul{{padding-left:18px;}}.exp li{{font-size:13px;color:#444;line-height:1.65;margin-bottom:5px;}}
</style></head><body>
<div class="cv">
  <div class="lc">
    <div class="sh-left">Contact</div>
    <p>{contact.replace(' | ','<br>')}</p>
    {"<div class='sh-left'>Education</div><p>"+education+"</p>" if has_edu else ""}
    <div class="sh-left">Skills</div>
    <ul>{"".join([f'<li class="sk">{s}</li>' for s in skills])}</ul>
    {"<div class='sh-left'>Certifications</div><p>"+certificates+"</p>" if has_cert else ""}
  </div>
  <div class="rc">
    <div class="bigname">{name.replace(" ", "<br>")}</div>
    <hr class="divider">
    <div style="font-size:13px;color:#888;text-transform:uppercase;letter-spacing:2px;margin-bottom:24px;">{headline}</div>
    <div class="sh-right">Work Experience</div>
    <div class="exp">{experience}</div>
    {"<div class='sh-right'>Projects</div><div class='exp'>"+projects+"</div>" if has_proj else ""}
  </div>
</div></body></html>"""

    # =============================================
    # TEMPLATE 5 — Modern Single Column (Theodora Ref)
    # Teal accent, clean professional centre layout
    # =============================================
    elif template_name == "5. Modern Single Column (Teal Accent)":
        sk_tags = "".join([f'<span class="tag">{s}</span>' for s in skills])
        return f"""<html><head>
<link href="https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}body{{font-family:'Nunito Sans',sans-serif;background:#f0f4f8;}}
.cv{{max-width:820px;margin:30px auto;background:#fff;box-shadow:0 6px 20px rgba(0,0,0,.08);}}
.hdr{{background:#0d9488;color:#fff;padding:36px 50px;}}
.name{{font-size:36px;font-weight:800;letter-spacing:1px;}}
.hl{{font-size:15px;color:#ccfbf1;margin-top:4px;}}
.ct{{font-size:12.5px;color:#a7f3d0;margin-top:10px;}}
.body{{padding:36px 50px;}}
.sh{{font-size:14px;font-weight:800;text-transform:uppercase;letter-spacing:1.5px;color:#0d9488;padding-bottom:5px;border-bottom:2px solid #0d9488;margin:28px 0 14px;}}
.tag{{display:inline-block;background:#f0fdfa;border:1px solid #0d9488;color:#0d9488;font-size:12px;padding:3px 10px;border-radius:12px;margin:3px;}}
.job-title{{font-size:14px;font-weight:700;color:#1e293b;margin:18px 0 6px;}}
.exp ul{{padding-left:18px;margin-top:4px;}}.exp li{{font-size:13px;color:#475569;line-height:1.65;margin-bottom:5px;}}
.st{{font-size:13px;color:#475569;line-height:1.6;}}
</style></head><body>
<div class="cv">
  <div class="hdr">
    <div class="name">{name}</div>
    <div class="hl">{headline}</div>
    <div class="ct">{contact.replace(' | ',' · ')}</div>
  </div>
  <div class="body">
    <div class="sh">Skills & Expertise</div>
    <div style="margin-bottom:8px;">{sk_tags}</div>
    <div class="sh">Experience</div>
    <div class="exp">{experience}</div>
    {"<div class='sh'>Projects</div><div class='exp'>"+projects+"</div>" if has_proj else ""}
    {"<div class='sh'>Education</div><div class='st'>"+education+"</div>" if has_edu else ""}
    {"<div class='sh'>Certifications</div><div class='st'>"+certificates+"</div>" if has_cert else ""}
  </div>
</div></body></html>"""

    # =============================================
    # TEMPLATE 6 — Academic / Structured (Joanne Ref)
    # Classic serif layout, great for academia & research
    # =============================================
    elif template_name == "6. Academic Structured (Classic)":
        sk_grid = "".join([f'<li class="sk">{s}</li>' for s in skills])
        return f"""<html><head>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;600;700&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}body{{font-family:'EB Garamond',serif;background:#fff;color:#111;}}
.cv{{max-width:820px;margin:30px auto;padding:50px;}}
.name{{font-size:36px;font-weight:700;text-align:center;text-transform:uppercase;letter-spacing:2px;}}
.ct{{text-align:center;font-size:14px;color:#555;margin:8px 0;}}
.hl{{text-align:center;font-size:15px;color:#444;font-style:italic;margin-bottom:24px;}}
hr{{border:none;border-top:2px solid #111;margin:14px 0;}}
.sh{{font-size:15px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;margin:24px 0 10px;border-bottom:1px solid #ccc;padding-bottom:4px;}}
.sk{{list-style:none;display:inline-block;margin-right:14px;font-size:13.5px;color:#333;}}
.sk::before{{content:"▪ ";color:#888;}}
.job-title{{font-size:14.5px;font-weight:600;color:#111;margin:16px 0 6px;}}
.exp ul{{padding-left:22px;margin-top:4px;}}.exp li{{font-size:13.5px;color:#333;line-height:1.7;margin-bottom:5px;}}
.st{{font-size:13.5px;color:#333;line-height:1.7;}}
</style></head><body>
<div class="cv">
  <div class="name">{name}</div>
  <div class="hl">{headline}</div>
  <div class="ct">{contact.replace(' | ',' · ')}</div>
  <hr>
  <div class="sh">Core Competencies</div>
  <ul style="padding:0;margin-bottom:10px;">{"".join([f'<li class="sk">{s}</li>' for s in skills])}</ul>
  <div class="sh">Professional Experience</div>
  <div class="exp">{experience}</div>
  {"<div class='sh'>Projects & Research</div><div class='exp'>"+projects+"</div>" if has_proj else ""}
  {"<div class='sh'>Education</div><div class='st'>"+education+"</div>" if has_edu else ""}
  {"<div class='sh'>Awards & Certifications</div><div class='st'>"+certificates+"</div>" if has_cert else ""}
</div></body></html>"""

    # =============================================
    # TEMPLATE 7 — Dark Premium (Two-Column Dark)
    # Modern dark/charcoal with gold accents
    # =============================================
    else:  # "7. Dark Premium (Gold & Charcoal)"
        sk_pills = "".join([f'<span class="pill">{s}</span>' for s in skills])
        return f"""<html><head>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}body{{font-family:'Poppins',sans-serif;background:#1a1a2e;}}
.cv{{max-width:900px;margin:30px auto;display:flex;min-height:1100px;box-shadow:0 15px 40px rgba(0,0,0,.5);}}
.lc{{width:35%;background:#16213e;color:#e2e8f0;padding:40px 28px;}}
.rc{{width:65%;background:#0f3460;color:#e2e8f0;padding:40px 38px;}}
.name{{font-size:28px;font-weight:700;color:#f1c40f;letter-spacing:1px;line-height:1.2;margin-bottom:6px;}}
.hl{{font-size:13px;color:#94a3b8;margin-bottom:30px;font-style:italic;}}
.lsh{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#f1c40f;border-bottom:1px solid #1e3a5f;padding-bottom:5px;margin:26px 0 12px;}}
.lc p,.lc li{{font-size:12.5px;color:#94a3b8;line-height:1.6;}}
.pill{{display:inline-block;background:rgba(241,196,15,.1);border:1px solid #f1c40f;color:#f1c40f;font-size:11px;padding:3px 9px;border-radius:4px;margin:3px;}}
.rsh{{font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#f1c40f;border-left:3px solid #f1c40f;padding-left:10px;margin:26px 0 14px;}}
.job-title{{font-size:13.5px;font-weight:700;color:#f8fafc;margin:18px 0 6px;}}
.exp ul{{padding-left:18px;margin-top:4px;}}.exp li{{font-size:12.5px;color:#94a3b8;line-height:1.65;margin-bottom:5px;}}
.st{{font-size:12.5px;color:#94a3b8;line-height:1.6;}}
</style></head><body>
<div class="cv">
  <div class="lc">
    <div class="name">{name}</div>
    <div class="hl">{headline}</div>
    <div class="lsh">Contact</div>
    <p>{contact.replace(' | ','<br>')}</p>
    <div class="lsh">Skills</div>
    <div>{sk_pills}</div>
    {"<div class='lsh'>Education</div><div class='st'>"+education+"</div>" if has_edu else ""}
    {"<div class='lsh'>Certifications</div><div class='st'>"+certificates+"</div>" if has_cert else ""}
  </div>
  <div class="rc">
    <div class="rsh">Experience</div>
    <div class="exp">{experience}</div>
    {"<div class='rsh'>Projects</div><div class='exp'>"+projects+"</div>" if has_proj else ""}
  </div>
</div></body></html>"""
