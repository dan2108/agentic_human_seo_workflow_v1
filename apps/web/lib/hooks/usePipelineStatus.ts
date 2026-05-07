"use client";
import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase/client";

// usePipelineStatus - subscribes to Supabase Realtime for live job step updates
export function usePipelineStatus(jobId: string) {
  const [steps, setSteps] = useState<Record<string, string>>({});

  useEffect(() => {
    const supabase = createClient();
    const channel = supabase
      .channel(`job-${jobId}`)
      .on("postgres_changes", { event: "*", schema: "public", table: "job_steps", filter: `job_id=eq.${jobId}` },
        (payload) => {
          setSteps((prev) => ({ ...prev, [(payload.new as any).step_id]: (payload.new as any).status }));
        }
      )
      .subscribe();
    return () => { supabase.removeChannel(channel); };
  }, [jobId]);

  return steps;
}
