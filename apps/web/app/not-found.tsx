import Link from "next/link";

export default function NotFound() {
  return (
    <div>
      <h1 className="text-2xl font-semibold">Not found</h1>
      <p className="mt-2 text-muted">
        <Link href="/" className="underline">
          Back home
        </Link>
      </p>
    </div>
  );
}
