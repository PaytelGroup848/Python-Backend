export function QueueStatusCard() {
  return (
    <div className="rounded-xl border p-6">

      <h2 className="mb-4 text-xl font-semibold">
        Queue Status
      </h2>

      <div className="space-y-3">

        <div className="flex justify-between">
          <span>chat_requests</span>
          <span>0</span>
        </div>

        <div className="flex justify-between">
          <span>chat_responses</span>
          <span>0</span>
        </div>

        <div className="flex justify-between">
          <span>rag_tasks</span>
          <span>0</span>
        </div>

        <div className="flex justify-between">
          <span>embedding_requests</span>
          <span>0</span>
        </div>

      </div>

    </div>
  );
}