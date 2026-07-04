"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/", label: "Dashboard" },
  { href: "/books", label: "Books" },
  { href: "/members", label: "Members" },
  { href: "/borrowings", label: "Borrowings" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex w-64 shrink-0 flex-col border-r border-library-border bg-library-paper">
      <div className="border-b border-library-border px-6 py-5">
        <p className="text-xs font-semibold uppercase tracking-widest text-library-sage">
          Neighborhood
        </p>
        <h1 className="font-serif text-xl font-bold text-library-forest">
          Library
        </h1>
      </div>
      <nav className="flex flex-1 flex-col gap-1 p-4">
        {navItems.map((item) => {
          const active =
            item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                active
                  ? "bg-library-forest text-white"
                  : "text-library-ink hover:bg-library-cream"
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="border-t border-library-border px-4 py-4 text-xs text-library-sage">
        Staff portal · REST API
      </div>
    </aside>
  );
}
