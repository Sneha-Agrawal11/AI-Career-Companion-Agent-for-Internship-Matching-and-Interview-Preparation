import api from "./api";

export const uploadResume = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post("/resume/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

export const fetchAllResumes = async () => {
  const response = await api.get("/resume/all");
  return response.data;
};
