"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import Alert from "@/components/Alert";
import LoadingSpinner from "@/components/LoadingSpinner";
import PageHeader from "@/components/PageHeader";
import { isActive, isOverdue } from "@/lib/format";
import { booksApi, borrowingsApi, membersApi } from "@/lib/services";
import type { Book, Borrowing, Member } from "@/lib/types";
import { ApiRequestError } from "@/lib/api";

type Stats = {
  books: number;
  members: number;
  activeBorrowings: number;
  overdueBorrowings: number;
};

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [recentBorrowings, setRecentBorrowings] = useState<Borrowing[]>([]);
  const [books, setBooks] = useState<Book[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [booksData, membersData, borrowingsData] = await Promise.all([
        booksApi.list(),
        membersApi.list(),
        borrowingsApi.list(),
      ]);
      const active = borrowingsData.filter(isActive);
      const overdue = active.filter(isOverdue);
      setStats({
        books: booksData.length,
        members: membersData.length,
        activeBorrowings: active.length,
        overdueBorrowings: overdue.length,
      });
      setRecentBorrowings(
        [...borrowingsData]
          .sort(
            (a, b) =>
              new Date(b.borrow_date).getTime() -
              new Date(a.borrow_date).getTime(),
          )
          .slice(0, 5),
      );
      setBooks(booksData);
      setMembers(membersData);
    } catch (err) {
      setError(
        err instanceof ApiRequestError
          ? err.message
          : "Failed to load dashboard data.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const bookMap = new Map(books.map((b) => [b.id, b]));
  const memberMap = new Map(members.map((m) => [m.id, m]));

  return (
    <>
      <PageHeader
        title="Dashboard"
        description="Overview of books, members, and current lending activity."
      />

      {error && <Alert message={error} onDismiss={() => setError(null)} />}

      {loading ? (
        <LoadingSpinner label="Loading dashboard…" />
      ) : (
        <>
          <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label="Books" value={stats?.books ?? 0} href="/books" />
            <StatCard
              label="Members"
              value={stats?.members ?? 0}
              href="/members"
            />
            <StatCard
              label="Active Loans"
              value={stats?.activeBorrowings ?? 0}
              href="/borrowings"
            />
            <StatCard
              label="Overdue"
              value={stats?.overdueBorrowings ?? 0}
              href="/borrowings?filter=overdue"
              highlight={(stats?.overdueBorrowings ?? 0) > 0}
            />
          </div>

          <div className="card">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="font-serif text-lg font-semibold text-library-forest">
                Recent Borrowings
              </h3>
              <Link href="/borrowings" className="text-sm text-library-forest hover:underline">
                View all
              </Link>
            </div>
            {recentBorrowings.length === 0 ? (
              <p className="text-sm text-library-sage">No borrowings recorded yet.</p>
            ) : (
              <ul className="divide-y divide-library-border">
                {recentBorrowings.map((b) => (
                  <li
                    key={b.id}
                    className="flex flex-wrap items-center justify-between gap-2 py-3 text-sm"
                  >
                    <span>
                      <strong>{bookMap.get(b.book_id)?.name ?? `Book #${b.book_id}`}</strong>
                      {" · "}
                      {memberMap.get(b.member_id)?.name ?? `Member #${b.member_id}`}
                    </span>
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                        b.return_date
                          ? "bg-library-sage/15 text-library-sage"
                          : isOverdue(b)
                            ? "bg-library-rust/15 text-library-rust"
                            : "bg-library-forest/15 text-library-forest"
                      }`}
                    >
                      {b.return_date
                        ? "Returned"
                        : isOverdue(b)
                          ? "Overdue"
                          : "On loan"}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </>
      )}
    </>
  );
}

function StatCard({
  label,
  value,
  href,
  highlight,
}: {
  label: string;
  value: number;
  href: string;
  highlight?: boolean;
}) {
  return (
    <Link
      href={href}
      className={`card transition-shadow hover:shadow-md ${highlight ? "border-library-rust/40" : ""}`}
    >
      <p className="text-sm text-library-sage">{label}</p>
      <p
        className={`mt-1 font-serif text-3xl font-bold ${highlight ? "text-library-rust" : "text-library-forest"}`}
      >
        {value}
      </p>
    </Link>
  );
}
