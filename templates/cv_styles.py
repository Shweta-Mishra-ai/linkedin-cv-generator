def render_cv(template_name, data):
    name = data.get("name", "Name Not Found")
    headline = data.get("headline", "Professional Headline")
    contact = data.get("contact", "Not Provided")
    skills = data.get("skills", "Communication")
    experience = data.get("experience", "<p>Experience details missing.</p>")

    skills_html = "".join([f'<span class="skill-tag">{skill.strip()}</span>' for skill in skills.split(',') if skill.strip()])

    if template_name == "Modern Sidebar":
        return f"""
        <html><head><style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #f4f4f9; margin: 0; padding: 20px; }}
            .cv-box {{ max-width: 850px; margin: auto; background: white; display: flex; min-height: 1050px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
            .left {{ width: 35%; background: #2A3B4C; color: white; padding: 30px 20px; }}
            .right {{ width: 65%; padding: 40px 30px; color: #333; }}
            h1 {{ border-bottom: 2px solid #4CAF50; padding-bottom: 10px; text-transform: uppercase; font-size: 28px; margin-top:0;}}
            h2 {{ color: #2A3B4C; border-bottom: 2px solid #ddd; padding-bottom: 5px; text-transform: uppercase; }}
            h3 {{ color: #4CAF50; text-transform: uppercase; margin-top:30px;}}
            .skill-tag {{ display: inline-block; background: rgba(255,255,255,0.1); padding: 5px 10px; margin: 5px; border-radius: 3px; font-size: 13px; border: 1px solid #4CAF50; }}
        </style></head><body>
            <div class="cv-box">
                <div class="left">
                    <h1>{name}</h1><p><i>{headline}</i></p>
                    <h3>Contact</h3><p>📧 {contact}</p>
                    <h3>Top Skills</h3><div>{skills_html}</div>
                </div>
                <div class="right"><h2>Professional Details</h2><div>{experience}</div></div>
            </div>
        </body></html>
        """

    elif template_name == "Classic Corporate":
        skills_bullet = "".join([f'<li>{skill.strip()}</li>' for skill in skills.split(',') if skill.strip()])
        return f"""
        <html><head><style>
            body {{ font-family: 'Times New Roman', serif; background: #fff; margin: 0; padding: 40px; color: #000; }}
            .cv-box {{ max-width: 800px; margin: auto; }}
            h1 {{ text-align: center; font-size: 32px; margin-bottom: 5px; text-transform: uppercase; }}
            .contact {{ text-align: center; font-size: 14px; margin-bottom: 30px; border-bottom: 2px solid #000; padding-bottom: 15px; }}
            h2 {{ font-size: 18px; text-transform: uppercase; border-bottom: 1px solid #000; margin-top: 25px; padding-bottom: 3px; }}
            .skills-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; margin-top: 10px; }}
        </style></head><body>
            <div class="cv-box">
                <h1>{name}</h1>
                <div class="contact">{headline} | {contact}</div>
                <h2>Core Competencies</h2>
                <ul class="skills-grid">{skills_bullet}</ul>
                <h2>Professional Experience</h2>
                <div>{experience}</div>
            </div>
        </body></html>
        """

    else: # Minimalist Tech
        return f"""
        <html><head><style>
            body {{ font-family: 'Helvetica Neue', sans-serif; background: #fff; margin: 0; padding: 40px; color: #333; }}
            .cv-box {{ max-width: 800px; margin: auto; }}
            h1 {{ font-size: 40px; font-weight: 800; letter-spacing: -1px; margin-bottom: 0; }}
            .headline {{ font-size: 20px; color: #666; margin-top: 5px; margin-bottom: 20px; }}
            h2 {{ font-size: 20px; color: #000; margin-top: 40px; text-transform: uppercase; letter-spacing: 1px; }}
            .skill-tag {{ display: inline-block; background: #f0f0f0; color: #333; padding: 6px 12px; margin: 4px; border-radius: 20px; font-size: 13px; font-weight: 600; }}
        </style></head><body>
            <div class="cv-box">
                <h1>{name}</h1>
                <div class="headline">{headline}</div>
                <p><strong>Contact:</strong> {contact}</p>
                <h2>Skills</h2><div>{skills_html}</div>
                <h2>Experience & Projects</h2><div>{experience}</div>
            </div>
        </body></html>
        """
