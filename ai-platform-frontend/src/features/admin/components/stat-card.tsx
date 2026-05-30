import { LucideIcon } from "lucide-react";

type StatCardProps = {
  title: string;
  value: string | number;
  trend?: string;
  icon: LucideIcon;
};

export function StatCard({
  title,
  value,
  trend,
  icon: Icon,
}: StatCardProps) {
  return (
    <div
      className="
        rounded-2xl
        border
        border-zinc-200
        bg-white
        p-6
        shadow-sm
        transition
        hover:shadow-md
      "
    >
      <div className="flex items-center justify-between">

        <div>

          <p
            className="
              text-sm
              font-medium
              text-zinc-500
            "
          >
            {title}
          </p>

          <h2
            className="
              mt-2
              text-3xl
              font-bold
            "
          >
            {value}
          </h2>

          {trend && (
            <p
              className="
                mt-2
                text-sm
                text-green-600
              "
            >
              {trend}
            </p>
          )}

        </div>

        <div
          className="
            rounded-xl
            bg-zinc-100
            p-3
          "
        >
          <Icon size={24} />
        </div>

      </div>
    </div>
  );
}