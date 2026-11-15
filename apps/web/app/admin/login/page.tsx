import { Suspense } from "react";
import { PageHeader } from "@/components/page-header";
import { sendMagicLink } from "./actions";
import { control } from "@/lib/design/controls";

export const metadata = { title: "Admin sign in", robots: { index: false } };

const messages: Record<string, string> = {
  "not-configured": "Supabase is not configured for this deployment.",
  "not-allowed": "That account is not an admin.",
  link: "That sign-in link is invalid or expired.",
};

async function Status({ searchParams }: { searchParams: PageProps<"/admin/login">["searchParams"] }) {
  const sp = await searchParams;
  const error = typeof sp.error === "string" ? messages[sp.error] : undefined;
  if (error) return <p className="mb-4 text-sm text-danger">{error}</p>;
  if (sp.sent) return <p className="mb-4 text-sm">If that email is an admin, a sign-in link is on its way.</p>;
  return null;
}

export default function LoginPage({ searchParams }: PageProps<"/admin/login">) {
  return (
    <div className="max-w-sm">
      <PageHeader title="Admin" />
      <Suspense>
        <Status searchParams={searchParams} />
      </Suspense>
      <form action={sendMagicLink} className="flex gap-2">
        <label htmlFor="admin-email" className="sr-only">
          Email
        </label>
        <input
          id="admin-email"
          name="email"
          type="email"
          required
          autoComplete="email"
          placeholder="email"
          className={`flex-1 ${control.input}`}
        />
        <button type="submit" className={control.button}>
          Send link
        </button>
      </form>
    </div>
  );
}
