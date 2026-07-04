"use client";

import { useCallback, useEffect, useState } from "react";
import Alert from "@/components/Alert";
import BookForm from "@/components/books/BookForm";
import EmptyState from "@/components/EmptyState";
import LoadingSpinner from "@/components/LoadingSpinner";
import Modal from "@/components/Modal";
import PageHeader from "@/components/PageHeader";
import { formatDateTime } from "@/lib/format";
import { booksApi } from "@/lib/services";
import type { Book, BookCreate, Member } from "@/lib/types";
import { ApiRequestError } from "@/lib/api";

export default function BooksPage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [borrowers, setBorrowers] = useState<Map<number, Member | null>>(
    new Map(),
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingBook, setEditingBook] = useState<Book | null>(null);
  const [historyBook, setHistoryBook] = useState<Book | null>(null);
  const [history, setHistory] = useState<
    { id: number; borrow_date: string; return_date: string | null }[]
  >([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await booksApi.list();
      setBooks(data);
      const borrowerEntries = await Promise.all(
        data.map(async (book) => {
          try {
            const borrower = await booksApi.currentBorrower(book.id);
            return [book.id, borrower] as const;
          } catch {
            return [book.id, null] as const;
          }
        }),
      );
      setBorrowers(new Map(borrowerEntries));
    } catch (err) {
      setError(
        err instanceof ApiRequestError ? err.message : "Failed to load books.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const openCreate = () => {
    setEditingBook(null);
    setModalOpen(true);
  };

  const openEdit = (book: Book) => {
    setEditingBook(book);
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setEditingBook(null);
  };

  const handleSubmit = async (data: BookCreate) => {
    try {
      if (editingBook) {
        await booksApi.update(editingBook.id, data);
        setSuccess("Book updated successfully.");
      } else {
        await booksApi.create(data);
        setSuccess("Book added successfully.");
      }
      closeModal();
      await load();
    } catch (err) {
      throw err;
    }
  };

  const handleDelete = async (book: Book) => {
    if (!confirm(`Delete "${book.name}"? This cannot be undone.`)) return;
    setError(null);
    try {
      await booksApi.delete(book.id);
      setSuccess("Book deleted.");
      await load();
    } catch (err) {
      setError(
        err instanceof ApiRequestError ? err.message : "Failed to delete book.",
      );
    }
  };

  const openHistory = async (book: Book) => {
    setHistoryBook(book);
    setHistoryLoading(true);
    try {
      const data = await booksApi.borrowings(book.id);
      setHistory(data);
    } catch (err) {
      setError(
        err instanceof ApiRequestError
          ? err.message
          : "Failed to load borrowing history.",
      );
      setHistoryBook(null);
    } finally {
      setHistoryLoading(false);
    }
  };

  return (
    <>
      <PageHeader
        title="Books"
        description="Manage the library catalogue — add, update, or remove titles."
        action={
          <button type="button" className="btn-primary" onClick={openCreate}>
            Add Book
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

      {loading ? (
        <LoadingSpinner label="Loading books…" />
      ) : books.length === 0 ? (
        <EmptyState
          title="No books in the catalogue"
          description="Add your first book to get started."
          action={
            <button type="button" className="btn-primary" onClick={openCreate}>
              Add Book
            </button>
          }
        />
      ) : (
        <div className="overflow-hidden rounded-xl border border-library-border bg-library-paper">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-library-border bg-library-cream/60">
              <tr>
                <th className="px-4 py-3 font-medium">Title</th>
                <th className="px-4 py-3 font-medium">Author</th>
                <th className="px-4 py-3 font-medium">Publisher</th>
                <th className="px-4 py-3 font-medium">Genre</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-library-border">
              {books.map((book) => {
                const borrower = borrowers.get(book.id);
                return (
                  <tr key={book.id} className="hover:bg-library-cream/40">
                    <td className="px-4 py-3 font-medium">{book.name}</td>
                    <td className="px-4 py-3">{book.author}</td>
                    <td className="px-4 py-3">{book.publisher}</td>
                    <td className="px-4 py-3">{book.genre}</td>
                    <td className="px-4 py-3">
                      {borrower ? (
                        <span className="rounded-full bg-library-amber/15 px-2 py-0.5 text-xs font-medium text-library-amber">
                          On loan · {borrower.name}
                        </span>
                      ) : (
                        <span className="rounded-full bg-library-forest/15 px-2 py-0.5 text-xs font-medium text-library-forest">
                          Available
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex justify-end gap-1">
                        <button
                          type="button"
                          className="btn-ghost px-2 py-1"
                          onClick={() => openHistory(book)}
                        >
                          History
                        </button>
                        <button
                          type="button"
                          className="btn-ghost px-2 py-1"
                          onClick={() => openEdit(book)}
                        >
                          Edit
                        </button>
                        <button
                          type="button"
                          className="btn-ghost px-2 py-1 text-library-rust"
                          onClick={() => handleDelete(book)}
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <Modal
        open={modalOpen}
        title={editingBook ? "Edit Book" : "Add Book"}
        onClose={closeModal}
      >
        <BookFormWrapper
          initial={editingBook ?? undefined}
          onSubmit={handleSubmit}
          onCancel={closeModal}
          onError={setError}
        />
      </Modal>

      <Modal
        open={!!historyBook}
        title={historyBook ? `History — ${historyBook.name}` : "History"}
        onClose={() => setHistoryBook(null)}
        wide
      >
        {historyLoading ? (
          <LoadingSpinner label="Loading history…" />
        ) : history.length === 0 ? (
          <p className="text-sm text-library-sage">No borrowing history.</p>
        ) : (
          <ul className="divide-y divide-library-border text-sm">
            {history.map((h) => (
              <li key={h.id} className="flex justify-between py-2">
                <span>Borrowed {formatDateTime(h.borrow_date)}</span>
                <span>
                  {h.return_date
                    ? `Returned ${formatDateTime(h.return_date)}`
                    : "Still on loan"}
                </span>
              </li>
            ))}
          </ul>
        )}
      </Modal>
    </>
  );
}

function BookFormWrapper({
  initial,
  onSubmit,
  onCancel,
  onError,
}: {
  initial?: Book;
  onSubmit: (data: BookCreate) => Promise<void>;
  onCancel: () => void;
  onError: (msg: string) => void;
}) {
  const wrappedSubmit = async (data: BookCreate) => {
    try {
      await onSubmit(data);
    } catch (err) {
      onError(
        err instanceof ApiRequestError ? err.message : "Failed to save book.",
      );
    }
  };

  return (
    <BookForm initial={initial} onSubmit={wrappedSubmit} onCancel={onCancel} />
  );
}
