import { apiClient }
  from "@/services/api/client";

export async function forgotPassword(
  email: string
) {

  const response =
    await apiClient.post(

      "/auth/forgot-password",

      {
        email,
      }
    );

  return response.data;
}