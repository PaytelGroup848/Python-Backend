import { apiClient }
  from "@/services/api/client";

export async function uploadDocument(
  file: File
) {

  const formData =
    new FormData();

  formData.append(
    "file",
    file
  );

  const response =
    await apiClient.post(

      "/pdf/upload-pdf",

      formData,

      {
        headers: {
          "Content-Type":
            "multipart/form-data",
        },
      }
    );

  return response.data;
}