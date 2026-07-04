"use client";

import { useCallback, useEffect, useState } from "react";
import Alert from "@/components/Alert";
import EmptyState from "@/components/EmptyState";
import LoadingSpinner from "@/components/LoadingSpinner";
import MemberForm from "@/components/members/MemberForm";
import Modal from "@/components/Modal";
import PageHeader from "@/components/PageHeader";
import { bookLabel, formatDate, formatDateTime } from "@/lib/format";
import { booksApi, membersApi } from "@/lib/services";
import type { Book, Borrowing, Member, MemberCreate } from "@/lib/types";
import { ApiRequestError } from "@/lib/api";

export default function MembersPage() {
  const [members, setMembers] = useState<Member[]>([]);
  const [books, setBooks] = useState<Book[]>([]);
  const [activeCounts, setActiveCounts] = useState<Map<number, number>>(
    new Map(),
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingMember, setEditingMember] = useState<Member | null>(null);
  const [detailMember, setDetailMember] = useState<Member | null>(null);
  const [activeBorrowings, setActiveBorrowings] = useState<Borrowing[]>([]);
  const [detailLoading, setDetailLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [data, booksData] = await Promise.all([
        membersApi.list(),
        booksApi.list(),
      ]);
      setMembers(data);
      setBooks(booksData);
      const counts = await Promise.all(
        data.map(async (member) => {
          try {
            const active = await membersApi.activeBorrowings(member.id);
            return [member.id, active.length] as const;
          } catch {
            return [member.id, 0] as const;
          }
        }),
      );
      setActiveCounts(new Map(counts));
    } catch (err) {
      setError(
        err instanceof ApiRequestError ? err.message : "Failed to load members.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const openCreate = () => {
    setEditingMember(null);
    setModalOpen(true);
  };

  const openEdit = (member: Member) => {
    setEditingMember(member);
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setEditingMember(null);
  };

  const handleSubmit = async (data: MemberCreate) => {
    if (editingMember) {
      await membersApi.update(editingMember.id, data);
      setSuccess("Member updated successfully.");
    } else {
      await membersApi.create(data);
      setSuccess("Member added successfully.");
    }
    closeModal();
    await load();
  };

  const handleDelete = async (member: Member) => {
    if (!confirm(`Delete member "${member.name}"? This cannot be undone.`))
      return;
    setError(null);
    try {
      await membersApi.delete(member.id);
      setSuccess("Member deleted.");
      await load();
    } catch (err) {
      setError(
        err instanceof ApiRequestError
          ? err.message
          : "Failed to delete member.",
      );
    }
  };

  const openDetail = async (member: Member) => {
    setDetailMember(member);
    setDetailLoading(true);
    try {
      const active = await membersApi.activeBorrowings(member.id);
      setActiveBorrowings(active);
    } catch (err) {
      setError(
        err instanceof ApiRequestError
          ? err.message
          : "Failed to load active borrowings.",
      );
      setDetailMember(null);
    } finally {
      setDetailLoading(false);
    }
  };

  return (
    <>
      <PageHeader
        title="Members"
        description="Register and manage library members."
        action={
          <button type="button" className="btn-primary" onClick={openCreate}>
            Add Member
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
        <LoadingSpinner label="Loading members…" />
      ) : members.length === 0 ? (
        <EmptyState
          title="No members registered"
          description="Add your first member to enable borrowing."
          action={
            <button type="button" className="btn-primary" onClick={openCreate}>
              Add Member
            </button>
          }
        />
      ) : (
        <div className="overflow-hidden rounded-xl border border-library-border bg-library-paper">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-library-border bg-library-cream/60">
              <tr>
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Contact</th>
                <th className="px-4 py-3 font-medium">Joined</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Books Out</th>
                <th className="px-4 py-3 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-library-border">
              {members.map((member) => (
                <tr key={member.id} className="hover:bg-library-cream/40">
                  <td className="px-4 py-3 font-medium">{member.name}</td>
                  <td className="px-4 py-3">{member.contact}</td>
                  <td className="px-4 py-3">{formatDate(member.joining_date)}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                        member.is_active
                          ? "bg-library-forest/15 text-library-forest"
                          : "bg-library-sage/15 text-library-sage"
                      }`}
                    >
                      {member.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {activeCounts.get(member.id) ?? 0}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex justify-end gap-1">
                      <button
                        type="button"
                        className="btn-ghost px-2 py-1"
                        onClick={() => openDetail(member)}
                      >
                        Loans
                      </button>
                      <button
                        type="button"
                        className="btn-ghost px-2 py-1"
                        onClick={() => openEdit(member)}
                      >
                        Edit
                      </button>
                      <button
                        type="button"
                        className="btn-ghost px-2 py-1 text-library-rust"
                        onClick={() => handleDelete(member)}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal
        open={modalOpen}
        title={editingMember ? "Edit Member" : "Add Member"}
        onClose={closeModal}
      >
        <MemberFormWrapper
          initial={editingMember ?? undefined}
          onSubmit={handleSubmit}
          onCancel={closeModal}
          onError={setError}
        />
      </Modal>

      <Modal
        open={!!detailMember}
        title={detailMember ? `Active Loans — ${detailMember.name}` : "Loans"}
        onClose={() => setDetailMember(null)}
        wide
      >
        {detailLoading ? (
          <LoadingSpinner label="Loading loans…" />
        ) : activeBorrowings.length === 0 ? (
          <p className="text-sm text-library-sage">
            No books currently checked out.
          </p>
        ) : (
          <ul className="divide-y divide-library-border text-sm">
            {activeBorrowings.map((b) => {
              const book = books.find((bk) => bk.id === b.book_id);
              return (
                <li key={b.id} className="flex justify-between py-2">
                  <span>{bookLabel(book, b.book_id)}</span>
                  <span>Due {formatDateTime(b.due_date)}</span>
                </li>
              );
            })}
          </ul>
        )}
      </Modal>
    </>
  );
}

function MemberFormWrapper({
  initial,
  onSubmit,
  onCancel,
  onError,
}: {
  initial?: Member;
  onSubmit: (data: MemberCreate) => Promise<void>;
  onCancel: () => void;
  onError: (msg: string) => void;
}) {
  const wrappedSubmit = async (data: MemberCreate) => {
    try {
      await onSubmit(data);
    } catch (err) {
      onError(
        err instanceof ApiRequestError ? err.message : "Failed to save member.",
      );
    }
  };

  return (
    <MemberForm
      initial={initial}
      onSubmit={wrappedSubmit}
      onCancel={onCancel}
    />
  );
}
