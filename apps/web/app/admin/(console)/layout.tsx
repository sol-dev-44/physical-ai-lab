import Link from "next/link";

export const metadata = { title: "Admin", robots: { index: false } };

export default function AdminLayout({ children }: LayoutProps<"/admin">) {
  return (
    <div>
      <div className="mb-8 flex items-center gap-4 border-b border-line pb-3 text-sm">
        <Link href="/admin" className="font-semibold">
          Admin
        </Link>
        <form action="/auth/signout" method="post" className="ml-auto">
          <button type="submit" className="text-muted hover:text-fg">
            Sign out
          </button>
        </form>
      </div>
      {children}
    </div>
  );
}
