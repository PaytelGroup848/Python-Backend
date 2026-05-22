import { apiClient }
  from "@/services/api/client";

export async function registerUser(
  name: string,
  email: string,
  password: string
) {

  const response =
    await apiClient.post(

      "/auth/signup",

      {
        name,
        email,
        password,
      }
    );

  return response.data;
}