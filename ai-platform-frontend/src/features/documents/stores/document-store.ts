import { create }
  from "zustand";

export interface UploadedDocument {

  filename: string;

  status:
    "uploading" |
    "uploaded" |
    "failed";
}

interface DocumentState {

  documents:
    UploadedDocument[];

  addDocument: (
    document:
      UploadedDocument
  ) => void;

  removeDocument: (
    filename: string
  ) => void;

  clearDocuments: () => void;
}

export const useDocumentStore =
  create<DocumentState>(
    (set) => ({

      documents: [],

      addDocument: (
        document
      ) =>

        set((state) => ({

          documents: [

            ...state.documents,

            document,
          ],
        })),

      removeDocument: (
        filename
      ) =>

        set((state) => ({

          documents:
            state.documents.filter(
              (doc) =>

                doc.filename !==
                filename
            ),
        })),

      clearDocuments: () =>

        set({
          documents: [],
        }),
    })
  );