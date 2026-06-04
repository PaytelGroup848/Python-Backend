import {
  ModelTable
} from "@/features/admin/components/model-table";

export default function ModelsPage() {

  return (

    <div className="space-y-6">

      <div>

        <h1 className="text-2xl font-bold">

          Models

        </h1>

        <p>

          Manage AI Models
        </p>

      </div>

      <ModelTable />

    </div>
  );
}