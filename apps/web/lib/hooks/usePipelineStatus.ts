"use client";
import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase/client";

interface JobStepPayload {
  step_id: string;
  status: string;
}

export function usePipelineStatus(jobId: string) {
  const [steps, setSteps] = useState<Record<string, string>>({});

  useEffect(() => {
    if (!jobId) return;
    const supabase = createClient();
    const channel = supabase
      .channel(`job-${jobId}`)
      .on(
        "postgres_changes",
        { event: "*", schema: "public", table: "job_steps", filter: `job_id=eq.${jobId}` },
        (payload) => {
          const row = payload.new as JobStepPayload;
          setSteps((prev) => ({ ...prev, [row.step_id]: row.status }));
        }
      )
      .subscribe();
    return () => { supabase.removeChannel(channel); };
  }, [jobId]);

  return steps;
}
