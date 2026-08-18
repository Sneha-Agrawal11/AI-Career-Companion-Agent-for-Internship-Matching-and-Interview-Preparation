import api from "./api";

export const fetchProfile = async () => {
  const response = await api.get("/users/profile");
  return response.data;
};

export const updateProfile = async ({ full_name }) => {
  const response = await api.put("/users/profile", null, {
    params: { full_name },
  });
  return response.data;
};

export const deleteAccount = async () => {
  const response = await api.delete("/users/delete");
  return response.data;
};
