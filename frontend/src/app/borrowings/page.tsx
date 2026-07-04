"use client";

import { Suspense } from "react";
import LoadingSpinner from "@/components/LoadingSpinner";
import BorrowingsContent from "./BorrowingsContent";

export default function BorrowingsPage() {
  return (
    <Suspense fallback={<LoadingSpinner label="Loading borrowings…" />}>
      <BorrowingsContent />
    </Suspense>
  );
}
