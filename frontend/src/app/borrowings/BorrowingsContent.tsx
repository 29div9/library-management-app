"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import Alert from "@/components/Alert";
import BorrowForm from "@/components/borrowings/BorrowForm";
import EmptyState from "@/components/EmptyState";
import LoadingSpinner from "@/components/LoadingSpinner";
import Modal from "@/components/Modal";
import PageHeader from "@/components/PageHeader";
import {
  bookLabel,
  buildLookupMap,
  formatDateTime,
  isActive,
  isOverdue,
  memberLabel,
} from "@/lib/format";
import { booksApi, borrowingsApi, membersApi } from "@/lib/services";
import type { Book, Borrowing, Member } from "@/lib/types";
import { ApiRequestError } from "@/lib/api";

type Filter = "all" | "active" | "overdue" | "returned";

export default function BorrowingsContent() {
  const searchParams = useSearchParams();
  const initialFilter = (searchParams.get("filter") as Filter) || "all";

  const [borrowings, setBorrowings] = useState<Borrowing[]>([]);
  const [returnedBorrowings, setReturnedBorrowings] = useState<Borrowing[]>([]);
  const [books, setBooks] = useState<Book[]>([]);
  const [availableBooks, setAvailableBooks] = useState<Book[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [filter, setFilter] = useState<Filter>(
    ["all", "active", "overdue", "returned"].includes(initialFilter)
      ? initialFilter
      : "all",
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [borrowModalOpen, setBorrowModalOpen] = useState(false);
  const [returningId, setReturningId] = useState<number | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [borrowingsData, booksData, membersData] = await Promise.all([
        borrowingsApi.list(),
        booksApi.list(),
        membersApi.list(),
      ]);
      setBorrowings(borrowingsData);
      const availability = await Promise.all(
        booksData.map(async (book) => ({
          book,
          ...(await booksApi.availability(book.id)),
        })),
      );
      setBooks(booksData);
      setAvailableBooks(
        availability.filter(({ available }) => available).map(({ book }) => book),
      );
      setMembers(membersData);
    } catch (err) {
      setError(
        err instanceof ApiRequestError
          ? err.message
          : "Failed to load borrowings.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const bookMap = useMemo(() => buildLookupMap(books), [books]);
  const memberMap = useMemo(() => buildLookupMap(members), [members]);

  const filtered = useMemo(() => {
    let list = [
      ...(filter === "returned" ? returnedBorrowings : borrowings),
    ].sort(
      (a, b) =>
        new Date(b.borrow_date).getTime() - new Date(a.borrow_date).getTime(),
    );
    switch (filter) {
      case "active":
        list = list.filter(isActive);
        break;
      case "overdue":
        list = list.filter((b) => isOverdue(b));
        break;
    }
    return list;
  }, [borrowings, filter, returnedBorrowings]);

  useEffect(() => {
    if (filter !== "returned") return;

    setLoading(true);
    borrowingsApi
      .returned()
      .then(setReturnedBorrowings)
      .catch((err) =>
        setError(
          err instanceof ApiRequestError
            ? err.message
            : "Failed to load returned borrowings.",
        ),
      )
      .finally(() => setLoading(false));
  }, [filter]);

  const handleBorrow = async (bookId: number, memberId: number) => {
    await borrowingsApi.create({ book_id: bookId, member_id: memberId });
    setSuccess("Borrowing recorded.");
    setBorrowModalOpen(false);
    await load();
  };

  const handleReturn = async (borrowing: Borrowing) => {
    if (
      !confirm(
        `Mark "${bookLabel(bookMap.get(borrowing.book_id), borrowing.book_id)}" as returned?`,
      )
    ) {
      return;
    }
    setReturningId(borrowing.id);
    setError(null);
    try {
      const updated = await borrowingsApi.returnBook(borrowing.id);
      const fineMsg =
        updated.fine && updated.fine > 0 ? ` Fine: ₹${updated.fine}.` : "";
      setSuccess(`Book returned successfully.${fineMsg}`);
      await load();
    } catch (err) {
      setError(
        err instanceof ApiRequestError
          ? err.message
          : "Failed to return book.",
      );
    } finally {
      setReturningId(null);
    }
  };

  const filters: { key: Filter; label: string }[] = [
    { key: "all", label: "All" },
    { key: "active", label: "Active" },
    { key: "overdue", label: "Overdue" },
    { key: "returned", label: "Returned" },
  ];

  return (
    <>
      <PageHeader
        title="Borrowings"
        description="Record loans and returns, and track overdue items."
        action={
          <button
            type="button"
            className="btn-primary"
            onClick={() => setBorrowModalOpen(true)}
          >
            New Borrowing
          </button>
        }
      />

      {error && <Alert message={error} onDismiss={() => setError(null)} />}
      {success && (
        <Alert
          variant="success"
          message={success}
          onDismiss={() => setSuccess(null)}
        />
      )}

      <div className="mb-4 flex flex-wrap gap-2">
        {filters.map((f) => (
          <button
            key={f.key}
            type="button"
            onClick={() => setFilter(f.key)}
            className={`rounded-full px-3 py-1 text-sm font-medium transition-colors ${
              filter === f.key
                ? "bg-library-forest text-white"
                : "bg-library-paper text-library-sage ring-1 ring-library-border hover:bg-library-cream"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {loading ? (
        <LoadingSpinner label="Loading borrowings…" />
      ) : filtered.length === 0 ? (
        <EmptyState
          title="No borrowings found"
          description={
            filter === "all"
              ? "Record a borrowing to get started."
              : `No ${filter} borrowings at the moment.`
          }
          action={
            filter === "all" ? (
              <button
                type="button"
                className="btn-primary"
                onClick={() => setBorrowModalOpen(true)}
              >
                New Borrowing
              </button>
            ) : undefined
          }
        />
      ) : (
        <div className="overflow-hidden rounded-xl border border-library-border bg-library-paper">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-library-border bg-library-cream/60">
              <tr>
                <th className="px-4 py-3 font-medium">Book</th>
                <th className="px-4 py-3 font-medium">Member</th>
                <th className="px-4 py-3 font-medium">Borrowed</th>
                <th className="px-4 py-3 font-medium">Due</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-library-border">
              {filtered.map((b) => (
                <tr key={b.id} className="hover:bg-library-cream/40">
                  <td className="px-4 py-3 font-medium">
                    {bookLabel(bookMap.get(b.book_id), b.book_id)}
                  </td>
                  <td className="px-4 py-3">
                    {memberLabel(memberMap.get(b.member_id), b.member_id)}
                  </td>
                  <td className="px-4 py-3">{formatDateTime(b.borrow_date)}</td>
                  <td className="px-4 py-3">{formatDateTime(b.due_date)}</td>
                  <td className="px-4 py-3">
                    {b.return_date ? (
                      <span className="text-library-sage">
                        Returned
                        {b.fine != null && b.fine > 0 && (
                          <span className="ml-1 text-library-rust">
                            (Fine ₹{b.fine})
                          </span>
                        )}
                      </span>
                    ) : isOverdue(b) ? (
                      <span className="rounded-full bg-library-rust/15 px-2 py-0.5 text-xs font-medium text-library-rust">
                        Overdue
                      </span>
                    ) : (
                      <span className="rounded-full bg-library-forest/15 px-2 py-0.5 text-xs font-medium text-library-forest">
                        On loan
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right">
                    {!b.return_date && (
                      <button
                        type="button"
                        className="btn-secondary px-3 py-1"
                        disabled={returningId === b.id}
                        onClick={() => handleReturn(b)}
                      >
                        {returningId === b.id ? "Returning…" : "Return"}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal
        open={borrowModalOpen}
        title="New Borrowing"
        onClose={() => setBorrowModalOpen(false)}
      >
        <BorrowFormWrapper
          books={availableBooks}
          members={members}
          onSubmit={handleBorrow}
          onCancel={() => setBorrowModalOpen(false)}
          onError={setError}
        />
      </Modal>
    </>
  );
}

function BorrowFormWrapper({
  books,
  members,
  onSubmit,
  onCancel,
  onError,
}: {
  books: Book[];
  members: Member[];
  onSubmit: (bookId: number, memberId: number) => Promise<void>;
  onCancel: () => void;
  onError: (msg: string) => void;
}) {
  const wrappedSubmit = async (bookId: number, memberId: number) => {
    try {
      await onSubmit(bookId, memberId);
    } catch (err) {
      onError(
        err instanceof ApiRequestError
          ? err.message
          : "Failed to record borrowing.",
      );
    }
  };

  return (
    <BorrowForm
      books={books}
      members={members}
      onSubmit={wrappedSubmit}
      onCancel={onCancel}
    />
  );
}
