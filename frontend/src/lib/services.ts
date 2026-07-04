import type {
  Book,
  BookAvailability,
  BookCreate,
  BookUpdate,
  Borrowing,
  BorrowingCreate,
  Member,
  MemberCreate,
  MemberUpdate,
} from "./types";
import { api } from "./api";

export const booksApi = {
  list: () => api.get<Book[]>("/books/"),
  get: (id: number) => api.get<Book>(`/books/${id}`),
  create: (data: BookCreate) => api.post<Book>("/books/", data),
  update: (id: number, data: BookUpdate) =>
    api.patch<Book>(`/books/${id}`, data),
  delete: (id: number) => api.delete(`/books/${id}`),
  borrowings: (id: number) =>
    api.get<Borrowing[]>(`/books/${id}/borrowings`),
  currentBorrower: (id: number) =>
    api.get<Member | null>(`/books/${id}/current-borrower`),
  availability: (id: number) =>
    api.get<BookAvailability>(`/books/${id}/availability`),
};

export const membersApi = {
  list: () => api.get<Member[]>("/members/"),
  get: (id: number) => api.get<Member>(`/members/${id}`),
  create: (data: MemberCreate) => api.post<Member>("/members/", data),
  update: (id: number, data: MemberUpdate) =>
    api.patch<Member>(`/members/${id}`, data),
  delete: (id: number) => api.delete(`/members/${id}`),
  borrowings: (id: number) =>
    api.get<Borrowing[]>(`/members/${id}/borrowings`),
  activeBorrowings: (id: number) =>
    api.get<Borrowing[]>(`/members/${id}/active-borrowings`),
};

export const borrowingsApi = {
  list: () => api.get<Borrowing[]>("/borrowings/"),
  get: (id: number) => api.get<Borrowing>(`/borrowings/${id}`),
  create: (data: BorrowingCreate) =>
    api.post<Borrowing>("/borrowings/", data),
  returnBook: (id: number) =>
    api.patch<Borrowing>(`/borrowings/${id}/return`),
  returned: () => api.get<Borrowing[]>("/borrowings/returned"),
};
