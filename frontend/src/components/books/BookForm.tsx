"use client";

import { useState } from "react";
import type { Book, BookCreate } from "@/lib/types";

type BookFormProps = {
  initial?: Book;
  onSubmit: (data: BookCreate) => Promise<void>;
  onCancel: () => void;
};

const emptyForm: BookCreate = {
  name: "",
  author: "",
  publisher: "",
  genre: "",
};

export default function BookForm({ initial, onSubmit, onCancel }: BookFormProps) {
  const [form, setForm] = useState<BookCreate>(
    initial
      ? {
          name: initial.name,
          author: initial.author,
          publisher: initial.publisher,
          genre: initial.genre,
        }
      : emptyForm,
  );
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (field: keyof BookCreate, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await onSubmit(form);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="label" htmlFor="book-name">
          Title
        </label>
        <input
          id="book-name"
          className="input"
          value={form.name}
          onChange={(e) => handleChange("name", e.target.value)}
          required
          maxLength={100}
        />
      </div>
      <div>
        <label className="label" htmlFor="book-author">
          Author
        </label>
        <input
          id="book-author"
          className="input"
          value={form.author}
          onChange={(e) => handleChange("author", e.target.value)}
          required
        />
      </div>
      <div>
        <label className="label" htmlFor="book-publisher">
          Publisher
        </label>
        <input
          id="book-publisher"
          className="input"
          value={form.publisher}
          onChange={(e) => handleChange("publisher", e.target.value)}
          required
        />
      </div>
      <div>
        <label className="label" htmlFor="book-genre">
          Genre
        </label>
        <input
          id="book-genre"
          className="input"
          value={form.genre}
          onChange={(e) => handleChange("genre", e.target.value)}
          required
        />
      </div>
      <div className="flex justify-end gap-2 pt-2">
        <button type="button" className="btn-secondary" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="btn-primary" disabled={submitting}>
          {submitting ? "Saving…" : initial ? "Update Book" : "Add Book"}
        </button>
      </div>
    </form>
  );
}
