type AlertProps = {
  variant?: "error" | "success" | "info";
  message: string;
  onDismiss?: () => void;
};

const styles = {
  error: "border-library-rust/30 bg-library-rust/10 text-library-rust",
  success: "border-library-forest/30 bg-library-forest/10 text-library-forest",
  info: "border-library-amber/30 bg-library-amber/10 text-library-amber",
};

export default function Alert({
  variant = "error",
  message,
  onDismiss,
}: AlertProps) {
  return (
    <div
      className={`mb-4 flex items-start justify-between gap-3 rounded-lg border px-4 py-3 text-sm ${styles[variant]}`}
      role="alert"
    >
      <span>{message}</span>
      {onDismiss && (
        <button
          type="button"
          onClick={onDismiss}
          className="shrink-0 opacity-70 hover:opacity-100"
          aria-label="Dismiss"
        >
          ×
        </button>
      )}
    </div>
  );
}
