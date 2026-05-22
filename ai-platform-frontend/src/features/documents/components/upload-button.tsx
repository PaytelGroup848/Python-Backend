"use client";

import {
  useRef,
  useState,
} from "react";

import {
  Upload,
} from "lucide-react";

import {
  uploadDocument,
} from "../services/document-service";

export function UploadButton() {

  const inputRef =
    useRef<HTMLInputElement>(null);

  const [loading, setLoading] =
    useState(false);

  const [uploadedFile, setUploadedFile] =
    useState("");

  async function handleUpload(
    file: File
  ) {

    try {

      setLoading(true);

      const response =
        await uploadDocument(
          file
        );

      setUploadedFile(
        response.filename
      );

      alert(
        "Document uploaded successfully"
      );

    } catch (error) {

      console.error(error);

      alert(
        "Upload failed"
      );

    } finally {

      setLoading(false);
    }
  }

  return (
    <div
      className="
        flex
        flex-col
        gap-4
      "
    >
      {/* BUTTON */}

      <button
        onClick={() =>
          inputRef.current?.click()
        }

        disabled={loading}

        className="
          flex
          items-center
          justify-center
          gap-2
          rounded-2xl
          border
          border-white/10
          bg-zinc-900
          px-5
          py-4
          text-white
          transition-all
          hover:bg-zinc-800
          disabled:opacity-50
        "
      >
        <Upload size={18} />

        {loading
          ? "Uploading..."
          : "Upload Document"}
      </button>

      {/* FILE INPUT */}

      <input
        ref={inputRef}

        type="file"

        accept="
          .pdf,
          .docx,
          .txt,
          .csv,
          .xlsx,
          .pptx,
          .png,
          .jpg,
          .jpeg
        "

        className="hidden"

        onChange={(e) => {

          const file =
            e.target.files?.[0];

          if (file) {

            handleUpload(file);
          }
        }}
      />

      {/* SUCCESS */}

      {uploadedFile && (

        <div
          className="
            rounded-xl
            border
            border-emerald-500/20
            bg-emerald-500/10
            px-4
            py-3
            text-sm
            text-emerald-400
          "
        >
          Uploaded:
          {" "}
          {uploadedFile}
        </div>
      )}
    </div>
  );
}