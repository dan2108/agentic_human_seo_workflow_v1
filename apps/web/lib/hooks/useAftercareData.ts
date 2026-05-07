"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api/client";

// useAftercareData - fetches Day 7 / 30 / 90 reports for a job
export function useAftercareData(jobId: string) {
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    api.aftercare.getReports(jobId).then((data: any) => { setReports(data); setLoading(false); });
  }, [jobId]);
  return { reports, loading };
}
