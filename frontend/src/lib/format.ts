import type { Book, Borrowing, Member } from "./types";

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function isOverdue(borrowing: Borrowing): boolean {
  if (borrowing.return_date) return false;
  return new Date() > new Date(borrowing.due_date);
}

export function isActive(borrowing: Borrowing): boolean {
  return borrowing.return_date === null;
}

export function bookLabel(book: Book | undefined, bookId: number): string {
  if (!book) return `Book #${bookId}`;
  return `${book.name} — ${book.author}`;
}

export function memberLabel(member: Member | undefined, memberId: number): string {
  if (!member) return `Member #${memberId}`;
  return member.name;
}

export function buildLookupMap<T extends { id: number }>(
  items: T[],
): Map<number, T> {
  return new Map(items.map((item) => [item.id, item]));
}
