export type Book = {
  id: number;
  name: string;
  author: string;
  publisher: string;
  genre: string;
};

export type BookCreate = Omit<Book, "id">;
export type BookUpdate = Partial<BookCreate>;

export type BookAvailability = {
  available: boolean;
};

export type Member = {
  id: number;
  name: string;
  joining_date: string;
  exit_date: string | null;
  is_active: boolean;
  contact: string;
  address: string | null;
};

export type MemberCreate = {
  name: string;
  contact: string;
  address?: string | null;
};

export type MemberUpdate = Partial<MemberCreate>;

export type Borrowing = {
  id: number;
  book_id: number;
  member_id: number;
  borrow_date: string;
  due_date: string;
  return_date: string | null;
  fine: number | null;
};

export type BorrowingCreate = {
  book_id: number;
  member_id: number;
};

export type ValidationError = {
  loc: (string | number)[];
  msg: string;
  type: string;
};

export type ApiError = {
  detail: string | ValidationError[];
};
