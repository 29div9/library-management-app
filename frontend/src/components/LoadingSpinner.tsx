export default function LoadingSpinner({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-library-sage">
      <div
        className="h-8 w-8 animate-spin rounded-full border-2 border-library-border border-t-library-forest"
        role="status"
        aria-label={label}
      />
      <p className="text-sm">{label}</p>
    </div>
  );
}
