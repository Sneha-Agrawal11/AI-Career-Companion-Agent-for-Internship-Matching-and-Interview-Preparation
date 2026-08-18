const listFrom = (value) => {
  if (!value) return [];
  if (Array.isArray(value)) return value.filter(Boolean).map((v) => String(v));
  if (typeof value === "string") {
    if (!value.trim()) return [];
    if (value.includes(",")) {
      return value
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean);
    }
    return [value.trim()];
  }
  return [String(value)];
};

const firstText = (value) => {
  if (typeof value === "string") return value;
  if (Array.isArray(value) && value.length > 0) return String(value[0]);
  return "";
};

export const mapParsedResumeToCandidateInput = (source = {}) => {
  const skills = listFrom(source.skills);
  const workExperience = listFrom(source.work_experience || source.experience);

  return {
    full_name: source.full_name || source.name || "",
    email: source.email || firstText(source.emails),
    phone: source.phone || firstText(source.phones),
    address: source.address || "",
    linkedin: source.linkedin || "",
    github: source.github || "",
    professional_summary: source.professional_summary || source.summary || "",
    skills,
    technical_skills: listFrom(source.technical_skills || skills),
    soft_skills: listFrom(source.soft_skills),
    education: listFrom(source.education),
    work_experience: workExperience,
    internships: listFrom(source.internships),
    projects: listFrom(source.projects),
    certifications: listFrom(source.certifications),
    languages: listFrom(source.languages),
    achievements: listFrom(source.achievements),
    other_relevant_information: listFrom(source.other_relevant_information),
  };
};

export const parseStoredResumeRecord = (resumeRecord) => {
  if (!resumeRecord?.parsed_data) return {};
  try {
    return JSON.parse(resumeRecord.parsed_data);
  } catch {
    return {};
  }
};
