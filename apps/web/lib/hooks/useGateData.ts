"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api/client";

// useGateData - fetches gate data and polls for status changes
export function useGateData(gateId: string) {
  const [gate, setGate] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    api.gates.get(gateId).then((data) => { setGate(data); setLoading(false); });
  }, [gateId]);
  return { gate, loading };
}
