from schemas import ResumeData

def render_resume(data: ResumeData) -> str:
    lines = []

    lines.append(data.full_name.upper())
    contact = " | ".join(filter(None, [data.location, data.email, data.phone]))
    if contact:
        lines.append(contact)
    links = " | ".join(filter(None, [data.linkedin, data.github]))
    if links:
        lines.append(links)
    lines.append("")

    if data.summary:
        lines.append("PROFESSIONAL SUMMARY")
        lines.append(data.summary)
        lines.append("")

    if data.education:
        lines.append("EDUCATION")
        for edu in data.education:
            line = edu.institution
            if edu.degree:
                line += f" — {edu.degree}"
            if edu.field_of_study:
                line += f", {edu.field_of_study}"
            if edu.score:
                line += f" ({edu.score})"
            if edu.graduation_year:
                line += f" | {edu.graduation_year}"
            lines.append(line)
        lines.append("")

    if data.experience:
        lines.append("EXPERIENCE")
        for exp in data.experience:
            date_range = f"{exp.start_date or ''} – {exp.end_date or ''}".strip(" –")
            header = f"{exp.title} | {exp.company}"
            if date_range:
                header += f" | {date_range}"
            lines.append(header)
            for point in exp.highlights:
                lines.append(f"  • {point}")
        lines.append("")

    if data.projects:
        lines.append("PROJECTS")
        for proj in data.projects:
            header = proj.title
            if proj.date:
                header += f" — {proj.date}"
            lines.append(header)
            for point in proj.description:
                lines.append(f"  • {point}")
        lines.append("")

    if data.skills:
        lines.append("TECHNICAL SKILLS")
        lines.append(", ".join(data.skills))
        lines.append("")

    if data.certifications:
        lines.append("CERTIFICATIONS & ACHIEVEMENTS")
        for cert in data.certifications:
            lines.append(f"  • {cert}")

    return "\n".join(lines)