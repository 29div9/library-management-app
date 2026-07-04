"use client";

import { useState } from "react";
import type { Member, MemberCreate } from "@/lib/types";

type MemberFormProps = {
  initial?: Member;
  onSubmit: (data: MemberCreate) => Promise<void>;
  onCancel: () => void;
};

const emptyForm: MemberCreate = {
  name: "",
  contact: "",
  address: "",
};

export default function MemberForm({
  initial,
  onSubmit,
  onCancel,
}: MemberFormProps) {
  const [form, setForm] = useState<MemberCreate>(
    initial
      ? {
          name: initial.name,
          contact: initial.contact,
          address: initial.address ?? "",
        }
      : emptyForm,
  );
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (field: keyof MemberCreate, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await onSubmit({
        ...form,
        address: form.address?.trim() ? form.address.trim() : null,
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="label" htmlFor="member-name">
          Name
        </label>
        <input
          id="member-name"
          className="input"
          value={form.name}
          onChange={(e) => handleChange("name", e.target.value)}
          required
          maxLength={50}
        />
      </div>
      <div>
        <label className="label" htmlFor="member-contact">
          Contact
        </label>
        <input
          id="member-contact"
          className="input"
          value={form.contact}
          onChange={(e) => handleChange("contact", e.target.value)}
          required
          minLength={10}
          maxLength={20}
          pattern="^\+?[1-9]\d{9,19}$"
          title="Enter a valid phone number (10–20 digits, optional + prefix)"
          placeholder="9876543210"
        />
      </div>
      <div>
        <label className="label" htmlFor="member-address">
          Address <span className="font-normal text-library-sage">(optional)</span>
        </label>
        <textarea
          id="member-address"
          className="input min-h-[80px] resize-y"
          value={form.address ?? ""}
          onChange={(e) => handleChange("address", e.target.value)}
          rows={3}
        />
      </div>
      <div className="flex justify-end gap-2 pt-2">
        <button type="button" className="btn-secondary" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="btn-primary" disabled={submitting}>
          {submitting ? "Saving…" : initial ? "Update Member" : "Add Member"}
        </button>
      </div>
    </form>
  );
}
