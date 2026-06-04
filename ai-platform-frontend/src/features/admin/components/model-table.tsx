"use client";

import { useModels } from "../hooks/use-models";

import { useState } from "react";

import { modelService } from "../services/model-service";

import { CreateModelModal } from "./create-model-modal";

import { EditModelModal } from "./edit-model-modal";

export function ModelTable() {

  const [open, setOpen] =
    useState(false);

  const [editOpen, setEditOpen] =
    useState(false);

const [selectedModel, setSelectedModel] =
  useState<any>(null);

  const {
    models,
    loading,
    refresh
  } = useModels();

  if (loading) {
    return (
      <div className="rounded-xl border bg-white p-6">
        Loading models...
      </div>
    );
  }

  return (

    <div className="space-y-6">

      {/* Stats */}

      <div className="grid gap-4 md:grid-cols-3">

        <div className="rounded-xl border bg-white p-5">
          <p className="text-sm text-zinc-500">
            Total Models
          </p>

          <h2 className="mt-2 text-3xl font-bold">
            {models.length}
          </h2>
        </div>

        <div className="rounded-xl border bg-white p-5">
          <p className="text-sm text-zinc-500">
            Active Models
          </p>

          <h2 className="mt-2 text-3xl font-bold">
            {
              models.filter(
                model => model.is_active
              ).length
            }
          </h2>
        </div>

        <div className="rounded-xl border bg-white p-5">
          <p className="text-sm text-zinc-500">
            Providers
          </p>

          <h2 className="mt-2 text-3xl font-bold">
            {
              new Set(
                models.map(
                  model => model.provider
                )
              ).size
            }
          </h2>
        </div>

      </div>

      {/* Table */}

      <div className="rounded-xl border bg-white overflow-hidden">

        <div className="flex items-center justify-between border-b p-4">

          <div>

            <h2 className="font-semibold text-lg">
              Registered Models
            </h2>

            <p className="text-sm text-zinc-500">
              Available AI models
            </p>

          </div>

          <button

            onClick={() =>
                setOpen(true)
            }

            className="
               rounded-lg
               bg-black
               px-4
               py-2
               text-white
            "
        >
            Add Model
        </button>

        </div>

        <table className="w-full">

          <thead>

            <tr className="border-b bg-zinc-50">

              <th className="p-4 text-left">
                Model
              </th>

              <th className="p-4 text-left">
                Provider
              </th>

              <th className="p-4 text-left">
                Status
              </th>

              <th className="p-4 text-right">
                Actions
              </th>

            </tr>

          </thead>

          <tbody>

            {models.map(
              (model) => (

                <tr
                  key={model.id}
                  className="border-b"
                >

                  <td className="p-4">

                    <div className="font-medium">
                      {model.model_name}
                    </div>

                  </td>

                  <td className="p-4">

                    <span
                      className="
                        rounded-full
                        bg-blue-100
                        px-3
                        py-1
                        text-sm
                        text-blue-700
                      "
                    >
                      {model.provider}
                    </span>

                  </td>

                  <td className="p-4">

                    <span
                      className={`
                        rounded-full
                        px-3
                        py-1
                        text-sm
                        ${
                          model.is_active
                            ? "bg-green-100 text-green-700"
                            : "bg-red-100 text-red-700"
                        }
                      `}
                    >
                      {
                        model.is_active
                          ? "Active"
                          : "Disabled"
                      }
                    </span>

                  </td>

                  <td className="p-4 text-right">

                    <div className="flex justify-end gap-2">

                      <button

                        onClick={() => {

                          setSelectedModel(
                            model
                          );

                          setEditOpen(
                            true
                          );
                        }}

                        className="
                          rounded-lg
                          border
                          px-3
                          py-1
                        "
                      >
                        Edit
                      </button>

                      <button

                        onClick={async () => {

                          const confirmed =
                            window.confirm(

                              `Delete model ${model.model_name}?`
                            );

                          if (!confirmed) {
                            return;
                          }

                          try {

                            await modelService.deleteModel(
                              model.model_name
                            );

                            await refresh();

                          } catch (error) {

                            console.error(error);

                            alert(
                              "Failed to delete model"
                            );
                          }
                        }}

                        className="
                          rounded-lg
                          border
                          border-red-500
                          px-3
                          py-1
                          text-red-500
                        "
                      >
                        Delete
                      </button>

                    </div>

                  </td>

                </tr>

              )
            )}

          </tbody>

        </table>

      </div>

      <CreateModelModal

        open={open}

        onClose={() =>
          setOpen(false)
        }

        onSubmit={async (
          payload
        ) => {

          await modelService.createModel(
            payload
          );

          await refresh();
        }}
      />

      <EditModelModal

        open={editOpen}

        model={selectedModel}

        onClose={() =>
          setEditOpen(false)
        }

        onSubmit={async (
          payload
        ) => {

          await modelService.updateModel(

            selectedModel.model_name,

            payload
          );

          await refresh();
        }}
      />

    </div>

  );
}