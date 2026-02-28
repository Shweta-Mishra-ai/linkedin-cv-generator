def render_cv(template_name, data):
    name = data.get("name", "Name Not Found")
    headline = data.get("headline", "")
    contact = data.get("contact", "")
    skills = data.get("skills", "")
    experience = data.get("experience", "<p>No experience data found.</p>")
    education = data.get("education", "")
    certificates = data.get("certificates", "")

    # Base HTML for Edu & Certs (Only shows if real data exists)
    edu_html = f'<h2 style="margin-top: 30px; margin-bottom: 10px;">Education</h2><div style="font-size: 14px; line-height: 1.6;">{education}</div>' if education and len(education) > 5 and "hidden" not in education.lower() else ''
    cert_html = f'<h2 style="margin-top: 30px; margin-bottom: 10px;">Certifications</h2><div style="font-size: 14px; line-height: 1.6;">{certificates}</div>' if certificates and len(certificates) > 5 and "hidden" not in certificates.lower() else ''

    # ==========================================
    # 1. Executive Blue (Premium)
    # ==========================================
    if template_name == "Executive Blue (Premium)":
        skills_html = "".join([f'<div style="background:rgba(255,255,255,0.2); padding:6px 12px; margin:4px; border-radius:4px; font-size:13px; display:inline-block;">{s.strip()}</div>' for s in skills.split(',') if s.strip()])
        e_html = edu_html.replace('<h2', '<h2 style="color: #1e3a8a; font-size: 22px; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; text-transform: uppercase;"')
        c_html = cert_html.replace('<h2', '<h2 style="color: #1e3a8a; font-size: 22px; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; text-transform: uppercase;"')
        
        return f"""
        <html><body style="font-family: 'Segoe UI', Tahoma, sans-serif; background: #e9ecef; margin: 0; padding: 20px;">
            <div style="max-width: 850px; margin: auto; background: white; display: flex; min-height: 1050px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden;">
                <div style="width: 35%; background: #1e3a8a; color: white; padding: 40px 25px;">
                    <h1 style="margin: 0; font-size: 32px; font-weight: 700; border-bottom: 2px solid #60a5fa; padding-bottom: 15px; margin-bottom: 15px;">{name}</h1>
                    <p style="font-size: 16px; color: #bfdbfe; font-style: italic; margin-bottom: 40px;">{headline}</p>
                    <h3 style="color: #60a5fa; text-transform: uppercase; font-size: 14px;">Contact Info</h3>
                    <p style="font-size: 14px; line-height: 1.6;">{contact}</p>
                    <h3 style="color: #60a5fa; text-transform: uppercase; font-size: 14px; margin-top: 40px;">Core Skills</h3>
                    <div>{skills_html}</div>
                </div>
                <div style="width: 65%; padding: 40px 35px; color: #334155;">
                    <h2 style="color: #1e3a8a; font-size: 22px; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; text-transform: uppercase;">Experience & Projects</h2>
                    <div style="font-size: 14px; line-height: 1.8;">{experience}</div>
                    {e_html}
                    {c_html}
                </div>
            </div>
        </body></html>
        """

    # ==========================================
    # 2. Modern Accent (Clean)
    # ==========================================
    elif template_name == "Modern Accent (Clean)":
        skills_html = "".join([f'<span style="display:inline-block; border: 1px solid #14b8a6; color: #14b8a6; padding: 4px 10px; margin: 4px 6px 4px 0; border-radius: 20px; font-size: 12px; font-weight: 600;">{s.strip()}</span>' for s in skills.split(',') if s.strip()])
        e_html = edu_html.replace('<h2', '<h2 style="color: #0f172a; font-size: 18px; text-transform: uppercase; border-bottom: 2px solid #f1f5f9; padding-bottom: 8px;"')
        c_html = cert_html.replace('<h2', '<h2 style="color: #0f172a; font-size: 18px; text-transform: uppercase; border-bottom: 2px solid #f1f5f9; padding-bottom: 8px;"')
        
        return f"""
        <html><body style="font-family: 'Helvetica Neue', Arial, sans-serif; background: #f8fafc; margin: 0; padding: 20px;">
            <div style="max-width: 850px; margin: auto; background: white; min-height: 1050px; border-top: 8px solid #14b8a6; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                <div style="padding: 40px 50px; text-align: center; border-bottom: 1px solid #f1f5f9;">
                    <h1 style="margin: 0; font-size: 36px; color: #0f172a; text-transform: uppercase;">{name}</h1>
                    <p style="font-size: 18px; color: #64748b; margin-top: 10px;">{headline}</p>
                    <p style="font-size: 14px; color: #94a3b8;">{contact}</p>
                </div>
                <div style="padding: 40px 50px; color: #334155;">
                    <h2 style="color: #0f172a; font-size: 18px; text-transform: uppercase; border-bottom: 2px solid #f1f5f9; padding-bottom: 8px;">Technical Expertise</h2>
                    <div style="margin-bottom: 30px;">{skills_html}</div>
                    <h2 style="color: #0f172a; font-size: 18px; text-transform: uppercase; border-bottom: 2px solid #f1f5f9; padding-bottom: 8px;">Experience</h2>
                    <div style="font-size: 14px; line-height: 1.7;">{experience}</div>
                    {e_html}
                    {c_html}
                </div>
            </div>
        </body></html>
        """

    # ==========================================
    # 3. Classic Corporate
    # ==========================================
    elif template_name == "Classic Corporate":
        skills_bullet = "".join([f'<li style="margin-bottom: 8px;">{s.strip()}</li>' for s in skills.split(',') if s.strip()])
        e_html = edu_html.replace('<h2', '<h2 style="font-size: 18px; text-transform: uppercase; border-bottom: 1px solid #111;"')
        c_html = cert_html.replace('<h2', '<h2 style="font-size: 18px; text-transform: uppercase; border-bottom: 1px solid #111;"')
        
        return f"""
        <html><body style="font-family: 'Georgia', serif; background: #fff; margin: 0; padding: 40px; color: #111;">
            <div style="max-width: 800px; margin: auto;">
                <h1 style="text-align: center; font-size: 38px; text-transform: uppercase;">{name}</h1>
                <div style="text-align: center; font-size: 15px; margin-bottom: 30px; border-bottom: 2px solid #111; padding-bottom: 15px;">{headline} | {contact}</div>
                <h2 style="font-size: 18px; text-transform: uppercase; border-bottom: 1px solid #111;">Core Competencies</h2>
                <ul style="display: grid; grid-template-columns: 1fr 1fr 1fr; font-size: 14px;">{skills_bullet}</ul>
                <h2 style="font-size: 18px; text-transform: uppercase; border-bottom: 1px solid #111; margin-top: 30px;">Professional Experience</h2>
                <div style="font-size: 14px; line-height: 1.6;">{experience}</div>
                {e_html}
                {c_html}
            </div>
        </body></html>
        """

    # ==========================================
    # 4. Modern Sidebar (Original)
    # ==========================================
    elif template_name == "Modern Sidebar (Original)":
        skills_html = "".join([f'<span style="display: inline-block; background: rgba(255,255,255,0.1); padding: 5px 10px; margin: 5px; border-radius: 3px; font-size: 13px; border: 1px solid #4CAF50;">{s.strip()}</span>' for s in skills.split(',') if s.strip()])
        e_html = edu_html.replace('<h2', '<h2 style="color: #2A3B4C; border-bottom: 2px solid #ddd; padding-bottom: 5px; text-transform: uppercase; font-size: 22px;"')
        c_html = cert_html.replace('<h2', '<h2 style="color: #2A3B4C; border-bottom: 2px solid #ddd; padding-bottom: 5px; text-transform: uppercase; font-size: 22px;"')
        
        return f"""
        <html><body style="font-family: 'Segoe UI', sans-serif; background: #f4f4f9; margin: 0; padding: 20px;">
            <div style="max-width: 850px; margin: auto; background: white; display: flex; min-height: 1050px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                <div style="width: 35%; background: #2A3B4C; color: white; padding: 30px 20px;">
                    <h1 style="border-bottom: 2px solid #4CAF50; padding-bottom: 10px; text-transform: uppercase; font-size: 28px; margin-top:0;">{name}</h1>
                    <p><i>{headline}</i></p>
                    <h3 style="color: #4CAF50; text-transform: uppercase; margin-top:30px;">Contact</h3><p>📧 {contact}</p>
                    <h3 style="color: #4CAF50; text-transform: uppercase; margin-top:30px;">Top Skills</h3><div>{skills_html}</div>
                </div>
                <div style="width: 65%; padding: 40px 30px; color: #333;">
                    <h2 style="color: #2A3B4C; border-bottom: 2px solid #ddd; padding-bottom: 5px; text-transform: uppercase; font-size: 22px;">Professional Details</h2>
                    <div>{experience}</div>
                    {e_html}
                    {c_html}
                </div>
            </div>
        </body></html>
        """

    # ==========================================
    # 5. Minimalist Tech (Original)
    # ==========================================
    else: 
        skills_html = "".join([f'<span style="display: inline-block; background: #f0f0f0; color: #333; padding: 6px 12px; margin: 4px; border-radius: 20px; font-size: 13px; font-weight: 600;">{s.strip()}</span>' for s in skills.split(',') if s.strip()])
        e_html = edu_html.replace('<h2', '<h2 style="font-size: 20px; color: #000; text-transform: uppercase; letter-spacing: 1px;"')
        c_html = cert_html.replace('<h2', '<h2 style="font-size: 20px; color: #000; text-transform: uppercase; letter-spacing: 1px;"')
        
        return f"""
        <html><body style="font-family: 'Helvetica Neue', sans-serif; background: #fff; margin: 0; padding: 40px; color: #333;">
            <div style="max-width: 800px; margin: auto;">
                <h1 style="font-size: 40px; font-weight: 800; letter-spacing: -1px; margin-bottom: 0;">{name}</h1>
                <div style="font-size: 20px; color: #666; margin-top: 5px; margin-bottom: 20px;">{headline}</div>
                <p><strong>Contact:</strong> {contact}</p>
                <h2 style="font-size: 20px; color: #000; margin-top: 40px; text-transform: uppercase; letter-spacing: 1px;">Skills</h2><div>{skills_html}</div>
                <h2 style="font-size: 20px; color: #000; margin-top: 40px; text-transform: uppercase; letter-spacing: 1px;">Experience & Projects</h2><div>{experience}</div>
                {e_html}
                {c_html}
            </div>
        </body></html>
        """
