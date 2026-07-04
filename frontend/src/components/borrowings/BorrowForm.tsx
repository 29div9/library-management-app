"use client";

import { useState } from "react";
import type { Book, Member } from "@/lib/types";
import { bookLabel } from "@/lib/format";

type BorrowFormProps = {
  books: Book[];
  members: Member[];
  onSubmit: (bookId: number, memberId: number) => Promise<void>;
  onCancel: () => void;
};

export default function BorrowForm({
  books,
  members,
  onSubmit,
  onCancel,
}: BorrowFormProps) {
  const activeMembers = members.filter((m) => m.is_active);

  const [bookId, setBookId] = useState<number>(
    books[0]?.id ?? 0,
  );
  const [memberId, setMemberId] = useState<number>(
    activeMembers[0]?.id ?? 0,
  );
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!bookId || !memberId) return;
    setSubmitting(true);
    try {
      await onSubmit(bookId, memberId);
    } finally {
      setSubmitting(false);
    }
  };

  const noBooks = books.length === 0;
  const noMembers = activeMembers.length === 0;

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {noBooks && (
        <p className="rounded-md bg-library-amber/10 px-3 py-2 text-sm text-library-amber">
          All books are currently checked out.
        </p>
      )}
      {noMembers && (
        <p className="rounded-md bg-library-amber/10 px-3 py-2 text-sm text-library-amber">
          No active members available. Add or activate a member first.
        </p>
      )}
      <div>
        <label className="label" htmlFor="borrow-book">
          Book
        </label>
        <select
          id="borrow-book"
          className="input"
          value={bookId || ""}
          onChange={(e) => setBookId(Number(e.target.value))}
          required
          disabled={noBooks}
        >
          {books.map((book) => (
            <option key={book.id} value={book.id}>
              {bookLabel(book, book.id)}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label className="label" htmlFor="borrow-member">
          Member
        </label>
        <select
          id="borrow-member"
          className="input"
          value={memberId || ""}
          onChange={(e) => setMemberId(Number(e.target.value))}
          required
          disabled={noMembers}
        >
          {activeMembers.map((member) => (
            <option key={member.id} value={member.id}>
              {member.name} ({member.contact})
            </option>
          ))}
        </select>
      </div>
      <div className="flex justify-end gap-2 pt-2">
        <button type="button" className="btn-secondary" onClick={onCancel}>
          Cancel
        </button>
        <button
          type="submit"
          className="btn-primary"
          disabled={submitting || noBooks || noMembers}
        >
          {submitting ? "Recording…" : "Record Borrowing"}
        </button>
      </div>
    </form>
  );
}
