

"use client";

import { useUsers }
from "@/features/admin/hooks/use-users";

import type {
  User,
} from "@/features/admin/services/user-service";

export default function UsersPage() {

  const {
    data,
    isLoading,
    error,
  } = useUsers();

  if (isLoading) {

    return (
      <div className="p-6">
        Loading users...
      </div>
    );
  }

  if (error) {

    return (
      <div className="p-6">
        Failed to load users
      </div>
    );
  }

  return (
    <div className="space-y-6">

      <div>

        <h1 className="text-3xl font-bold">
          User Management
        </h1>

        <p className="text-zinc-500">
          Platform users overview
        </p>

      </div>

      <div
        className="
          overflow-hidden
          rounded-2xl
          border
          bg-white
          shadow-sm
        "
      >

        <table className="w-full">

          <thead
            className="
              border-b
              bg-zinc-50
            "
          >
            <tr>

              <th className="p-4 text-left">
                ID
              </th>

              <th className="p-4 text-left">
                Name
              </th>

              <th className="p-4 text-left">
                Email
              </th>

              <th className="p-4 text-left">
                Role
              </th>

              <th className="p-4 text-left">
                Status
              </th>

            </tr>
          </thead>

          <tbody>

            {data?.users.map((user: User) => (

              <tr
                key={user.id}
                className="border-b"
              >

                <td className="p-4">
                  {user.id}
                </td>

                <td className="p-4">
                  {user.name}
                </td>

                <td className="p-4">
                  {user.email}
                </td>

                <td className="p-4">

                  <span
                    className="
                      rounded-full
                      bg-blue-100
                      px-3
                      py-1
                      text-sm
                      font-medium
                      text-blue-700
                    "
                  >
                    {user.role}
                  </span>

                </td>

                <td className="p-4">

                  <span
                    className={`
                      rounded-full
                      px-3
                      py-1
                      text-sm
                      font-medium
                      ${
                        user.is_active
                          ? "bg-green-100 text-green-700"
                          : "bg-red-100 text-red-700"
                      }
                    `}
                  >
                    {user.is_active
                      ? "Active"
                      : "Inactive"}
                  </span>

                </td>

              </tr>

            ))}

          </tbody>

        </table>

      </div>

    </div>
  );
}