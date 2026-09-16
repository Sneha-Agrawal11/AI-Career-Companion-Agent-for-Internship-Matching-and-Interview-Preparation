import api from "./api";

export const fetchInternships = async () => {
  const response = await api.get("/internships");
  return response.data;
};

export const fetchInternshipById = async (internshipId) => {
  const response = await api.get(`/internships/${internshipId}`);
  return response.data;
};

export const fetchMatches = async (candidate, topK = 5) => {
  const response = await api.post("/internships/match", candidate, {
    params: { top_k: topK },
  });
  return response.data;
};

export const fetchInternshipsWithMatch = async () => {
  const response = await api.get("/internships/match-all");
  return response.data;
};

export const applyToInternship = async (internshipId) => {
  const response = await api.post(`/internships/${internshipId}/apply`);
  return response.data;
};

export const fetchApplications = async () => {
  const response = await api.get("/internships/applications");
  return response.data;
};
