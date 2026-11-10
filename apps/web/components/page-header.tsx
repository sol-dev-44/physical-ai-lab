export function PageHeader({ title, intro }: { title: string; intro?: string }) {
  return (
    <div className="mb-8">
      <h1 className="text-2xl font-semibold">{title}</h1>
      {intro ? <p className="mt-2 text-muted">{intro}</p> : null}
    </div>
  );
}
