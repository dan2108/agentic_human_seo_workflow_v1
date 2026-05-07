// TODO: deep-link to a specific job node in the pipeline
export default function PipelineJobPage({ params }: { params: { jobId: string } }) {
  return <div>Job {params.jobId}</div>;
}
