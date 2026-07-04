type EmptyStateProps = {
  title: string;
  description?: string;
  action?: React.ReactNode;
};

export default function EmptyState({
  title,
  description,
  action,
}: EmptyStateProps) {
  return (
    <div className="rounded-xl border border-dashed border-library-border bg-library-paper px-6 py-12 text-center">
      <p className="font-medium text-library-ink">{title}</p>
      {description && (
        <p className="mt-1 text-sm text-library-sage">{description}</p>
      )}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
