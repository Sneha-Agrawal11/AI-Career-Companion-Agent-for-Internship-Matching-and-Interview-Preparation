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
